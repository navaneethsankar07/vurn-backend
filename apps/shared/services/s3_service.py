import boto3

from botocore.config import Config
from django.conf import settings


class S3Service:

    @staticmethod
    def get_client():
        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
        )

    @staticmethod
    def check_connection():
        client = S3Service.get_client()

        return client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)

    @staticmethod
    def generate_upload_url(*, object_key, content_type, expires_in=3600):
        client = S3Service.get_client()

        return client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

    @staticmethod
    def generate_download_url(*, object_key, expires_in=3600):
        client = S3Service.get_client()

        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": object_key},
            ExpiresIn=expires_in,
        )

    @staticmethod
    def head_object(*, object_key):
        client = S3Service.get_client()

        return client.head_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=object_key
        )

    @staticmethod
    def delete_object(*, object_key):
        client = S3Service.get_client()

        return client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=object_key
        )
