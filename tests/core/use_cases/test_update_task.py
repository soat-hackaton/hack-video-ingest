import pytest
from unittest.mock import MagicMock
from src.core.use_cases.update_task import UpdateTaskUseCase

class TaskStatus:
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"

def test_update_task_success_no_auto_feeding():
    mock_repo = MagicMock()
    mock_update_status_use_case = MagicMock()
    mock_storage = MagicMock()
    mock_broker = MagicMock()
    
    mock_repo.update_status.return_value = {"id": "1", "filename": "video.mp4"}

    use_case = UpdateTaskUseCase(
        mock_repo, mock_update_status_use_case, mock_storage, mock_broker, "url"
    )

    result = use_case.execute(
        task_id="1", status="PROCESSING", user_email="test@example.com"
    )

    assert result["id"] == "1"
    assert result["status"] == "PROCESSING"

    mock_repo.update_status.assert_called_once_with("1", "PROCESSING", None)
    mock_update_status_use_case.execute.assert_called_once_with(
        user_email="test@example.com",
        status="PROCESSING",
        filename="video.mp4",
        download_url=None
    )
    mock_repo.get_oldest_queued_by_user.assert_not_called()
    mock_broker.send_message.assert_not_called()

def test_update_task_done_with_auto_feeding():
    mock_repo = MagicMock()
    mock_update_status_use_case = MagicMock()
    mock_storage = MagicMock()
    mock_broker = MagicMock()
    
    mock_repo.update_status.return_value = {
        "id": "1", 
        "filename": "video.mp4", 
        "s3_download_path": "results/1.zip"
    }
    
    mock_repo.get_oldest_queued_by_user.return_value = {
        "id": "2",
        "s3_path": "uploads/2",
        "filename": "video2.mp4",
        "user_email": "test@example.com"
    }

    mock_storage.generate_download_url.return_value = "http://fake-download"

    use_case = UpdateTaskUseCase(
        mock_repo, mock_update_status_use_case, mock_storage, mock_broker, "url"
    )

    result = use_case.execute(
        task_id="1", status="DONE", user_email="test@example.com", s3_download_path="results/1.zip"
    )

    assert result["id"] == "1"
    
    # Check update status
    mock_repo.update_status.assert_any_call("1", "DONE", "results/1.zip")
    mock_storage.generate_download_url.assert_called_once_with("results/1.zip", expiration=604800)
    
    mock_update_status_use_case.execute.assert_called_once_with(
        user_email="test@example.com",
        status="DONE",
        filename="video.mp4",
        download_url="http://fake-download"
    )
    
    # Check auto-feeding mechanism
    mock_repo.get_oldest_queued_by_user.assert_called_once_with("test@example.com")
    mock_broker.send_message.assert_called_once_with("url", {
        "task_id": "2",
        "s3_path": "uploads/2",
        "filename": "video2.mp4",
        "user_email": "test@example.com"
    })
    mock_repo.update_status.assert_any_call("2", TaskStatus.PROCESSING)
