from src.core.interfaces.email_sender import EmailSender

class UpdateVideoStatusUseCase:

    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender

    def execute(self, user_email: str, status: str, filename: str, download_url: str = None) -> None:
        # Normaliza o status para garantir que o map encontre a chave
        normalized_status = status.upper().strip()
        
        # Busca o HTML específico para o status
        html_content = self.get_template_by_status(normalized_status, download_url)

        translated_status = self._translate_status(normalized_status)
        subject = f"Atualização do Vídeo '{filename}': {translated_status}"
        # Ex: "Atualização do Vídeo 'meu_video_ferias.mp4': Concluído"

        self.email_sender.send(
            to_emails=[user_email],
            subject=subject,
            text=f"O status do seu vídeo {filename} mudou para: {translated_status}",
            html=html_content
        )

    def get_template_by_status(self, status: str, download_url: str = None) -> str:
        """
        Map que despacha para o método de template correspondente.
        """
        templates_map = {
            # Sucesso
            "DONE": self._template_concluido(download_url),
            
            # Erro
            "ERROR": self._template_erro,
            
            # Processando
            "PROCESSING": self._template_processando,
            
            # Na Fila
            "QUEUED": self._template_na_fila
        }

        # Pega o método do map ou usa um default
        template_method = templates_map.get(status, self._template_generico)
        return template_method()

    # --- TEMPLATES ESPECÍFICOS ---

    def _template_concluido(self, download_url: str = None) -> str:
        title = "Processamento Concluído!"
        message = (
            "Seu vídeo foi processado com sucesso e todas as imagens foram extraídas. "
            "Ele já está disponível para download."
        )
        cta_text = "Baixar Arquivo .ZIP"
        footer_text = "Aproveite para enviar um novo vídeo agora mesmo."
        color = "#10b981" # Verde
        link = download_url if download_url else "#"
        
        return self._build_base_html(title, message, cta_text, footer_text, color, link)

    def _template_erro(self) -> str:
        title = "Falha no Processamento"
        message = (
            "Infelizmente ocorreu um erro ao processar seu vídeo. "
            "Não se preocupe, você pode tentar processá-lo novamente."
        )
        cta_text = "Tentar Novamente (Retry)"
        footer_text = "Se o erro persistir, verifique o formato do arquivo."
        color = "#ef4444" # Vermelho
        
        return self._build_base_html(title, message, cta_text, footer_text, color)

    def _template_processando(self) -> str:
        title = "Vídeo em Processamento"
        message = (
            "Estamos processando seu vídeo neste momento. "
            "Assim que terminarmos, avisaremos você."
        )
        cta_text = "Acompanhar Status"
        footer_text = "Isso costuma ser rápido."
        color = "#f59e0b" # Laranja
        
        return self._build_base_html(title, message, cta_text, footer_text, color)

    def _template_na_fila(self) -> str:
        title = "Vídeo na Fila"
        message = (
            "Recebemos seu vídeo! Ele está na fila e será processado em breve. "
            "Você receberá outro e-mail quando o processo iniciar."
        )
        cta_text = "Ver Minha Lista"
        footer_text = "Obrigado pela paciência."
        color = "#3b82f6" # Azul
        
        return self._build_base_html(title, message, cta_text, footer_text, color)

    def _template_generico(self) -> str:
        return self._build_base_html(
            "Status Atualizado", 
            "O status do seu vídeo foi alterado.", 
            "Acessar Plataforma", 
            "", 
            "#6b7280"
        )

    # --- WRAPPER HTML ---

    def _build_base_html(self, title, message, cta_text, footer_text, color, link="#") -> str:
        # Nota: URL do frontend seria ideal vir via env var ou config. 
        # Coloquei um placeholder '#' no href do botão.
        
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
                                    Hackathon Video Ingest &copy; 2026
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def _translate_status(self, status: str) -> str:
        translations = {
            "DONE": "Concluído",
            "ERROR": "Erro",
            "PROCESSING": "Processando",
            "QUEUED": "Na Fila"
        }
        return translations.get(status, status)