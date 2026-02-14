class ListVideosUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, user_email: str):
        items = self.repo.list_by_user(user_email)
        
        return [
            {
                "id": item.get("id"),
                "filename": item.get("filename"),
                "status": item.get("status", "pending"),
                "created_at": item.get("created_at"),
                "downloadUrl": item.get("s3_path") if item.get("status") == "processed" else None
            }
            for item in items
        ]