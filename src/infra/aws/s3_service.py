import boto3
from botocore.exceptions import ClientError
from src.core.interfaces import StorageInterface
from botocore.config import Config

class S3Service(StorageInterface):
    def __init__(self, bucket_name: str):
        self.client = boto3.client('s3', region_name="us-west-2", config=Config(signature_version="s3v4"))
        self.bucket = bucket_name

    def generate_presigned_url(self, key: str, content_type: str) -> str:
        return self.client.generate_presigned_url(
            'put_object',
            Params={'Bucket': self.bucket, 'Key': key, 'ContentType': content_type},
            ExpiresIn=3600
        )

    def file_exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False