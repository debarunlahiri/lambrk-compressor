import boto3
import os
import logging
from typing import Optional
from uuid import UUID
from botocore.exceptions import ClientError, BotoCoreError

from app.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    _client: Optional[boto3.client] = None
    
    @classmethod
    def get_client(cls):
        """Get or create S3 client."""
        if cls._client is None:
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                logger.warning("AWS credentials not configured. S3 uploads will fail.")
                return None
            
            cls._client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        return cls._client
    
    @staticmethod
    def upload_file(local_file_path: str, video_id: UUID, filename: str, quality: str) -> Optional[str]:
        """
        Upload a video file to S3.
        
        Args:
            local_file_path: Path to local file
            video_id: Video UUID
            filename: Original filename
            quality: Quality level (e.g., '720p', 'original')
        
        Returns:
            S3 URL if successful, None otherwise
        """
        if not os.path.exists(local_file_path):
            logger.error(f"File not found: {local_file_path}")
            return None
        
        client = S3Service.get_client()
        if not client:
            logger.error("S3 client not available")
            return None
        
        # Generate S3 key: videos/{video_id}/{filename}_{quality}.mp4
        file_extension = os.path.splitext(filename)[1] or '.mp4'
        base_filename = os.path.splitext(filename)[0]
        s3_key = f"{settings.AWS_S3_VIDEOS_PREFIX}/{str(video_id)}/{base_filename}_{quality}{file_extension}"
        
        try:
            # Upload file with public-read ACL
            client.upload_file(
                local_file_path,
                settings.AWS_S3_BUCKET,
                s3_key,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': 'video/mp4'
                }
            )
            
            # Generate public URL
            s3_url = f"{settings.AWS_S3_BASE_URL}/{s3_key}"
            logger.info(f"Successfully uploaded {s3_key} to S3")
            return s3_url
            
        except ClientError as e:
            logger.error(f"Error uploading {s3_key} to S3: {e}")
            return None
        except BotoCoreError as e:
            logger.error(f"BotoCore error uploading to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}")
            return None
    
    @staticmethod
    def delete_file(video_id: UUID, filename: str, quality: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            video_id: Video UUID
            filename: Original filename
            quality: Quality level
        
        Returns:
            True if successful, False otherwise
        """
        client = S3Service.get_client()
        if not client:
            return False
        
        file_extension = os.path.splitext(filename)[1] or '.mp4'
        base_filename = os.path.splitext(filename)[0]
        s3_key = f"{settings.AWS_S3_VIDEOS_PREFIX}/{str(video_id)}/{base_filename}_{quality}{file_extension}"
        
        try:
            client.delete_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=s3_key
            )
            logger.info(f"Successfully deleted {s3_key} from S3")
            return True
        except ClientError as e:
            logger.error(f"Error deleting {s3_key} from S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting from S3: {e}")
            return False
    
    @staticmethod
    def file_exists(video_id: UUID, filename: str, quality: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            video_id: Video UUID
            filename: Original filename
            quality: Quality level
        
        Returns:
            True if file exists, False otherwise
        """
        client = S3Service.get_client()
        if not client:
            return False
        
        file_extension = os.path.splitext(filename)[1] or '.mp4'
        base_filename = os.path.splitext(filename)[0]
        s3_key = f"{settings.AWS_S3_VIDEOS_PREFIX}/{str(video_id)}/{base_filename}_{quality}{file_extension}"
        
        try:
            client.head_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=s3_key
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Error checking file existence in S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking S3 file: {e}")
            return False

