"""Reusable native UzHi components. No web runtime or network assets."""
from pathlib import Path
from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QAbstractButton, QFrame, QHBoxLayout, QLabel, QPushButton,
                              QToolButton, QVBoxLayout, QWidget, QSizePolicy)
from app.ui.icons import icon
from app.ui.style import animations_enabled, tokens

RESOURCES=Path(__file__).resolve().parents[1]/'resources'


def label(text='',name='',wrap=False):
    widget=QLabel(text)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    widget.setObjectName(name)
    widget.setWordWrap(wrap)
    return widget


class UzHiLogo(QAbstractButton):
    """Original shield/infinity with a finite, clipped expanding wordmark."""
    def __init__(self,parent=None,compact=False):
        super().__init__(parent)
        self.renderer=QSvgRenderer(str(RESOURCES/'uzhi-mark.svg'),self)
        self.compact=compact
        self._reveal=0.0
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName('UzHi — Uzluksiz Himoya')
        self.setToolTip('UzHi — Uzluksiz Himoya. Nomni ochish yoki yig‘ish.')
        self.setMinimumHeight(56)
        self.animation=QPropertyAnimation(self,b'reveal',self)
        self.animation.setDuration(320)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.toggled.connect(self.animate)

    def sizeHint(self):return QSize(260,60)
    def get_reveal(self):return self._reveal
    def set_reveal(self,value):self._reveal=value;self.update()
    reveal=Property(float,get_reveal,set_reveal)

    def animate(self,expanded):
        self.animation.stop()
        if animations_enabled():
            self.animation.setStartValue(self._reveal)
            self.animation.setEndValue(1.0 if expanded else 0.0)
            self.animation.start()
        else:self.set_reveal(1.0 if expanded else 0.0)

    def enterEvent(self,event):
        if not self.compact:self.animate(True)
        super().enterEvent(event)

    def leaveEvent(self,event):
        if not self.isChecked():self.animate(False)
        super().leaveEvent(event)

    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.renderer.render(p,QRectF(2,6,44,44))
        if not self.compact:
            p.setClipRect(54,0,max(0,self.width()-54),self.height())
            font=QFont('Noto Sans',18,QFont.Weight.Bold)
            p.setFont(font)
            fm=p.fontMetrics()
            x=56.0
            for word,color,fraction in [('Uz','#ffffff',1),('luksiz ','#e2e8f0',self._reveal),('Hi','#5ffbf1',1),('moya','#00d2d3',self._reveal)]:
                width=fm.horizontalAdvance(word)
                p.save();p.setClipRect(QRectF(x,0,width*fraction,self.height()),Qt.ClipOperation.IntersectClip)
                p.setPen(QColor(color));p.drawText(QRectF(x,5,width,34),Qt.AlignmentFlag.AlignVCenter,word);p.restore()
                x+=width*fraction
            p.setFont(QFont('Noto Sans',8));p.setPen(QColor('#b9d5e2'))
            p.drawText(56,49,'RISKGUARD  /  UZLUKSIZ HIMOYA')
        if self.hasFocus():
            p.setClipping(False);p.setPen(QPen(QColor('#5ffbf1'),2));p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(self.rect().adjusted(1,1,-1,-1),6,6)


class GradientPanel(QFrame):
    def __init__(self,parent=None,name='hero'):
        super().__init__(parent);self.setObjectName(name)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient=QLinearGradient(0,0,self.width(),self.height())
        gradient.setColorAt(0,QColor('#09223d'));gradient.setColorAt(.55,QColor('#0f3554'));gradient.setColorAt(1,QColor('#07535c'))
        p.setBrush(gradient);p.setPen(QPen(QColor('#29737b'),1))
        p.drawRoundedRect(self.rect().adjusted(1,1,-1,-1),16,16)
        p.setClipRect(self.rect().adjusted(12,12,-12,-12))
        p.setPen(QPen(QColor(100,220,204,28),1))
        for radius in (85,120,155):p.drawEllipse(QRectF(self.width()-radius-40,-radius+40,radius*2,radius*2))
        p.setPen(QColor(220,255,250,22))
        for x in range(max(0,self.width()-330),self.width(),24):
            for y in range(18,self.height(),24):p.drawPoint(x,y)


class IconButton(QToolButton):
    def __init__(self,name,title,action,parent=None):
        super().__init__(parent)
        self.setProperty('uzhiIcon',name);self.setIcon(icon(name,tokens().accent));self.setIconSize(QSize(20,20))
        self.setToolTip(title);self.setAccessibleName(title);self.setFixedSize(38,36)
        self.clicked.connect(action)


class PageHeader(QWidget):
    def __init__(self,back,forward,home,parent=None):
        super().__init__(parent)
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(8)
        row=QHBoxLayout()
        self.back=IconButton('back','Orqaga (Alt+Left)',back)
        self.forward=IconButton('forward','Oldinga (Alt+Right)',forward)
        row.addWidget(self.back);row.addWidget(self.forward)
        dashboard=QPushButton('Bosh sahifa');dashboard.setFlat(True);dashboard.clicked.connect(home)
        row.addWidget(dashboard)
        self.breadcrumb=label('','breadcrumb');row.addWidget(self.breadcrumb,1)
        self.quick=QPushButton('');self.quick.setObjectName('primary');row.addWidget(self.quick)
        layout.addLayout(row)
        heading=QHBoxLayout()
        self.page_icon=QLabel();self.page_icon.setFixedSize(28,28);heading.addWidget(self.page_icon)
        self.title=label('','pageTitle');heading.addWidget(self.title,1)
        layout.addLayout(heading)

    def set_page(self,title,category,icon_name):
        self.title.setText(title)
        self.breadcrumb.setText('›  '+category+'  ›  '+title)
        self.breadcrumb.setToolTip(category+' / '+title)
        self.page_icon.setPixmap(icon(icon_name,tokens().accent).pixmap(26,26))


