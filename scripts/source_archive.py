"""Create a clean standalone source delivery; never include venvs or user databases."""
import hashlib
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parent.parent
output=root/"release"/"UzluksizBCMS-Desktop-1.0.0-source.zip"
included=[]
for folder in ("app","tests","docs","scripts","assets",".github"):
    for path in (root/folder).rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            included.append(path)
for name in ("README.md","USER_MANUAL.md","requirements.txt","requirements-dev.txt","requirements-lock.txt","requirements-windows.txt","pytest.ini","build.ps1",".gitignore"):
    included.append(root/name)
for name in ("test-results.xml","windows-build-status.json","linux-package-verification.json","DELIVERY.md"):
    path=root/"release"/name
    if path.is_file():included.append(path)
for name in ("dashboard.png","assessment.pdf","register.pdf","plan.pdf","register.csv","result.json"):
    path=root/"release/source-smoke-final"/name
    if path.is_file():included.append(path)
with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(included):
        archive.write(path,Path("UzluksizBCMS-Desktop")/path.relative_to(root))
print(f"Source archive: {output} ({output.stat().st_size:,} bytes)")
checksum=hashlib.sha256(output.read_bytes()).hexdigest()
output.with_suffix(".zip.sha256").write_text(f"{checksum}  {output.name}\n",encoding="ascii")
