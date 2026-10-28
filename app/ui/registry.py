import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QTextBrowser, QVBoxLayout, QWidget)

from app.algorithms.scoring import CATEGORIES, COLORS
from app.reports.export import esc, table as html_table, category
from app.ui.fields import fields_for, LABELS
from app.ui.forms import FormDialog
from app.ui.widgets import button, setup_table, StepEditor
from app.ui.components import EmptyState, SearchToolbar, FilterToolbar, StatusBadge, ConfirmDialog
from app.ui.icons import icon
from app.ui.style import tokens


class Registry(QWidget):
    def __init__(self, main, entity, columns, provider=None, note=""):
        super().__init__()
        self.main,self.service,self.entity = main,main.service,entity
        self.columns,self.provider,self.rows = columns,provider,[]
        self.metric_filter=None
        self.setObjectName("pageSurface")
        v = QVBoxLayout(self)
        v.setContentsMargins(0,8,0,0)
        if note:
            label=QLabel(note)
            label.setWordWrap(True)
            label.setObjectName("subtitle")
            v.addWidget(label)
        searchbar=SearchToolbar();h=searchbar.body
        self.search=searchbar.search
        self.search.textChanged.connect(self.clear_metric_filter)
        h.addWidget(self.search,1)
        self.filter=QComboBox()
        self.filter.addItem("Barcha darajalar",None)
        for k,c in CATEGORIES.items(): self.filter.addItem(c,k)
        self.filter.currentIndexChanged.connect(self.clear_metric_filter)
        self.filter.setVisible(entity in ("business_process","bia_assessment","risk"))
        h.addWidget(self.filter)
        v.addWidget(searchbar)
        toolbar=FilterToolbar();actions=toolbar.body
        self.add_button=button('+ Qo‘shish',lambda:self.edit(),True);self.add_button.setIcon(icon('plus'))
        actions.addWidget(self.add_button)
        self.selection_actions=[]
        for title,handler,name in [('Tahrirlash',self.edit_selected,None),('Tafsilot',self.detail,None),('O‘chirish',self.delete,'danger')]:
            control=button(title,handler,name=name);actions.addWidget(control);self.selection_actions.append(control)
        actions.addStretch()
        self.count_label=QLabel();actions.addWidget(self.count_label)
        v.addWidget(toolbar)
        self.table=QTableWidget(0,len(columns))
        setup_table(self.table)
        self.table.setHorizontalHeaderLabels([title for key,title in columns])
        self.table.doubleClicked.connect(lambda _:self.detail())
        self.table.itemSelectionChanged.connect(self.update_actions)
        v.addWidget(self.table,1)
        self.empty=EmptyState('Yozuvlar hali kiritilmagan','Boshlash uchun birinchi yozuvni yarating.',lambda:self.edit(),'+ Qo‘shish')
        v.addWidget(self.empty)
        self.toolbar=QHBoxLayout()
        v.addLayout(self.toolbar)
        if entity == "scenario":
            self.toolbar.addWidget(button("Ssenariyni baholash",self.evaluate,True))
            self.toolbar.addWidget(button("Saqlangan natija",self.scenario_result))
        if entity == "continuity_plan":
            self.toolbar.addWidget(button("Tanlangan rejani PDFga chiqarish",self.export_plan,True))
        self.toolbar.addStretch()
        self.update_actions()

    def clear_metric_filter(self):
        self.metric_filter=None
        self.populate()

    def refresh(self):
        self.rows=self.provider() if self.provider else self.service.repo.all(self.entity)
        self.populate()

    def populate(self):
        query=self.search.text().casefold()
        severity=self.filter.currentData()
        shown=[r for r in self.rows if query in " ".join(str(v) for v in r.values()).casefold() and (not severity or r.get("category")==severity)]
        if self.metric_filter=='high_risks':shown=[r for r in shown if r.get('category') in ('High','Critical')]
        if self.metric_filter=='assessments':shown=[r for r in shown if self.service.latest_result(r['id'])]
        self.table.setRowCount(len(shown))
        self.displayed=shown
        for i,row in enumerate(shown):
            for j,(key,title) in enumerate(self.columns):
                value=row.get(key)
                text=category(value) if key=="category" else "—" if value is None else f"{value:.2f}" if key=="score" else str(value)
                item=QTableWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole,row["id"])
                item.setToolTip(text)
                if key=="category" and value:
                    item.setForeground(QColor({'Critical':'#ffabb8','High':'#ffc087','Medium':'#f2d675','Low':'#6ee7c4'}[value] if tokens().base=='#142331' else COLORS[value]))
                self.table.setItem(i,j,item)
                if key=='category' and value:
                    badge=StatusBadge(text,value)
                    self.table.setCellWidget(i,j,badge)
        self.table.resizeColumnsToContents()
        for i in range(len(self.columns)):
            self.table.setColumnWidth(i,min(290,max(92,self.table.columnWidth(i))))
        self.empty.setVisible(not shown)
        self.table.setVisible(bool(shown))
        prefix='Yuqori / kritik · ' if self.metric_filter=='high_risks' else 'Baholangan · ' if self.metric_filter=='assessments' else ''
        self.count_label.setText(prefix+f'{len(shown)} / {len(self.rows)} yozuv')
        self.empty.title.setText('Qidiruv natijasi yo‘q' if self.rows else 'Yozuvlar hali kiritilmagan')
        self.empty.action.setVisible(not self.rows)
        self.update_actions()
        self.empty.setText("Qidiruv bo‘yicha yozuv topilmadi." if self.rows else "Hozircha yozuvlar yo‘q. «Qo‘shish» orqali boshlang.")

    def update_actions(self):
        selected=self.table.currentRow()>=0
        for control in self.selection_actions:control.setEnabled(selected)

    def selected(self):
        row=self.table.currentRow()
        if row<0:
            QMessageBox.information(self,"Tanlash","Avval jadvaldan yozuvni tanlang.")
            return None
        return self.displayed[row]["id"]

    def edit_selected(self):
        rid=self.selected()
        if rid is not None:self.edit(rid)

    def edit(self, record_id=None):
        service=self.service
        values=service.repo.get(self.entity,record_id) if record_id else {}
        if self.entity=="scenario" and record_id:
            values["process_ids"],values["plan_ids"]=service.scenario_links(record_id)
        note = "* Majburiy maydon. Bog‘langan yozuvlar haqiqiy baza kalitlari bilan saqlanadi."
        if self.entity=="bia_assessment":
            note="Tadqiqot modeli: 20 × (0.30×M + 0.35×O + 0.20×Ob + 0.15×H). RTO ≤ MTPD; RPO alohida maqsad. Rasmiy ISO formulasi emas."
        dlg=FormDialog("Yozuvni tahrirlash" if record_id else "Yangi yozuv",fields_for(self.entity,service),values,self,note)
        # Reference labels include process names and filter by process to avoid invalid links.
        if self.entity=="continuity_plan":
            def sync_refs():
                pid=dlg.widgets["process_id"].currentData()
                for field,table,label in (("risk_id","risk","title"),("strategy_id","recovery_strategy","name")):
                    w=dlg.widgets[field]
                    old=w.currentData()
                    w.clear()
                    w.addItem("Bog‘lanmagan",None)
                    for r in service.repo.all(table):
                        if r["process_id"]==pid: w.addItem(r[label],r["id"])
                    index=w.findData(old)
                    w.setCurrentIndex(max(0,index))
            dlg.widgets["process_id"].currentIndexChanged.connect(sync_refs)
            sync_refs()
            steps=StepEditor(service.steps(record_id) if record_id else [])
            dlg.layout().insertWidget(dlg.layout().count()-1,steps)
            dlg.resize(680,690)
        while dlg.exec()==QDialog.DialogCode.Accepted:
            try:
                data=dlg.values()
                if self.entity=="continuity_plan":
                    service.save_plan(data,steps.values(),record_id)
                elif self.entity=="scenario":
                    processes,plans=data.pop("process_ids"),data.pop("plan_ids")
                    service.save_scenario(data,processes,plans,record_id)
                else:
                    service.save(self.entity,data,record_id)
                self.main.refresh_all()
                self.main.notify("Yozuv saqlandi.")
                return
            except (ValueError,sqlite3.Error) as exc:
                self.main.show_error(exc)

    def delete(self):
        rid=self.selected()
        if rid is None:return
        message="Yozuv o‘chirilsinmi? Bu amalni ortga qaytarib bo‘lmaydi."
        if self.entity=="business_process":message+=" Jarayon BIA tahlili ham o‘chiriladi. Bog‘langan risk, reja va ssenariy mavjud bo‘lsa, o‘chirish bloklanadi."
        if self.entity=="continuity_plan":message+=" Tiklash bosqichlari va ssenariydagi ushbu reja bog‘lanishlari o‘chiriladi."
        if self.entity=="scenario":message+=" Bog‘langan baholash natijalari ham o‘chiriladi."
        if self.entity in ("risk","recovery_strategy"):message+=" Rejalarda ushbu ixtiyoriy bog‘lanish olib tashlanadi."
        if not ConfirmDialog.ask(self,"O‘chirishni tasdiqlash",message):return
        try:
            self.service.repo.delete(self.entity,rid)
            self.main.refresh_all()
        except (ValueError,sqlite3.Error) as exc:self.main.show_error(exc)

    def show_html(self,title,body):
        dlg=QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(760,570)
        layout=QVBoxLayout(dlg)
        browser=QTextBrowser()
        browser.setOpenExternalLinks(False)
        t=tokens()
        # Report HTML is reused as content, but on-screen colors follow the theme.
        browser.document().setDefaultStyleSheet(f'body {{color:{t.text}; background:{t.surface};}} table {{border-collapse:collapse;}} th,td {{padding:8px; border:1px solid {t.border};}} th {{background:{t.raised}; color:{t.text};}}')
        browser.setHtml(body)
        layout.addWidget(browser)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)
        dlg.exec()

    def detail(self):
        rid=self.selected()
        if rid is None:return
        row=next(r for r in self.rows if r["id"]==rid)
        body=html_table(["Maydon","Qiymat"],[(LABELS.get(k,k),category(v) if k=="category" else v) for k,v in row.items() if k in LABELS])
        if self.entity=="business_process":
            body+="<h3>Bog‘langan risklar</h3>"+html_table(["Nomi","Ball","Daraja"],[(r["title"],r["score"],category(r["category"])) for r in self.service.risks() if r["process_id"]==rid])
            body+="<h3>Uzluksizlik rejalari</h3>"+html_table(["Kod","Nomi","Tayyorlik"],[(p["code"],p["name"],p["readiness"]) for p in self.service.plans() if p["process_id"]==rid])
        if self.entity=="bia_assessment":
            body+="<p>BIA = 20 × (0.30×moliyaviy + 0.35×operatsion + 0.20×obro‘ + 0.15×huquqiy). 75+: kritik, 50+: yuqori, 25+: o‘rta. Tadqiqot parametrlari; rasmiy ISO formulasi emas.</p>"
        if self.entity=="continuity_plan":
            body+="<h3>Tiklash tartibi</h3>"+html_table(["№","Amal","Bajarilgan"],[(s["position"],s["instruction"],"Ha" if s["completed"] else "Yo‘q") for s in self.service.steps(rid)])
        if self.entity=="scenario":
            processes,plans=self.service.scenario_links(rid)
            body+="<h3>Ta’sirlangan jarayonlar</h3><p>"+esc(", ".join(p["name"] for p in self.service.processes() if p["id"] in processes))+"</p>"
            body+="<h3>Tanlangan rejalar</h3><p>"+esc(", ".join(p["name"] for p in self.service.plans() if p["id"] in plans))+"</p>"
        self.show_html("Yozuv tafsilotlari",body)

    def evaluate(self):
        rid=self.selected()
        if rid is None:return
        try:
            self.service.evaluate(rid)
            self.main.refresh_all()
            self.show_result(rid)
        except (ValueError,sqlite3.Error) as exc:self.main.show_error(exc)

    def scenario_result(self):
        rid=self.selected()
        if rid is not None:self.show_result(rid)

    def show_result(self,rid):
        result=self.service.latest_result(rid)
        if not result:
            QMessageBox.information(self,"Baholash","Avval ssenariyni baholang. Tahrirdan keyin qayta baholash zarur.")
            return
        snapshot=result["result"]
        yes=lambda x:"BIA yo‘q" if x is None else "Ha" if x else "Yo‘q"
        body=f'<h2>{esc(snapshot["scenario"]["name"])}</h2><p>{esc(result["evaluated_at"])} • {esc(snapshot["model"])}</p>'
        body+=html_table(["Jarayon","Soat","RTO oshdi","MTPD oshdi","Rejalar","Tavsiya"],[(r["name"],r["duration"],yes(r["rto_violation"]),yes(r["mtpd_violation"]),", ".join(r["plans"]),r["recommendation"]) for r in snapshot["rows"]])
        body+="<p>Bu saqlangan baholash nusxasi. BIA yoki rejalar o‘zgargan bo‘lsa, yangi baholashni bajaring. Resurslar modelda avtomatik vaqt yutug‘iga aylantirilmaydi.</p>"
        self.show_html("Stol usti baholashi",body)

    def export_plan(self):
        rid=self.selected()
        if rid is not None:self.main.export("plan",rid)
