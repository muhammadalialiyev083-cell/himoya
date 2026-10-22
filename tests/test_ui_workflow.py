import time
from datetime import date,timedelta
from PySide6.QtCore import QDate,QTimer,Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QDialog,QFileDialog,QMessageBox
from app.database.store import Database
from app.services.auth import Authentication
from app.ui.forms import FormDialog,authenticate
from app.ui.window import MainWindow


def fill_dialog(data,steps=None):
    errors=[]
    def fill():
        try:
            dlg=QApplication.activeModalWidget()
            assert isinstance(dlg,FormDialog)
            for key,value in data.items():
                widget=dlg.widgets[key]
                kind=next(f[2] for f in dlg.fields if f[0]==key)
                if kind=="choice":
                    index=widget.findData(value);assert index>=0
                    widget.setCurrentIndex(index)
                elif kind in ("integer","number","impact"):widget.setValue(value)
                elif kind=="date":widget.setDate(QDate.fromString(value,"yyyy-MM-dd"))
                elif kind=="text":widget.setPlainText(value)
                elif kind=="multi":
                    for i in range(widget.count()):
                        item=widget.item(i)
                        item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in value else Qt.CheckState.Unchecked)
                else:widget.setText(value)
            if steps is not None:
                from app.ui.widgets import StepEditor
                editor=dlg.findChild(StepEditor)
                assert editor
                for step in steps:editor.add(step=step)
            dlg.accept()
        except BaseException as exc:
            errors.append(exc)
            modal=QApplication.activeModalWidget()
            if modal:modal.reject()
    QTimer.singleShot(30,fill)
    return errors


def test_full_desktop_workflow(qapp,tmp_path,monkeypatch):
    errors=[]
    def fail_dialog(*args,**kwargs):
        errors.append(str(args))
        return QMessageBox.StandardButton.Ok
    monkeypatch.setattr(QMessageBox,"warning",fail_dialog)
    database=Database(tmp_path/"e2e.sqlite3")
    auth=Authentication(database)
    form_errors=fill_dialog(dict(username="administrator",password="A safe test password",confirm="A safe test password"))
    assert authenticate(auth)
    assert not form_errors
    main=MainWindow(database)
    main.show();qapp.processEvents()
    def submit(action,data,steps=None):
        form_errors=fill_dialog(data,steps)
        action()
        assert not form_errors and not errors
        qapp.processEvents()
    submit(main.edit_org,dict(name="O‘zbekiston — Uzluksizlik",industry="Xizmat",description="E2E sinov",responsible="Ali"))
    submit(main.departments.edit,dict(name="Operatsiyalar",responsible="Vali"))
    submit(main.processes.edit,dict(code="P-001",name="To‘lovlar",description="Hisob-kitob",department_id=1,responsible="Ali",resources="Noutbuk",it_dependency="Baza",status="Faol"))
    submit(main.bia.edit,dict(process_id=1,financial=4,operational=5,reputational=3,compliance=3,mtpd=24,rto=4,rpo=1))
    submit(main.risks.edit,dict(title="Elektr uzilishi",process_id=1,threat="Elektr yo‘q",vulnerability="Bitta manba",likelihood=4,impact=4,mitigation="UPS",owner="Ali",action="Generator",status="Ochiq"))
    submit(main.strategies.edit,dict(name="Zaxira ish joyi",process_id=1,actions="Ko‘chish",resources="Ofis",responsible="Vali",priority=1))
    submit(main.plans.edit,dict(code="BCP-001",name="To‘lovlar uzluksizligi",process_id=1,risk_id=1,strategy_id=1,responsible="Ali",objectives="RTO 4 soat; RPO 1 soat",resources="UPS, noutbuk",review_date=(date.today()+timedelta(days=365)).isoformat(),status="Tasdiqlangan"),[{"instruction":"Xabar berish","completed":True},{"instruction":"Xizmatni tiklash","completed":False}])
    submit(main.scenarios.edit,dict(name="Elektr uzilishi mashqi",description="Stol usti",duration=8,resources="UPS",actions="Tiklash",process_ids=[1],plan_ids=[1]))
    main.scenarios.table.selectRow(0)
    # Exercise evaluation through the real UI action; close only the result dialog.
    QTimer.singleShot(30,lambda:QApplication.activeModalWidget().accept())
    main.scenarios.evaluate()
    assert main.service.latest_result(1)["result"]["rows"][0]["rto_violation"] is True
    assert main.bia.table.item(0,2).text()=="80.00"
    assert "1 ta" in main.matrix.item(1,3).text()
    assert main.cards["processes"].text()=="1"
    for i in range(9):
        main.nav.setCurrentRow(i);qapp.processEvents()
        assert main.stack.currentIndex()==i
    main.processes.search.setText("missing")
    assert main.processes.table.rowCount()==0
    main.processes.search.setText("To‘lov")
    assert main.processes.table.rowCount()==1
    main.risks.filter.setCurrentIndex(main.risks.filter.findData("Low"))
    assert main.risks.table.rowCount()==0
    main.risks.filter.setCurrentIndex(0)
    # Export through the UI's background worker, then wait while processing Qt events.
    report=tmp_path/"desktop-report.pdf"
    monkeypatch.setattr(QFileDialog,"getSaveFileName",lambda *a,**k:(str(report),"PDF"))
    main.export("assessment")
    deadline=time.monotonic()+15
    while main.jobs and time.monotonic()<deadline:
        QTest.qWait(20)
    assert not main.jobs and report.read_bytes().startswith(b"%PDF-")
    assert not errors
    main.close();qapp.processEvents();database.close()
    # A new database connection and window require authentication and retain all work.
    database=Database(tmp_path/"e2e.sqlite3")
    fill_dialog(dict(username="administrator",password="A safe test password"))
    assert authenticate(Authentication(database))
    reopened=MainWindow(database);reopened.show();qapp.processEvents()
    assert reopened.service.metrics()==dict(departments=1,processes=1,critical=1,bia=1,high_risks=1,plans=1,scenarios=1,assessments=1)
    assert reopened.service.steps(1)[0]["instruction"]=="Xabar berish"
    reopened.close();database.close()


def test_delete_requires_confirmation(qapp,populated,monkeypatch):
    window=MainWindow(populated.db)
    window.risks.table.selectRow(0)
    monkeypatch.setattr(QMessageBox,"question",lambda *a,**k:QMessageBox.StandardButton.No)
    window.risks.delete()
    assert len(populated.risks())==1
    monkeypatch.setattr(QMessageBox,"question",lambda *a,**k:QMessageBox.StandardButton.Yes)
    window.risks.delete()
    assert populated.risks()==[]
    assert populated.repo.get("continuity_plan",1)["risk_id"] is None
    assert "0 ta" in window.matrix.item(1,3).text()
    window.close()
