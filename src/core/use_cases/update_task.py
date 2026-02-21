import logging
from src.core.interfaces import RepositoryInterface, StorageInterface, MessageBrokerInterface
from src.core.use_cases.update_video_status import UpdateVideoStatusUseCase
from src.infra.logging.context import set_correlation_id

class TaskStatus:
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"

logger = logging.getLogger(__name__)

class UpdateTaskUseCase:
    def __init__(
        self, 
        repo: RepositoryInterface, 
        update_status_use_case: UpdateVideoStatusUseCase, 
        storage: StorageInterface,
        broker: MessageBrokerInterface,
        queue_url: str
    ):
        self.repo = repo
        self.update_status_use_case = update_status_use_case
        self.storage = storage
        self.broker = broker
        self.queue_url = queue_url

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

        # Auto-Feeding Mechanism
        if status in [TaskStatus.DONE, TaskStatus.ERROR]:
            try:
                oldest_queued = self.repo.get_oldest_queued_by_user(user_email)
                if oldest_queued:
                    queued_task_id = oldest_queued['id']
                    logger.info("Vaga aberta. Iniciando Auto-Feeding do vídeo da fila.", extra={"next_task": queued_task_id, "user": user_email})
                    
                    message = {
                        "task_id": queued_task_id,
                        "s3_path": oldest_queued['s3_path'],
                        "filename": oldest_queued.get('filename'),
                        "user_email": oldest_queued['user_email']
                    }
                    
                    self.broker.send_message(self.queue_url, message)
                    self.repo.update_status(queued_task_id, TaskStatus.PROCESSING)
                    
                    logger.info("Auto-Feeding concluído com sucesso. Vídeo enviado ao SQS.", extra={"next_task": queued_task_id})
            except Exception as e:
                # Falhas no Auto-Feeding não devem quebrar o fluxo principal de Update da Task atual
                logger.error(f"Falha ao executar rotina de Auto-Feeding: {e}", exc_info=True)

        return {"id": task_id, "status": status}
