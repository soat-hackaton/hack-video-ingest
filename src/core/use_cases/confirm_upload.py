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

        try:
            item = self.repo.find_by_id(task_id)
            if not item:
                logger.warning("Tentativa de confirmação para Task inexistente")
                raise ResourceNotFoundException("Task não encontrada")

            if not self.storage.file_exists(item['s3_path']):
                logger.error("Arquivo não encontrado no S3 após confirmação do cliente")
                raise BusinessRuleException("Arquivo não encontrado no Storage")
        
            # Check Concurrency limit BEFORE processing: Fair Queuing
            active_tasks = self.repo.count_processing_by_user(item['user_email'])
            
            if active_tasks < 5:
                message = {
                    "task_id": task_id,
                    "s3_path": item['s3_path'],
                    "filename": item['filename'],
                    "user_email": item['user_email']
                }

                logger.info("Limite respeitado, enviando mensagem para SQS", extra={"queue_url": self.queue_url, "active": active_tasks})
                self.broker.send_message(self.queue_url, message)
                self.repo.update_status(task_id, TaskStatus.PROCESSING)
                logger.info("Processo de ingestão finalizado com sucesso, enviado para worker", extra={"step": "ingest_complete"})
                return {"status": "success", "message": "Vídeo enfileirado para processamento"}
            else:
                logger.info("Limite de concorrência atingido para o usuário. Mantendo vídeo na fila.", extra={"active": active_tasks, "user_email": item['user_email']})
                self.repo.update_status(task_id, TaskStatus.QUEUED)
                return {"status": "success", "message": "Vídeo aguardando vaga para processamento (limite excedido)."}

        except Exception as e:
            logger.error("Erro crítico ao processar confirmação. Atualizando status para ERROR.", exc_info=True)
            try:
                self.repo.update_status(task_id, TaskStatus.ERROR)
            except Exception as db_error:
                logger.error(f"Falha secundária ao tentar atualizar status para ERROR: {db_error}")
            raise e