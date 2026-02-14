class ListVideosUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, user_email: str):
        # Busca a lista crua do repositório
        items = self.repo.list_by_user(user_email)
        
        # Formata cada item individualmente
        formatted_items = [
            {
                "id": item.get("id"),
                "filename": item.get("filename"),
                "status": item.get("status", "pending"),
                "created_at": item.get("created_at"),
                "download_url": item.get("s3_path") if item.get("status") == "processed" else None
            }
            for item in items
        ]

        # Retorna um objeto com a chave "items"
        return {
            "items": formatted_items
        }