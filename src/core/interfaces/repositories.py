from abc import ABC, abstractmethod
from src.core.entities.video_task import VideoTask

class VideoRepositoryInterface(ABC):
    @abstractmethod
    def save(self, task: VideoTask):
        pass

    @abstractmethod
    def update_status(self, task_id: str, new_status: str):
        pass