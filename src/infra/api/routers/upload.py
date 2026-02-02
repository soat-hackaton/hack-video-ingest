import os
import json
import boto3
from fastapi import APIRouter, Depends, HTTPException
from src.core.use_cases import RequestUploadUseCase, ConfirmUploadUseCase
from src.infra.aws import S3Service, SQSService
from src.infra.persistence.dynamo_repository import DynamoDBVideoRepo
from src.infra.api.schemas.upload import UploadVideoRequest, UploadVideoResponse
from src.infra.api.schemas.lifecycle import ConfirmVideoUploadRequest, ConfirmVideoUploadResponsefaz
from src.infra.api.dependencies import get_request_upload_use_case, get_confirm_use_case
from pydantic import BaseModel

router = APIRouter()

@router.post("/request-upload", response_model=UploadVideoResponse)
def request_upload(
    data: UploadVideoRequest, 
    use_case: RequestUploadUseCase = Depends(get_request_upload_use_case)
):
    return use_case.execute(data.filename, data.content_type)

@router.post("/confirm-upload", response_model=ConfirmVideoUploadResponse)
def confirm_upload(
    request: ConfirmVideoUploadRequest,
    use_case: ConfirmUploadUseCase = Depends(get_confirm_use_case)
):
    try:
        return use_case.execute(request.task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))