import logging
import uuid
from src.core.interfaces import StorageInterface, RepositoryInterface
from src.core.entities.video_task import VideoTask
from src.infra.logging.context import set_correlation_id

logger = logging.getLogger(__name__)

class RequestUploadUseCase:
    def __init__(self, storage: StorageInterface, repo: RepositoryInterface):
        self.storage = storage
        self.repo = repo

    def execute(self, filename: str, content_type: str):
        task_id = str(uuid.uuid4())
        set_correlation_id(task_id)

        logger.info("Iniciando processo de solicitação de upload", extra={
            "video_filename": filename,
            "step": "request_upload_start"
        })

        s3_key = f"hack-uploaded-videos/uploads/{task_id}"
        
        try:
            url = self.storage.generate_presigned_url(s3_key, content_type)
            
            task = VideoTask(id=task_id, filename=filename, s3_path=s3_key, status="PENDING")
            self.repo.save(task)

            logger.info("URL Pré-assinada gerada com sucesso", extra={
                "s3_key": s3_key,
                "step": "request_upload_success"
            })
            
            return {"upload_url": url, "task_id": task_id}
        except Exception as e:
            logger.error("Erro ao gerar solicitação de upload", exc_info=True)
            raise e