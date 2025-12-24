from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Video:
    id: UUID
    title: str
    description: Optional[str]
    url: str
    thumbnail_url: Optional[str]
    duration: Optional[int]
    user_id: UUID
    views: int
    likes: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_db_row(cls, row: tuple):
        return cls(
            id=row[0],
            title=row[1],
            description=row[2],
            url=row[3],
            thumbnail_url=row[4],
            duration=row[5],
            user_id=row[6],
            views=row[7],
            likes=row[8],
            status=row[9],
            created_at=row[10],
            updated_at=row[11]
        )


@dataclass
class VideoQuality:
    id: UUID
    video_id: UUID
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
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_db_row(cls, row: tuple):
        return cls(
            id=row[0],
            video_id=row[1],
            quality=row[2],
            url=row[3],
            file_size=row[4],
            bitrate=row[5],
            resolution_width=row[6],
            resolution_height=row[7],
            codec=row[8],
            container=row[9],
            duration=row[10],
            is_default=row[11],
            status=row[12],
            created_at=row[13],
            updated_at=row[14]
        )

