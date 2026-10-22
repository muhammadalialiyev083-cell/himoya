"""A bundled, licensed font makes offline/offscreen PDF output portable."""
from functools import lru_cache
from pathlib import Path
from PySide6.QtGui import QFontDatabase


@lru_cache(maxsize=1)
def report_font():
    path = Path(__file__).resolve().parents[1] / "resources/fonts/NotoSans-Regular.ttf"
    font_id = QFontDatabase.addApplicationFont(str(path))
    families = QFontDatabase.applicationFontFamilies(font_id) if font_id >= 0 else []
    if not families:
        raise RuntimeError("Hisobot shrifti yuklanmadi; dastur resurslarini tekshiring.")
    return families[0]
