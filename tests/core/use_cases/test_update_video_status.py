import pytest
from unittest.mock import MagicMock
from src.core.use_cases.update_video_status import UpdateVideoStatusUseCase

def test_update_video_status_done():
    mock_email_sender = MagicMock()
    use_case = UpdateVideoStatusUseCase(mock_email_sender)
    
    use_case.execute(
        user_email="test@example.com",
        status="DONE",
        filename="video.mp4",
        download_url="http://fake-url"
    )
    
    mock_email_sender.send.assert_called_once()
    args, kwargs = mock_email_sender.send.call_args
    assert kwargs["to_emails"] == ["test@example.com"]
    assert "Concluído" in kwargs["subject"]
    assert "Concluído" in kwargs["text"]
    assert "http://fake-url" in kwargs["html"]
    assert "Processamento Concluído" in kwargs["html"]

def test_update_video_status_error():
    mock_email_sender = MagicMock()
    use_case = UpdateVideoStatusUseCase(mock_email_sender)
    
    use_case.execute(
        user_email="test@example.com",
        status="ERROR",
        filename="video.mp4"
    )
    
    mock_email_sender.send.assert_called_once()
    args, kwargs = mock_email_sender.send.call_args
    assert "Erro" in kwargs["subject"]
    assert "Falha no Processamento" in kwargs["html"]

def test_update_video_status_queued():
    mock_email_sender = MagicMock()
    use_case = UpdateVideoStatusUseCase(mock_email_sender)
    
    use_case.execute(
        user_email="test@example.com",
        status="QUEUED",
        filename="video.mp4"
    )
    
    mock_email_sender.send.assert_called_once()
    args, kwargs = mock_email_sender.send.call_args
    assert "Na Fila" in kwargs["subject"]
    assert "Vídeo na Fila" in kwargs["html"]

def test_update_video_status_processing():
    mock_email_sender = MagicMock()
    use_case = UpdateVideoStatusUseCase(mock_email_sender)
    
    use_case.execute(
        user_email="test@example.com",
        status=" PROCESSING ", # With spaces to test strip
        filename="video.mp4"
    )
    
    mock_email_sender.send.assert_called_once()
    args, kwargs = mock_email_sender.send.call_args
    assert "Processando" in kwargs["subject"]
    assert "Vídeo em Processamento" in kwargs["html"]
