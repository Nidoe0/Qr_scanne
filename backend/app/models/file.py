from datetime import datetime, timedelta, timezone
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.config import FILE_TTL_HOURS
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class SharedFile(Base):
    __tablename__ = "shared_files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(80), unique=True)
    size: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64))
    token: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: utcnow() + timedelta(hours=FILE_TTL_HOURS)
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
