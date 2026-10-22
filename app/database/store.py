"""SQLite lifecycle and validated, recoverable backups."""
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1


class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = self._open()
        try:
            version = self.conn.execute("PRAGMA user_version").fetchone()[0]
            if version > SCHEMA_VERSION:
                raise ValueError("Baza yangi dastur versiyasiga tegishli. Yangilangan dasturni ishlating.")
            if version == 0:
                if self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchone():
                    raise ValueError("Noma’lum baza formati; avtomatik almashtirish bekor qilindi.")
                schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
                try:
                    self.conn.executescript("BEGIN IMMEDIATE;\n" + schema + "\nCOMMIT;")
                except Exception:
                    self.conn.rollback()
                    raise
            # Future migrations must back up first and run in one transaction.
            self._check(self.conn)
        except Exception:
            self.conn.close()
            raise

    def _open(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    @staticmethod
    def _check(conn):
        if conn.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
            raise ValueError("Zaxira nusxasi versiyasi mos emas.")
        if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Baza yaxlitligi buzilgan.")
        if conn.execute("PRAGMA foreign_key_check").fetchone():
            raise ValueError("Bazada buzilgan bog‘lanishlar mavjud.")
        # Match all column definitions and foreign keys against the authoritative schema.
        expected = sqlite3.connect(":memory:")
        try:
            expected.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))
            names = [r[0] for r in expected.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            actual = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if set(names) != actual:
                raise ValueError("Baza jadval tuzilmasi mos emas.")
            for name in names:
                saved_sql = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()[0]
                expected_sql = expected.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()[0]
                if saved_sql != expected_sql:
                    raise ValueError("Baza cheklovlari mos emas.")
                for pragma in ("table_info", "foreign_key_list"):
                    left = [tuple(r) for r in conn.execute(f'PRAGMA {pragma}("{name}")')]
                    right = list(expected.execute(f'PRAGMA {pragma}("{name}")'))
                    if left != right:
                        raise ValueError("Baza ustunlari yoki bog‘lanishlari mos emas.")
            if conn.execute("SELECT name FROM sqlite_master WHERE type IN ('trigger','view')").fetchone():
                raise ValueError("Noma’lum baza kengaytmalari mavjud.")
            admin = conn.execute("SELECT salt,password_hash,iterations FROM admin WHERE id=1").fetchone()
            if admin:
                try:
                    if len(bytes.fromhex(admin[0])) != 32 or len(bytes.fromhex(admin[1])) != 32 or not 100_000 <= admin[2] <= 2_000_000:
                        raise ValueError
                except (ValueError, TypeError):
                    raise ValueError("Administrator hisobi formati buzilgan.") from None
        finally:
            expected.close()

    def backup(self, destination):
        destination = Path(destination)
        if destination.resolve() == self.path.resolve():
            raise ValueError("Zaxira uchun boshqa faylni tanlang.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix="bcms-backup-", suffix=".sqlite3", dir=destination.parent)
        os.close(fd)
        try:
            target = sqlite3.connect(tmp)
            try:
                self.conn.backup(target)
                self._check(target)
            finally:
                target.close()
            os.replace(tmp, destination)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return destination

    def restore(self, source):
        source = Path(source)
        if not source.is_file() or source.resolve() == self.path.resolve():
            raise ValueError("Boshqa, mavjud zaxira faylini tanlang.")
        candidate = sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            self._check(candidate)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
            safety = self.backup(self.path.parent / "backups" / f"before-restore-{stamp}.sqlite3")
            fd, temp = tempfile.mkstemp(dir=self.path.parent, suffix=".sqlite3")
            os.close(fd)
            try:
                target = sqlite3.connect(temp)
                try:
                    candidate.backup(target)
                    self._check(target)
                finally:
                    target.close()
                self.conn.close()
                try:
                    os.replace(temp, self.path)
                finally:
                    self.conn = self._open()
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)
            return safety
        finally:
            candidate.close()

    def close(self):
        self.conn.close()
