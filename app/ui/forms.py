from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QAction, QIcon
from pathlib import Path
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton,
    QMessageBox, QPlainTextEdit, QScrollArea, QSpinBox, QVBoxLayout, QWidget)

from app.ui.components import GradientPanel, UzHiLogo, FormSection, label
from app.ui.icons import icon


def password_toggle(widget):
    widget.setMaxLength(1024)
    action=QAction(icon("eye"),"Parolni ko‘rsatish",widget)
    action.setCheckable(True)
    def toggle(visible):
        widget.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password)
        action.setText("Parolni yashirish" if visible else "Parolni ko‘rsatish")
        action.setIcon(icon("eye-off" if visible else "eye"))
    action.toggled.connect(toggle)
    widget.addAction(action,QLineEdit.ActionPosition.TrailingPosition)
    return action


class FormDialog(QDialog):
    """Scrollable validated form; reference selectors carry actual integer keys."""
    def __init__(self, title, fields, values=None, parent=None, note=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(620, 620)
        self.setMinimumSize(480, 350)
        self.fields, self.widgets = fields, {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22,20,22,20)
        layout.setSpacing(12)
        heading=QLabel(title)
        heading.setObjectName("formHeading")
        heading.setWordWrap(True)
        layout.addWidget(heading)
        if note:
            label = QLabel(note)
            label.setWordWrap(True)
            layout.addWidget(label)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = FormSection()
        form = content.form
        values = values or {}
        for key, label, kind, options in fields:
            value = values.get(key)
            if kind == "text":
                w = QPlainTextEdit(str(value or ""))
                w.setMaximumHeight(76)
            elif kind == "choice":
                w = QComboBox()
                for caption, data in options:
                    w.addItem(str(caption), data)
                idx = w.findData(value)
                if idx >= 0:
                    w.setCurrentIndex(idx)
            elif kind in ("integer", "number", "impact"):
                w = QSpinBox() if kind == "integer" else QDoubleSpinBox()
                w.setRange(*options)
                if kind != "integer":
                    w.setDecimals(2)
                w.setValue(value if value is not None else options[0])
            elif kind == "date":
                w = QDateEdit()
                w.setCalendarPopup(True)
                w.setDisplayFormat("yyyy-MM-dd")
                qdate = QDate.fromString(str(value), "yyyy-MM-dd") if value else QDate.currentDate()
                w.setDate(qdate)
            elif kind == "multi":
                w = QListWidget()
                w.setMaximumHeight(145)
                for caption, data in options:
                    item = QListWidgetItem(str(caption))
                    item.setData(Qt.ItemDataRole.UserRole, data)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Checked if data in (value or []) else Qt.CheckState.Unchecked)
                    w.addItem(item)
            else:
                w = QLineEdit(str(value or ""))
                w.setMaxLength(500)
                if kind == "password":
                    w.setEchoMode(QLineEdit.EchoMode.Password)
                    password_toggle(w)
            w.setObjectName(key)
            self.widgets[key] = w
            caption=QLabel(label)
            caption.setBuddy(w)
            form.addRow(caption, w)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.error=QLabel();self.error.setObjectName("error");self.error.setWordWrap(True);self.error.hide()
        layout.addWidget(self.error)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Saqlash")
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName("primary")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Bekor qilish")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def showEvent(self,event):
        super().showEvent(event)
        available=self.screen().availableGeometry()
        self.resize(min(self.width(),available.width()-32),min(self.height(),available.height()-48))

    def accept(self):
        values=self.values()
        for key,caption,kind,options in self.fields:
            if '*' in caption and (values[key] is None or (isinstance(values[key],str) and not values[key].strip()) or (kind=='multi' and not values[key])):
                self.error.setText(caption.replace('*','').strip()+': majburiy maydon.');self.error.show()
                self.widgets[key].setFocus();return
        super().accept()

    def values(self):
        out = {}
        for key, label, kind, options in self.fields:
            w = self.widgets[key]
            if kind == "choice":
                value = w.currentData()
            elif kind in ("integer", "number", "impact"):
                value = w.value()
            elif kind == "text":
                value = w.toPlainText()
            elif kind == "date":
                value = w.date().toString("yyyy-MM-dd")
            elif kind == "multi":
                value = [w.item(i).data(Qt.ItemDataRole.UserRole) for i in range(w.count()) if w.item(i).checkState() == Qt.CheckState.Checked]
            else:
                value = w.text()
            out[key] = value
        return out


