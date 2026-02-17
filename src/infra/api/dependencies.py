import os
import boto3
from src.infra.email.gmail_email_sender import GmailSmtpEmailSender
from src.core.use_cases.update_task import UpdateTaskUseCase
from fastapi import Depends
from src.infra.aws.s3_service import S3Service
from src.infra.persistence.dynamo_repository import DynamoDBVideoRepo
from src.infra.aws.sqs_service import SQSService
from src.core.use_cases import (
    RequestUploadUseCase,
    ConfirmUploadUseCase,
    ListVideosUseCase
)

# --- Factories de Serviços Básicos ---
def get_s3_service():
    return S3Service()

def get_repo():
    return DynamoDBVideoRepo(table_name=os.getenv("DYNAMO_TABLE_NAME"))

def get_sqs_service():
    # O SQSService interno já deve lidar com a sessão boto3 internamente
    # ou receber o client pronto. Vamos assumir que ele se vira bem.
    return SQSService()

# --- Factories de Use Cases ---
def get_request_upload_use_case(
    s3: S3Service = Depends(get_s3_service),
    repo: DynamoDBVideoRepo = Depends(get_repo)
):
    return RequestUploadUseCase(storage=s3, repo=repo)

def get_confirm_use_case(
    repo: DynamoDBVideoRepo = Depends(get_repo),
    s3: S3Service = Depends(get_s3_service),
    sqs: SQSService = Depends(get_sqs_service)
):
    # Aqui injetamos a URL da fila explicitamente
    return ConfirmUploadUseCase(
        repo=repo,
        storage=s3,
        broker=sqs,
        queue_url=os.getenv("SQS_QUEUE_URL")
    )

def get_list_videos_use_case(
    repo: DynamoDBVideoRepo = Depends(get_repo),
    storage: S3Service = Depends(get_s3_service)
):
    """
    Injeta o Repositório do DynamoDB dentro do Caso de Uso de Listagem
    """
    return ListVideosUseCase(repo=repo, storage=storage)


def get_update_task_use_case(
    repo: DynamoDBVideoRepo = Depends(get_repo)
):
    """
    Injeta o Repositório do DynamoDB dentro do Caso de Uso de Listagem
    """
    email_sender = GmailSmtpEmailSender()
    return UpdateTaskUseCase(repo=repo, email_sender=email_sender)