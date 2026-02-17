from src.core.use_cases.update_video_status import UpdateVideoStatusUseCase
from src.infra.api.schemas.upload import TaskStatus

from pprint import pprint

class UpdateTaskUseCase:
    def __init__(self, repo, email_sender):
        self.repo = repo
        self.email_sender = email_sender

    def execute(self, task_id: str, status: TaskStatus, user_email: str) -> None:
        send_email_use_case = UpdateVideoStatusUseCase(email_sender=self.email_sender)
        send_email_use_case.execute(user_email=user_email, status=status.value)
        self.repo.update_status(task_id, status)
