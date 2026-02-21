from typing import Optional

class VideoStatusEmailBuilder:
    @staticmethod
    def get_template_by_status(status: str, download_url: Optional[str] = None) -> str:
        if status == "DONE":
            return VideoStatusEmailBuilder._template_done(download_url)

        templates_map = {
            "ERROR": VideoStatusEmailBuilder._template_error,
            "PROCESSING": VideoStatusEmailBuilder._template_processing,
            "QUEUED": VideoStatusEmailBuilder._template_queued
        }

        template_method = templates_map.get(status, VideoStatusEmailBuilder._template_generic)
        return template_method()

    @staticmethod
    def translate_status(status: str) -> str:
        translations = {
            "DONE": "Concluído",
            "ERROR": "Erro",
            "PROCESSING": "Processando",
            "QUEUED": "Na Fila"
        }
        return translations.get(status, status)

    @staticmethod
    def _template_done(download_url: Optional[str] = None) -> str:
        title = "Processamento Concluído!"
        message = (
            "Seu vídeo foi processado com sucesso e todas as imagens foram extraídas. "
            "Ele já está disponível para download."
        )
        cta_text = "Baixar Arquivo .ZIP"
        footer_text = "Aproveite para enviar um novo vídeo agora mesmo."
        color = "#10b981" # Verde
        link = download_url if download_url else "#"
        
        return VideoStatusEmailBuilder._build_base_html(title, message, cta_text, footer_text, color, link)

    @staticmethod
    def _template_error() -> str:
        title = "Falha no Processamento"
        message = (
            "Infelizmente ocorreu um erro ao processar seu vídeo. "
            "Não se preocupe, você pode tentar processá-lo novamente."
        )
        cta_text = "Tentar Novamente"
        footer_text = "Se o erro persistir, envie uma evidência para nosso Fale Conosco."
        color = "#ef4444" # Vermelho
        
        return VideoStatusEmailBuilder._build_base_html(title, message, cta_text, footer_text, color)

    @staticmethod
    def _template_processing() -> str:
        title = "Vídeo em Processamento"
        message = (
            "Estamos processando seu vídeo neste momento. "
            "Assim que terminarmos, avisaremos você."
        )
        cta_text = "Acompanhar Status"
        footer_text = "Isso costuma ser rápido."
        color = "#f59e0b" # Laranja
        
        return VideoStatusEmailBuilder._build_base_html(title, message, cta_text, footer_text, color)

    @staticmethod
    def _template_queued() -> str:
        title = "Vídeo na Fila"
        message = (
            "Recebemos seu vídeo! Ele está na fila e será processado em breve. "
            "Você receberá outro e-mail quando o processo iniciar."
        )
        cta_text = "Ver Minha Lista"
        footer_text = "Obrigado pela paciência."
        color = "#3b82f6" # Azul
        
        return VideoStatusEmailBuilder._build_base_html(title, message, cta_text, footer_text, color)

    @staticmethod
    def _template_generic() -> str:
        return VideoStatusEmailBuilder._build_base_html(
            "Status Atualizado", 
            "O status do seu vídeo foi alterado.", 
            "Acessar Plataforma", 
            "", 
            "#6b7280"
        )

    @staticmethod
    def _build_base_html(title, message, cta_text, footer_text, color, link="#") -> str:        
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="margin:0; padding:0; background:#f4f6f8; font-family:Arial, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
                <tr>
                    <td align="center">
                        <table width="500" cellpadding="0" cellspacing="0" 
                            style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                            
                            <tr>
                                <td style="background:{color}; height:8px;"></td>
                            </tr>

                            <tr>
                                <td style="padding:40px 30px; text-align:center;">
                                    <h2 style="margin:0 0 16px 0; color:#1f2937; font-size:24px;">{title}</h2>
                                    
                                    <p style="color:#4b5563; font-size:16px; line-height:1.5; margin-bottom:30px;">
                                        {message}
                                    </p>

                                    <div style="margin-bottom:30px;">
                                        <a href="{link}" style="
                                            background-color:{color};
                                            color:#ffffff;
                                            text-decoration:none;
                                            padding:12px 24px;
                                            border-radius:6px;
                                            font-weight:bold;
                                            display:inline-block;
                                        ">
                                            {cta_text}
                                        </a>
                                    </div>

                                    <p style="color:#6b7280; font-size:14px; margin:0;">
                                        {footer_text}
                                    </p>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="background:#f9fafb; padding:15px; text-align:center; font-size:12px; color:#9ca3af;">
                                    FIAP Hackathon &copy; 2026
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
