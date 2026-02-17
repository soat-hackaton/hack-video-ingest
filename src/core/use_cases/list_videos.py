from src.infra.api.schemas.upload import TaskStatus
from src.core.interfaces.repositories import RepositoryInterface
from src.core.interfaces.storage import StorageInterface

class ListVideosUseCase:
    def __init__(self, repo: RepositoryInterface, storage: StorageInterface):
        self.repo = repo
        self.storage = storage

    def execute(self, user_email: str):
        items = self.repo.list_by_user(user_email)
        
        formatted_items = []
        for item in items:
            status = item.get("status", TaskStatus.ERROR.value)
            download_url = None
            
            s3_download_path = item.get("s3_download_path")
            
            if (status == "DONE") and s3_download_path:
                download_url = self.storage.generate_download_url(s3_download_path)

            formatted_items.append({
                "id": item.get("id"),
                "filename": item.get("filename"),
                "status": status,
                "created_at": item.get("created_at"),
                "download_url": download_url
            })

        return {
            "items": formatted_items
        }