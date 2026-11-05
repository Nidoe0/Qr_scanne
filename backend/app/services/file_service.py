from pathlib import Path
import hashlib
import secrets
from app.config import STORAGE_DIR

def ensure_storage():
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

def new_storage_path():
    ensure_storage()
    name = secrets.token_hex(24)
    return name, STORAGE_DIR / name

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def delete_stored_file(name: str):
    path = STORAGE_DIR / Path(name).name
    path.unlink(missing_ok=True)
