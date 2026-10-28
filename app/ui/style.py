"""UzHi Design System: shared semantic tokens, Fusion palettes and widget styles."""
import os
from dataclasses import dataclass
from pathlib import Path
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

@dataclass(frozen=True)
class Tokens:
    base: str
    surface: str
    raised: str
    text: str
    muted: str
    border: str
    accent: str
    selected: str
    danger: str
    sidebar: str = '#0e2339'
    radius: int = 12
    gap: int = 12
    control: int = 36

LIGHT = Tokens('#f2f6f8','#ffffff','#e8f0f3','#172f44','#506779','#d6e2e8','#087f7a','#d9f3ed','#b42335')
DARK = Tokens('#142331','#1d3042','#263e52','#eef6fa','#b2c7d5','#3e566b','#56dfc8','#194e50','#ffabb8')

def tokens():
    app=QApplication.instance()
    return DARK if app and app.property('uzhiTheme')=='dark' else LIGHT

def animations_enabled():
    app=QApplication.instance()
    return bool(app and app.property('uzhiMotion'))

def motion_allowed():
    if os.environ.get('UZHI_REDUCED_MOTION')=='1':return False
    if os.name=='nt':
        try:
            import ctypes
            value=ctypes.c_int(1)
            if ctypes.windll.user32.SystemParametersInfoW(0x1042,0,ctypes.byref(value),0):return bool(value.value)
        except (AttributeError,OSError):pass
    return True

