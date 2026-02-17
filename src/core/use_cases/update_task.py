from src.infra.api.schemas.upload import TaskStatus

class UpdateTaskUseCase:
    def __init__(self, repo, update_status_use_case):
        self.repo = repo
        self.update_status_use_case = update_status_use_case

    def execute(self, task_id: str, status: TaskStatus, user_email: str) -> None:
        # Buscar a Task para pegar os dados (email e filename)
        task = self.repo.find_by_id(task_id)

        if not task:
            raise Exception("Task não encontrada")

        # Atualiza no banco
        self.repo.update_status(task_id, new_status)

        # Envia o e-mail
        filename = task.get('filename', 'Unknown Video')
        user_email = task.get('user_email')

        if user_email:
            self.update_status_use_case.execute(
                user_email=user_email, 
                status=new_status, 
                filename=filename
            )
