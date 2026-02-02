from pydantic import BaseModel

class UploadVideoRequest(BaseModel):
    filename: str
    content_type: str

class UploadVideoResponse(BaseModel):
    upload_url: str
    task_id: str