class SectionCard(QFrame):
    def __init__(self,title='',parent=None):
        super().__init__(parent);self.setObjectName('sectionCard')
        self.body=QVBoxLayout(self);self.body.setContentsMargins(18,16,18,16);self.body.setSpacing(10)
        if title:self.body.addWidget(label(title,'cardLabel'))


class MetricCard(QPushButton):
    def __init__(self,title,explanation,icon_name,action,parent=None):
        super().__init__(parent)
        self.setObjectName('metric');self.setMinimumWidth(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred)
        self.setToolTip(explanation);self.setAccessibleName(title)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(action)
        layout=QVBoxLayout(self);layout.setContentsMargins(15,12,15,12);layout.setSpacing(3)
        row=QHBoxLayout();self.caption=label(title,'cardLabel',True);row.addWidget(self.caption,1)
        image=QLabel();image.setPixmap(icon(icon_name,'#24ab9d').pixmap(25,25));row.addWidget(image)
        layout.addLayout(row)
        self.value=label('0','cardValue');layout.addWidget(self.value)
        layout.addWidget(label('Tegishli yozuvlarni ochish →','subtitle',True))
        for child in self.findChildren(QLabel):child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def sizeHint(self):return QSize(220,132)


class EmptyState(QFrame):
    def __init__(self,title,description,action=None,action_text='Boshlash',parent=None):
        super().__init__(parent);self.setObjectName('emptyState')
        v=QVBoxLayout(self);v.setContentsMargins(22,18,22,18)
        graphic=QLabel();graphic.setPixmap(icon('catalog','#24ab9d').pixmap(32,32))
        v.addWidget(graphic,0,Qt.AlignmentFlag.AlignHCenter)
        self.title=label(title,'cardLabel',True);self.title.setAlignment(Qt.AlignmentFlag.AlignCenter);v.addWidget(self.title)
        self.description=label(description,'subtitle',True);self.description.setAlignment(Qt.AlignmentFlag.AlignCenter);v.addWidget(self.description)
        self.action=QPushButton(action_text);self.action.setObjectName('primary')
        if action:self.action.clicked.connect(action)
        self.action.setVisible(action is not None);v.addWidget(self.action,0,Qt.AlignmentFlag.AlignHCenter)

    def setText(self,text):self.description.setText(text)


class ToastNotification(QFrame):
    """Overlay notification; it never changes the page layout."""
    def __init__(self,parent):
        super().__init__(parent);self.setObjectName('toast')
        h=QHBoxLayout(self);self.message=label('',wrap=True);h.addWidget(self.message)
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.timeout.connect(self.hide)
        self.hide();self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def show_message(self,message):
        self.message.setText(message)
        self.setFixedWidth(min(480,max(250,self.parentWidget().width()-40)))
        self.adjustSize()
        self.move(max(12,self.parentWidget().width()-self.width()-20),max(12,self.parentWidget().height()-self.height()-24))
        self.show();self.raise_();self.timer.start(4500)


class SearchToolbar(QWidget):
    def __init__(self,parent=None):
        from PySide6.QtWidgets import QLineEdit
        super().__init__(parent)
        self.body=QHBoxLayout(self);self.body.setContentsMargins(0,0,0,0)
        self.search=QLineEdit();self.search.setClearButtonEnabled(True)
        self.search.setAccessibleName('Reyestr yozuvlarini qidirish')
        self.search.setPlaceholderText('Qidirish: nom, kod, mas’ul yoki bo‘lim…')
        self.body.addWidget(self.search,1)


class FilterToolbar(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.body=QHBoxLayout(self);self.body.setContentsMargins(0,0,0,0)


class StatusBadge(QLabel):
    def __init__(self,text,severity,parent=None):
        super().__init__(text,parent)
        self.setTextFormat(Qt.TextFormat.PlainText)
        dark=tokens().base=='#142331'
        colors={'Critical':('#b42335','#ffabb8'),'High':('#964600','#ffc087'),
                'Medium':('#746000','#f2d675'),'Low':('#087f68','#6ee7c4')}
        color=colors.get(severity,('#506779','#b2c7d5'))[int(dark)]
        background='#263e52' if dark else '#eef3f6'
        self.setStyleSheet(f'color:{color}; background:{background}; border-radius:6px; padding:3px 7px; font-size:11px; font-weight:600;')


class ConfirmDialog:
    @staticmethod
    def ask(parent,title,message):
        from PySide6.QtWidgets import QMessageBox
        return QMessageBox.question(parent,title,message,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes


class FormSection(QFrame):
    def __init__(self,parent=None):
        from PySide6.QtWidgets import QFormLayout
        super().__init__(parent)
        self.form=QFormLayout(self)
        self.form.setSpacing(14)
        self.form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)


class StepIndicator(QLabel):
    def set_complete(self,complete):
        self.setText('✓ Kiritilgan' if complete else 'Kutilmoqda')
        self.setObjectName('subtitle')
        self.setAccessibleName('Kiritilgan' if complete else 'Kutilmoqda')
