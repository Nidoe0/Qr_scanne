import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = Path(os.getenv("QR_STORAGE_DIR", str(BASE_DIR / "storage"))).resolve()
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'qr_connect.db'}")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(1024 * 1024 * 1024)))
FILE_TTL_HOURS = int(os.getenv("FILE_TTL_HOURS", "24"))
QR_CONNECT_BASE_URL = os.getenv("QR_CONNECT_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
