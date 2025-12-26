import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from typing import Optional, List, Dict, Any
import logging
from uuid import UUID
from datetime import datetime

from app.config import settings
from models.video import Video, VideoQuality

logger = logging.getLogger(__name__)


class DatabaseService:
    _pool: Optional[ThreadedConnectionPool] = None
    
    @classmethod
    def get_pool(cls) -> ThreadedConnectionPool:
        if cls._pool is None:
            cls._pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB
            )
        return cls._pool
    
    @classmethod
    def get_connection(cls):
        pool = cls.get_pool()
        return pool.getconn()
    
    @classmethod
    def put_connection(cls, conn):
        pool = cls.get_pool()
        pool.putconn(conn)
    
    @classmethod
    def close_all(cls):
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
    
    @staticmethod
    def get_video_by_id(video_id: UUID) -> Optional[Video]:
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, title, description, url, thumbnail_url, duration, 
                           user_id, views, likes, status, created_at, updated_at
                    FROM videos
                    WHERE id = %s
                    """,
                    (str(video_id),)
                )
                row = cur.fetchone()
                if row:
                    return Video.from_db_row(row)
                return None
        except Exception as e:
            logger.error(f"Error fetching video {video_id}: {e}")
            conn.rollback()
            return None
        finally:
            DatabaseService.put_connection(conn)
    
    @staticmethod
    def create_video_quality(video_id: UUID, quality: str, url: str, 
                            file_size: Optional[int] = None,
                            bitrate: Optional[int] = None,
                            resolution_width: Optional[int] = None,
                            resolution_height: Optional[int] = None,
                            codec: Optional[str] = None,
                            container: Optional[str] = None,
                            duration: Optional[int] = None,
                            is_default: bool = False,
                            status: str = "processing",
                            processing_started_at: Optional[datetime] = None) -> Optional[VideoQuality]:
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO video_qualities 
                    (video_id, quality, url, file_size, bitrate, resolution_width, 
                     resolution_height, codec, container, duration, is_default, status,
                     processing_started_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, video_id, quality, url, file_size, bitrate, 
                              resolution_width, resolution_height, codec, container, 
                              duration, is_default, status, created_at, updated_at
                    """,
                    (str(video_id), quality, url, file_size, bitrate, resolution_width,
                     resolution_height, codec, container, duration, is_default, status,
                     processing_started_at or datetime.now())
                )
                row = cur.fetchone()
                conn.commit()
                if row:
                    return VideoQuality.from_db_row(row)
                return None
        except Exception as e:
            logger.error(f"Error creating video quality: {e}")
            conn.rollback()
            return None
        finally:
            DatabaseService.put_connection(conn)
    
    @staticmethod
    def update_video_quality_status(quality_id: UUID, status: str) -> bool:
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE video_qualities
                    SET status = %s
                    WHERE id = %s
                    """,
                    (status, str(quality_id))
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating video quality status: {e}")
            conn.rollback()
            return False
        finally:
            DatabaseService.put_connection(conn)
    
    @staticmethod
    def update_video_quality(quality_id: UUID, url: Optional[str] = None,
                            file_size: Optional[int] = None,
                            bitrate: Optional[int] = None,
                            resolution_width: Optional[int] = None,
                            resolution_height: Optional[int] = None,
                            codec: Optional[str] = None,
                            container: Optional[str] = None,
                            duration: Optional[int] = None,
                            status: Optional[str] = None,
                            fps: Optional[float] = None,
                            pixel_format: Optional[str] = None,
                            color_space: Optional[str] = None,
                            color_range: Optional[str] = None,
                            audio_codec: Optional[str] = None,
                            audio_bitrate: Optional[int] = None,
                            audio_sample_rate: Optional[int] = None,
                            audio_channels: Optional[int] = None,
                            aspect_ratio: Optional[str] = None,
                            frame_count: Optional[int] = None,
                            encoding_time: Optional[int] = None,
                            processing_completed_at: Optional[datetime] = None) -> bool:
        conn = DatabaseService.get_connection()
        try:
            updates = []
            params = []
            
            if url is not None:
                updates.append("url = %s")
                params.append(url)
            if file_size is not None:
                updates.append("file_size = %s")
                params.append(file_size)
            if bitrate is not None:
                updates.append("bitrate = %s")
                params.append(bitrate)
            if resolution_width is not None:
                updates.append("resolution_width = %s")
                params.append(resolution_width)
            if resolution_height is not None:
                updates.append("resolution_height = %s")
                params.append(resolution_height)
            if codec is not None:
                updates.append("codec = %s")
                params.append(codec)
            if container is not None:
                updates.append("container = %s")
                params.append(container)
            if duration is not None:
                updates.append("duration = %s")
                params.append(duration)
            if status is not None:
                updates.append("status = %s")
                params.append(status)
            if fps is not None:
                updates.append("fps = %s")
                params.append(fps)
            if pixel_format is not None:
                updates.append("pixel_format = %s")
                params.append(pixel_format)
            if color_space is not None:
                updates.append("color_space = %s")
                params.append(color_space)
            if color_range is not None:
                updates.append("color_range = %s")
                params.append(color_range)
            if audio_codec is not None:
                updates.append("audio_codec = %s")
                params.append(audio_codec)
            if audio_bitrate is not None:
                updates.append("audio_bitrate = %s")
                params.append(audio_bitrate)
            if audio_sample_rate is not None:
                updates.append("audio_sample_rate = %s")
                params.append(audio_sample_rate)
            if audio_channels is not None:
                updates.append("audio_channels = %s")
                params.append(audio_channels)
            if aspect_ratio is not None:
                updates.append("aspect_ratio = %s")
                params.append(aspect_ratio)
            if frame_count is not None:
                updates.append("frame_count = %s")
                params.append(frame_count)
            if encoding_time is not None:
                updates.append("encoding_time = %s")
                params.append(encoding_time)
            if processing_completed_at is not None:
                updates.append("processing_completed_at = %s")
                params.append(processing_completed_at)
            
            if not updates:
                return False
            
            params.append(str(quality_id))
            query = f"""
                UPDATE video_qualities
                SET {', '.join(updates)}
                WHERE id = %s
            """
            
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating video quality: {e}")
            conn.rollback()
            return False
        finally:
            DatabaseService.put_connection(conn)
    
    @staticmethod
    def get_video_qualities(video_id: UUID) -> List[VideoQuality]:
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, video_id, quality, url, file_size, bitrate, 
                           resolution_width, resolution_height, codec, container, 
                           duration, is_default, status, created_at, updated_at
                    FROM video_qualities
                    WHERE video_id = %s
                    ORDER BY 
                        CASE quality
                            WHEN '2160p' THEN 1
                            WHEN '1440p' THEN 2
                            WHEN '1080p' THEN 3
                            WHEN '720p' THEN 4
                            WHEN '480p' THEN 5
                            WHEN '360p' THEN 6
                            WHEN '240p' THEN 7
                            WHEN '144p' THEN 8
                            WHEN 'original' THEN 9
                        END
                    """,
                    (str(video_id),)
                )
                rows = cur.fetchall()
                return [VideoQuality.from_db_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching video qualities: {e}")
            conn.rollback()
            return []
        finally:
            DatabaseService.put_connection(conn)
    
    @staticmethod
    def update_video_status(video_id: UUID, status: str) -> bool:
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE videos
                    SET status = %s
                    WHERE id = %s
                    """,
                    (status, str(video_id))
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating video status: {e}")
            conn.rollback()
            return False
        finally:
            DatabaseService.put_connection(conn)
    
    @staticmethod
    def set_default_quality(video_id: UUID, quality_id: UUID) -> bool:
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute(
                    """
                    UPDATE video_qualities
                    SET is_default = false
                    WHERE video_id = %s AND is_default = true
                    """,
                    (str(video_id),)
                )
                cur.execute(
                    """
                    UPDATE video_qualities
                    SET is_default = true
                    WHERE id = %s
                    """,
                    (str(quality_id),)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error setting default quality: {e}")
            conn.rollback()
            return False
        finally:
            DatabaseService.put_connection(conn)

