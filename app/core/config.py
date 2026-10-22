import os
from pathlib import Path


def data_directory() -> Path:
    override = os.environ.get("UZLUKSIZ_DATA_DIR")
    if override:
        root = Path(override)
    elif os.name == "nt":
        root = Path(os.environ["LOCALAPPDATA"]) / "UzluksizBCMS"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "UzluksizBCMS"
    root.mkdir(parents=True, exist_ok=True)
    return root
