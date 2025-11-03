"""MinIO object storage for files and documents."""

import os
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from datetime import timedelta


class StorageConfig:
    """MinIO configuration from environment variables."""
    
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio_secure_password_change_me")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"


class ObjectStorage:
    """MinIO object storage manager."""
    
    def __init__(self):
        """Initialize MinIO client."""
        self.config = StorageConfig()
        self.client = Minio(
            self.config.MINIO_ENDPOINT,
            access_key=self.config.MINIO_ACCESS_KEY,
            secret_key=self.config.MINIO_SECRET_KEY,
            secure=self.config.MINIO_SECURE
        )
        self._ensure_buckets()
    
    def _ensure_buckets(self):
        """Create default buckets if they don't exist."""
        buckets = [
            "agent-documents",
            "agent-artifacts",
            "agent-logs",
            "user-uploads"
        ]
        
        for bucket in buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
    
    def upload_file(self, bucket: str, object_name: str, file_path: str, 
                   content_type: str = "application/octet-stream"):
        """Upload a file to storage.
        
        Args:
            bucket: Bucket name
            object_name: Object name in bucket
            file_path: Local file path
            content_type: MIME type
        """
        try:
            self.client.fput_object(
                bucket,
                object_name,
                file_path,
                content_type=content_type
            )
            return f"s3://{bucket}/{object_name}"
        except S3Error as e:
            raise Exception(f"Upload failed: {e}")
    
    def upload_data(self, bucket: str, object_name: str, data: bytes,
                   content_type: str = "application/octet-stream"):
        """Upload data to storage.
        
        Args:
            bucket: Bucket name
            object_name: Object name in bucket
            data: Data bytes
            content_type: MIME type
        """
        try:
            data_stream = BytesIO(data)
            self.client.put_object(
                bucket,
                object_name,
                data_stream,
                length=len(data),
                content_type=content_type
            )
            return f"s3://{bucket}/{object_name}"
        except S3Error as e:
            raise Exception(f"Upload failed: {e}")
    
    def download_file(self, bucket: str, object_name: str, file_path: str):
        """Download a file from storage.
        
        Args:
            bucket: Bucket name
            object_name: Object name in bucket
            file_path: Local file path to save to
        """
        try:
            self.client.fget_object(bucket, object_name, file_path)
            return file_path
        except S3Error as e:
            raise Exception(f"Download failed: {e}")
    
    def download_data(self, bucket: str, object_name: str) -> bytes:
        """Download data from storage.
        
        Args:
            bucket: Bucket name
            object_name: Object name in bucket
            
        Returns:
            File data as bytes
        """
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise Exception(f"Download failed: {e}")
    
    def list_objects(self, bucket: str, prefix: str = "") -> list:
        """List objects in a bucket.
        
        Args:
            bucket: Bucket name
            prefix: Object prefix filter
            
        Returns:
            List of object names
        """
        try:
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            raise Exception(f"List failed: {e}")
    
    def delete_object(self, bucket: str, object_name: str):
        """Delete an object from storage.
        
        Args:
            bucket: Bucket name
            object_name: Object name to delete
        """
        try:
            self.client.remove_object(bucket, object_name)
        except S3Error as e:
            raise Exception(f"Delete failed: {e}")
    
    def get_presigned_url(self, bucket: str, object_name: str, expires: int = 3600) -> str:
        """Get a presigned URL for temporary access.
        
        Args:
            bucket: Bucket name
            object_name: Object name
            expires: URL expiration in seconds
            
        Returns:
            Presigned URL
        """
        try:
            url = self.client.presigned_get_object(
                bucket,
                object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            raise Exception(f"URL generation failed: {e}")


# Singleton instance
_object_storage = None


def get_object_storage() -> ObjectStorage:
    """Get ObjectStorage instance."""
    global _object_storage
    if _object_storage is None:
        _object_storage = ObjectStorage()
    return _object_storage
