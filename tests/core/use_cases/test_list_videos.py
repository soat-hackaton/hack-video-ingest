import pytest
from unittest.mock import MagicMock
from src.core.use_cases.list_videos import ListVideosUseCase

class TaskStatus:
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"

def test_list_videos_success():
    mock_repo = MagicMock()
    mock_storage = MagicMock()

    mock_repo.list_by_user.return_value = [
        {"id": "1", "filename": "video1.mp4", "status": "QUEUED", "created_at": "2024-01-01"},
        {"id": "2", "filename": "video2.mp4", "status": "DONE", "s3_download_path": "path", "created_at": "2024-01-02"},
        {"id": "3", "filename": "video3.mp4", "status": "ERROR", "created_at": "2024-01-03"}
    ]
    mock_storage.generate_download_url.return_value = "http://fake-download-url"

    use_case = ListVideosUseCase(mock_repo, mock_storage)
    result = use_case.execute("test@example.com")
    
    assert "items" in result
    items = result["items"]
    assert len(items) == 3
    
    # Check item 1
    assert items[0]["status"] == "QUEUED"
    assert items[0]["download_url"] is None
    
    # Check item 2 (DONE)
    assert items[1]["status"] == "DONE"
    assert items[1]["download_url"] == "http://fake-download-url"
    mock_storage.generate_download_url.assert_called_once_with("path")

def test_list_videos_empty():
    mock_repo = MagicMock()
    mock_storage = MagicMock()
    mock_repo.list_by_user.return_value = []

    use_case = ListVideosUseCase(mock_repo, mock_storage)
    result = use_case.execute("test@example.com")
    
    assert "items" in result
    assert len(result["items"]) == 0
