from pydantic import BaseModel

class UploadRequestSchema(BaseModel):
    filename: str
    content_type: str

class UploadResponseSchema(BaseModel):
    upload_url: str
    task_id: str