import hashlib
import hmac
import secrets

ITERATIONS = 600_000


class Authentication:
    def __init__(self, db):
        self.db = db

    def configured(self):
        return self.db.conn.execute("SELECT 1 FROM admin WHERE id=1").fetchone() is not None

    def create(self, username, password):
        username = username.strip()
        if not username or len(username) > 100:
            raise ValueError("Administrator nomini kiriting (1–100 belgi).")
        if len(password) < 10 or len(password) > 1024:
            raise ValueError("Parol 10–1024 belgidan iborat bo‘lsin.")
        if self.configured():
            raise ValueError("Administrator allaqachon yaratilgan.")
        salt = secrets.token_hex(32)
        digest = self._hash(password, salt, ITERATIONS)
        with self.db.conn:
            self.db.conn.execute("INSERT INTO admin VALUES(1,?,?,?,?)", (username, salt, digest, ITERATIONS))

    @staticmethod
    def _hash(password, salt, iterations):
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations).hex()

    def verify(self, username, password):
        row = self.db.conn.execute("SELECT * FROM admin WHERE id=1").fetchone()
        if row is None or len(password) > 1024:
            return False
        try:
            iterations = int(row["iterations"])
            if not 100_000 <= iterations <= 2_000_000:
                return False
            digest = self._hash(password, row["salt"], iterations)
        except (ValueError, TypeError):
            return False
        try:
            return hmac.compare_digest(digest, row["password_hash"]) and hmac.compare_digest(username.strip().encode(), row["username"].encode())
        except (TypeError, AttributeError):
            return False

    def change_password(self, username, old, new):
        if not self.verify(username, old):
            raise ValueError("Amaldagi hisob yoki parol noto‘g‘ri.")
        if not 10 <= len(new) <= 1024:
            raise ValueError("Yangi parol 10–1024 belgidan iborat bo‘lsin.")
        salt = secrets.token_hex(32)
        with self.db.conn:
            self.db.conn.execute("UPDATE admin SET salt=?, password_hash=?, iterations=? WHERE id=1",
                                 (salt, self._hash(new, salt, ITERATIONS), ITERATIONS))
