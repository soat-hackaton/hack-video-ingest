


from src.core.interfaces.email_sender import EmailSender


class UpdateVideoStatusUseCase:

    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender

    def execute(self, user_email: str, status: str) -> None:

        subject = f"Status do vídeo: {status}"
        html = self.build_video_status_template(status)

        self.email_sender.send(
            to_emails=[user_email],
            subject=subject,
            text=f"O status do seu vídeo foi atualizado para: {status}",
            html=html
        )

    def build_video_status_template(self, status: str) -> str:
        status_colors = {
            "PROCESSING": "#f59e0b",
            "DONE": "#10b981",
            "FAILED": "#ef4444"
        }

        color = status_colors.get(status.upper(), "#2563eb")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="margin:0; padding:0; background:#f4f6f8; font-family:Arial, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
                <tr>
                    <td align="center">
                        <table width="480" cellpadding="0" cellspacing="0"
                            style="background:#ffffff; border-radius:10px; padding:30px;">

                            <tr>
                                <td align="center">
                                    <h3 style="margin:0; color:#1f2937;">
                                        Status do vídeo
                                    </h3>
                                </td>
                            </tr>

                            <tr>
                                <td align="center" style="padding-top:24px;">
                                    <div style="
                                        padding:16px 24px;
                                        border-radius:8px;
                                        font-size:18px;
                                        font-weight:bold;
                                        color:{color};
                                        background:{color}15;
                                    ">
                                        {status}
                                    </div>
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
