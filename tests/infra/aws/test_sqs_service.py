import pytest
import json
from unittest.mock import MagicMock, patch
from src.infra.aws.sqs_service import SQSService

@pytest.fixture
def mock_boto_session():
    with patch("src.infra.aws.sqs_service.get_boto_session") as mock_get_session:
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client
        mock_get_session.return_value = mock_session
        yield mock_client

def test_send_message(mock_boto_session):
    service = SQSService()
    queue_url = "http://fake-queue"
    message = {"task_id": "123", "filename": "video.mp4"}
    
    service.send_message(queue_url, message)
    
    mock_boto_session.send_message.assert_called_once_with(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )
