from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFormLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPlainTextEdit, QScrollArea, QSpinBox, QVBoxLayout, QWidget)


class FormDialog(QDialog):
    """Scrollable validated form; reference selectors carry actual integer keys."""
    def __init__(self, title, fields, values=None, parent=None, note=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(620, 620)
        self.setMinimumSize(480, 350)
        self.fields, self.widgets = fields, {}
        layout = QVBoxLayout(self)
        if note:
            label = QLabel(note)
            label.setWordWrap(True)
            layout.addWidget(label)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form = QFormLayout(content)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
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
            w.setObjectName(key)
            self.widgets[key] = w
            form.addRow(label, w)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Saqlash")
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName("primary")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Bekor qilish")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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


def authenticate(auth, parent=None):
    first = not auth.configured()
    fields = [("username","Administrator nomi","line",None),("password","Parol","password",None)]
    if first:
        fields.append(("confirm","Parolni takrorlang","password",None))
    dlg = FormDialog("Administrator yaratish" if first else "UzluksizBCMS — Kirish", fields, parent=parent,
                     note="Birinchi ishga tushirish. Kamida 10 belgili parol yarating." if first else "Mahalliy administrator hisobi bilan kiring.")
    dlg.resize(500,360)
    while dlg.exec() == QDialog.DialogCode.Accepted:
        values = dlg.values()
        try:
            if first:
                if values["password"] != values["confirm"]:
                    raise ValueError("Parollar mos kelmadi.")
                auth.create(values["username"],values["password"])
            elif not auth.verify(values["username"],values["password"]):
                raise ValueError("Hisob yoki parol noto‘g‘ri.")
            return True
        except ValueError as exc:
            QMessageBox.warning(dlg,"Kirish",str(exc))
            dlg.widgets["password"].clear()
    return False
