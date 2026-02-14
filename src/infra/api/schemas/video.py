from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VideoItemResponse(BaseModel):
    id: str
    filename: str
    status: str
    created_at: datetime
    download_url: Optional[str] = None

class VideoListResponse(BaseModel):
    items: list[VideoItemResponse]