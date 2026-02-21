import pytest
from unittest.mock import MagicMock
from src.core.use_cases.request_upload import RequestUploadUseCase

class TaskStatus:
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"

def test_request_upload_success():
    mock_storage = MagicMock()
    mock_storage.generate_presigned_url.return_value = "http://fake-s3-url.com"
    mock_repo = MagicMock()

    use_case = RequestUploadUseCase(storage=mock_storage, repo=mock_repo)
    result = use_case.execute(
        filename="video.mp4",
        content_type="video/mp4",
        user_email="test@example.com"
    )

    assert "upload_url" in result
    assert result["upload_url"] == "http://fake-s3-url.com"
    assert "task_id" in result
    
    mock_storage.generate_presigned_url.assert_called_once()
    mock_repo.save.assert_called_once()
    
    saved_task = mock_repo.save.call_args[0][0]
    assert saved_task.filename == "video.mp4"
    assert saved_task.user_email == "test@example.com"
    assert saved_task.status == TaskStatus.QUEUED

def test_request_upload_exception_handling():
    mock_storage = MagicMock()
    mock_storage.generate_presigned_url.side_effect = Exception("S3 error")
    mock_repo = MagicMock()

    use_case = RequestUploadUseCase(storage=mock_storage, repo=mock_repo)
    
    with pytest.raises(Exception, match="S3 error"):
        use_case.execute(
            filename="video.mp4",
            content_type="video/mp4",
            user_email="test@example.com"
        )
