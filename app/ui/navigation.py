"""One route catalog drives the tree, menu bar, history, breadcrumbs and catalog."""
from dataclasses import dataclass
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHeaderView, QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from app.ui.components import IconButton, UzHiLogo
from app.ui.icons import icon
from app.ui.style import animations_enabled

@dataclass(frozen=True)
class Destination:
    key: str
    title: str
    group: str
    icon: str
    page: int = -1
    tab: int = -1
    command: str = ''

GROUPS=[('Asosiy ish maydoni','dashboard'),('Tashkilot boshqaruvi','building'),('BIA va risklar','shield'),
        ('Tiklash va uzluksizlik','recovery'),('Hisobot va ma’lumotlar','report'),('Tizim','settings')]
DESTINATIONS=[
 Destination('dashboard','Boshqaruv paneli',GROUPS[0][0],'dashboard',0),
 Destination('setup','Boshlang‘ich sozlash',GROUPS[0][0],'check',9),
 Destination('catalog','Interaktiv katalog',GROUPS[0][0],'catalog',10),
 Destination('organization','Tashkilot profili',GROUPS[1][0],'building',1),
 Destination('departments','Bo‘limlar',GROUPS[1][0],'people',1),
 Destination('processes','Biznes jarayonlari',GROUPS[1][0],'process',2),
 Destination('bia','BIA tahlili',GROUPS[2][0],'chart',3),
 Destination('risks','Risklar reyestri',GROUPS[2][0],'risk',4),
 Destination('matrix','Risk matritsasi',GROUPS[2][0],'matrix',4),
 Destination('strategies','Tiklash strategiyalari',GROUPS[3][0],'recovery',5,1),
 Destination('plans','Uzluksizlik rejalari',GROUPS[3][0],'plan',5,0),
 Destination('steps','Reja bosqichlari',GROUPS[3][0],'steps',5,0),
 Destination('scenarios','Simulyatsiya va ssenariylar',GROUPS[3][0],'scenario',6),
 Destination('statistics','Dashboard statistikasi',GROUPS[4][0],'chart',0),
 Destination('reports','PDF/CSV hisobotlar',GROUPS[4][0],'report',7),
 Destination('exports','Ma’lumotlarni eksport qilish',GROUPS[4][0],'export',7),
 Destination('settings','Sozlamalar',GROUPS[5][0],'settings',8),
 Destination('password','Parolni almashtirish',GROUPS[5][0],'lock',command='change_password'),
 Destination('backup','Zaxira nusxa yaratish',GROUPS[5][0],'backup',command='backup'),
 Destination('restore','Zaxiradan tiklash',GROUPS[5][0],'recovery',command='restore'),
 Destination('about','Dastur haqida',GROUPS[5][0],'info',command='about'),
]
ROUTES={d.key:d for d in DESTINATIONS}
LEGACY=['dashboard','organization','processes','bia','risks','plans','scenarios','reports','settings']

class NavigationHistory:
    def __init__(self):self.entries=[];self.position=-1
    def visit(self,key):
        if self.position>=0 and self.entries[self.position]==key:return
        self.entries=self.entries[:self.position+1]+[key];self.position+=1
    def move(self,delta):
        target=self.position+delta
        if 0<=target<len(self.entries):self.position=target;return self.entries[target]
        return None
    @property
    def can_back(self):return self.position>0
    @property
    def can_forward(self):return self.position<len(self.entries)-1

