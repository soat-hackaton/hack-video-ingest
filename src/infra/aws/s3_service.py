import boto3
import os
from botocore.exceptions import ClientError
from src.core.interfaces import StorageInterface
from botocore.config import Config

class S3Service(StorageInterface):
    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION", "us-west-2")

        self.client = boto3.client(
            's3',
            region_name=self.region,
            endpoint_url=f"https://s3.{self.region}.amazonaws.com", 
            config=Config(signature_version='s3v4')
        )

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
    
    def generate_download_url(self, key: str, expiration=3600) -> str:
        try:
            return self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': key
                },
                ExpiresIn=expiration
            )
        except Exception as e:
            print(f"Erro ao gerar URL de download: {e}")
            return None