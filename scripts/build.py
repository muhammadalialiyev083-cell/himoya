"""Run only on the target OS; PyInstaller does not cross-compile Windows binaries."""
import argparse
import json
from pathlib import Path
import platform
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--target",choices=["windows","linux"],default="windows")
    args=parser.parse_args()
    expected="Windows" if args.target=="windows" else "Linux"
    (ROOT/"release").mkdir(exist_ok=True)
    if platform.system()!=expected:
        message={"status":"blocked","target":args.target,"host":platform.system(),"reason":"PyInstaller requires a native target-OS Python environment; cross-compilation is unsupported.","windows_exe_exists":(ROOT/"dist/UzluksizBCMS.exe").is_file()}
        (ROOT/"release"/f"{args.target}-build-status.json").write_text(json.dumps(message,indent=2),encoding="utf-8")
        print(message["reason"])
        return 2
    if sys.version_info[:2]!=(3,12) or struct.calcsize("P")!=8:
        raise SystemExit("Python 3.12 x64 is required.")
    # Application imports provide PyInstaller's static dependency graph.
    command=[sys.executable,"-m","PyInstaller","--noconfirm","--clean","--onefile","--windowed",
             "--name","UzluksizBCMS","--distpath",str(ROOT/"dist"),"--workpath",str(ROOT/"build"),
             "--specpath",str(ROOT/"build"),"--paths",str(ROOT),
             "--add-data",f"{ROOT/'app/database/schema.sql'}:app/database",
             "--add-data",f"{ROOT/'app/resources/icon.svg'}:app/resources",
             "--exclude-module","PySide6.QtWebEngineCore","--exclude-module","PySide6.QtWebEngineWidgets",
             "--exclude-module","PySide6.QtQml","--exclude-module","PySide6.QtQuick"]
    if args.target=="windows":
        icon=ROOT/"assets"/"UzluksizBCMS.ico"
        if not icon.is_file():
            subprocess.run([sys.executable,str(ROOT/"scripts"/"make_icon.py")],check=True,cwd=ROOT)
        command += ["--icon",str(icon),"--version-file",str(ROOT/"scripts"/"windows_version.txt")]
    command.append(str(ROOT/"app"/"main.py"))
    subprocess.run(command,check=True,cwd=ROOT)
    binary=ROOT/"dist"/("UzluksizBCMS.exe" if args.target=="windows" else "UzluksizBCMS")
    header=binary.read_bytes()[:4]
    assert header.startswith(b"MZ" if args.target=="windows" else b"\x7fELF")
    print(f"Built {binary} ({binary.stat().st_size:,} bytes). Run the packaged smoke test next.")
    return 0


if __name__=="__main__":raise SystemExit(main())
