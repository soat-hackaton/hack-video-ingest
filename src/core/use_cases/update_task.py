import logging
from src.core.interfaces import RepositoryInterface, StorageInterface
from src.core.use_cases.update_video_status import UpdateVideoStatusUseCase
from src.infra.logging.context import set_correlation_id

logger = logging.getLogger(__name__)

class UpdateTaskUseCase:
    def __init__(self, repo: RepositoryInterface, update_status_use_case: UpdateVideoStatusUseCase, storage: StorageInterface):
        self.repo = repo
        self.update_status_use_case = update_status_use_case
        self.storage = storage

    def execute(self, task_id: str, status: str, user_email: str, s3_download_path: str = None):
        set_correlation_id(task_id)
        
        logger.info(f"Atualizando status da task {task_id} para {status}")

        updated_task = self.repo.update_status(task_id, status, s3_download_path)

        try:
            filename = updated_task.get("filename", "Vídeo")

            download_url = None
            if status in ["DONE"]:
                s3_path = updated_task.get("s3_download_path")          
                download_url = self.storage.generate_download_url(s3_path)

            self.update_status_use_case.execute(
                user_email=user_email,
                status=status,
                filename=filename,
                download_url=download_url
            )
            
        except Exception as e:
            # Não queremos que falha no envio de e-mail quebre a atualização do status
            logger.error(f"Status atualizado, mas falha ao enviar notificação: {e}")

        return {"id": task_id, "status": status}
