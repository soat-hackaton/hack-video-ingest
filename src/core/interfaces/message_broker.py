from abc import ABC, abstractmethod

class MessageBrokerInterface(ABC):
    @abstractmethod
    def send_message(self, queue_url: str, message: dict):
        pass