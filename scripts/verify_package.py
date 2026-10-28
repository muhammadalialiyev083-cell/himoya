"""Launch the real frozen program, inspect its fresh results and exported documents."""
import argparse
import csv
import hashlib
import json
import os
import secrets
from pathlib import Path
import subprocess
import sys
from datetime import datetime,timezone
from pypdf import PdfReader

root=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument("binary",type=Path)
args=parser.parse_args()
binary=args.binary.resolve()
if sys.platform=='win32':
    import struct
    with binary.open('rb') as handle:
        assert handle.read(2)==b'MZ'
        handle.seek(0x3c);offset=struct.unpack('<I',handle.read(4))[0]
        handle.seek(offset);assert handle.read(4)==b'PE\0\0'
        assert struct.unpack('<H',handle.read(2))[0]==0x8664
        handle.seek(offset+24+68);assert struct.unpack('<H',handle.read(2))[0]==2
stamp=datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
output=root/"release"/f"packaged-smoke-{stamp}"
environment=dict(os.environ)
environment["QT_QPA_PLATFORM"]="offscreen"
environment["XDG_CACHE_HOME"]=str(root/".cache")
# No Python path or site packages from the development venv may assist the bundle.
environment.pop("PYTHONPATH",None)
environment.pop("PYTHONHOME",None)
environment["UZHI_SMOKE_PASSWORD"]=secrets.token_urlsafe(24)
result=subprocess.run([str(binary),"--self-test-dir",str(output)],env=environment,cwd=root,timeout=120)
if result.returncode:
    raise SystemExit(f"Frozen smoke test failed ({result.returncode}). Inspect {output}")
restart=subprocess.run([str(binary),"--self-test-restart-dir",str(output)],env=environment,cwd=root,timeout=120)
if restart.returncode:raise SystemExit(f"Frozen restart failed ({restart.returncode}); inspect {output}")
restart_report=json.loads((output/"restart-result.json").read_text(encoding="utf-8"))
assert restart_report['status']=='passed' and restart_report['new_executable_process'] and restart_report['authentication']
report=json.loads((output/"result.json").read_text(encoding="utf-8"))
assert report["status"]=="passed" and report["restart_persistence"] and report["backup_restore"]
for name in ("assessment.pdf","register.pdf","plan.pdf"):
    reader=PdfReader(output/name)
    text=" ".join(page.extract_text() for page in reader.pages)
    assert "NAMUNA" in text and ("o‘" in text or "g‘" in text)
with (output/"register.csv").open(encoding="utf-8-sig",newline="") as handle:
    assert any("Kritik" in row for row in csv.reader(handle))
assert (output/"dashboard.png").stat().st_size>5000
metadata={"binary":str(binary),"bytes":binary.stat().st_size,"sha256":hashlib.sha256(binary.read_bytes()).hexdigest(),
          "result_directory":str(output),"status":"passed","host":sys.platform,
          "windows_interactive_verified":False,"two_executable_processes_verified":True,"note":"Headless executable smoke test; interactive Windows verification remains a separate release gate."}
(root/"release"/f"{sys.platform}-package-verification.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
print(json.dumps(metadata,indent=2))

(root/'release'/'SHA256SUMS.txt').write_text(metadata['sha256']+'  '+binary.name+'\n',encoding='utf-8')
