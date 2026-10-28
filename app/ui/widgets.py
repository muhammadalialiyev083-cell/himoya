from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtWidgets import (QAbstractItemView, QFrame, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView)

from app.algorithms.scoring import COLORS, risk_score
from app.ui.style import tokens


def button(text, action, primary=False, name=None):
    b = QPushButton(text)
    if primary:
        b.setObjectName("primary")
    elif name:
        b.setObjectName(name)
    b.clicked.connect(action)
    return b


def setup_table(table):
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.setWordWrap(False)
    table.setSortingEnabled(False)
    table.horizontalHeader().setStretchLastSection(True)
    table.verticalHeader().setDefaultSectionSize(38)


class Bars(QWidget):
    def __init__(self, maximum=100, parent=None):
        super().__init__(parent)
        self.maximum, self.rows = maximum, []
        self.setMinimumHeight(150)

    def set_rows(self, rows):
        self.rows = rows[:8]
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.rows:
            p.setPen(QColor(tokens().muted))
            p.drawText(self.rect().adjusted(8,8,-8,-8), Qt.AlignmentFlag.AlignCenter|Qt.TextFlag.TextWordWrap,"Tahlil kiritilgach, haqiqiy ma’lumotlar diagrammasi ko‘rinadi.")
            return
        label_width = min(180, int(self.width()*.40))
        row_height = min(36, max(23,self.height()//len(self.rows)))
        available = max(20,self.width()-label_width-60)
        for i,(name,value,color) in enumerate(self.rows):
            y = i*row_height+6
            p.setPen(QColor(tokens().text))
            label = p.fontMetrics().elidedText(name,Qt.TextElideMode.ElideRight,label_width-8)
            p.drawText(0,y+15,label)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(tokens().raised))
            p.drawRoundedRect(label_width,y,available,20,4,4)
            p.setBrush(QColor(color))
            p.drawRoundedRect(label_width,y,int(available*min(value/self.maximum,1)),20,4,4)
            p.setPen(QColor(tokens().text))
            p.drawText(label_width+available+7,y+15,f"{value:g}")


class RiskMatrix(QTableWidget):
    def __init__(self):
        super().__init__(5,5)
        self.setHorizontalHeaderLabels([f"Ta’sir {i}" for i in range(1,6)])
        self.setVerticalHeaderLabels([str(i) for i in range(5,0,-1)])
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setMaximumHeight(220)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setMinimumHeight(205)
        self.update_risks([])

    def update_risks(self, risks):
        for row in range(5):
            likelihood = 5-row
            for col in range(5):
                impact = col+1
                matches = [r for r in risks if r["likelihood"]==likelihood and r["impact"]==impact]
                score, category = risk_score(likelihood,impact)
                item = QTableWidgetItem(f"{score}  ·  {len(matches)} ta")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(QColor(COLORS[category]))
                item.setForeground(QColor("white"))
                item.setToolTip("\n".join(r["title"] for r in matches) or "Bu katakda risk yo‘q")
                self.setItem(row,col,item)


class StepEditor(QWidget):
    def __init__(self, steps=None):
        super().__init__()
        v = QVBoxLayout(self)
        v.setContentsMargins(0,0,0,0)
        v.addWidget(QLabel("Tiklash tartibi • matnni tahrirlang, bajarilganini belgilang"))
        self.table = QTableWidget(0,2)
        self.table.setHorizontalHeaderLabels(["Amal / tartib","Bajarildi"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.ResizeToContents)
        self.table.setMaximumHeight(140)
        v.addWidget(self.table)
        h=QHBoxLayout()
        h.addWidget(button("+ Bosqich",self.add))
        h.addWidget(button("↑",lambda:self.move(-1)))
        h.addWidget(button("↓",lambda:self.move(1)))
        h.addWidget(button("O‘chirish",self.remove))
        h.addStretch()
        v.addLayout(h)
        for step in steps or []:
            self.add(step=step)

    def add(self, checked=False, step=None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row,0,QTableWidgetItem(step["instruction"] if step else ""))
        completed = QTableWidgetItem()
        completed.setFlags(Qt.ItemFlag.ItemIsEnabled|Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsUserCheckable)
        completed.setCheckState(Qt.CheckState.Checked if step and step["completed"] else Qt.CheckState.Unchecked)
        self.table.setItem(row,1,completed)
        self.table.setCurrentCell(row,0)

    def remove(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def move(self, delta):
        row = self.table.currentRow()
        target = row+delta
        if row < 0 or not 0<=target<self.table.rowCount():
            return
        for col in range(2):
            a,b=self.table.takeItem(row,col),self.table.takeItem(target,col)
            self.table.setItem(row,col,b)
            self.table.setItem(target,col,a)
        self.table.setCurrentCell(target,0)

    def values(self):
        return [{"instruction":self.table.item(i,0).text(), "completed":self.table.item(i,1).checkState()==Qt.CheckState.Checked} for i in range(self.table.rowCount())]
