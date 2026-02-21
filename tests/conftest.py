import pytest
from unittest.mock import MagicMock

@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient
    from src.infra.api.main import app
    return TestClient(app)

@pytest.fixture
def mock_s3_service(mocker):
    mock = mocker.patch("src.infra.aws.s3_service.S3Service")
    return mock.return_value

@pytest.fixture
def mock_sqs_service(mocker):
    mock = mocker.patch("src.infra.aws.sqs_service.SQSService")
    return mock.return_value

@pytest.fixture
def mock_dynamo_repo(mocker):
    mock = mocker.patch("src.infra.persistence.dynamo_repository.DynamoRepository")
    return mock.return_value
