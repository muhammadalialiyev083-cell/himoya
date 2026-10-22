import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
from pathlib import Path
import pytest
from PySide6.QtWidgets import QApplication
from app.database.store import Database
from app.services.bcms import BCMS
from app.ui.style import STYLE
from app.core.fonts import report_font


@pytest.fixture(scope="session")
def qapp():
    application=QApplication.instance() or QApplication([])
    report_font()
    application.setStyle("Fusion")
    application.setStyleSheet(STYLE)
    yield application


@pytest.fixture
def db(tmp_path):
    database=Database(tmp_path/"test.sqlite3")
    yield database
    database.close()


@pytest.fixture
def service(db):
    return BCMS(db)


@pytest.fixture
def populated(service):
    from app.services.demo import add_demo
    add_demo(service)
    return service
