import pytest
import os
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.infra.api.schemas.upload import TaskStatus
from src.core.entities.video_task import VideoTask
from src.infra.persistence.dynamo_repository import DynamoDBVideoRepo

@pytest.fixture
def mock_boto_session():
    with patch("src.infra.persistence.dynamo_repository.get_boto_session") as mock_get_session:
        mock_session = MagicMock()
        mock_resource = MagicMock()
        mock_table = MagicMock()
        
        mock_resource.Table.return_value = mock_table
        mock_session.resource.return_value = mock_resource
        mock_get_session.return_value = mock_session
        
        yield mock_table

def test_save_video_task(mock_boto_session, monkeypatch):
    monkeypatch.setenv("DYNAMO_TABLE_NAME", "test-table")
    repo = DynamoDBVideoRepo()
    
    task = VideoTask(
        id="123",
        filename="video.mp4",
        s3_path="path/123",
        user_email="test@example.com",
        status="QUEUED"
    )
    
    repo.save(task)
    mock_boto_session.put_item.assert_called_once()
    args, kwargs = mock_boto_session.put_item.call_args
    assert kwargs["Item"]["PK"] == "123"
    assert kwargs["Item"]["SK"] == "METADATA"

def test_find_by_id(mock_boto_session, monkeypatch):
    monkeypatch.setenv("DYNAMO_TABLE_NAME", "test-table")
    repo = DynamoDBVideoRepo()
    
    expected_item = {"PK": "123", "filename": "video.mp4"}
    mock_boto_session.get_item.return_value = {"Item": expected_item}
    
    result = repo.find_by_id("123")
    assert result == expected_item
    mock_boto_session.get_item.assert_called_once_with(Key={'PK': '123', 'SK': "METADATA"})

def test_count_processing_by_user(mock_boto_session, monkeypatch):
    monkeypatch.setenv("DYNAMO_TABLE_NAME", "test-table")
    repo = DynamoDBVideoRepo()
    
    mock_boto_session.query.return_value = {
        "Items": [
            {"PK": "1", "status": "PROCESSING"},
            {"PK": "2", "status": "PROCESSING"},
            {"PK": "3", "status": "QUEUED"}
        ]
    }
    
    count = repo.count_processing_by_user("test@example.com")
    assert count == 2

def test_get_oldest_queued_by_user(mock_boto_session, monkeypatch):
    monkeypatch.setenv("DYNAMO_TABLE_NAME", "test-table")
    repo = DynamoDBVideoRepo()
    
    mock_boto_session.query.return_value = {
        "Items": [
            {"PK": "1", "status": "QUEUED", "created_at": "2024-01-02T00:00:00"},
            {"PK": "2", "status": "PROCESSING", "created_at": "2024-01-01T00:00:00"},
            {"PK": "3", "status": "QUEUED", "created_at": "2024-01-01T12:00:00"}
        ]
    }
    
    oldest = repo.get_oldest_queued_by_user("test@example.com")
    assert oldest is not None
    assert oldest["PK"] == "3" # oldest QUEUED item
