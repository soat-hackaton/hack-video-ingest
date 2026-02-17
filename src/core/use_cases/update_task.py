import logging
from src.core.interfaces import RepositoryInterface
from src.core.use_cases.update_video_status import UpdateVideoStatusUseCase
from src.infra.logging.context import set_correlation_id

logger = logging.getLogger(__name__)

class UpdateTaskUseCase:
    # 1. O init agora recebe o UseCase de status, não mais o email_sender direto
    def __init__(self, repo: RepositoryInterface, update_status_use_case: UpdateVideoStatusUseCase):
        self.repo = repo
        self.update_status_use_case = update_status_use_case

    def execute(self, task_id: str, status: str, user_email: str):
        set_correlation_id(task_id)
        
        logger.info(f"Atualizando status da task {task_id} para {status}")

        # 2. Atualiza o status no banco
        self.repo.update_status(task_id, status)

        # 3. Precisamos buscar o 'filename' para o template de e-mail funcionar bonito
        # (Se o seu método update_status já retorna o item atualizado, melhor ainda,
        # senão fazemos um find_by_id rápido)
        try:
            task = self.repo.find_by_id(task_id)
            filename = task.get("filename", "Vídeo Sem Nome") if task else "Vídeo Desconhecido"

            # 4. Chama o caso de uso de notificação passando os 3 argumentos obrigatórios
            self.update_status_use_case.execute(
                user_email=user_email,
                status=status,
                filename=filename
            )
            
        except Exception as e:
            # Não queremos que falha no envio de e-mail quebre a atualização do status
            logger.error(f"Status atualizado, mas falha ao enviar notificação: {e}")

        return {"id": task_id, "status": status}
