from src.core.interfaces.storage import StorageInterface
from src.core.interfaces.repositories import VideoRepositoryInterface
from src.core.entities.video_task import VideoTask
import uuid

class RequestUploadUseCase:
    # Recebemos as interfaces no construtor (Injeção de Dependência)
    def __init__(self, storage: StorageInterface, repo: VideoRepositoryInterface):
        self.storage = storage
        self.repo = repo

    def execute(self, filename: str, content_type: str):
        task_id = str(uuid.uuid4())
        s3_key = f"uploads/{task_id}"
        
        # O UseCase não sabe que é AWS S3, só sabe que é um "Storage"
        url = self.storage.generate_presigned_url(s3_key, content_type)
        
        task = VideoTask(id=task_id, filename=filename, s3_path=s3_key, status="PENDING")
        self.repo.save(task)
        
        return {"upload_url": url, "task_id": task_id}