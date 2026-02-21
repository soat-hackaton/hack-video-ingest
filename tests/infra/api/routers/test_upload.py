import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from src.infra.api.main import app
from src.infra.api.security import verify_token, get_current_user_email
from src.infra.api.dependencies import (
    get_request_upload_use_case,
    get_confirm_use_case,
    get_list_videos_use_case,
    get_update_task_use_case
)

# Mock Use Cases
mock_request_use_case = MagicMock()
mock_confirm_use_case = MagicMock()
mock_list_use_case = MagicMock()
mock_update_task_use_case = MagicMock()

def override_verify_token():
    return {"sub": "test@example.com"}

def override_get_current_user_email():
    return "test@example.com"

app.dependency_overrides[verify_token] = override_verify_token
app.dependency_overrides[get_current_user_email] = override_get_current_user_email
app.dependency_overrides[get_request_upload_use_case] = lambda: mock_request_use_case
app.dependency_overrides[get_confirm_use_case] = lambda: mock_confirm_use_case
app.dependency_overrides[get_list_videos_use_case] = lambda: mock_list_use_case
app.dependency_overrides[get_update_task_use_case] = lambda: mock_update_task_use_case

client = TestClient(app)

def test_request_upload_endpoint():
    mock_request_use_case.execute.return_value = {
        "upload_url": "http://s3",
        "task_id": "123"
    }
    
    response = client.post("/api/video/request-upload", json={
        "filename": "video.mp4",
        "content_type": "video/mp4"
    })
    
    assert response.status_code == 200
    assert response.json()["task_id"] == "123"
    assert response.json()["upload_url"] == "http://s3"
    mock_request_use_case.execute.assert_called_once_with("video.mp4", "video/mp4", "test@example.com")

def test_confirm_upload_endpoint():
    mock_confirm_use_case.execute.return_value = {
        "status": "success",
        "message": "Enfileirado"
    }
    
    response = client.post("/api/video/confirm-upload", json={"task_id": "123"})
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_confirm_use_case.execute.assert_called_once_with("123")

def test_list_videos_endpoint():
    mock_list_use_case.execute.return_value = {"items": []}
    
    response = client.get("/api/video/list")
    
    assert response.status_code == 200
    assert "items" in response.json()
    mock_list_use_case.execute.assert_called_once_with("test@example.com")

def test_update_task_status_endpoint():
    mock_update_task_use_case.execute.return_value = {"id": "123", "status": "DONE"}
    
    response = client.patch("/api/video/123", json={
        "status": "DONE",
        "user_email": "test@example.com",
        "s3_download_path": "path/123.zip"
    })
    
    assert response.status_code == 201
    assert response.json()["status"] == "DONE"
    mock_update_task_use_case.execute.assert_called_once_with(
        task_id="123",
        status="DONE",
        user_email="test@example.com",
        s3_download_path="path/123.zip"
    )
