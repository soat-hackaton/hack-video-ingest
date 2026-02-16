import logging
import os
from src.core.interfaces import MessageBrokerInterface, RepositoryInterface, StorageInterface
from src.core.exceptions import ResourceNotFoundException, BusinessRuleException
from src.infra.logging.context import set_correlation_id
from src.infra.api.schemas.upload import TaskStatus

logger = logging.getLogger(__name__)

class ConfirmUploadUseCase:
    def __init__(
        self,
        repo: RepositoryInterface,
        storage: StorageInterface,
        broker: MessageBrokerInterface,
        queue_url: str
    ):
        self.repo = repo
        self.storage = storage
        self.broker = broker
        self.queue_url = queue_url

    def execute(self, task_id: str):
        set_correlation_id(task_id)

        logger.info("Iniciando confirmação de upload", extra={"step": "confirm_start"})

        item = self.repo.find_by_id(task_id)
        if not item:
            logger.warning("Tentativa de confirmação para Task inexistente")
            raise ResourceNotFoundException("Task não encontrada")

        if not self.storage.file_exists(item['s3_path']):
            self.repo.update_status(task_id, TaskStatus.ERROR)
            logger.error("Arquivo não encontrado no S3 após confirmação do cliente")
            raise BusinessRuleException("Arquivo não encontrado no Storage")

        try:
            message = {
                "task_id": task_id,
                "s3_path": item['s3_path'],
                "filename": item['filename'],
                "user_email": item['user_email']
            }

            logger.info("Enviando mensagem para SQS", extra={"queue_url": self.queue_url})
            self.broker.send_message(self.queue_url, message)

            self.repo.update_status(task_id, TaskStatus.QUEUED)

            logger.info("Processo de ingestão finalizado com sucesso", extra={"step": "ingest_complete"})
            return {"status": "success", "message": "Vídeo enfileirado para processamento"}

        except Exception as e:
            self.repo.update_status(task_id, TaskStatus.ERROR)
            logger.error("Erro crítico ao processar confirmação", exc_info=True)
            raise e