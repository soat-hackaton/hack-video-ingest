from fastapi import APIRouter, Depends
from src.core.use_cases import RequestUploadUseCase, ConfirmUploadUseCase
from src.infra.api.schemas.upload import UploadVideoRequest, UploadVideoResponse
from src.infra.api.schemas.lifecycle import ConfirmVideoUploadRequest, ConfirmVideoUploadResponse
from src.infra.api.schemas.errors import COMMON_ERROR_RESPONSES
from src.infra.api.dependencies import get_request_upload_use_case, get_confirm_use_case
from src.infra.api.security import verify_token

# dependencies: protege as rotas abaixo (request-upload e confirm-upload)
router = APIRouter(dependencies=[Depends(verify_token)])

@router.post(
    "/request-upload", 
    response_model=UploadVideoResponse,
    responses=COMMON_ERROR_RESPONSES
)
def request_upload(
    data: UploadVideoRequest, 
    use_case: RequestUploadUseCase = Depends(get_request_upload_use_case)
):
    """
    Cria uma URL pré-assinada do S3 
    então é feito o upload do video pelo front
    e atualiza o status do pipeline
    """
    return use_case.execute(data.filename, data.content_type)

@router.post(
    "/confirm-upload", 
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