class NavigationSidebar(QWidget):
    requested=Signal(str)
    widthChanged=Signal()
    def __init__(self,settings,parent=None):
        super().__init__(parent);self.settings=settings;self.compact=False
        self.setObjectName('sidebar');self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground,True);self.setFixedWidth(284)
        self.width_animation=QPropertyAnimation(self,b'maximumWidth',self)
        self.width_animation.setDuration(180);self.width_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.width_animation.finished.connect(self.widthChanged.emit)
        self.width_animation.valueChanged.connect(lambda value:self.setMinimumWidth(value))
        layout=QVBoxLayout(self);layout.setContentsMargins(12,16,12,16);layout.setSpacing(10)
        self.logo=UzHiLogo();layout.addWidget(self.logo)
        self.toggle=IconButton('menu','Yon menyuni yig‘ish / kengaytirish (Ctrl+B)',lambda:self.set_compact(not self.compact))
        self.toggle.setIcon(icon('menu','#c6dde8'));layout.addWidget(self.toggle)
        self.search=QLineEdit();self.search.setPlaceholderText('Modulni qidirish…  Ctrl+K')
        self.search.setAccessibleName('Modullarni qidirish');self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.filter);layout.addWidget(self.search)
        self.tree=QTreeWidget();self.tree.setObjectName('navigation');self.tree.setHeaderHidden(True)
        self.tree.setIconSize(QSize(20,20));self.tree.setIndentation(14)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tree.setAnimated(animations_enabled());self.tree.setExpandsOnDoubleClick(False);layout.addWidget(self.tree,1)
        self.groups={};self.items={}
        for title,category_icon in GROUPS:
            group=QTreeWidgetItem(self.tree,[title]);group.setIcon(0,icon(category_icon,'#7ed9cf'))
            font=QFont();font.setBold(True);group.setFont(0,font)
            group.setToolTip(0,title);self.groups[title]=group
            for route in (r for r in DESTINATIONS if r.group==title):
                item=QTreeWidgetItem(group,[route.title]);item.setData(0,Qt.ItemDataRole.UserRole,route.key)
                item.setIcon(0,icon(route.icon,'#9fcecf'));item.setToolTip(0,route.title);self.items[route.key]=item
            group.setExpanded(settings.value('groups/'+title,title==GROUPS[0][0],type=bool))
        self.tree.itemClicked.connect(self.activate)
        self.tree.itemActivated.connect(self.activate)
        self.tree.itemExpanded.connect(self.save_group)
        self.tree.itemCollapsed.connect(self.save_group)
        self.search_empty=QLabel('Modul topilmadi.');self.search_empty.hide();layout.addWidget(self.search_empty)
        self.footer=QLabel('MAHALLIY ISH REJIMI\nSQLite · Internet talab qilinmaydi');self.footer.setWordWrap(True)
        layout.addWidget(self.footer)
        self.set_compact(settings.value('sidebar/compact',False,type=bool),animate=False)

    def save_group(self,item):
        if not self.search.text() and not self.compact:self.settings.setValue('groups/'+item.toolTip(0),item.isExpanded())

    def activate(self,item,column=0):
        key=item.data(0,Qt.ItemDataRole.UserRole)
        if key:self.requested.emit(key)
        elif self.compact:
            self.set_compact(False);item.setExpanded(True)
        else:item.setExpanded(not item.isExpanded())

    def select(self,key):
        self.active_key=key
        item=self.items[key]
        self.tree.setCurrentItem(item.parent() if self.compact else item)
        # Keep the exact active destination visible, even after a module search.
        if self.search.text():self.search.clear()
        if not self.compact:item.parent().setExpanded(True)
        self.tree.scrollToItem(item)

    def setCurrentRow(self,index):
        """Stable page-index API used by the packaged regression smoke test."""
        if 0<=index<len(LEGACY):self.requested.emit(LEGACY[index])

    def filter(self,query):
        query=query.casefold().strip()
        for group in self.groups.values():
            visible=False
            for i in range(group.childCount()):
                item=group.child(i);match=not query or query in item.toolTip(0).casefold() or query in group.toolTip(0).casefold()
                item.setHidden(not match);visible=visible or match
            group.setHidden(not visible)
            group.setExpanded(True if query else self.settings.value('groups/'+group.toolTip(0),group.toolTip(0)==GROUPS[0][0],type=bool))

        if hasattr(self,"search_empty"):self.search_empty.setVisible(bool(query) and all(g.isHidden() for g in self.groups.values()))

    def set_compact(self,compact,animate=True):
        self.width_animation.stop();self.compact=bool(compact)
        self.settings.setValue('sidebar/compact',self.compact)
        self.logo.compact=self.compact;self.logo.update()
        self.search.setVisible(not self.compact);self.footer.setVisible(not self.compact)
        self.tree.setIndentation(0 if self.compact else 14)
        for group in self.groups.values():
            group.setText(0,'' if self.compact else group.toolTip(0))
            group.setExpanded(False if self.compact else self.settings.value('groups/'+group.toolTip(0),group.toolTip(0)==GROUPS[0][0],type=bool))
            for i in range(group.childCount()):
                child=group.child(i);child.setText(0,'' if self.compact else child.toolTip(0))
        target=76 if self.compact else 284
        if animate and animations_enabled():
            self.width_animation.setStartValue(self.width());self.width_animation.setEndValue(target);self.width_animation.start()
        else:self.setFixedWidth(target);self.widthChanged.emit()
        if hasattr(self,"active_key"):self.select(self.active_key)

    def focus_search(self):
        if self.compact:self.set_compact(False,animate=False)
        self.search.setFocus();self.search.selectAll()
