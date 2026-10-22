import sqlite3
import pytest
from app.database.store import Database
from app.services.bcms import BCMS
from app.services.auth import Authentication
from app.services.demo import add_demo


def test_schema_initialization_is_repeatable(db):
    assert db.conn.execute("PRAGMA user_version").fetchone()[0]==1
    assert db.conn.execute("PRAGMA foreign_keys").fetchone()[0]==1
    path=db.path
    other=Database(path)
    assert BCMS(other).metrics()["processes"]==0
    other.close()


def test_crud_and_parameterization(service):
    service.save("organization",dict(name="O‘zgarmas",industry="IT",description="",responsible="Ali"))
    did=service.save("department",dict(name="x'); DROP TABLE admin; --",responsible="A"))
    assert len(service.repo.all("department"))==1
    service.save("department",dict(name="Tahrir",responsible="B"),did)
    assert service.repo.get("department",did)["name"]=="Tahrir"
    service.repo.delete("department",did)
    assert service.repo.all("department")==[]
    with pytest.raises(ValueError):service.repo.all("admin; DELETE FROM admin")


def test_foreign_keys_and_unique_codes(populated):
    s=populated
    with pytest.raises(sqlite3.IntegrityError):s.repo.delete("department",1)
    with pytest.raises(sqlite3.IntegrityError):s.repo.delete("business_process",1)
    p=s.repo.get("business_process",1)
    p.pop("id")
    p["code"]="NEW"
    p["department_id"]=999
    with pytest.raises(sqlite3.IntegrityError):s.save("business_process",p)
    p["department_id"]=1;p["code"]="NAMUNA-01"
    with pytest.raises(sqlite3.IntegrityError):s.save("business_process",p)
    assert not s.db.conn.execute("PRAGMA foreign_key_check").fetchall()


def test_plan_steps_atomic_and_cascade(populated):
    s=populated
    p=s.repo.get("continuity_plan",1);p.pop("id")
    old=s.steps(1)
    p["name"]="Must roll back"
    with pytest.raises(ValueError):s.save_plan(p,[{"instruction":"","completed":False}],1)
    assert s.repo.get("continuity_plan",1)["name"]!="Must roll back"
    assert s.steps(1)==old
    s.repo.delete("continuity_plan",1)
    assert s.steps(1)==[]
    assert s.scenario_links(1)[1]==[]


def test_priority_ties_use_shorter_rto(populated):
    s=populated
    p=s.repo.get("business_process",1);p.pop("id");p["code"]="FAST";p["name"]="Fast"
    pid=s.save("business_process",p)
    s.save("bia_assessment",dict(process_id=pid,financial=4,operational=5,reputational=3,compliance=3,mtpd=24,rto=2,rpo=0))
    assert [p["code"] for p in s.rankings()]==["FAST","NAMUNA-01"]
    assert s.rankings()[0]["rpo"]==0


def test_backup_restore_and_invalid_backup(populated,tmp_path):
    s=populated
    path=s.db.backup(tmp_path/"saved.sqlite3")
    s.save("department",dict(name="After backup",responsible=""))
    safety=s.db.restore(path)
    assert safety.is_file()
    assert len(s.repo.all("department"))==1
    prior=Database(safety)
    assert len(BCMS(prior).repo.all("department"))==2
    prior.close()
    bad=tmp_path/"bad.db";bad.write_bytes(b"not a database")
    with pytest.raises(sqlite3.DatabaseError):s.db.restore(bad)
    assert s.metrics()["processes"]==1
    with pytest.raises(ValueError):s.db.backup(s.db.path)
    with pytest.raises(ValueError):s.db.restore(s.db.path)


def test_future_database_untouched(tmp_path):
    path=tmp_path/"future.db"
    con=sqlite3.connect(path);con.execute("PRAGMA user_version=99");con.close()
    before=path.read_bytes()
    with pytest.raises(ValueError):Database(path)
    assert path.read_bytes()==before


