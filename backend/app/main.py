from fastapi import FastAPI
from app.database import Base, engine
from app.models.file import SharedFile  # noqa: F401
from app.config import STORAGE_DIR
from app.routers.files import router as files_router

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="QR Connect API",
    version="0.2.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.include_router(files_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "qr-connect-api"}