def stylesheet(t):
    sheet='''
QWidget { font-family: 'Noto Sans', 'Segoe UI'; font-size: 12px; color: TEXT; }
QMainWindow, QDialog, QWidget#pageSurface { background: BASE; }
QLabel { background: transparent; }
QLabel#pageTitle { font-size: 24px; font-weight: 700; }
QLabel#subtitle, QLabel#breadcrumb { color: MUTED; }
QLabel#eyebrow { color: ACCENT; font-size: 10px; font-weight: 700; }
QLabel#cardValue { color: ACCENT; font-size: 30px; font-weight: 700; }
QLabel#cardLabel { font-size: 12px; font-weight: 600; }
QLabel#formHeading { font-size: 22px; font-weight: 700; }
QLabel#error { color: DANGER; padding: 8px; border: 1px solid DANGER; border-radius: 7px; }
QFrame#sectionCard, QPushButton#metric, QFrame#emptyState { background: SURFACE; border: 1px solid BORDER; border-radius: 12px; }
QPushButton#metric { text-align: left; min-height: 108px; }
QPushButton#metric:hover, QPushButton#metric:focus { border: 2px solid ACCENT; }
QPushButton#metric:pressed { background: SELECTED; }
QGroupBox { background: SURFACE; border: 1px solid BORDER; border-radius: 12px; margin-top: 18px; padding: 17px 12px 12px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; color: TEXT; }
QPushButton, QToolButton { background: SURFACE; border: 1px solid BORDER; border-radius: 8px; padding: 8px 12px; color: TEXT; min-height: 18px; }
QPushButton:hover, QToolButton:hover { background: RAISED; border-color: ACCENT; }
QPushButton:pressed, QToolButton:pressed { background: SELECTED; }
QPushButton:focus, QToolButton:focus { border: 2px solid ACCENT; padding: 7px 11px; }
QPushButton:disabled, QToolButton:disabled { background: RAISED; color: MUTED; }
QPushButton#primary { background: #087f7a; color: white; border-color: #087f7a; font-weight: 600; }
QPushButton#primary:hover { background: #096b68; border-color: #34d2b6; }
QPushButton#primary:pressed { background: #075653; }
QPushButton#danger { color: DANGER; }
QLineEdit, QTextEdit, QPlainTextEdit, QTextBrowser, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QListWidget { background: SURFACE; color: TEXT; border: 1px solid BORDER; border-radius: 7px; padding: 8px; selection-background-color: SELECTED; selection-color: TEXT; }
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus { border: 2px solid ACCENT; padding: 7px; }
QComboBox QAbstractItemView { background: SURFACE; color: TEXT; selection-background-color: SELECTED; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow, QDateEdit::down-arrow { image: url(RESOURCE/caret-down.svg); width: 12px; height: 12px; }
QSpinBox::up-button, QDoubleSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 24px; border: none; background: RAISED; border-top-right-radius: 7px; }
QSpinBox::down-button, QDoubleSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 24px; border: none; background: RAISED; border-bottom-right-radius: 7px; }
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow { image: url(RESOURCE/caret-up.svg); width: 12px; height: 12px; }
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow { image: url(RESOURCE/caret-down.svg); width: 12px; height: 12px; }
QTableWidget, QTreeView { background: SURFACE; alternate-background-color: BASE; color: TEXT; border: 1px solid BORDER; border-radius: 8px; gridline-color: BORDER; selection-background-color: SELECTED; selection-color: TEXT; outline: none; }
QTableWidget::item { padding: 5px; }
QTableWidget::item:selected { background: SELECTED; color: TEXT; }
QHeaderView::section, QTableCornerButton::section { background: RAISED; color: TEXT; border: none; padding: 9px 6px; font-weight: 600; }
QTabWidget::pane { border: none; }
QTabBar::tab { padding: 10px 16px; background: RAISED; border-radius: 6px; margin-right: 4px; }
QTabBar::tab:selected { background: #087f7a; color: white; }
QStatusBar, QMenuBar { background: SURFACE; color: TEXT; border-bottom: 1px solid BORDER; }
QMenuBar::item { padding: 7px 13px; background: transparent; }
QMenuBar::item:selected, QMenu::item:selected { background: SELECTED; color: TEXT; }
QMenu { background: SURFACE; color: TEXT; border: 1px solid BORDER; padding: 5px; }
QMenu::item { padding: 8px 28px 8px 14px; border-radius: 5px; }
QMenu::item:disabled { color: MUTED; }
QMenu::separator { height: 1px; background: BORDER; margin: 5px; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: BASE; width: 10px; margin: 0; }
QScrollBar:horizontal { background: BASE; height: 10px; margin: 0; }
QScrollBar::handle { background: #8095a5; border: 2px solid BASE; border-radius: 5px; min-height: 24px; min-width: 24px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }
QProgressBar { background: RAISED; border: none; border-radius: 4px; text-align: center; min-height: 19px; color: TEXT; }
QProgressBar::chunk { background: #26b9a0; border-radius: 4px; }
QCheckBox { spacing: 8px; padding: 4px; }
QCheckBox::indicator { width: 16px; height: 16px; }
QToolTip { color: #f4fcff; background: #0e2339; border: 1px solid #42647d; padding: 6px; }
QWidget#sidebar { background: #0e2339; }
QWidget#sidebar QLabel { color: #b4cfdf; }
QWidget#sidebar QLineEdit { background: #19364d; color: #f4fcff; border: 1px solid #42647d; }
QTreeWidget#navigation { background: transparent; color: #d3e3ee; border: none; }
QTreeWidget#navigation::item { padding: 9px 5px; margin: 1px 0; border-radius: 6px; }
QTreeWidget#navigation::branch { background: #0e2339; }
QTreeWidget#navigation::branch:selected { background: #0e2339; }
QWidget#sidebar QScrollBar { background: #0e2339; }
QWidget#sidebar QScrollBar::handle { background: #42647d; border-color: #0e2339; }
QTreeWidget#navigation::item:hover { background: #1a3c55; }
QTreeWidget#navigation::item:selected { background: #155451; color: white; border-left: 3px solid #34d2b6; }
QWidget#sidebar QToolButton { background: #19364d; color: #e8faff; border-color: #42647d; }
QFrame#hero, QFrame#authBrand { background: transparent; }
QFrame#hero QLabel, QFrame#authBrand QLabel { color: #f1fbff; }
QFrame#hero QLabel#subtitle, QFrame#authBrand QLabel#subtitle { color: #b9d5e2; }
QFrame#hero QPushButton { background: #16465a; color: white; border-color: #4b7c88; }
QFrame#hero QPushButton#primary { background: #34d2b6; color: #082c3c; border-color: #34d2b6; }
QFrame#toast { background: #0e4a47; border: 1px solid #34d2b6; border-radius: 9px; }
QFrame#toast QLabel { color: white; }
'''
    for name,value in {'SELECTED':t.selected,'SURFACE':t.surface,'BORDER':t.border,'RAISED':t.raised,'BASE':t.base,'TEXT':t.text,'MUTED':t.muted,'ACCENT':t.accent,'DANGER':t.danger}.items():sheet=sheet.replace(name,value)
    return sheet.replace("RESOURCE",(Path(__file__).resolve().parents[1]/"resources").as_posix())

def apply_theme(application,name='light'):
    name='dark' if name=='dark' else 'light'
    t=DARK if name=='dark' else LIGHT
    palette=QPalette()
    roles={'Window':t.base,'WindowText':t.text,'Base':t.surface,'AlternateBase':t.base,'Text':t.text,'Button':t.surface,'ButtonText':t.text,'Highlight':t.selected,'HighlightedText':t.text,'ToolTipBase':t.sidebar,'ToolTipText':'#ffffff','PlaceholderText':t.muted,'Link':t.accent,'BrightText':t.danger}
    for role,color in roles.items():palette.setColor(getattr(QPalette.ColorRole,role),QColor(color))
    for role in (QPalette.ColorRole.Text,QPalette.ColorRole.ButtonText,QPalette.ColorRole.WindowText):palette.setColor(QPalette.ColorGroup.Disabled,role,QColor(t.muted))
    application.setProperty('uzhiTheme',name)
    application.setPalette(palette)
    application.setFont(QFont('Noto Sans',10))
    application.setStyleSheet(stylesheet(t))

STYLE=stylesheet(LIGHT)
