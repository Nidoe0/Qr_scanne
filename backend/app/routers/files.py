from datetime import datetime, timezone
from pathlib import Path
import secrets

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import MAX_FILE_SIZE, STORAGE_DIR
from app.database import get_db
from app.models.file import SharedFile
from app.schemas.file import SharedFileResponse
from app.services.file_service import new_storage_path, sha256_file
from app.services.qr_service import make_qr

router = APIRouter(tags=["Transferts"])

@router.post("/files/upload", response_model=SharedFileResponse, status_code=201)
async def upload_file(uploaded_file: UploadFile = File(...), db: Session = Depends(get_db)):
    original_name = Path(uploaded_file.filename or "fichier").name[:255]
    if not original_name or original_name in {".", ".."}:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide.")
    stored_name, destination = new_storage_path()
    size = 0
    try:
        with destination.open("wb") as output:
            while chunk := await uploaded_file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Fichier trop volumineux. Maximum : {MAX_FILE_SIZE // (1024 * 1024)} Mo.",
                    )
                output.write(chunk)
        if size == 0:
            raise HTTPException(status_code=400, detail="Le fichier est vide.")
        item = SharedFile(
            original_name=original_name,
            stored_name=stored_name,
            size=size,
            sha256=sha256_file(destination),
            token=secrets.token_urlsafe(32),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise
    finally:
        await uploaded_file.close()

@router.get("/files/{token}/qr")
def get_qr(token: str, db: Session = Depends(get_db)):
    item = db.scalar(select(SharedFile).where(
        SharedFile.token == token, SharedFile.is_active.is_(True)
    ))
    if not item:
        raise HTTPException(status_code=404, detail="Partage introuvable.")
    if item.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=410, detail="Ce partage a expiré.")
    return StreamingResponse(make_qr(item.token), media_type="image/png")

@router.get("/files/{token}")
def get_file_info(token: str, db: Session = Depends(get_db)):
    item = db.scalar(select(SharedFile).where(
        SharedFile.token == token, SharedFile.is_active.is_(True)
    ))
    if not item:
        raise HTTPException(status_code=404, detail="Partage introuvable.")
    if item.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=410, detail="Ce partage a expiré.")
    return {
        "original_name": item.original_name,
        "size": item.size,
        "sha256": item.sha256,
        "expires_at": item.expires_at.isoformat(),
    }

@router.get("/download/{token}")
def download_file(token: str, db: Session = Depends(get_db)):
    item = db.scalar(select(SharedFile).where(
        SharedFile.token == token, SharedFile.is_active.is_(True)
    ))
    if not item:
        raise HTTPException(status_code=404, detail="Jeton invalide ou fichier supprimé.")
    if item.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=410, detail="Lien expiré.")
    path = STORAGE_DIR / item.stored_name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Fichier introuvable sur le serveur.")
    return FileResponse(
        path=path,
        filename=item.original_name,
        media_type="application/octet-stream",
        headers={"X-File-Name": item.original_name, "X-File-SHA256": item.sha256},
    )
