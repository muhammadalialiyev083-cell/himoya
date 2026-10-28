"""Behavioral UI regressions for the native UzHi shell, using isolated SQLite."""
import pytest
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QPalette, QRawFont
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QLineEdit, QMessageBox
from app.services.auth import Authentication
from app.services.demo import add_demo
from app.ui.forms import FormDialog, LoginDialog
from app.ui.navigation import ROUTES
from app.ui.style import DARK, LIGHT, apply_theme, animations_enabled
from app.ui.window import MainWindow

@pytest.fixture
def window(qapp,db):
    widget=MainWindow(db);widget.set_motion(False);widget.show();qapp.processEvents()
    yield widget
    widget.close();widget.deleteLater();qapp.processEvents();apply_theme(qapp,'light')


def test_first_run_validation_visibility_and_keyboard(qapp,db):
    auth=Authentication(db);dialog=LoginDialog(auth);dialog.show();qapp.processEvents()
    dialog.accept()
    assert not auth.configured() and dialog.error.isVisible()
    dialog.widgets['username'].setText('Oʻzbekiston admin')
    dialog.widgets['password'].setText('Long test password')
    dialog.widgets['confirm'].setText('Different password')
    dialog.accept()
    assert not auth.configured() and 'mos' in dialog.error.text()
    assert not dialog.widgets['password'].text()
    dialog.widgets['password'].setText('Long test password')
    dialog.password_actions['password'].trigger()
    assert dialog.widgets['password'].echoMode()==QLineEdit.EchoMode.Normal
    dialog.password_actions['password'].trigger()
    assert dialog.widgets['password'].echoMode()==QLineEdit.EchoMode.Password
    dialog.widgets['confirm'].setText('Long test password')
    QTest.keyClick(dialog.widgets['confirm'],Qt.Key.Key_Return)
    assert dialog.result()==QDialog.DialogCode.Accepted
    assert auth.verify('Oʻzbekiston admin','Long test password')
    assert not dialog.widgets['password'].text()
    login=LoginDialog(auth);login.show();qapp.processEvents()
    assert not login.first and 'confirm' not in login.widgets
    login.widgets['username'].setText('Oʻzbekiston admin');login.widgets['password'].setText('Wrong password')
    login.accept()
    assert login.result()!=QDialog.DialogCode.Accepted and login.error.isVisible()
    login.widgets['password'].setText('Long test password');login.accept()
    assert login.result()==QDialog.DialogCode.Accepted
    cancel=LoginDialog(auth);cancel.show();QTest.keyClick(cancel,Qt.Key.Key_Escape)
    assert cancel.result()==QDialog.DialogCode.Rejected and not cancel.isVisible()


def test_nested_tree_keyboard_search_and_compact(window,qapp):
    nav=window.nav
    group=nav.groups[ROUTES['bia'].group]
    assert not group.isExpanded()
    nav.tree.setCurrentItem(group);QTest.keyClick(nav.tree,Qt.Key.Key_Right)
    assert group.isExpanded()
    nav.tree.setCurrentItem(nav.items['bia']);QTest.keyClick(nav.tree,Qt.Key.Key_Return)
    assert window.current_route=='bia' and window.stack.currentIndex()==3
    assert 'BIA' in window.header.breadcrumb.text()
    nav.search.setText('matritsa');qapp.processEvents()
    assert not nav.items['matrix'].isHidden() and nav.items['plans'].isHidden()
    nav.search.clear()
    QTest.mouseClick(nav.toggle,Qt.MouseButton.LeftButton);qapp.processEvents()
    assert nav.compact and nav.width()==76 and not nav.search.isVisible()
    assert nav.tree.currentItem()==nav.items['bia'].parent()
    assert nav.tree.currentItem().toolTip(0)==ROUTES['bia'].group
    nav.focus_search();qapp.processEvents()
    assert not nav.compact and nav.width()==284 and nav.search.hasFocus()


def test_history_branching_and_menu_navigation(window,qapp):
    window.actions['nav_processes'].trigger();window.actions['nav_bia'].trigger()
    expected=list(window.history.entries)
    window.actions['back'].trigger()
    assert window.current_route=='processes' and window.history.entries==expected
    window.actions['forward'].trigger()
    assert window.current_route=='bia' and window.history.entries==expected
    window.go_back();window.navigate('risks')
    assert not window.history.can_forward and window.history.entries[-1]=='risks'
    assert not window.actions['forward'].isEnabled()
    assert window.header.title.text()==ROUTES['risks'].title
    assert window.nav.tree.currentItem()==window.nav.items['risks']
    window.navigate('strategies');assert window.plan_tabs.currentIndex()==1
    window.navigate('steps');assert window.plan_tabs.currentIndex()==0
    window.actions['home'].trigger();assert window.current_route=='dashboard'
    assert not window.actions['new'].isEnabled()
    window.navigate('departments');assert window.actions['new'].isEnabled()
    assert len(window.menuBar().actions())==5


