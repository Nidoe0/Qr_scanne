from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SharedFileResponse(BaseModel):
    id: int
    original_name: str
    size: int
    sha256: str
    token: str
    created_at: datetime
    expires_at: datetime
    model_config = ConfigDict(from_attributes=True)