def test_backup_schema_validation(populated,tmp_path):
    path=populated.db.backup(tmp_path/"bad-schema.db")
    con=sqlite3.connect(path);con.execute("CREATE TABLE intruder (x TEXT)");con.close()
    with pytest.raises(ValueError):populated.db.restore(path)
    assert populated.metrics()["processes"]==1


def test_persistence(populated):
    path=populated.db.path
    other=Database(path)
    assert BCMS(other).metrics()==populated.metrics()
    assert BCMS(other).latest_result(1)["result"]["rows"][0]["rto_violation"] is True
    other.close()


def test_scenario_edit_invalidates_saved_result(populated):
    s=populated
    data=s.repo.get("scenario",1);data.pop("id");data["duration"]=25
    s.save_scenario(data,[1],[1],1)
    assert s.latest_result(1) is None
    result=s.evaluate(1)
    assert result["result"]["rows"][0]["mtpd_violation"] is True


def test_cross_process_links_rejected(populated):
    s=populated
    p=s.repo.get("business_process",1);p.pop("id");p["code"]="SECOND"
    second=s.save("business_process",p)
    data=s.repo.get("continuity_plan",1);data.pop("id");data["process_id"]=second
    with pytest.raises(ValueError):s.save_plan(data,s.steps(1),1)
    risk=s.repo.get("risk",1);risk.pop("id");risk["process_id"]=second
    with pytest.raises(ValueError):s.save("risk",risk,1)
    scenario=s.repo.get("scenario",1);scenario.pop("id")
    with pytest.raises(ValueError):s.save_scenario(scenario,[second],[1])


def test_demo_preserves_organization(service):
    service.save("organization",dict(name="Real organization",industry="IT",description="",responsible=""))
    add_demo(service)
    assert service.repo.get("organization",1)["name"]=="Real organization"
    with pytest.raises(ValueError):add_demo(service)
    assert service.metrics()["processes"]==1


def test_admin_salted_hash_and_change(db):
    auth=Authentication(db)
    assert not auth.configured()
    with pytest.raises(ValueError):auth.create("admin","short")
    auth.create("admin","Long password 123")
    assert auth.verify("admin","Long password 123")
    assert not auth.verify("wrong","Long password 123")
    assert not auth.verify("admin","Wrong password")
    row=dict(db.conn.execute("SELECT * FROM admin").fetchone())
    assert row["password_hash"]!="Long password 123" and len(row["salt"])==64
    with pytest.raises(ValueError):auth.create("second","Long password 123")
    auth.change_password("admin","Long password 123","A new long password")
    assert auth.verify("admin","A new long password") and not auth.verify("admin","Long password 123")


def test_plan_readiness_is_derived(populated):
    s=populated
    p=s.repo.get("continuity_plan",1);p.pop("id")
    steps=s.steps(1)
    assert s.plans()[0]["readiness"]!="Tayyor"
    for step in steps:step["completed"]=True
    s.save_plan(p,steps,1)
    assert s.plans()[0]["readiness"]=="Tayyor"
    p["review_date"]="2000-01-01"
    s.save_plan(p,steps,1)
    assert s.plans()[0]["readiness"]!="Tayyor"


def test_corrupt_authentication_fails_safely(db):
    auth=Authentication(db)
    auth.create("admin","A secure password")
    with db.conn:
        db.conn.execute("UPDATE admin SET password_hash=?",("buzilgan‘",))
    assert not auth.verify("admin","A secure password")


def test_restore_rejects_corrupt_administrator(db,tmp_path):
    auth=Authentication(db)
    auth.create("admin","A secure password")
    backup=db.backup(tmp_path/"corrupt-account.sqlite3")
    con=sqlite3.connect(backup)
    with con:con.execute("UPDATE admin SET salt='00'")
    con.close()
    with pytest.raises(ValueError):db.restore(backup)
    assert auth.verify("admin","A secure password")


def test_coordinated_plan_save_preserves_procedures(populated):
    s=populated
    data=s.repo.get("continuity_plan",1);data.pop("id")
    data["name"]="Updated plan"
    steps=s.steps(1)
    s.save("continuity_plan",data,1)
    assert [r["instruction"] for r in s.steps(1)]==[r["instruction"] for r in steps]
