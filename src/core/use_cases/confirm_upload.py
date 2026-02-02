import os
from src.core.interfaces import MessageBrokerInterface, RepositoryInterface, StorageInterface
from src.core.exceptions import ResourceNotFoundException, BusinessRuleException

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
        item = self.repo.find_by_id(task_id)
        if not item:
            raise ResourceNotFoundException("Task não encontrada")

        if not self.storage.file_exists(item['s3_path']):
            self.repo.update_status(task_id, "UPLOAD_FAILED")
            raise BusinessRuleException("Arquivo não encontrado no Storage")

        try:
            message = {
                "task_id": task_id,
                "s3_path": item['s3_path'],
                "filename": item['filename']
            }
            self.broker.send_message(self.queue_url, message)
            
            self.repo.update_status(task_id, "QUEUED")
            
            return {"status": "success", "message": "Vídeo enfileirado para processamento"}
            
        except Exception as e:
            self.repo.update_status(task_id, "SQS_ERROR")
            raise e