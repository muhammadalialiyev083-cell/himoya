STYLE = """
* { font-family: 'Segoe UI', 'DejaVu Sans'; font-size: 12px; }
QMainWindow, QDialog { background: #f3f6fa; color: #182e43; }
QWidget#sidebar { background: #102b40; }
QLabel#brand { color: white; font-size: 23px; font-weight: 700; }
QLabel#brandSub { color: #90babd; font-size: 11px; }
QLabel#ornament { color: #35b2a0; font-size: 17px; }
QListWidget#nav { background: transparent; border: none; outline: none; color: #bdcfdc; }
QListWidget#nav::item { padding: 13px 10px; margin: 3px 8px; border-radius: 7px; }
QListWidget#nav::item:selected { background: #175346; color: #e4fff6; border-left: 3px solid #48d6ad; }
QListWidget#nav::item:hover { background: #193e54; }
QLabel#pageTitle { font-size: 25px; font-weight: 700; color: #122f45; }
QLabel#subtitle { color: #627889; }
QLabel#cardValue { font-size: 27px; font-weight: 700; color: #087f70; }
QLabel#cardLabel { color: #627889; font-size: 11px; }
QFrame#card, QGroupBox { background: white; border: 1px solid #dce5ed; border-radius: 9px; }
QGroupBox { margin-top: 16px; padding: 15px 10px 10px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 5px; }
QPushButton { padding: 8px 13px; border-radius: 6px; background: white; border: 1px solid #ccd9e2; color: #254156; }
QPushButton:hover { background: #e5f1ef; border-color: #42a18d; }
QPushButton:disabled { color: #8897a2; background: #ebeff3; }
QPushButton#primary { background: #087f70; color: white; border-color: #087f70; font-weight: 600; }
QPushButton#primary:hover { background: #096c60; }
QPushButton#danger { color: #b42335; }
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit { background: white; color: #182e43; padding: 7px; border: 1px solid #cbd8e1; border-radius: 5px; selection-background-color: #087f70; }
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDoubleSpinBox:focus { border-color: #087f70; }
QTableWidget { background: white; alternate-background-color: #f5f8fa; border: 1px solid #dce5ed; border-radius: 7px; gridline-color: #edf1f5; selection-background-color: #d5eee7; selection-color: #102b40; }
QHeaderView::section { background: #eaf0f5; color: #425e72; padding: 10px 6px; border: none; border-bottom: 1px solid #dae3eb; font-weight: 600; }
QTabWidget::pane { border: none; }
QTabBar::tab { padding: 10px 18px; background: #e5ecf1; border-radius: 4px; margin-right: 4px; }
QTabBar::tab:selected { background: #087f70; color: white; }
QStatusBar { background: #e9f0f5; color: #3b5b6e; }
QScrollArea { border: none; background: transparent; }
QProgressBar { border: none; border-radius: 4px; background: #e5edf3; text-align: center; min-height: 19px; color: #173d4b; }
QProgressBar::chunk { background: #68cbb1; border-radius: 4px; }
QToolTip { color: white; background: #102b40; border: none; padding: 5px; }
"""
