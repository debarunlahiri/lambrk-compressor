# API Reference

Complete API documentation for the Lambrk Compression Service.

## Base URL

```
http://localhost:4500/api/compression
```

## Authentication

Currently, the API does not require authentication. This can be added based on your security requirements.

## Endpoints

### 1. Compress Single Video

Compress a single video file into multiple quality versions.

**Endpoint:** `POST /api/compression/compress`

**Request Body:**
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "my_video.mp4",
  "video_url_base": "https://example.com/videos"
}
```

**Parameters:**
- `video_id` (string, required): UUID of the video record in the database
- `filename` (string, required): Name of the video file in the pending directory
- `video_url_base` (string, optional): Base URL for video file URLs (default: "https://example.com/videos")

**Response:**
```json
{
  "success": true,
  "message": "Compression job started",
  "video_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Status Codes:**
- `200 OK`: Compression job started successfully
- `400 Bad Request`: Invalid video_id format or missing required fields
- `404 Not Found`: Video not found in database or file not found in pending directory
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl -X POST "http://localhost:4500/api/compression/compress" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "my_video.mp4",
    "video_url_base": "https://example.com/videos"
  }'
```

---

### 2. Batch Compress Videos

Compress multiple videos in parallel.

**Endpoint:** `POST /api/compression/compress/batch`

**Request Body:**
```json
{
  "videos": [
    {
      "video_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "video1.mp4",
      "video_url_base": "https://example.com/videos"
    },
    {
      "video_id": "660e8400-e29b-41d4-a716-446655440001",
      "filename": "video2.mp4",
      "video_url_base": "https://example.com/videos"
    }
  ],
  "max_workers": 4
}
```

**Parameters:**
- `videos` (array, required): Array of video compression requests
  - `video_id` (string, required): UUID of the video record
  - `filename` (string, required): Name of the video file
  - `video_url_base` (string, optional): Base URL for video file URLs
- `max_workers` (integer, optional): Maximum number of parallel workers (default: 4)

**Response:**
```json
{
  "success": true,
  "total": 2,
  "success_count": 0,
  "failed_count": 0,
  "results": []
}
```

**Status Codes:**
- `200 OK`: Batch compression job started
- `400 Bad Request`: No valid videos to process or invalid format
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl -X POST "http://localhost:4500/api/compression/compress/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "videos": [
      {
        "video_id": "550e8400-e29b-41d4-a716-446655440000",
        "filename": "video1.mp4"
      }
    ],
    "max_workers": 4
  }'
```

---

### 3. Get Video Qualities

Retrieve all quality versions for a specific video.

**Endpoint:** `GET /api/compression/video/{video_id}/qualities`

**Path Parameters:**
- `video_id` (string, required): UUID of the video

**Response:**
```json
{
  "success": true,
  "qualities": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "video_id": "550e8400-e29b-41d4-a716-446655440000",
      "quality": "720p",
      "url": "https://example.com/videos/550e8400-e29b-41d4-a716-446655440000/video_720p.mp4",
      "file_size": 104857600,
      "bitrate": 5000,
      "resolution_width": 1280,
      "resolution_height": 720,
      "codec": "h264",
      "container": "mp4",
      "duration": 3600,
      "is_default": true,
      "status": "ready",
      "created_at": "2024-01-01T00:00:00.000Z",
      "updated_at": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid video_id format
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl "http://localhost:4500/api/compression/video/550e8400-e29b-41d4-a716-446655440000/qualities"
```

---

### 4. Get Video Status

Get the compression status for a video and all its quality versions.

**Endpoint:** `GET /api/compression/video/{video_id}/status`

**Path Parameters:**
- `video_id` (string, required): UUID of the video

**Response:**
```json
{
  "success": true,
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_status": "published",
  "qualities": {
    "144p": "ready",
    "240p": "ready",
    "360p": "ready",
    "480p": "ready",
    "720p": "ready",
    "1080p": "processing"
  }
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid video_id format
- `404 Not Found`: Video not found
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl "http://localhost:4500/api/compression/video/550e8400-e29b-41d4-a716-446655440000/status"
```

---

### 5. Health Check

Check the health status of the service.

**Endpoint:** `GET /api/compression/health`

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "pending_dir": "/Volumes/Expansion/Lambrk/pending",
  "completed_dir": "/Volumes/Expansion/Lambrk/completed"
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `200 OK`: Service is unhealthy (check error field)

**Example:**
```bash
curl "http://localhost:4500/api/compression/health"
```

---

## Data Models

### CompressionRequest

```typescript
{
  video_id: string;        // UUID
  filename: string;        // Video filename
  video_url_base?: string; // Base URL for video files
}
```

### CompressionResponse

```typescript
{
  success: boolean;
  message: string;
  video_id?: string;
  error?: string;
}
```

### VideoQualityResponse

```typescript
{
  id: string;
  video_id: string;
  quality: string;              // '144p' | '240p' | '360p' | '480p' | '720p' | '1080p' | '1440p' | '2160p' | 'original'
  url: string;
  file_size?: number;
  bitrate?: number;
  resolution_width?: number;
  resolution_height?: number;
  codec?: string;
  container?: string;
  duration?: number;
  is_default: boolean;
  status: string;                // 'processing' | 'ready' | 'failed'
  created_at: string;
  updated_at: string;
}
```

### BatchCompressionRequest

```typescript
{
  videos: CompressionRequest[];
  max_workers?: number;         // Default: 4
}
```

### BatchCompressionResponse

```typescript
{
  success: boolean;
  total: number;
  success_count: number;
  failed_count: number;
  results: Array<{
    video_id: string;
    filename: string;
    success: boolean;
    error?: string;
    qualities: Array<{
      quality: string;
      status: string;
      file_size?: number;
    }>;
  }>;
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently, there is no rate limiting implemented. Consider adding rate limiting for production use.

## Notes

- All compression jobs run asynchronously in the background
- Video files must be placed in the `PENDING_DIR` before starting compression
- Compressed videos are saved to `COMPLETED_DIR/{video_id}/`
- The service automatically selects a default quality (prefers 720p, then 1080p, 480p, 360p)
- Processing status can be checked using the status endpoint

