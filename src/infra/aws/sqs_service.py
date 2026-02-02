import json
from src.core.interfaces import MessageBrokerInterface
from src.infra.aws.session import get_boto_session

class SQSService(MessageBrokerInterface):
    def __init__(self):
        session = get_boto_session()
        self.client = session.client('sqs')

    def send_message(self, queue_url: str, message: dict):
        self.client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )