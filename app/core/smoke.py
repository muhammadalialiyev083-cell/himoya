"""Executable self-test: isolated data, real Qt window, DB, reports and restart."""
import json
import secrets
import traceback
from pathlib import Path

from app.database.store import Database
from app.reports.export import snapshot, write_csv, write_pdf
from app.services.auth import Authentication
from app.services.demo import add_demo
from app.services.bcms import BCMS
from app.ui.window import MainWindow


def run_smoke(application, output):
    output=Path(output).resolve()
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):
        return 2  # Never change an existing data directory during verification.
    db=None
    window=None
    try:
        password=secrets.token_urlsafe(24)
        db=Database(output/"smoke.sqlite3")
        auth=Authentication(db)
        auth.create("smoke-admin",password)
        assert auth.verify("smoke-admin",password)
        assert not auth.verify("smoke-admin",password+"x")
        window=MainWindow(db)
        window.show()
        application.processEvents()
        add_demo(window.service)
        window.refresh_all()
        for i in range(9):
            window.nav.setCurrentRow(i)
            application.processEvents()
            assert window.stack.currentIndex()==i
        window.nav.setCurrentRow(0)
        application.processEvents()
        window.grab().save(str(output/"dashboard.png"))
        data=snapshot(window.service)
        write_pdf(output/"assessment.pdf",data)
        write_pdf(output/"register.pdf",data,"register")
        write_pdf(output/"plan.pdf",data,"plan",data["plans"][0]["id"])
        write_csv(output/"register.csv",data)
        db.backup(output/"backup.sqlite3")
        metrics=window.service.metrics()
        assert metrics["bia"]==1 and metrics["high_risks"]==1 and metrics["assessments"]==1
        result=window.service.latest_result(1)["result"]["rows"][0]
        assert result["rto_violation"] is True and result["mtpd_violation"] is False
        window.close()
        window=None
        db.close()
        db=Database(output/"smoke.sqlite3")
        assert Authentication(db).verify("smoke-admin",password)
        assert BCMS(db).metrics()==metrics
        window=MainWindow(db)
        window.show()
        application.processEvents()
        assert window.plans.table.rowCount()==1
        window.close()
        window=None
        db.restore(output/"backup.sqlite3")
        assert BCMS(db).metrics()==metrics
        report={"status":"passed","version":"1.0.0","platform":__import__("sys").platform,
                "qt_window":True,"pages":9,"authentication":True,"restart_persistence":True,
                "backup_restore":True,"metrics":metrics,
                "exports":["assessment.pdf","register.pdf","plan.pdf","register.csv"],
                "network_required":False,"note":"Automated Qt smoke test; interactive Windows sign-off is separate."}
        (output/"result.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        return 0
    except Exception:
        (output/"failure.txt").write_text(traceback.format_exc(),encoding="utf-8")
        return 1
    finally:
        if window:window.close()
        if db:db.close()
