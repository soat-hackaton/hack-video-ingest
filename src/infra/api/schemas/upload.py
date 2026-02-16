from enum import Enum
from pydantic import BaseModel

class UploadVideoRequest(BaseModel):
    filename: str
    content_type: str

class UploadVideoResponse(BaseModel):
    upload_url: str
    task_id: str


class TaskStatus(str, Enum):
    ERROR = "ERROR"
    QUEUE = "QUEUE"
    PROCESSING = "PROCESSING"
    DONE = "DONE"


class UpdateTaskStatusRequest(BaseModel):
    status: TaskStatus
    user_email: str