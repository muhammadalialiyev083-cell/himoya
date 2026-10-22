"""Desktop entry point. Mutable data never lives alongside the frozen executable."""
import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

if not getattr(sys,"frozen",False):
    sys.path.insert(0,str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QLockFile
from app.core.config import data_directory
from app.core.fonts import report_font
from app.database.store import Database
from app.services.auth import Authentication
from app.ui.forms import authenticate
from app.ui.style import STYLE
from app.ui.window import MainWindow


def main():
    parser=argparse.ArgumentParser(description="UzluksizBCMS Desktop 1.0.0")
    parser.add_argument("--self-test-dir",type=Path,help="Run isolated packaged smoke test in a new directory")
    args=parser.parse_args()
    application=QApplication(sys.argv[:1])
    report_font()
    application.setApplicationName("UzluksizBCMS")
    application.setOrganizationName("UzluksizBCMS")
    application.setStyle("Fusion")
    application.setStyleSheet(STYLE)
    if args.self_test_dir:
        from app.core.smoke import run_smoke
        return run_smoke(application,args.self_test_dir)
    root=data_directory()
    lock=QLockFile(str(root/"application.lock"))
    if not lock.tryLock(100):
        QMessageBox.warning(None,"UzluksizBCMS","Ushbu baza uchun dastur allaqachon ochilgan. Avval ochilgan oynadan foydalaning.")
        return 1
    handler=RotatingFileHandler(root/"application.log",maxBytes=512000,backupCount=2,encoding="utf-8")
    logging.basicConfig(level=logging.INFO,handlers=[handler],format="%(asctime)s %(levelname)s %(message)s")
    db=None
    try:
        db=Database(root/"uzluksiz.sqlite3")
        if not authenticate(Authentication(db)):return 0
        window=MainWindow(db)
        window.show()
        logging.info("Application session started; version 1.0.0")
        return application.exec()
    except Exception:
        # Do not write user fields or secret-bearing exception details to logs.
        logging.error("Application startup or session failed")
        QMessageBox.critical(None,"UzluksizBCMS","Dastur ishga tushmadi. Baza formati, yozish ruxsati va bo‘sh joyni tekshiring. Yangi versiya bazasini eski dastur bilan ochmang.")
        return 1
    finally:
        if db:db.close()


if __name__=="__main__":
    raise SystemExit(main())
