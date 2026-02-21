import pytest
from unittest.mock import MagicMock
from src.core.use_cases.confirm_upload import ConfirmUploadUseCase
from src.core.exceptions import ResourceNotFoundException, BusinessRuleException

class TaskStatus:
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"

def test_confirm_upload_success_under_limit():
    mock_repo = MagicMock()
    mock_repo.find_by_id.return_value = {
        "s3_path": "uploads/123",
        "filename": "video.mp4",
        "user_email": "test@example.com"
    }
    mock_repo.count_processing_by_user.return_value = 2 # under limit of 5

    mock_storage = MagicMock()
    mock_storage.file_exists.return_value = True

    mock_broker = MagicMock()
    queue_url = "http://fake-queue"

    use_case = ConfirmUploadUseCase(mock_repo, mock_storage, mock_broker, queue_url)
    
    result = use_case.execute("task_123")
    
    assert result["status"] == "success"
    assert "enfileirado" in result["message"]
    
    mock_broker.send_message.assert_called_once()
    mock_repo.update_status.assert_called_once_with("task_123", TaskStatus.PROCESSING)

def test_confirm_upload_success_over_limit():
    mock_repo = MagicMock()
    mock_repo.find_by_id.return_value = {
        "s3_path": "uploads/123",
        "filename": "video.mp4",
        "user_email": "test@example.com"
    }
    mock_repo.count_processing_by_user.return_value = 5 # limit reached

    mock_storage = MagicMock()
    mock_storage.file_exists.return_value = True

    mock_broker = MagicMock()
    queue_url = "http://fake-queue"

    use_case = ConfirmUploadUseCase(mock_repo, mock_storage, mock_broker, queue_url)
    
    result = use_case.execute("task_123")
    
    assert result["status"] == "success"
    assert "aguardando vaga" in result["message"]
    
    mock_broker.send_message.assert_not_called()
    mock_repo.update_status.assert_called_once_with("task_123", TaskStatus.QUEUED)

def test_confirm_upload_task_not_found():
    mock_repo = MagicMock()
    mock_repo.find_by_id.return_value = None
    mock_storage = MagicMock()
    mock_broker = MagicMock()

    use_case = ConfirmUploadUseCase(mock_repo, mock_storage, mock_broker, "url")
    
    with pytest.raises(ResourceNotFoundException):
        use_case.execute("task_invalid")

def test_confirm_upload_file_not_found_in_storage():
    mock_repo = MagicMock()
    mock_repo.find_by_id.return_value = {"s3_path": "url"}
    mock_storage = MagicMock()
    mock_storage.file_exists.return_value = False
    mock_broker = MagicMock()

    use_case = ConfirmUploadUseCase(mock_repo, mock_storage, mock_broker, "url")
    
    with pytest.raises(BusinessRuleException):
        use_case.execute("task_123")
