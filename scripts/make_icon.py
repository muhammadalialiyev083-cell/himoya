"""Render the bundled vector icon into a 256-pixel Windows ICO."""
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

root=Path(__file__).resolve().parent.parent
app=QApplication.instance() or QApplication([])
(root/"assets").mkdir(exist_ok=True)
icon=QIcon(str(root/"app/resources/icon.svg"))
if not icon.pixmap(256,256).save(str(root/"assets/UzluksizBCMS.ico"),"ICO"):
    raise SystemExit("Qt ICO writer failed")
