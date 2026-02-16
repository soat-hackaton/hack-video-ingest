from abc import ABC, abstractmethod
from typing import List


class EmailSender(ABC):

    @abstractmethod
    def send(
        self,
        to_emails: List[str],
        subject: str,
        text: str,
        html: str
    ) -> None:
        pass
