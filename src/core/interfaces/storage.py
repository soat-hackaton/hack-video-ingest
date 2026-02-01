from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def generate_presigned_url(self, key: str, content_type: str) -> str:
        pass
    
    @abstractmethod
    def file_exists(self, key: str) -> bool:
        pass