from fastapi import APIRouter, Depends
from src.core.use_cases.request_upload import RequestUploadUseCase
from src.infra.aws.s3_service import S3Service
from src.infra.db.repositories import SqlAlchemyVideoRepo

router = APIRouter()

# Factory para instanciar o Use Case com as dependências
def get_request_upload_use_case():
    return RequestUploadUseCase(
        storage=S3Service(bucket_name="meu-bucket"),
        repo=SqlAlchemyVideoRepo()
    )

@router.post("/request-upload")
def request_upload(
    data: UploadRequestSchema, 
    use_case: RequestUploadUseCase = Depends(get_request_upload_use_case)
):
    return use_case.execute(data.filename, data.content_type)