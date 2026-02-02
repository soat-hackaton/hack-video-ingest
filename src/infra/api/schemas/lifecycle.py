from pydantic import BaseModel

class ConfirmVideoUploadRequest(BaseModel):
    task_id: str

class ConfirmVideoUploadResponse(BaseModel):
    status: str
    message: str