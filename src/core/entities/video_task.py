from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))

def get_now_brt():
    """Retorna o horário atual em UTC-3"""
    return datetime.now(BRT)

@dataclass
class VideoTask:
    id: str
    filename: str
    s3_path: str
    s3_download_path: str
    status: str
    user_email: str
    created_at: datetime = field(default_factory=get_now_brt)