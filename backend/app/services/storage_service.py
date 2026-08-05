import boto3
from botocore.config import Config
from app.config import get_settings

settings = get_settings()


class StorageService:
    """
    S3-compatible file storage service for Cloudflare R2.
    """

    def __init__(self):
        self.account_id = settings.R2_ACCOUNT_ID
        self.access_key = settings.R2_ACCESS_KEY_ID
        self.secret_key = settings.R2_SECRET_ACCESS_KEY
        self.bucket_name = settings.R2_BUCKET_NAME or "resume-storage"
        self._client = None

    @property
    def client(self):
        if self._client is None and self.account_id and self.access_key and self.secret_key:
            try:
                endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
                self._client = boto3.client(
                    "s3",
                    endpoint_url=endpoint_url,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    config=Config(signature_version="s3v4"),
                    region_name="auto",
                )
            except Exception as e:
                print(f"Warning: Failed to initialize Cloudflare R2 client ({e})")
                self._client = None
        return self._client

    def upload_file(self, file_bytes: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
        """
        Uploads in-memory file bytes directly to Cloudflare R2 bucket.
        Returns the stored file path/key string.
        """
        key = f"resumes/{filename}"
        if self.client:
            try:
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file_bytes,
                    ContentType=content_type,
                )
                return f"r2://{self.bucket_name}/{key}"
            except Exception as e:
                print(f"Warning: Cloudflare R2 upload error ({e}). Falling back to key reference.")
                return key
        return key
