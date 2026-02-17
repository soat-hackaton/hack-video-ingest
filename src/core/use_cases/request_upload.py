import logging
import uuid
from src.core.interfaces import StorageInterface, RepositoryInterface
from src.core.entities.video_task import VideoTask
from src.infra.logging.context import set_correlation_id
from src.infra.api.schemas.upload import TaskStatus

logger = logging.getLogger(__name__)

class RequestUploadUseCase:
    def __init__(self, storage: StorageInterface, repo: RepositoryInterface):
        self.storage = storage
        self.repo = repo

    def execute(self, filename: str, content_type: str, user_email: str):
        task_id = str(uuid.uuid4())
        set_correlation_id(task_id)

        logger.info("Iniciando processo de solicitação de upload", extra={
            "video_filename": filename,
            "step": "request_upload_start"
        })

        s3_key = f"uploads/{task_id}"
        s3_download_key = f"results/{task_id}.zip"

        try:
            url = self.storage.generate_presigned_url(s3_key, content_type)

            logger.info("URL Pré-assinada gerada com sucesso", extra={
                "s3_key": s3_key,
                "step": "request_presigned_url"
            })

            task = VideoTask (
                id=task_id,
                filename=filename,
                s3_path=s3_key,
                s3_download_path=s3_download_key,
                status=TaskStatus.QUEUED.value,
                user_email=user_email
            )
            self.repo.save(task)

            logger.info("Registro criado com sucesso no S3", extra={
                "s3_key": s3_key,
                "step": "request_upload_success"
            })

            return {"upload_url": url, "task_id": task_id}

        except Exception as e:
            logger.error("Erro crítico ao gerar solicitação de upload. Atualizando status para ERROR.", exc_info=True)
            try:
                self.repo.update_status(task_id, TaskStatus.ERROR)
            except Exception as db_error:
                logger.error(f"Falha secundária ao tentar atualizar status para ERROR: {db_error}")
            raise e