def test_real_metrics_and_click_through_filters(window,qapp):
    assert window.dashboard_empty.isVisible()
    assert all(value.text()=='0' for value in window.cards.values())
    assert not window.priority_chart.rows and not window.risk_chart.rows
    add_demo(window.service);window.refresh_all();qapp.processEvents()
    assert not window.dashboard_empty.isVisible()
    assert window.cards['processes'].text()=='1'
    assert window.cards['critical'].text()=='1'
    # Add a low risk so the high-risk card must actually filter the registry.
    original=window.service.repo.get('risk',1)
    values={k:v for k,v in original.items() if k!='id'}
    values.update(title='Past risk',likelihood=1,impact=1)
    window.service.save('risk',values);window.refresh_all()
    QTest.mouseClick(window.metric_widgets['high_risks'],Qt.MouseButton.LeftButton)
    assert window.current_route=='risks' and window.risks.table.rowCount()==1
    assert window.risks.displayed[0]['score']==16
    window.navigate('dashboard');QTest.mouseClick(window.metric_widgets['critical'],Qt.MouseButton.LeftButton)
    assert window.bia.filter.currentData()=='Critical' and window.bia.table.rowCount()==1
    assert window.bia.table.item(0,2).text()=='80.00'
    assert '1 ta' in window.dashboard_matrix.item(1,3).text()
    for card in window.metric_widgets.values():
        assert card.height()>=120 and card.value.height()>=card.value.fontMetrics().height()


def test_themes_motion_and_preferences_persist(window,qapp,db):
    path=db.path
    window.actions['theme_dark'].trigger()
    assert qapp.palette().color(QPalette.ColorRole.Base).name()==DARK.surface
    assert qapp.palette().color(QPalette.ColorRole.Text).name()==DARK.text
    window.nav.set_compact(True,animate=False)
    window.set_motion(False);assert not animations_enabled()
    window.close()
    reopened=MainWindow(db)
    assert qapp.property('uzhiTheme')=='dark' and reopened.nav.compact
    assert not animations_enabled() and reopened.db.path==path
    reopened.set_theme('light')
    assert qapp.palette().color(QPalette.ColorRole.Base).name()==LIGHT.surface
    reopened.close();reopened.deleteLater();qapp.processEvents()


def test_backup_restore_reauthenticates_and_retains_data(window,qapp,monkeypatch,tmp_path):
    auth=Authentication(window.db);auth.create('restore-admin','Restore test password')
    add_demo(window.service);window.refresh_all();metrics=window.service.metrics()
    backup=tmp_path/'saved.sqlite3'
    monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *a,**k:(str(backup),''))
    window.actions['backup'].trigger();assert backup.is_file()
    window.service.save('department',{'name':'Temporary','responsible':''})
    monkeypatch.setattr(QFileDialog,'getOpenFileName',lambda *a,**k:(str(backup),''))
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    failures=[]
    def login():
        try:
            dialog=QApplication.activeModalWidget();assert isinstance(dialog,LoginDialog)
            dialog.widgets['username'].setText('restore-admin');dialog.widgets['password'].setText('Restore test password');dialog.accept()
        except BaseException as exc:
            failures.append(exc)
            if QApplication.activeModalWidget():QApplication.activeModalWidget().reject()
    QTimer.singleShot(50,login)
    window.actions['restore'].trigger()
    assert not failures and window.service.metrics()==metrics
    assert window.stack.isVisible() and window.nav.isEnabled() and window.menuBar().isEnabled()
    assert list((window.db.path.parent/'backups').glob('before-restore-*.sqlite3'))


def test_required_form_fields_have_inline_validation(qapp):
    dialog=FormDialog('Tashkilot',[('name','Nomi *','line',None)])
    dialog.show();qapp.processEvents();dialog.accept()
    assert dialog.result()!=QDialog.DialogCode.Accepted and dialog.error.isVisible()
    dialog.widgets['name'].setText('Tashkilot');dialog.accept()
    assert dialog.result()==QDialog.DialogCode.Accepted


def test_embedded_font_supports_uzbek_latin(qapp):
    raw=QRawFont.fromFont(QFont('Noto Sans',12))
    assert raw.isValid()
    for char in 'Oʻ oʻ Gʻ gʻ O‘ o‘ G‘ g‘':assert raw.supportsCharacter(ord(char))


@pytest.mark.parametrize('width,height',[(1366,768),(1920,1080),(900,560)])
def test_responsive_layout_has_no_horizontal_overflow(window,qapp,width,height):
    window.resize(width,height);qapp.processEvents()
    assert window.dashboard.horizontalScrollBar().maximum()==0
    assert window.header.quick.geometry().right()<=window.header.width()
    for card in window.metric_widgets.values():
        assert card.width()>=160 and card.height()>=120
        assert card.value.height()>=card.value.fontMetrics().height()
    window.navigate('risks');qapp.processEvents()
    assert window.matrix.horizontalScrollBar().maximum()==0


def test_finite_sidebar_logo_and_page_animations(window,qapp):
    from app.ui.style import motion_allowed
    if not motion_allowed():
        window.set_motion(True)
        assert not animations_enabled()
        return
    window.set_motion(True)
    window.nav.set_compact(True)
    QTest.qWait(240)
    assert window.nav.width()==76 and window.nav.width_animation.loopCount()==1
    window.nav.set_compact(False);QTest.qWait(240)
    assert window.nav.width()==284
    window.nav.logo.setChecked(True);QTest.qWait(380)
    assert window.nav.logo.reveal==1.0 and window.nav.logo.animation.loopCount()==1
    window.navigate('bia');QTest.qWait(200)
    assert window.fade_effect.opacity()==1.0
    window.set_motion(False)
    assert not window.nav.tree.isAnimated()


def test_theme_text_contrast_is_readable():
    def luminance(color):
        values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
        linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
        return sum(v*w for v,w in zip(linear,(.2126,.7152,.0722)))
    for theme in (LIGHT,DARK):
        for foreground in (theme.text,theme.muted):
            for background in (theme.base,theme.surface):
                a,b=sorted((luminance(foreground),luminance(background)))
                assert (b+.05)/(a+.05)>=4.5
