"""Capture isolated Qt review evidence at the caller's QT_SCALE_FACTOR."""
import argparse
import json
import os
from pathlib import Path
import secrets
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from app.core.fonts import report_font
from app.database.store import Database
from app.services.auth import Authentication
from app.services.demo import add_demo
from app.ui.fields import fields_for
from app.ui.forms import FormDialog, LoginDialog
from app.ui.style import apply_theme
from app.ui.window import MainWindow


def capture(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    application=QApplication.instance() or QApplication([])
    application.setStyle('Fusion');report_font();apply_theme(application,'light')
    evidence=[]
    with tempfile.TemporaryDirectory(prefix='uzhi-visual-') as folder:
        db=Database(Path(folder)/'visual.sqlite3')
        auth=Authentication(db)
        def save(widget,name):
            application.processEvents()
            image=widget.grab()
            assert not image.isNull() and image.save(str(output/(name+'.png')))
            evidence.append({'name':name,'logical_size':[widget.width(),widget.height()],
                             'image_size':[image.width(),image.height()],'device_pixel_ratio':image.devicePixelRatio()})
        first=LoginDialog(auth);first.show();save(first,'first-run-light');first.close()
        auth.create('visual-admin',secrets.token_urlsafe(24))
        login=LoginDialog(auth);login.show();save(login,'login-light');login.close()
        window=MainWindow(db);window.set_motion(False);window.set_theme('light');window.resize(1366,768);window.show()
        save(window,'empty-light-1366x768')
        assert all(value.text()=='0' for value in window.cards.values())
        add_demo(window.service);window.refresh_all()
        for theme in ('light','dark'):
            window.set_theme(theme)
            login=LoginDialog(auth);login.show();save(login,'login-'+theme);login.close()
            for width,height in ((1366,768),(1920,1080)):
                window.resize(width,height);window.navigate('dashboard');application.processEvents()
                assert window.dashboard.horizontalScrollBar().maximum()==0
                assert window.nav.tree.viewport().width()>0
                for card in window.metric_widgets.values():
                    assert card.height()>=120 and card.value.height()>=card.value.fontMetrics().height()
                save(window,f'dashboard-{theme}-{width}x{height}')
            window.resize(1366,768)
            for key in ('organization','processes','bia','risks','plans','strategies','scenarios','reports','settings','setup','catalog'):
                window.navigate(key);save(window,key+'-'+theme)
            form=FormDialog('BIA tahlili',fields_for('bia_assessment',window.service),parent=window)
            form.show();save(form,'bia-form-'+theme);form.close()
            window.navigate('dashboard');window.nav.set_compact(True,animate=False)
            save(window,'compact-'+theme);window.nav.set_compact(False,animate=False)
        window.close();db.close()
    report={'platform':sys.platform,'qt_platform':application.platformName(),
            'scale_factor':os.environ.get('QT_SCALE_FACTOR','1'),'interactive_windows_verified':False,
            'records':'isolated NAMUNA data only','captures':evidence}
    (output/'visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    result=capture(parser.parse_args().output)
    print(f"Captured {len(result['captures'])} Qt screenshots at scale {result['scale_factor']}.")
