"""Desktop entry point. Mutable data never lives alongside the frozen executable."""
import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

if not getattr(sys,"frozen",False):
    sys.path.insert(0,str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QLockFile, QSettings
from app.core.config import data_directory
from app.core.fonts import report_font
from app.database.store import Database
from app.services.auth import Authentication
from app.ui.forms import authenticate
from app.ui.style import apply_theme, motion_allowed
from app.ui.window import MainWindow


def main():
    parser=argparse.ArgumentParser(description="UzluksizBCMS Desktop 1.1.0")
    parser.add_argument("--self-test-dir",type=Path,help="Run isolated packaged smoke test in a new directory")
    parser.add_argument("--self-test-restart-dir",type=Path,help="Verify persistence of an existing isolated self-test")
    args=parser.parse_args()
    application=QApplication(sys.argv[:1])
    report_font()
    application.setApplicationName("UzluksizBCMS")
    application.setOrganizationName("UzluksizBCMS")
    application.setStyle("Fusion")
    apply_theme(application,"light")
    application.setProperty("uzhiMotion",motion_allowed())
    if args.self_test_restart_dir:
        from app.core.smoke import run_restart_smoke
        return run_restart_smoke(application,args.self_test_restart_dir)
    if args.self_test_dir:
        from app.core.smoke import run_smoke
        return run_smoke(application,args.self_test_dir)
    root=data_directory()
    preferences=QSettings(str(root/"ui.ini"),QSettings.Format.IniFormat)
    apply_theme(application,preferences.value("appearance/theme","light"))
    application.setProperty("uzhiMotion",preferences.value("appearance/motion",True,type=bool) and motion_allowed())
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
        logging.info("Application session started; version 1.1.0")
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