class LoginDialog(FormDialog):
    """Dedicated authentication layout; success is granted only by Authentication."""
    def __init__(self,auth,parent=None):
        QDialog.__init__(self,parent)
        self.auth=auth
        self.first=not auth.configured()
        self.setWindowTitle('UzHi — Administrator yaratish' if self.first else 'UzHi — Kirish')
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parents[1]/"resources/icon.svg")))
        self.resize(880,560);self.setMinimumSize(680,420)
        self.fields=[('username','Administrator nomi','line',None),('password','Parol','password',None)]
        if self.first:self.fields.append(('confirm','Parolni takrorlang','password',None))
        self.widgets={};self.password_actions={}
        layout=QHBoxLayout(self);layout.setContentsMargins(16,16,16,16);layout.setSpacing(24)
        brand=GradientPanel(name='authBrand');left=QVBoxLayout(brand);left.setContentsMargins(28,24,28,24);left.setSpacing(16)
        left.addWidget(UzHiLogo());left.addStretch()
        left.addWidget(label('Har bir jarayon.\nUzluksiz himoya.','pageTitle',True))
        left.addWidget(label('Biznes uzluksizligi va risklarni boshqarish','subtitle',True))
        left.addWidget(label('Jarayonlar  →  BIA  →  Risklar\nTiklash rejasi  →  Ssenariylar','subtitle',True))
        left.addStretch()
        left.addWidget(label('MAHALLIY ISH MUHITI\nMa’lumotlar shu qurilmadagi SQLite bazada saqlanadi.','subtitle',True))
        layout.addWidget(brand,1)
        card=QWidget();right=QVBoxLayout(card);right.setContentsMargins(0,14,14,14);right.setSpacing(10)
        right.addStretch()
        right.addWidget(label('UzHi — Uzluksiz Himoya','formHeading',True))
        right.addWidget(label('Administrator yaratish' if self.first else 'Xush kelibsiz','cardLabel'))
        right.addWidget(label('Birinchi ishga tushirish. Kamida 10 belgili parol yarating.' if self.first else 'Mahalliy administrator hisobi bilan kiring.','subtitle',True))
        for key,caption,kind,_ in self.fields:
            field=QLineEdit();field.setObjectName(key);field.setMinimumHeight(25)
            field.setMaxLength(100 if key=='username' else 1024)
            field.setAccessibleName(caption)
            if kind=='password':
                field.setEchoMode(QLineEdit.EchoMode.Password)
                self.password_actions[key]=password_toggle(field)
            caption_label=label(caption);caption_label.setBuddy(field)
            right.addWidget(caption_label);right.addWidget(field)
            self.widgets[key]=field
        self.error=label('','error',True);self.error.hide();right.addWidget(self.error)
        self.submit=QPushButton('Administrator yaratish' if self.first else 'Kirish')
        self.submit.setObjectName('primary');self.submit.setDefault(True);self.submit.clicked.connect(self.accept)
        right.addWidget(self.submit)
        cancel=QPushButton('Bekor qilish');cancel.clicked.connect(self.reject);right.addWidget(cancel)
        right.addWidget(label('Parol tuzlangan PBKDF2-SHA256 xeshi bilan tekshiriladi.','subtitle',True))
        right.addStretch()
        form_scroll=QScrollArea();form_scroll.setWidgetResizable(True);form_scroll.setWidget(card)
        layout.addWidget(form_scroll,1)
        self.widgets['username'].setFocus()

    def accept(self):
        values=self.values()
        try:
            if not values['username'].strip() or not values['password']:
                raise ValueError('Administrator nomi va parolni kiriting.')
            if self.first:
                if values['password']!=values['confirm']:raise ValueError('Parollar mos kelmadi.')
                self.auth.create(values['username'],values['password'])
            elif not self.auth.verify(values['username'],values['password']):
                raise ValueError('Hisob yoki parol noto‘g‘ri.')
        except ValueError as exc:
            self.error.setText(str(exc));self.error.show()
            self.widgets['password'].clear()
            if 'confirm' in self.widgets:self.widgets['confirm'].clear()
            self.widgets['password'].setFocus()
            return
        # Do not retain cleartext passwords after authentication.
        for key in ('password','confirm'):
            if key in self.widgets:self.widgets[key].clear()
        QDialog.accept(self)


def authenticate(auth,parent=None):
    return LoginDialog(auth,parent).exec()==QDialog.DialogCode.Accepted
