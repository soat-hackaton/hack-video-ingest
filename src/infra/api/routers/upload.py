import os
import json
import boto3
from fastapi import APIRouter, Depends, HTTPException
from src.core.use_cases.request_upload import RequestUploadUseCase
from src.infra.aws.s3_service import S3Service
from src.infra.persistence.dynamo_repository import DynamoDBVideoRepo
from src.infra.api.schemas.video import UploadRequestSchema, UploadResponseSchema
from pydantic import BaseModel

router = APIRouter()

# --- Schemas ---
class ConfirmUploadRequest(BaseModel):
    task_id: str

# --- Dependências ---
def get_s3_service():
    return S3Service(bucket_name=os.getenv("S3_BUCKET_NAME"))

def get_repo():
    return DynamoDBVideoRepo(table_name=os.getenv("DYNAMO_TABLE_NAME"))

def get_sqs_client():
    return boto3.client(
        'sqs', 
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name=os.getenv("AWS_REGION", "us-west-2")
    )

def get_request_upload_use_case(
    s3: S3Service = Depends(get_s3_service),
    repo: DynamoDBVideoRepo = Depends(get_repo)
):
    return RequestUploadUseCase(storage=s3, repo=repo)

# --- Rotas ---

@router.post("/request-upload", response_model=UploadResponseSchema)
def request_upload(
    data: UploadRequestSchema, 
    use_case: RequestUploadUseCase = Depends(get_request_upload_use_case)
):
    return use_case.execute(data.filename, data.content_type)

@router.post("/confirm-upload")
def confirm_upload(
    request: ConfirmUploadRequest,
    repo: DynamoDBVideoRepo = Depends(get_repo),
    s3: S3Service = Depends(get_s3_service),
    sqs = Depends(get_sqs_client)
):
    # 1. Busca a tarefa no banco
    try:
        response = repo.table.get_item(Key={'PK': request.task_id, 'SK': "METADATA"})
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Task não encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # 2. Valida se o arquivo existe no S3
    if not s3.file_exists(item['s3_path']):
        repo.update_status(request.task_id, "UPLOAD_FAILED")
        raise HTTPException(status_code=400, detail="Arquivo não encontrado no S3")

    # 3. Envia para SQS
    try:
        sqs.send_message(
            QueueUrl=os.getenv("SQS_QUEUE_URL"),
            MessageBody=json.dumps({
                "task_id": request.task_id,
                "s3_path": item['s3_path'],
                "filename": item['filename']
            })
        )
        repo.update_status(request.task_id, "QUEUED")
    except Exception as e:
        repo.update_status(request.task_id, "SQS_ERROR")
        raise HTTPException(status_code=500, detail=f"Erro no SQS: {str(e)}")

    return {"status": "success", "message": "Processamento iniciado"}