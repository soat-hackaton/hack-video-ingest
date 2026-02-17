from src.core.use_cases.update_task import UpdateTaskUseCase
from fastapi import APIRouter, Depends, HTTPException
from src.core.use_cases import RequestUploadUseCase, ConfirmUploadUseCase, ListVideosUseCase
from src.infra.api.schemas.upload import UpdateTaskStatusRequest, UploadVideoRequest, UploadVideoResponse
from src.infra.api.schemas.lifecycle import ConfirmVideoUploadRequest, ConfirmVideoUploadResponse
from src.infra.api.schemas.video import VideoListResponse
from src.infra.api.schemas.errors import COMMON_ERROR_RESPONSES
from src.infra.api.dependencies import (
    get_request_upload_use_case,
    get_confirm_use_case,
    get_list_videos_use_case,
    get_update_task_use_case
)
from src.infra.api.security import verify_token, get_current_user_email

# Protege TODAS as rotas deste arquivo com JWT
router = APIRouter()

@router.post(
    "/request-upload",
    dependencies=[Depends(verify_token)],
    response_model=UploadVideoResponse,
    responses=COMMON_ERROR_RESPONSES
)
def request_upload(
    data: UploadVideoRequest,
    use_case: RequestUploadUseCase = Depends(get_request_upload_use_case),
    token_payload: dict = Depends(verify_token)
):
    """
    Cria uma URL pré-assinada do S3
    então é feito o upload do video pelo front
    e atualiza o status do pipeline
    """

    user_email = token_payload.get("sub")

    return use_case.execute(data.filename, data.content_type, user_email)

@router.post(
    "/confirm-upload",
    dependencies=[Depends(verify_token)],
    response_model=ConfirmVideoUploadResponse,
    responses=COMMON_ERROR_RESPONSES
)
def confirm_upload(
    request: ConfirmVideoUploadRequest,
    use_case: ConfirmUploadUseCase = Depends(get_confirm_use_case)
):
    """
    Valida a criação do video dentro do S3
    então dispara uma mensagem para o SQS
    e atualiza o status do pipeline
    """

    return use_case.execute(request.task_id)

@router.get(
    "/list",
    dependencies=[Depends(verify_token)],
    response_model=VideoListResponse,
    status_code=200
)
def list_videos(
    user_email: str = Depends(get_current_user_email),
    use_case: ListVideosUseCase = Depends(get_list_videos_use_case)
):
    """
    Lista os videos enviados para processamento
    por usuário
    """

    return use_case.execute(user_email)


@router.patch(
    "/{task_id}",
    status_code=201
)
def update_task_status(
    request_status: UpdateTaskStatusRequest,
    task_id: str,
    use_case: UpdateTaskUseCase = Depends(get_update_task_use_case)
):
    """
    Atualiza o status da tarefa e processa notificações
    """
    return use_case.execute(
        task_id=task_id, 
        status=request_status.status, 
        user_email=request_status.user_email,
        s3_download_path=request_status.s3_download_path
    )