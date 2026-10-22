import json
import socket
from app.core.smoke import run_smoke


def test_complete_smoke_without_python_network(qapp,tmp_path,monkeypatch):
    def denied(*args,**kwargs):
        raise AssertionError("Network use is forbidden in this offline workflow")
    monkeypatch.setattr(socket.socket,"connect",denied)
    monkeypatch.setattr(socket,"create_connection",denied)
    output=tmp_path/"offline-smoke"
    assert run_smoke(qapp,output)==0
    report=json.loads((output/"result.json").read_text(encoding="utf-8"))
    assert report["status"]=="passed" and report["restart_persistence"]
    # Verification must refuse to overwrite previous evidence or business records.
    before=(output/"smoke.sqlite3").read_bytes()
    assert run_smoke(qapp,output)==2
    assert (output/"smoke.sqlite3").read_bytes()==before
