from src.core.interfaces import StorageInterface, RepositoryInterface
from src.core.entities.video_task import VideoTask
import uuid

class RequestUploadUseCase:
    def __init__(self, storage: StorageInterface, repo: RepositoryInterface):
        self.storage = storage
        self.repo = repo

    def execute(self, filename: str, content_type: str):
        task_id = str(uuid.uuid4())
        s3_key = f"hack-uploaded-videos/uploads/{task_id}"
        
        url = self.storage.generate_presigned_url(s3_key, content_type)
        
        task = VideoTask(id=task_id, filename=filename, s3_path=s3_key, status="PENDING")
        self.repo.save(task)
        
        return {"upload_url": url, "task_id": task_id}