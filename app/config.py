import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "debarunlahiri")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "lambrk")
    
    PENDING_DIR: str = os.getenv("PENDING_DIR", "/Volumes/Expansion/Lambrk/pending")
    COMPLETED_DIR: str = os.getenv("COMPLETED_DIR", "/Volumes/Expansion/Lambrk/completed")
    
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "4500"))
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "lam-brk")
    AWS_S3_BASE_URL: str = os.getenv("AWS_S3_BASE_URL", "https://lam-brk.s3.ap-south-1.amazonaws.com")
    AWS_S3_VIDEOS_PREFIX: str = os.getenv("AWS_S3_VIDEOS_PREFIX", "videos")
    
    @property
    def database_url(self) -> str:
        if self.POSTGRES_PASSWORD:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            return f"postgresql://{self.POSTGRES_USER}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

