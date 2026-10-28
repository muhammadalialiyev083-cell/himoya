import os
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path

from PySide6.QtCore import QThread, Signal, Qt, QSettings, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QListWidget, QMainWindow, QMessageBox,
    QScrollArea, QStackedWidget, QTabWidget, QVBoxLayout, QWidget, QPushButton,
    QCheckBox, QToolButton, QDialogButtonBox, QTextBrowser, QProgressBar, QGraphicsOpacityEffect)

from app.algorithms.scoring import CATEGORIES, COLORS
from app.reports.export import snapshot, write_csv, write_pdf
from app.services.auth import Authentication
from app.services.bcms import BCMS
from app.services.demo import add_demo
from app.ui.fields import fields_for
from app.ui.forms import FormDialog, authenticate
from app.ui.registry import Registry
from app.ui.widgets import Bars, RiskMatrix, button
from app.ui.components import (EmptyState, GradientPanel, MetricCard, PageHeader,
                               SectionCard, ToastNotification, UzHiLogo, StepIndicator, ConfirmDialog, label)
from app.ui.icons import icon
from app.ui.navigation import DESTINATIONS, LEGACY, ROUTES, NavigationHistory, NavigationSidebar
from app.ui.style import apply_theme, animations_enabled, motion_allowed, tokens


class ExportJob(QThread):
    outcome=Signal(str,bool)

    def __init__(self,path,data,kind,plan_id=None,parent=None):
        super().__init__(parent)
        self.path,self.data,self.kind,self.plan_id=Path(path),data,kind,plan_id

    def run(self):
        temp=None
        try:
            fd,temp=tempfile.mkstemp(prefix="bcms-report-",suffix=self.path.suffix,dir=self.path.parent)
            os.close(fd)
            if self.kind=="csv":write_csv(temp,self.data)
            else:write_pdf(temp,self.data,self.kind,self.plan_id)
            os.replace(temp,self.path)
            self.outcome.emit(str(self.path),True)
        except Exception:
            self.outcome.emit("Hisobotni saqlab bo‘lmadi. Papka yozish ruxsati va bo‘sh joyni tekshiring.",False)
        finally:
            if temp and os.path.exists(temp):os.unlink(temp)


