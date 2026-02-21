from src.core.interfaces.email_sender import EmailSender
from src.core.utils.video_status_email_builder import VideoStatusEmailBuilder

class UpdateVideoStatusUseCase:

    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender

    def execute(self, user_email: str, status: str, filename: str, download_url: str = None) -> None:
        # Normaliza o status para garantir que o map encontre a chave
        normalized_status = status.upper().strip()
        
        # Busca o HTML específico para o status
        html_content = VideoStatusEmailBuilder.get_template_by_status(normalized_status, download_url)

        translated_status = VideoStatusEmailBuilder.translate_status(normalized_status)
        subject = f"Atualização do Vídeo '{filename}': {translated_status}"
        # Ex: "Atualização do Vídeo 'meu_video_ferias.mp4': Concluído"

        self.email_sender.send(
            to_emails=[user_email],
            subject=subject,
            text=f"O status do seu vídeo {filename} mudou para: {translated_status}",
            html=html_content
        )
