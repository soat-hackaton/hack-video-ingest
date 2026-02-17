import boto3
from botocore.exceptions import ClientError
from src.core.interfaces import StorageInterface
from botocore.config import Config

class S3Service(StorageInterface):
    def __init__(self):
        my_config = Config(
            region_name="us-west-2",
            signature_version="s3v4"
        )

        self.client = boto3.client('s3', config=my_config)
        self.bucket = os.getenv("S3_BUCKET_NAME")

    def generate_presigned_url(self, key: str, content_type: str) -> str:
        try:
            return self.client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket, 
                    'Key': key, 
                    'ContentType': content_type
                },
                ExpiresIn=3600
            )
        except Exception as e:
            print(f"Erro ao gerar URL: {e}")
            return None

    def file_exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False