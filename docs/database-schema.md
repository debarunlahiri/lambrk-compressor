# Database Schema Documentation

Complete database schema documentation for the Lambrk Compression Service.

## Database

- **Database Name**: `lambrk`
- **Database Type**: PostgreSQL 12+
- **Connection**: Uses connection pooling with psycopg2

## Tables

### videos

Main table storing video records. **This table is managed by the Node.js backend service, not by this compression service.** The compression service only reads from this table and manages the `video_qualities` table.

**Columns:**
- `id` (UUID, PRIMARY KEY): Unique video identifier
- `title` (VARCHAR(255)): Video title
- `description` (TEXT): Video description
- `url` (TEXT): Original video URL
- `thumbnail_url` (TEXT): Thumbnail image URL
- `duration` (INTEGER): Video duration in seconds
- `user_id` (UUID): Owner user ID
- `views` (INTEGER): View count
- `likes` (INTEGER): Like count
- `status` (VARCHAR(20)): Video status ('draft', 'published', 'processing')
- `created_at` (TIMESTAMP): Creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes:**
- `idx_videos_user_id`: Index on user_id
- `idx_videos_status`: Index on status
- `idx_videos_created_at`: Index on created_at (DESC)

**Triggers:**
- `update_videos_updated_at`: Automatically updates `updated_at` on row update

---

### video_qualities

Stores multiple quality versions for each video (YouTube-like multi-quality support).

**Columns:**
- `id` (UUID, PRIMARY KEY): Unique quality record identifier
- `video_id` (UUID, NOT NULL): Foreign key to videos.id
- `quality` (VARCHAR(20), NOT NULL): Quality level
  - Valid values: '144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p', 'original'
- `url` (TEXT, NOT NULL): URL to the quality version file
  - Typically an AWS S3 public URL: `https://lam-brk.s3.ap-south-1.amazonaws.com/videos/{video_id}/{filename}_{quality}.mp4`
  - Falls back to local URL if S3 upload fails
- `file_size` (BIGINT): File size in bytes
- `bitrate` (INTEGER): Video bitrate in kbps
- `resolution_width` (INTEGER): Video width in pixels
- `resolution_height` (INTEGER): Video height in pixels
- `codec` (VARCHAR(50)): Video codec (e.g., 'h264', 'h265')
- `container` (VARCHAR(20)): Container format (e.g., 'mp4', 'webm')
- `duration` (INTEGER): Duration in seconds
- `is_default` (BOOLEAN): Whether this is the default quality (default: false)
- `status` (VARCHAR(20)): Processing status
  - Valid values: 'processing', 'ready', 'failed'
  - Default: 'processing'
- `fps` (DECIMAL(10, 2)): Frames per second
- `pixel_format` (VARCHAR(20)): Pixel format (e.g., 'yuv420p')
- `color_space` (VARCHAR(20)): Color space (e.g., 'bt709')
- `color_range` (VARCHAR(20)): Color range (e.g., 'tv', 'pc')
- `audio_codec` (VARCHAR(50)): Audio codec (e.g., 'aac', 'mp3')
- `audio_bitrate` (INTEGER): Audio bitrate in kbps
- `audio_sample_rate` (INTEGER): Audio sample rate in Hz
- `audio_channels` (INTEGER): Number of audio channels
- `aspect_ratio` (VARCHAR(20)): Aspect ratio (e.g., '16:9')
- `frame_count` (BIGINT): Total number of frames
- `encoding_time` (INTEGER): Time taken to encode in seconds
- `processing_started_at` (TIMESTAMP): When processing started
- `processing_completed_at` (TIMESTAMP): When processing completed
- `created_at` (TIMESTAMP): Record creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Constraints:**
- Foreign key: `video_qualities_video_id_fkey` → `videos(id) ON DELETE CASCADE`
- Check constraint: `quality` must be one of the valid values
- Check constraint: `status` must be one of the valid values
- Unique constraint: Only one default quality per video (`idx_video_qualities_one_default`)

**Indexes:**
- `idx_video_qualities_video_id`: Index on video_id
- `idx_video_qualities_quality`: Index on quality
- `idx_video_qualities_status`: Index on status
- `idx_video_qualities_default`: Partial index on (video_id, is_default) WHERE is_default = true
- `idx_video_qualities_one_default`: Unique partial index ensuring one default per video
- `idx_video_qualities_processing_times`: Index on processing_started_at and processing_completed_at

**Triggers:**
- `update_video_qualities_updated_at`: Automatically updates `updated_at` on row update

---

## Functions

### update_updated_at_column()

PostgreSQL function that automatically updates the `updated_at` timestamp column.

**Usage:**
Triggered automatically on UPDATE operations for tables with this trigger.

---

## Migrations

The database schema is managed through migration files in the `migrations/` directory:

1. **001_initial_schema.sql**: Creates videos table and trigger function
2. **002_create_video_qualities_table.sql**: Creates video_qualities table with basic fields
3. **003_add_video_metadata_fields.sql**: Adds extended metadata fields

Migrations are automatically applied when running `scripts/migrate.py` or `./run.sh`.

## Relationships

```
videos (1) ──< (many) video_qualities
```

- One video can have multiple quality versions
- When a video is deleted, all its quality versions are cascade deleted
- Each video can have exactly one default quality version

## Data Flow

1. Video record is created in `videos` table (by main video service)
2. Compression service creates quality records in `video_qualities` with status 'processing'
3. FFmpeg compresses video to each quality
4. Compressed videos are uploaded to AWS S3
5. Quality records are updated with S3 URLs, metadata, and status 'ready'
6. One quality is marked as `is_default = true`

**S3 URL Format:**
- `https://lam-brk.s3.ap-south-1.amazonaws.com/videos/{video_id}/{filename}_{quality}.mp4`
- Example: `https://lam-brk.s3.ap-south-1.amazonaws.com/videos/550e8400-e29b-41d4-a716-446655440000/my_video_720p.mp4`

## Query Examples

### Get all qualities for a video

```sql
SELECT * FROM video_qualities 
WHERE video_id = '550e8400-e29b-41d4-a716-446655440000'
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
  END;
```

### Get default quality for a video

```sql
SELECT * FROM video_qualities 
WHERE video_id = '550e8400-e29b-41d4-a716-446655440000' 
  AND is_default = true;
```

### Get videos with processing status

```sql
SELECT v.*, COUNT(vq.id) as quality_count
FROM videos v
LEFT JOIN video_qualities vq ON v.id = vq.video_id
WHERE v.status = 'processing'
GROUP BY v.id;
```

### Get quality statistics

```sql
SELECT 
  quality,
  COUNT(*) as count,
  AVG(file_size) as avg_file_size,
  AVG(bitrate) as avg_bitrate,
  AVG(encoding_time) as avg_encoding_time
FROM video_qualities
WHERE status = 'ready'
GROUP BY quality;
```

## Connection Pooling

The service uses `ThreadedConnectionPool` from psycopg2 for efficient database connection management:

- **Min connections**: 1
- **Max connections**: 10
- Connections are automatically managed and reused

## Backup Recommendations

1. Regular backups of the `video_qualities` table
2. Backup video files in `COMPLETED_DIR`
3. Consider point-in-time recovery for production

## Performance Considerations

- Indexes are optimized for common query patterns
- Foreign key constraints ensure data integrity
- Partial indexes reduce index size for default quality queries
- Connection pooling reduces connection overhead

