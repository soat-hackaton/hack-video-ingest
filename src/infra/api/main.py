from fastapi import FastAPI
from dotenv import load_dotenv
from src.infra.api.routers import upload

load_dotenv()

app = FastAPI(title="Video Ingest API")

app.include_router(upload.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}