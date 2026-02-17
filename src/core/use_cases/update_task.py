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

    def execute(self, task_id: str, status: str, user_email: str):
        set_correlation_id(task_id)
        
        logger.info(f"Atualizando status da task {task_id} para {status}")

        self.repo.update_status(task_id, status)

        try:
            task = self.repo.find_by_id(task_id)
            filename = task.get("filename", "Vídeo Sem Nome") if task else "Vídeo Desconhecido"

            download_url = None
            if status in ["DONE"]:
                s3_path = task.get("s3_download_path")
                if s3_path:
                    if not s3_path.endswith('.zip'):
                        s3_path += '.zip'
                    
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
