from abc import ABC, abstractmethod
from src.core.entities.video_task import VideoTask

class RepositoryInterface(ABC):
    @abstractmethod
    def save(self, task: VideoTask):
        pass

    @abstractmethod
    def update_status(self, task_id: str, new_status: str):
        pass

    @abstractmethod
    def count_processing_by_user(self, user_email: str) -> int:
        pass

    @abstractmethod
    def get_oldest_queued_by_user(self, user_email: str) -> dict | None:
        pass