class MainWindow(QMainWindow):
    def __init__(self,db):
        super().__init__()
        self.db,self.service=db,BCMS(db)
        self.settings=QSettings(str(db.path.parent/'ui.ini'),QSettings.Format.IniFormat)
        application=QApplication.instance()
        apply_theme(application,self.settings.value('appearance/theme','light'))
        application.setProperty('uzhiMotion',self.settings.value('appearance/motion',True,type=bool) and motion_allowed())
        self.jobs=[]
        self.registries=[]
        self.history=NavigationHistory()
        self.current_route='dashboard'
        self.setWindowTitle('UzHi — UzluksizBCMS Desktop 1.1.0')
        self.resize(1366,768)
        self.setMinimumSize(780,480)
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parents[1]/'resources/icon.svg')))
        root=QWidget();root.setObjectName('pageSurface');self.setCentralWidget(root)
        layout=QHBoxLayout(root);layout.setContentsMargins(0,0,0,0);layout.setSpacing(0)
        self.nav=NavigationSidebar(self.settings);self.nav.requested.connect(self.navigate)
        layout.addWidget(self.nav)
        content=QWidget();content.setObjectName('pageSurface')
        c=QVBoxLayout(content);c.setContentsMargins(22,14,22,14);c.setSpacing(10)
        self.header=PageHeader(self.go_back,self.go_forward,lambda:self.navigate('dashboard'))
        self.header.quick.clicked.connect(self.context_action)
        self.title=self.header.title;c.addWidget(self.header)
        self.org_label=label('','subtitle');c.addWidget(self.org_label)
        self.stack=QStackedWidget();c.addWidget(self.stack,1);layout.addWidget(content,1)
        self.build_dashboard()
        self.build_organization()
        self.processes=self.registry('business_process',[('code','Kod'),('name','Jarayon'),('department','Bo‘lim'),('responsible','Mas’ul'),('category','BIA darajasi'),('status','Holat')],self.service.processes)
        self.stack.addWidget(self.processes)
        self.build_bia();self.build_risks();self.build_plans()
        self.scenarios=self.registry('scenario',[('name','Ssenariy'),('duration','Uzilish (soat)'),('resources','Resurslar')],note='Stol usti modeli: davomiylik RTO va MTPD bilan taqqoslanadi. O‘lchangan natija yoki ML bashorati emas.')
        self.stack.addWidget(self.scenarios)
        self.build_reports();self.build_settings();self.build_setup();self.build_catalog()
        self.build_menus()
        self.fade_effect=QGraphicsOpacityEffect(self.stack)
        self.stack.setGraphicsEffect(self.fade_effect)
        self.fade=QPropertyAnimation(self.fade_effect,b'opacity',self)
        self.fade.setDuration(140);self.fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.nav.widthChanged.connect(self.layout_dashboard)
        self.toast=ToastNotification(root)
        self.busy=QProgressBar();self.busy.setFixedWidth(130);self.busy.setRange(0,0);self.busy.hide()
        self.statusBar().addPermanentWidget(self.busy)
        self.refresh_all();self.navigate('dashboard');self.nav.tree.setFocus()
        self.statusBar().showMessage('Tayyor • Barcha ma’lumotlar mahalliy bazada saqlanadi.')

    def showEvent(self,event):
        super().showEvent(event)
        if not getattr(self,'_placed',False):
            self._placed=True
            if QApplication.platformName()!='offscreen':
                available=self.screen().availableGeometry()
                self.resize(min(self.width(),available.width()-16),min(self.height(),available.height()-40))

    def registry(self,*args,**kwargs):
        page=Registry(self,*args,**kwargs)
        self.registries.append(page)
        return page

    def navigate(self,key,record=True):
        if isinstance(key,int):key=LEGACY[key]
        route=ROUTES[key]
        if route.command:
            getattr(self,route.command)()
            self.nav.select(self.current_route)
            return
        if record:self.history.visit(key)
        self.current_route=key
        self.stack.setCurrentIndex(route.page)
        if route.tab>=0:self.plan_tabs.setCurrentIndex(route.tab)
        self.header.set_page(route.title,route.group,route.icon)
        self.nav.select(key)
        self.header.back.setEnabled(self.history.can_back)
        self.header.forward.setEnabled(self.history.can_forward)
        self.actions['back'].setEnabled(self.history.can_back)
        self.actions['forward'].setEnabled(self.history.can_forward)
        registry=self.active_registry()
        can_create=registry is not None or key=='organization'
        self.actions['new'].setEnabled(can_create)
        self.actions['new'].setStatusTip('Joriy modulda yangi yozuv' if can_create else 'Yangi yozuv uchun tashkilot yoki reyestr modulini oching.')
        self.header.quick.setText('Profilni tahrirlash' if key=='organization' else '+ Yangi yozuv' if registry else 'PDF/CSV eksport' if key in ('reports','exports') else 'Boshlang‘ich sozlash')
        if key=='departments':self.departments.search.setFocus()
        if key=='steps':self.statusBar().showMessage('Reja bosqichlari: rejani tanlang → Tahrirlash → Tiklash tartibi.',10000)
        if key=='statistics':self.dashboard.ensureWidgetVisible(self.metric_widgets['processes'])
        elif route.page==0:self.dashboard.verticalScrollBar().setValue(0)
        if animations_enabled() and self.isVisible():
            self.fade.stop();self.fade.setStartValue(.82);self.fade.setEndValue(1.0);self.fade.start()
        else:self.fade_effect.setOpacity(1.0)

    def go_back(self):
        key=self.history.move(-1)
        if key is not None:self.navigate(key,record=False)

    def go_forward(self):
        key=self.history.move(1)
        if key is not None:self.navigate(key,record=False)

    def active_registry(self):
        return {'departments':self.departments,'processes':self.processes,'bia':self.bia,
                'risks':self.risks,'matrix':self.risks,'plans':self.plans,'steps':self.plans,
                'strategies':self.strategies,'scenarios':self.scenarios}.get(self.current_route)

    def context_action(self):
        registry=self.active_registry()
        if registry:registry.edit()
        elif self.current_route=='organization':self.edit_org()
        elif self.current_route in ('reports','exports'):self.export('assessment')
        else:self.navigate('setup')

    def build_menus(self):
        self.actions={}
        def action(key,title,handler,shortcut=None,icon_name=''):
            item=QAction(icon(icon_name) if icon_name else QIcon(),title,self)
            if shortcut:item.setShortcut(QKeySequence(shortcut))
            item.triggered.connect(lambda checked=False:handler())
            self.actions[key]=item
            return item
        file=self.menuBar().addMenu('&Fayl')
        file.addAction(action('new','Yangi yozuv',self.context_action,'Ctrl+N','plus'))
        exports=file.addMenu('Eksport')
        for key,title in [('assessment','Baholash — PDF'),('register','Reyestr — PDF'),('csv','Reyestr — CSV')]:
            exports.addAction(action('export_'+key,title,lambda k=key:self.export(k),icon_name='export'))
        file.addAction(action('backup','Zaxira nusxa',self.backup,'Ctrl+Shift+B','backup'))
        file.addSeparator();file.addAction(action('exit','Chiqish',self.close,'Ctrl+Q'))
        manage=self.menuBar().addMenu('&Boshqaruv')
        for key in ('dashboard','organization','departments','processes','bia','risks','plans'):
            route=ROUTES[key];manage.addAction(action('nav_'+key,route.title,lambda k=key:self.navigate(k),icon_name=route.icon))
        view=self.menuBar().addMenu('&Ko‘rinish')
        group=QActionGroup(self);group.setExclusive(True)
        for key,title in [('light','Yorug‘ mavzu'),('dark','Qorong‘i mavzu')]:
            item=action('theme_'+key,title,lambda k=key:self.set_theme(k));item.setCheckable(True)
            item.setChecked(QApplication.instance().property('uzhiTheme')==key);group.addAction(item);view.addAction(item)
        view.addAction(action('sidebar','Yon menyuni yig‘ish / kengaytirish',lambda:self.nav.set_compact(not self.nav.compact),'Ctrl+B','menu'))
        view.addAction(action('search','Modulni qidirish',self.nav.focus_search,'Ctrl+K','search'))
        view.addAction(action('home','Dashboardga qaytish',lambda:self.navigate('dashboard'),'Alt+Home','dashboard'))
        view.addSeparator()
        view.addAction(action('back','Orqaga',self.go_back,'Alt+Left','back'))
        view.addAction(action('forward','Oldinga',self.go_forward,'Alt+Right','forward'))
        tools=self.menuBar().addMenu('&Asboblar')
        tools.addAction(action('simulation','Simulyatsiya',lambda:self.navigate('scenarios'),icon_name='scenario'))
        tools.addAction(action('reports','Hisobotlar',lambda:self.navigate('reports'),icon_name='report'))
        tools.addAction(action('refresh','Ma’lumotlarni yangilash',self.refresh_all,'F5','recovery'))
        tools.addAction(action('password','Parolni almashtirish',self.change_password,icon_name='lock'))
        tools.addAction(action('restore','Zaxiradan tiklash',self.restore,icon_name='recovery'))
        help_menu=self.menuBar().addMenu('&Yordam')
        help_menu.addAction(action('manual','Foydalanish qo‘llanmasi',self.show_manual,'F1','report'))
        help_menu.addAction(action('about','Dastur haqida',self.about,icon_name='info'))

    def set_theme(self,name):
        apply_theme(QApplication.instance(),name);self.settings.setValue('appearance/theme',name)
        self.theme_switch.setChecked(name=='dark')
        for key in ('light','dark'):self.actions['theme_'+key].setChecked(key==name)
        route=ROUTES[self.current_route];self.header.set_page(route.title,route.group,route.icon)
        for control in self.header.findChildren(QToolButton):
            name=control.property('uzhiIcon')
            if name:control.setIcon(icon(name,tokens().accent))
        for page in self.registries:page.populate()

    def set_motion(self,enabled):
        previous=self.motion_switch.blockSignals(True)
        self.motion_switch.setChecked(enabled)
        self.motion_switch.blockSignals(previous)
        self.settings.setValue('appearance/motion',enabled)
        QApplication.instance().setProperty('uzhiMotion',enabled and motion_allowed())
        self.nav.tree.setAnimated(animations_enabled())
        if not animations_enabled():
            self.fade.stop();self.fade_effect.setOpacity(1.0)
            self.nav.set_compact(self.nav.compact,animate=False)
            for logo in self.findChildren(UzHiLogo):logo.animation.stop();logo.set_reveal(float(logo.isChecked()))

    def notify(self,message):
        self.statusBar().showMessage(message,10000);self.toast.show_message(message)

    def show_manual(self):
        dlg=QDialog(self);dlg.setWindowTitle('UzHi — Foydalanish qo‘llanmasi');dlg.resize(780,580)
        layout=QVBoxLayout(dlg);browser=QTextBrowser();browser.setOpenExternalLinks(False)
        path=Path(__file__).resolve().parents[1]/'resources/user-manual.md'
        browser.setMarkdown(path.read_text(encoding='utf-8') if path.exists() else 'Tashkilot → Bo‘limlar → Jarayonlar → BIA → Risklar → Rejalar → Ssenariylar.\n\nCtrl+K: modul qidirish. Alt+Left/Right: Orqaga/Oldinga. F5: yangilash.')
        layout.addWidget(browser);buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dlg.reject);layout.addWidget(buttons);dlg.exec()

    def about(self):
        QMessageBox.about(self,'UzHi — Dastur haqida','UzHi — Uzluksiz Himoya\nUzluksizBCMS Desktop 1.1.0\n\nPython 3.12 · PySide6 · SQLite\nMahalliy biznes uzluksizligi va risklarni boshqarish.\n\nTadqiqot modeli. ISO sertifikati yoki DGU ro‘yxatidan o‘tganlik da’vo qilinmaydi.')

    def build_setup(self):
        scroll=QScrollArea();scroll.setWidgetResizable(True);page=QWidget();page.setObjectName('pageSurface')
        v=QVBoxLayout(page);v.setContentsMargins(0,0,0,0);v.setSpacing(10);self.setup_labels={}
        for key,title,text in [('organization','Tashkilot profili','Tashkilot nomi, soha va mas’ulni belgilang.'),('departments','Bo‘limlar','Jarayonlar tegishli bo‘lgan bo‘limlarni yarating.'),('processes','Biznes jarayonlari','Jarayonlar va ularning resurslarini kiriting.'),('bia','BIA tahlili','Ta’sirlar va RTO/RPO/MTPD vaqt maqsadlarini baholang.'),('risks','Risklar','Ehtimollik va ta’sir bo‘yicha risklarni baholang.'),('plans','Uzluksizlik rejalari','Strategiya, reja va bajariladigan bosqichlarni belgilang.')]:
            card=SectionCard(title);row=QHBoxLayout();status=StepIndicator();self.setup_labels[key]=status
            row.addWidget(label(text,'subtitle',True),1);row.addWidget(status)
            row.addWidget(button('Ochish →',lambda checked=False,k=key:self.navigate(k),True))
            card.body.addLayout(row);v.addWidget(card)
        v.addStretch();scroll.setWidget(page);self.stack.addWidget(scroll)

    def build_catalog(self):
        scroll=QScrollArea();scroll.setWidgetResizable(True);page=QWidget();page.setObjectName('pageSurface')
        grid=QGridLayout(page);grid.setContentsMargins(0,0,0,0);grid.setSpacing(12)
        for i,route in enumerate(r for r in DESTINATIONS if not r.command and r.key not in ('catalog','statistics','exports','departments','matrix','steps')):
            card=SectionCard(route.title);card.body.addWidget(label(route.group,'subtitle',True))
            open_button=button('Modulni ochish →',lambda checked=False,k=route.key:self.navigate(k));open_button.setIcon(icon(route.icon));card.body.addWidget(open_button)
            grid.addWidget(card,i//2,i%2)
        scroll.setWidget(page);self.stack.addWidget(scroll)

    def build_dashboard(self):
        self.dashboard=QScrollArea();self.dashboard.setWidgetResizable(True)
        page=QWidget();page.setObjectName('pageSurface');v=QVBoxLayout(page);v.setContentsMargins(0,0,0,0);v.setSpacing(14)
        hero=GradientPanel();h=QHBoxLayout(hero);h.setContentsMargins(24,20,24,20)
        text=QVBoxLayout();text.setSpacing(10);text.addWidget(UzHiLogo())
        text.addWidget(label('Biznes uzluksizligini boshqarish markazi','pageTitle',True))
        text.addWidget(label('Tashkilot jarayonlari, risklar, tiklash maqsadlari va uzluksizlik rejalarini yagona muhitda boshqaring.','subtitle',True))
        shortcuts=QGridLayout()
        for i,(title,key) in enumerate([('Tashkilotni sozlash','setup'),('BIA tahlilini boshlash','bia'),('Risklarni baholash','risks'),('Tiklash rejasini yaratish','plans')]):
            shortcuts.addWidget(button(title,lambda checked=False,k=key:self.navigate(k),i==0),i//2,i%2)
        text.addLayout(shortcuts);h.addLayout(text,1)
        self.hero_mark=QLabel();self.hero_mark.setPixmap(QIcon(str(Path(__file__).resolve().parents[1]/'resources/icon.svg')).pixmap(140,140))
        self.hero_mark.setFixedWidth(164);self.hero_mark.setAlignment(Qt.AlignmentFlag.AlignCenter);h.addWidget(self.hero_mark)
        v.addWidget(hero)
        self.dashboard_empty=EmptyState('Ishni tashkilot profilidan boshlang','Hozircha jarayonlar yo‘q. Profil va bo‘lim yarating, so‘ng birinchi jarayonni kiriting.',lambda:self.navigate('setup'))
        v.addWidget(self.dashboard_empty)
        v.addWidget(label('TASHKILOTNING JORIY HOLATI  /  SQLite ma’lumotlari','eyebrow'))
        self.metrics_grid=QGridLayout();self.metrics_grid.setSpacing(10);self.cards={};self.metric_widgets={}
        metrics=[('processes','Biznes jarayonlari','Ro‘yxatga olingan barcha biznes jarayonlari.','process','processes'),('departments','Bo‘limlar','Tashkilot bo‘limlari soni.','people','departments'),('critical','Kritik jarayonlar','BIA balli 75 yoki undan yuqori bo‘lgan jarayonlar.','chart','bia'),('high_risks','Yuqori / kritik risklar','Risk balli 11 yoki undan yuqori. Barcha holatdagi risklar.','risk','risks'),('bia','BIA tahlillari','Vaznli BIA bahosi kiritilgan jarayonlar.','chart','bia'),('plans','Uzluksizlik rejalari','Saqlangan barcha uzluksizlik rejalari.','plan','plans'),('scenarios','Ssenariylar','Saqlangan stol usti ssenariylari.','scenario','scenarios'),('assessments','Baholangan ssenariylar','Kamida bitta saqlangan natijasi bor ssenariylar.','shield','scenarios')]
        for i,(key,title,explanation,icon_name,destination) in enumerate(metrics):
            card=MetricCard(title,explanation,icon_name,lambda checked=False,k=key,d=destination:self.open_metric(k,d))
            self.cards[key]=card.value;self.metric_widgets[key]=card;self.metrics_grid.addWidget(card,i//4,i%4)
        v.addLayout(self.metrics_grid)
        self.analytics=QGridLayout();self.analytics.setSpacing(12)
        priority=SectionCard('Jarayonlar ustuvorligi • BIA / 100 (yuqori 8 ta)');self.priority_chart=Bars();priority.body.addWidget(self.priority_chart)
        priority.body.addWidget(button('BIA tahlilini ochish →',lambda:self.navigate('bia')))
        severity=SectionCard('Risklar darajasi • soni');self.risk_chart=Bars(1);severity.body.addWidget(self.risk_chart)
        severity.body.addWidget(button('Risklarni ochish →',lambda:self.navigate('risks')))
        matrix=SectionCard('Risk matritsasi • real yozuvlar');self.dashboard_matrix=RiskMatrix();matrix.body.addWidget(self.dashboard_matrix)
        matrix.body.addWidget(button('Risk matritsasini ochish →',lambda:self.navigate('matrix')))
        recovery=SectionCard('Jarayon va tiklash maqsadlari');self.recovery_summary=label('','subtitle',True);recovery.body.addWidget(self.recovery_summary)
        recovery.body.addWidget(button('Rejalarni ochish →',lambda:self.navigate('plans')))
        self.analytics_cards=[priority,severity,matrix,recovery]
        for i,card in enumerate(self.analytics_cards):self.analytics.addWidget(card,i//2,i%2)
        v.addLayout(self.analytics)
        v.addWidget(label('Tadqiqot modeli: vaznli BIA + risk matritsasi. Baholanmagan jarayonlar kritik yoki tayyor deb taxmin qilinmaydi. NAMUNA yozuvlari — faqat namoyish uchun.','subtitle',True))
        v.addStretch();self.dashboard.setWidget(page);self.stack.addWidget(self.dashboard)
        self._dashboard_columns=4;self._analytics_columns=2

    def open_metric(self,key,destination):
        self.navigate(destination)
        registry=self.active_registry()
        if registry:
            registry.search.clear();registry.filter.setCurrentIndex(0);registry.metric_filter=None
            if key=='critical':registry.filter.setCurrentIndex(registry.filter.findData('Critical'))
            elif key=='high_risks':registry.metric_filter='high_risks'
            elif key=='assessments':registry.metric_filter='assessments'
            registry.populate()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.layout_dashboard()

    def layout_dashboard(self):
        if not hasattr(self,'metrics_grid'):return
        available=self.width()-self.nav.width()-54
        columns=4 if available>=760 else 2
        if columns!=self._dashboard_columns:
            self._dashboard_columns=columns
            for i,card in enumerate(self.metric_widgets.values()):self.metrics_grid.removeWidget(card);self.metrics_grid.addWidget(card,i//columns,i%columns)
        columns=2 if available>=800 else 1
        if columns!=self._analytics_columns:
            self._analytics_columns=columns
            for i,card in enumerate(self.analytics_cards):self.analytics.removeWidget(card);self.analytics.addWidget(card,i//columns,i%columns)
        self.hero_mark.setVisible(available>=850)
        if hasattr(self,'toast') and self.toast.isVisible():self.toast.hide()

    def build_organization(self):
        page=QWidget()
        page.setObjectName("pageSurface")
        v=QVBoxLayout(page)
        v.setContentsMargins(0,0,0,0)
        profile=QGroupBox("Tashkilot profili")
        b=QVBoxLayout(profile)
        self.profile=QLabel()
        self.profile.setWordWrap(True)
        self.profile.setTextFormat(Qt.TextFormat.PlainText)
        b.addWidget(self.profile)
        b.addWidget(button("Profilni yaratish / tahrirlash",self.edit_org,True))
        v.addWidget(profile)
        self.departments=self.registry("department",[("name","Bo‘lim"),("responsible","Mas’ul shaxs")],note="Jarayon qo‘shishdan oldin tashkilot va kamida bitta bo‘lim yarating.")
        v.addWidget(self.departments,1)
        self.stack.addWidget(page)

    def edit_org(self):
        orgs=self.service.repo.all("organization")
        dlg=FormDialog("Tashkilot profili",fields_for("organization",self.service),orgs[0] if orgs else {},self)
        while dlg.exec()==QDialog.DialogCode.Accepted:
            try:
                self.service.save("organization",dlg.values())
                self.refresh_all()
                return
            except (ValueError,sqlite3.Error) as exc:self.show_error(exc)

    def build_bia(self):
        def assessments():
            return [{**p,"process_id":p["id"],"id":p["bia_id"]} for p in self.service.rankings()]
        self.bia=self.registry("bia_assessment",[("code","Kod"),("name","Jarayon"),("score","BIA / 100"),("category","Daraja"),("rto","RTO (soat)"),("mtpd","MTPD (soat)"),("rpo","RPO (soat)")],assessments,note="BIA = 20 × (0.30×moliyaviy + 0.35×operatsion + 0.20×obro‘ + 0.15×huquqiy). Tadqiqot parametrlari; rasmiy ISO formulasi emas. Reyting: ball kamayishi, teng bo‘lsa RTO o‘sishi.")
        self.stack.addWidget(self.bia)

    def build_risks(self):
        page=QWidget()
        page.setObjectName("pageSurface")
        v=QVBoxLayout(page)
        v.setContentsMargins(0,0,0,0)
        v.addWidget(QLabel("5×5 matritsa • satr: ehtimollik 5→1; ustun: ta’sir 1→5; katak: ball · risklar soni"))
        self.matrix=RiskMatrix()
        v.addWidget(self.matrix)
        self.risks=self.registry("risk",[("title","Risk"),("process","Jarayon"),("likelihood","Ehtimol"),("impact","Ta’sir"),("score","Ball"),("category","Daraja"),("status","Holat")],self.service.risks)
        v.addWidget(self.risks,1)
        self.stack.addWidget(page)

    def build_plans(self):
        tabs=QTabWidget()
        self.plan_tabs=tabs
        self.plans=self.registry("continuity_plan",[("code","Kod"),("name","Reja"),("process","Jarayon"),("completion","Bajarilishi %"),("readiness","Tayyorlik"),("status","Holat")],self.service.plans,note="Tayyor: tasdiqlangan reja, barcha bosqichlar bajarilgan, mas’ul/resurs/maqsad to‘ldirilgan va ko‘rib chiqish sanasi o‘tmagan.")
        self.strategies=self.registry("recovery_strategy",[("name","Strategiya"),("responsible","Mas’ul"),("priority","Ustuvorlik"),("resources","Resurslar")])
        tabs.addTab(self.plans,"Uzluksizlik rejalari")
        tabs.addTab(self.strategies,"Tiklanish strategiyalari")
        self.stack.addWidget(tabs)

    def build_reports(self):
        page=QWidget()
        page.setObjectName("pageSurface")
        v=QVBoxLayout(page)
        v.setContentsMargins(0,0,0,0)
        for title,description,kind in (("Biznes uzluksizligini baholash","Tashkilot, BIA reytingi, risklar, rejalar tayyorligi, ssenariylar va qoidaviy tavsiyalar.","assessment"),("Risk va ustuvorlik reyestri — PDF","Hisoblangan ballar, darajalar, vaqt maqsadlari va metodologiya.","register"),("Risk va ustuvorlik reyestri — CSV","UTF-8 (BOM). Elektron jadvallar uchun xavfli formula matnlari himoyalangan.","csv")):
            group=QGroupBox(title)
            layout=QVBoxLayout(group)
            label=QLabel(description)
            label.setWordWrap(True)
            layout.addWidget(label)
            layout.addWidget(button("Saqlash joyini tanlash va eksport",lambda checked=False,k=kind:self.export(k),True))
            v.addWidget(group)
        note=QLabel("PDFlar o‘zbek lotin matnini shrift bilan birga saqlaydi. Hisobot yaratish fon vazifasida bajariladi.\nHisobotlarda shaxsiy parol yoki parol xeshi mavjud emas. PDF faylini tizimdagi PDF ko‘ruvchi orqali chop etish mumkin.")
        note.setWordWrap(True)
        v.addWidget(note)
        v.addStretch()
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(page)
        self.stack.addWidget(scroll)

    def export(self,kind,plan_id=None):
        ext="csv" if kind=="csv" else "pdf"
        path,_=QFileDialog.getSaveFileName(self,"Hisobotni saqlash",f"UzluksizBCMS-{kind}.{ext}",f"{ext.upper()} (*.{ext})")
        if not path:return
        if not path.lower().endswith("."+ext):path+="."+ext
        job=ExportJob(path,snapshot(self.service),kind,plan_id,self)
        job.outcome.connect(self.export_done)
        self.jobs.append(job)
        self.busy.show()
        job.finished.connect(lambda:self.release_job(job))
        self.statusBar().showMessage("Hisobot tayyorlanmoqda…")
        job.start()

    def release_job(self,job):
        if job in self.jobs:self.jobs.remove(job)
        job.deleteLater()
        if not self.jobs:self.busy.hide()

    def export_done(self,message,ok):
        if ok:
            self.notify("Hisobot saqlandi: "+message)
        else:QMessageBox.warning(self,"Hisobot",message)

    def build_settings(self):
        page=QWidget()
        page.setObjectName("pageSurface")
        v=QVBoxLayout(page)
        v.setContentsMargins(0,0,0,0)
        appearance=SectionCard('UzHi Design System • Ko‘rinish')
        self.theme_switch=QCheckBox('Qorong‘i mavzu')
        self.theme_switch.setChecked(QApplication.instance().property('uzhiTheme')=='dark')
        self.theme_switch.toggled.connect(lambda checked:self.set_theme('dark' if checked else 'light'))
        self.motion_switch=QCheckBox('Dekorativ animatsiyalar')
        self.motion_switch.setChecked(animations_enabled());self.motion_switch.toggled.connect(self.set_motion)
        appearance.body.addWidget(self.theme_switch);appearance.body.addWidget(self.motion_switch)
        appearance.body.addWidget(label('Tizimdagi kamaytirilgan harakat sozlamasi ham hisobga olinadi.','subtitle',True))
        v.addWidget(appearance)
        data=QGroupBox("Mahalliy ma’lumotlar va xavfsizlik")
        d=QVBoxLayout(data)
        data_label=QLabel("Baza: "+str(self.db.path)+"\n\nSQLite shifrlanmagan. Administrator paroli tuzlangan PBKDF2-SHA256 xeshi sifatida saqlanadi. Mahalliy fayllarni operatsion tizim ruxsatlari va disk shifrlashi bilan himoyalang. Zaxira nusxalarida ham hisob xeshi va barcha ma’lumotlar bor.")
        data_label.setWordWrap(True)
        data_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        d.addWidget(data_label)
        d.addWidget(button("Baza zaxira nusxasini saqlash",self.backup,True))
        d.addWidget(button("Tekshirilgan zaxiradan tiklash",self.restore))
        d.addWidget(button("Administrator parolini almashtirish",self.change_password))
        v.addWidget(data)
        demo=QGroupBox("Namoyish ma’lumotlari • ixtiyoriy")
        de=QVBoxLayout(demo)
        txt=QLabel("NAMUNA bilan belgilangan o‘quv yozuvlarini qo‘shadi. Amaldagi tashkilot profili va yozuvlar almashtirilmaydi.")
        txt.setWordWrap(True)
        de.addWidget(txt)
        de.addWidget(button("NAMUNA to‘plamini qo‘shish",self.demo))
        v.addWidget(demo)
        v.addWidget(QLabel("UzHi — UzluksizBCMS Desktop 1.1.0\nMahalliy administrator • ISO sertifikati yoki DGU ro‘yxatdan o‘tganligi da’vo qilinmaydi."))
        v.addStretch()
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(page)
        self.stack.addWidget(scroll)

    def backup(self):
        path,_=QFileDialog.getSaveFileName(self,"Zaxira nusxasi","UzluksizBCMS-backup.sqlite3","SQLite (*.sqlite3)")
        if not path:return
        try:
            self.db.backup(path)
            self.notify("Zaxira nusxasi saqlandi.")
        except (OSError,sqlite3.Error,ValueError) as exc:self.show_error(exc)

    def restore(self):
        if self.jobs:
            QMessageBox.information(self,'Hisobot','Tiklashdan oldin hisobot yaratilishi tugashini kuting.')
            return
        path,_=QFileDialog.getOpenFileName(self,"Zaxira nusxasini tanlash","","SQLite (*.sqlite3 *.db)")
        if not path:return
        if not ConfirmDialog.ask(self,"Tiklashni tasdiqlash","Joriy ma’lumotlar tanlangan nusxa bilan almashtiriladi. Avval avtomatik xavfsizlik nusxasi saqlanadi. Zaxiradagi administrator paroli bilan qayta kirish talab etiladi. Davom etilsinmi?"):return
        try:
            safety=self.db.restore(path)
            self.stack.setVisible(False)
            self.nav.setEnabled(False)
            self.menuBar().setEnabled(False)
            if not authenticate(Authentication(self.db),self):
                self.close()
                return
            self.stack.setVisible(True)
            self.nav.setEnabled(True)
            self.menuBar().setEnabled(True)
            self.refresh_all()
            self.statusBar().showMessage("Tiklandi. Oldingi ma’lumotlar nusxasi: "+str(safety),20000)
        except (OSError,sqlite3.Error,ValueError) as exc:
            self.stack.setVisible(True)
            self.nav.setEnabled(True)
            self.menuBar().setEnabled(True)
            self.show_error(exc)

    def change_password(self):
        fields=[("username","Administrator nomi","line",None),("old","Amaldagi parol","password",None),("new","Yangi parol","password",None),("confirm","Yangi parol takrori","password",None)]
        dlg=FormDialog("Parolni almashtirish",fields,parent=self)
        while dlg.exec()==QDialog.DialogCode.Accepted:
            try:
                v=dlg.values()
                if v["new"]!=v["confirm"]:raise ValueError("Yangi parollar mos emas.")
                Authentication(self.db).change_password(v["username"],v["old"],v["new"])
                self.notify("Parol almashtirildi.")
                return
            except ValueError as exc:self.show_error(exc)

    def demo(self):
        if not ConfirmDialog.ask(self,"NAMUNA ma’lumotlari","Faqat namoyish yozuvlari qo‘shilsinmi?"):return
        try:
            add_demo(self.service)
            self.refresh_all()
            self.statusBar().showMessage("NAMUNA yozuvlari qo‘shildi.",6000)
        except (ValueError,sqlite3.Error) as exc:self.show_error(exc)

    def refresh_all(self):
        orgs=self.service.repo.all("organization")
        org=orgs[0] if orgs else None
        self.org_label.setText((org["name"] if org else "Boshlash: Tashkilot bo‘limida profil yarating.")+"    •    Mahalliy baza")
        self.profile.setText(f'{org["name"]}\nSoha: {org["industry"]}  |  Mas’ul: {org["responsible"]}\n{org["description"]}' if org else "Tashkilot profili hali yaratilmagan.")
        for page in self.registries:page.refresh()
        metrics=self.service.metrics()
        self.dashboard_empty.setVisible(metrics['processes']==0)
        for key,status in self.setup_labels.items():
            count=len(orgs) if key=='organization' else len(self.service.risks()) if key=='risks' else metrics[key]
            status.set_complete(bool(count))
        for key,value in metrics.items():
            if key in self.cards:self.cards[key].setText(str(value))
        self.priority_chart.set_rows([(p["name"],p["score"],COLORS[p["category"]]) for p in self.service.rankings()])
        risks=self.service.risks()
        counts=Counter(r["category"] for r in risks)
        self.risk_chart.maximum=max(1,max(counts.values(),default=1))
        self.risk_chart.set_rows([(label,counts[key],COLORS[key]) for key,label in CATEGORIES.items()] if risks else [])
        self.matrix.update_risks(risks)
        self.dashboard_matrix.update_risks(risks)
        rankings=self.service.rankings();plans=self.service.plans()
        self.recovery_summary.setText(f"BIA kiritilgan: {metrics['bia']} / {metrics['processes']} jarayon\n"
            f"RTO / RPO / MTPD belgilangan: {len(rankings)} jarayon\n"
            f"Tayyor rejalar: {sum(p['readiness']=='Tayyor' for p in plans)} / {len(plans)}\n\n"
            'Vaqt maqsadlari va tayyorlik mavjud BIA va reja yozuvlaridan olinadi. Baholanmagan holat tayyor deb hisoblanmaydi.')

    def show_error(self,exc):
        if isinstance(exc,sqlite3.IntegrityError):
            text="Ma’lumot saqlanmadi: majburiy qiymat, noyob kod yoki bog‘lanishni tekshiring. Bog‘langan yozuvlarni o‘chirishdan oldin ularning havolalarini olib tashlang."
        elif isinstance(exc,sqlite3.Error):text="Baza amali bajarilmadi. Baza fayli va ruxsatlarni tekshiring."
        elif isinstance(exc,OSError):text="Fayl amali bajarilmadi. Manzil va yozish ruxsatini tekshiring."
        else:text=str(exc)
        QMessageBox.warning(self,"Amal bajarilmadi",text)

    def closeEvent(self,event):
        if any(job.isRunning() for job in self.jobs):
            QMessageBox.information(self,"Hisobot","Hisobot yaratilishi tugashini kuting.")
            event.ignore()
            return
        self.settings.sync()
        event.accept()
