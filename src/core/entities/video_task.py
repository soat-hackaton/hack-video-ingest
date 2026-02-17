from dataclasses import dataclass
from datetime import datetime

@dataclass
class VideoTask:
    id: str
    filename: str
    s3_path: str
    s3_download_url: str
    status: str
    user_email: str
    created_at: datetime = field(default_factory=datetime.now)