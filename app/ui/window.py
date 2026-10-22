import os
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QListWidget, QMainWindow, QMessageBox,
    QScrollArea, QStackedWidget, QTabWidget, QVBoxLayout, QWidget)

from app.algorithms.scoring import CATEGORIES, COLORS
from app.reports.export import snapshot, write_csv, write_pdf
from app.services.auth import Authentication
from app.services.bcms import BCMS
from app.services.demo import add_demo
from app.ui.fields import fields_for
from app.ui.forms import FormDialog, authenticate
from app.ui.registry import Registry
from app.ui.widgets import Bars, RiskMatrix, button


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
        self.jobs=[]
        self.registries=[]
        self.setWindowTitle("UzluksizBCMS Desktop — 1.0.0")
        self.resize(1366,768)
        self.setMinimumSize(1080,680)
        icon=Path(__file__).resolve().parents[1]/"resources"/"icon.svg"
        if icon.exists():self.setWindowIcon(QIcon(str(icon)))
        root=QWidget()
        self.setCentralWidget(root)
        layout=QHBoxLayout(root)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        sidebar=QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(224)
        side=QVBoxLayout(sidebar)
        side.setContentsMargins(8,26,8,18)
        for text,name in (("◈  UZLUKSIZ","brand"),("    BCMS DESKTOP  /  1.0.0","brandSub"),("◇  ◇  ◈  ◇  ◇","ornament")):
            label=QLabel(text)
            label.setObjectName(name)
            side.addWidget(label)
        side.addSpacing(22)
        self.nav=QListWidget()
        self.nav.setObjectName("nav")
        self.titles=["Boshqaruv paneli","Tashkilot","Biznes jarayonlari","BIA tahlili","Risklarni baholash","Uzluksizlik rejalari","Simulyatsiya","Hisobotlar","Sozlamalar"]
        for i,title in enumerate(self.titles,1):self.nav.addItem(f"{i:02}   {title}")
        side.addWidget(self.nav,1)
        bottom=QLabel("●  Mahalliy ish rejimi\n\nSQLite • Internet talab qilinmaydi")
        bottom.setObjectName("brandSub")
        bottom.setContentsMargins(14,0,0,0)
        side.addWidget(bottom)
        layout.addWidget(sidebar)
        content=QWidget()
        c=QVBoxLayout(content)
        c.setContentsMargins(25,22,25,18)
        self.title=QLabel()
        self.title.setObjectName("pageTitle")
        c.addWidget(self.title)
        self.org_label=QLabel()
        self.org_label.setTextFormat(Qt.TextFormat.PlainText)
        self.org_label.setObjectName("subtitle")
        c.addWidget(self.org_label)
        c.addSpacing(10)
        self.stack=QStackedWidget()
        c.addWidget(self.stack,1)
        layout.addWidget(content,1)
        self.build_dashboard()
        self.build_organization()
        self.processes=self.registry("business_process",[("code","Kod"),("name","Jarayon"),("department","Bo‘lim"),("responsible","Mas’ul"),("category","BIA darajasi"),("status","Holat")],self.service.processes)
        self.stack.addWidget(self.processes)
        self.build_bia()
        self.build_risks()
        self.build_plans()
        self.scenarios=self.registry("scenario",[("name","Ssenariy"),("duration","Uzilish (soat)"),("resources","Resurslar")],note="Stol usti modeli: davomiylik RTO va MTPD bilan taqqoslanadi. O‘lchangan natija yoki ML bashorati emas.")
        self.stack.addWidget(self.scenarios)
        self.build_reports()
        self.build_settings()
        self.nav.currentRowChanged.connect(self.navigate)
        self.nav.setCurrentRow(0)
        self.refresh_all()
        self.statusBar().showMessage("Tayyor • Barcha ma’lumotlar mahalliy bazada saqlanadi.")

    def registry(self,*args,**kwargs):
        page=Registry(self,*args,**kwargs)
        self.registries.append(page)
        return page

    def navigate(self,index):
        self.stack.setCurrentIndex(index)
        self.title.setText(self.titles[index])

    def build_dashboard(self):
        scroll=QScrollArea()
        scroll.setWidgetResizable(True)
        page=QWidget()
        v=QVBoxLayout(page)
        v.setContentsMargins(0,0,0,0)
        intro=QLabel("FAOLIYAT UZLUKSIZLIGI  /  Umumiy holat")
        intro.setObjectName("subtitle")
        v.addWidget(intro)
        grid=QGridLayout()
        self.cards={}
        for i,(key,title) in enumerate((("processes","Biznes jarayonlari"),("departments","Bo‘limlar"),("critical","Kritik jarayonlar"),("high_risks","Yuqori / kritik risklar"),("bia","BIA tahlillari"),("plans","Uzluksizlik rejalari"),("scenarios","Ssenariylar"),("assessments","Baholangan ssenariylar"))):
            frame=QFrame()
            frame.setObjectName("card")
            box=QVBoxLayout(frame)
            box.setContentsMargins(17,12,17,12)
            value=QLabel("0")
            value.setObjectName("cardValue")
            caption=QLabel(title)
            caption.setWordWrap(True)
            caption.setObjectName("cardLabel")
            box.addWidget(value)
            box.addWidget(caption)
            self.cards[key]=value
            grid.addWidget(frame,i//4,i%4)
        v.addLayout(grid)
        h=QHBoxLayout()
        priority=QGroupBox("Jarayonlar ustuvorligi • BIA / 100 (yuqori 8 ta)")
        p=QVBoxLayout(priority)
        self.priority_chart=Bars()
        p.addWidget(self.priority_chart)
        h.addWidget(priority,3)
        severity=QGroupBox("Risklar darajasi • soni")
        s=QVBoxLayout(severity)
        self.risk_chart=Bars(1)
        s.addWidget(self.risk_chart)
        h.addWidget(severity,2)
        v.addLayout(h,1)
        note=QLabel("Tadqiqot modeli: vaznli BIA + risk matritsasi. Baholanmagan jarayonlar kritik deb taxmin qilinmaydi.\nNAMUNA yozuvlari namoyish uchun; haqiqiy ilmiy natijalar emas.")
        note.setWordWrap(True)
        note.setObjectName("subtitle")
        v.addWidget(note)
        scroll.setWidget(page)
        self.stack.addWidget(scroll)

    def build_organization(self):
        page=QWidget()
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
        self.plans=self.registry("continuity_plan",[("code","Kod"),("name","Reja"),("process","Jarayon"),("completion","Bajarilishi %"),("readiness","Tayyorlik"),("status","Holat")],self.service.plans,note="Tayyor: tasdiqlangan reja, barcha bosqichlar bajarilgan, mas’ul/resurs/maqsad to‘ldirilgan va ko‘rib chiqish sanasi o‘tmagan.")
        self.strategies=self.registry("recovery_strategy",[("name","Strategiya"),("responsible","Mas’ul"),("priority","Ustuvorlik"),("resources","Resurslar")])
        tabs.addTab(self.plans,"Uzluksizlik rejalari")
        tabs.addTab(self.strategies,"Tiklanish strategiyalari")
        self.stack.addWidget(tabs)

    def build_reports(self):
        page=QWidget()
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
        self.stack.addWidget(page)

    def export(self,kind,plan_id=None):
        ext="csv" if kind=="csv" else "pdf"
        path,_=QFileDialog.getSaveFileName(self,"Hisobotni saqlash",f"UzluksizBCMS-{kind}.{ext}",f"{ext.upper()} (*.{ext})")
        if not path:return
        if not path.lower().endswith("."+ext):path+="."+ext
        job=ExportJob(path,snapshot(self.service),kind,plan_id,self)
        job.outcome.connect(self.export_done)
        self.jobs.append(job)
        job.finished.connect(lambda:self.release_job(job))
        self.statusBar().showMessage("Hisobot tayyorlanmoqda…")
        job.start()

    def release_job(self,job):
        if job in self.jobs:self.jobs.remove(job)
        job.deleteLater()

    def export_done(self,message,ok):
        if ok:
            self.statusBar().showMessage("Hisobot saqlandi: "+message,15000)
        else:QMessageBox.warning(self,"Hisobot",message)

    def build_settings(self):
        page=QWidget()
        v=QVBoxLayout(page)
        v.setContentsMargins(0,0,0,0)
        data=QGroupBox("Mahalliy ma’lumotlar va xavfsizlik")
        d=QVBoxLayout(data)
        label=QLabel("Baza: "+str(self.db.path)+"\n\nSQLite shifrlanmagan. Administrator paroli tuzlangan PBKDF2-SHA256 xeshi sifatida saqlanadi. Mahalliy fayllarni operatsion tizim ruxsatlari va disk shifrlashi bilan himoyalang. Zaxira nusxalarida ham hisob xeshi va barcha ma’lumotlar bor.")
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        d.addWidget(label)
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
        v.addWidget(QLabel("UzluksizBCMS Desktop 1.0.0 MVP\nMahalliy administrator • ISO sertifikati yoki DGU ro‘yxatdan o‘tganligi da’vo qilinmaydi."))
        v.addStretch()
        self.stack.addWidget(page)

    def backup(self):
        path,_=QFileDialog.getSaveFileName(self,"Zaxira nusxasi","UzluksizBCMS-backup.sqlite3","SQLite (*.sqlite3)")
        if not path:return
        try:
            self.db.backup(path)
            self.statusBar().showMessage("Zaxira nusxasi saqlandi.",10000)
        except (OSError,sqlite3.Error,ValueError) as exc:self.show_error(exc)

    def restore(self):
        path,_=QFileDialog.getOpenFileName(self,"Zaxira nusxasini tanlash","","SQLite (*.sqlite3 *.db)")
        if not path:return
        if QMessageBox.question(self,"Tiklashni tasdiqlash","Joriy ma’lumotlar tanlangan nusxa bilan almashtiriladi. Avval avtomatik xavfsizlik nusxasi saqlanadi. Zaxiradagi administrator paroli bilan qayta kirish talab etiladi. Davom etilsinmi?",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:return
        try:
            safety=self.db.restore(path)
            self.stack.setVisible(False)
            self.nav.setEnabled(False)
            if not authenticate(Authentication(self.db),self):
                self.close()
                return
            self.stack.setVisible(True)
            self.nav.setEnabled(True)
            self.refresh_all()
            self.statusBar().showMessage("Tiklandi. Oldingi ma’lumotlar nusxasi: "+str(safety),20000)
        except (OSError,sqlite3.Error,ValueError) as exc:
            self.stack.setVisible(True)
            self.nav.setEnabled(True)
            self.show_error(exc)

    def change_password(self):
        fields=[("username","Administrator nomi","line",None),("old","Amaldagi parol","password",None),("new","Yangi parol","password",None),("confirm","Yangi parol takrori","password",None)]
        dlg=FormDialog("Parolni almashtirish",fields,parent=self)
        while dlg.exec()==QDialog.DialogCode.Accepted:
            try:
                v=dlg.values()
                if v["new"]!=v["confirm"]:raise ValueError("Yangi parollar mos emas.")
                Authentication(self.db).change_password(v["username"],v["old"],v["new"])
                self.statusBar().showMessage("Parol almashtirildi.",6000)
                return
            except ValueError as exc:self.show_error(exc)

    def demo(self):
        if QMessageBox.question(self,"NAMUNA ma’lumotlari","Faqat namoyish yozuvlari qo‘shilsinmi?",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:return
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
        for key,value in self.service.metrics().items():
            if key in self.cards:self.cards[key].setText(str(value))
        self.priority_chart.set_rows([(p["name"],p["score"],COLORS[p["category"]]) for p in self.service.rankings()])
        risks=self.service.risks()
        counts=Counter(r["category"] for r in risks)
        self.risk_chart.maximum=max(1,max(counts.values(),default=1))
        self.risk_chart.set_rows([(label,counts[key],COLORS[key]) for key,label in CATEGORIES.items()])
        self.matrix.update_risks(risks)

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
        event.accept()
