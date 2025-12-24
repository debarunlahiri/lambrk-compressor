from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import os
import logging

from app.config import settings
from services.database import DatabaseService
from services.compression import CompressionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/compression", tags=["compression"])


class CompressionRequest(BaseModel):
    video_id: str
    filename: str
    video_url_base: str = "https://example.com/videos"


class CompressionResponse(BaseModel):
    success: bool
    message: str
    video_id: Optional[str] = None
    error: Optional[str] = None


class VideoQualityResponse(BaseModel):
    id: str
    video_id: str
    quality: str
    url: str
    file_size: Optional[int]
    bitrate: Optional[int]
    resolution_width: Optional[int]
    resolution_height: Optional[int]
    codec: Optional[str]
    container: Optional[str]
    duration: Optional[int]
    is_default: bool
    status: str
    created_at: str
    updated_at: str


class VideoQualitiesResponse(BaseModel):
    success: bool
    qualities: List[VideoQualityResponse]


@router.post("/compress", response_model=CompressionResponse)
async def compress_video(
    request: CompressionRequest,
    background_tasks: BackgroundTasks
):
    try:
        video_id = UUID(request.video_id)
        
        video = DatabaseService.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        input_path = os.path.join(settings.PENDING_DIR, request.filename)
        if not os.path.exists(input_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Video file not found in pending directory: {request.filename}"
            )
        
        background_tasks.add_task(
            CompressionService.process_pending_video,
            video_id=video_id,
            filename=request.filename,
            video_url_base=request.video_url_base
        )
        
        DatabaseService.update_video_status(video_id, 'processing')
        
        return CompressionResponse(
            success=True,
            message="Compression job started",
            video_id=str(video_id)
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video_id format")
    except Exception as e:
        logger.error(f"Error starting compression: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/video/{video_id}/qualities", response_model=VideoQualitiesResponse)
async def get_video_qualities(video_id: str):
    try:
        video_uuid = UUID(video_id)
        
        qualities = DatabaseService.get_video_qualities(video_uuid)
        
        quality_responses = [
            VideoQualityResponse(
                id=str(q.id),
                video_id=str(q.video_id),
                quality=q.quality,
                url=q.url,
                file_size=q.file_size,
                bitrate=q.bitrate,
                resolution_width=q.resolution_width,
                resolution_height=q.resolution_height,
                codec=q.codec,
                container=q.container,
                duration=q.duration,
                is_default=q.is_default,
                status=q.status,
                created_at=q.created_at.isoformat(),
                updated_at=q.updated_at.isoformat()
            )
            for q in qualities
        ]
        
        return VideoQualitiesResponse(
            success=True,
            qualities=quality_responses
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video_id format")
    except Exception as e:
        logger.error(f"Error fetching video qualities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/video/{video_id}/status")
async def get_video_status(video_id: str):
    try:
        video_uuid = UUID(video_id)
        
        video = DatabaseService.get_video_by_id(video_uuid)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        qualities = DatabaseService.get_video_qualities(video_uuid)
        
        quality_statuses = {
            q.quality: q.status for q in qualities
        }
        
        return {
            "success": True,
            "video_id": str(video_id),
            "video_status": video.status,
            "qualities": quality_statuses
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video_id format")
    except Exception as e:
        logger.error(f"Error fetching video status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class BatchCompressionRequest(BaseModel):
    videos: List[CompressionRequest]
    max_workers: int = 4


class BatchCompressionResponse(BaseModel):
    success: bool
    total: int
    success_count: int
    failed_count: int
    results: List[dict]


@router.post("/compress/batch", response_model=BatchCompressionResponse)
async def compress_videos_batch(
    request: BatchCompressionRequest,
    background_tasks: BackgroundTasks
):
    try:
        video_tasks = []
        for video_req in request.videos:
            video_id = UUID(video_req.video_id)
            video = DatabaseService.get_video_by_id(video_id)
            if not video:
                continue
            
            input_path = os.path.join(settings.PENDING_DIR, video_req.filename)
            if not os.path.exists(input_path):
                continue
            
            video_tasks.append({
                'video_id': video_id,
                'filename': video_req.filename,
                'video_url_base': video_req.video_url_base
            })
            
            DatabaseService.update_video_status(video_id, 'processing')
        
        if not video_tasks:
            raise HTTPException(status_code=400, detail="No valid videos to process")
        
        background_tasks.add_task(
            CompressionService.process_batch,
            video_tasks=video_tasks,
            max_workers=request.max_workers
        )
        
        return BatchCompressionResponse(
            success=True,
            total=len(video_tasks),
            success_count=0,
            failed_count=0,
            results=[]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid video_id format: {e}")
    except Exception as e:
        logger.error(f"Error starting batch compression: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    try:
        conn = DatabaseService.get_connection()
        DatabaseService.put_connection(conn)
        return {
            "status": "healthy",
            "database": "connected",
            "pending_dir": settings.PENDING_DIR,
            "completed_dir": settings.COMPLETED_DIR
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

