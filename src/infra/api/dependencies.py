import os
from fastapi import Depends
from src.infra.email.gmail_email_sender import GmailSmtpEmailSender
from src.infra.aws.s3_service import S3Service
from src.infra.persistence.dynamo_repository import DynamoDBVideoRepo
from src.infra.aws.sqs_service import SQSService

# Interfaces
from src.core.interfaces import EmailSender

# Use Cases
from src.core.use_cases import (
    RequestUploadUseCase,
    ConfirmUploadUseCase,
    ListVideosUseCase,
    UpdateTaskUseCase,
    UpdateVideoStatusUseCase
)

# --- Factories de Serviços Básicos ---
def get_s3_service():
    return S3Service()

def get_repo():
    return DynamoDBVideoRepo()

def get_sqs_service():
    return SQSService()

def get_email_sender() -> EmailSender:
    return GmailSmtpEmailSender()

# --- Factories de Use Cases ---

# Request Upload
def get_request_upload_use_case(
    s3: S3Service = Depends(get_s3_service),
    repo: DynamoDBVideoRepo = Depends(get_repo)
):
    return RequestUploadUseCase(storage=s3, repo=repo)

# Confirm Upload
def get_confirm_use_case(
    repo: DynamoDBVideoRepo = Depends(get_repo),
    s3: S3Service = Depends(get_s3_service),
    sqs: SQSService = Depends(get_sqs_service)
):
    return ConfirmUploadUseCase(
        repo=repo,
        storage=s3,
        broker=sqs,
        queue_url=os.getenv("SQS_QUEUE_URL")
    )

# List Videos
def get_list_videos_use_case(
    repo: DynamoDBVideoRepo = Depends(get_repo),
    storage: S3Service = Depends(get_s3_service)
):
    """
    Injeta o Repositório do DynamoDB dentro do Caso de Uso de Listagem
    """
    return ListVideosUseCase(repo=repo, storage=storage)

# Update Video Status
def get_update_video_status_use_case(
    email_sender: EmailSender = Depends(get_email_sender)
) -> UpdateVideoStatusUseCase:
    return UpdateVideoStatusUseCase(email_sender)

# Update Task
def get_update_task_use_case(
    repo: DynamoDBVideoRepo = Depends(get_repo),
    update_status_use_case: UpdateVideoStatusUseCase = Depends(get_update_video_status_use_case),
    storage: S3Service = Depends(get_s3_service)
):
    """
    Injeta o Repositório e o Caso de Uso de Status
    """

    return UpdateTaskUseCase(
        repo=repo, 
        update_status_use_case=update_status_use_case,
        storage=storage
    )