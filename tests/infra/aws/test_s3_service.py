import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from src.infra.aws.s3_service import S3Service

@pytest.fixture
def mock_boto_client():
    with patch("boto3.client") as mock_client:
        mock = MagicMock()
        mock_client.return_value = mock
        yield mock

def test_generate_presigned_url_success(mock_boto_client, monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
    mock_boto_client.generate_presigned_url.return_value = "http://fake-presigned-url"
    
    service = S3Service()
    url = service.generate_presigned_url("uploads/123", "video/mp4")
    
    assert url == "http://fake-presigned-url"
    mock_boto_client.generate_presigned_url.assert_called_once_with(
        'put_object',
        Params={
            'Bucket': 'test-bucket', 
            'Key': 'uploads/123', 
            'ContentType': 'video/mp4'
        },
        ExpiresIn=3600
    )

def test_file_exists_true(mock_boto_client, monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
    mock_boto_client.head_object.return_value = {} # success
    
    service = S3Service()
    assert service.file_exists("uploads/123") is True
    mock_boto_client.head_object.assert_called_once_with(Bucket="test-bucket", Key="uploads/123")

def test_file_exists_false(mock_boto_client, monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
    mock_boto_client.head_object.side_effect = ClientError({"Error": {"Code": "404"}}, "HeadObject")
    
    service = S3Service()
    assert service.file_exists("uploads/123") is False

def test_generate_download_url(mock_boto_client, monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
    mock_boto_client.generate_presigned_url.return_value = "http://fake-download-url"
    
    service = S3Service()
    url = service.generate_download_url("results/123.zip", 7200)
    
    assert url == "http://fake-download-url"
    mock_boto_client.generate_presigned_url.assert_called_once_with(
        'get_object',
        Params={
            'Bucket': 'test-bucket', 
            'Key': 'results/123.zip', 
        },
        ExpiresIn=7200
    )
