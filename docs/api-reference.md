# API Reference

Complete API documentation for the Lambrk Compression Service.

## Base Information

**Base URL:** `http://localhost:4500/api/compression`

**Content-Type:** `application/json`

**Authentication:** Currently not required (can be added for production)

---

## API Endpoints

### CREATE Operations

#### 1. Compress Single Video

**Method:** `POST`  
**URL:** `http://localhost:4500/api/compression/compress`  
**Description:** Start compression job for a single video file. Creates multiple quality versions and uploads to S3.

**Request Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "my_video.mp4",
  "video_url_base": "https://example.com/videos"
}
```

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_id` | string (UUID) | Yes | UUID of the video record in the database |
| `filename` | string | Yes | Name of the video file in the pending directory |
| `video_url_base` | string | No | Base URL for fallback (default: "https://example.com/videos"). S3 URLs are used if AWS is configured |

**Full cURL Request:**
```bash
curl -X POST "http://localhost:4500/api/compression/compress" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "my_video.mp4",
    "video_url_base": "https://example.com/videos"
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Compression job started",
  "video_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Invalid video_id format"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Video not found"
}
```

**Error Response (404 Not Found - File):**
```json
{
  "detail": "Video file not found in pending directory: my_video.mp4"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "Error starting compression: [error details]"
}
```

---

#### 2. Batch Compress Videos

**Method:** `POST`  
**URL:** `http://localhost:4500/api/compression/compress/batch`  
**Description:** Start compression jobs for multiple videos in parallel.

**Request Headers:**
```http
Content-Type: application/json
```

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
    },
    {
      "video_id": "770e8400-e29b-41d4-a716-446655440002",
      "filename": "video3.mp4"
    }
  ],
  "max_workers": 4
}
```

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `videos` | array | Yes | Array of video compression requests |
| `videos[].video_id` | string (UUID) | Yes | UUID of the video record |
| `videos[].filename` | string | Yes | Name of the video file |
| `videos[].video_url_base` | string | No | Base URL for fallback |
| `max_workers` | integer | No | Maximum parallel workers (default: 4) |

**Full cURL Request:**
```bash
curl -X POST "http://localhost:4500/api/compression/compress/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "videos": [
      {
        "video_id": "550e8400-e29b-41d4-a716-446655440000",
        "filename": "video1.mp4",
        "video_url_base": "https://example.com/videos"
      },
      {
        "video_id": "660e8400-e29b-41d4-a716-446655440001",
        "filename": "video2.mp4"
      }
    ],
    "max_workers": 4
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "total": 2,
  "success_count": 0,
  "failed_count": 0,
  "results": []
}
```

**Note:** The `results` array will be empty initially as processing happens in the background. Use the status endpoint to check progress.

**Error Response (400 Bad Request):**
```json
{
  "detail": "No valid videos to process"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "Error starting batch compression: [error details]"
}
```

---

### READ Operations

#### 3. Get Video Qualities

**Method:** `GET`  
**URL:** `http://localhost:4500/api/compression/video/{video_id}/qualities`  
**Description:** Retrieve all quality versions for a specific video.

**URL Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_id` | string (UUID) | Yes | UUID of the video |

**Full cURL Request:**
```bash
curl -X GET "http://localhost:4500/api/compression/video/550e8400-e29b-41d4-a716-446655440000/qualities"
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "qualities": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "video_id": "550e8400-e29b-41d4-a716-446655440000",
      "quality": "720p",
      "url": "https://lam-brk.s3.ap-south-1.amazonaws.com/videos/550e8400-e29b-41d4-a716-446655440000/my_video_720p.mp4",
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
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440001",
      "video_id": "550e8400-e29b-41d4-a716-446655440000",
      "quality": "1080p",
      "url": "https://lam-brk.s3.ap-south-1.amazonaws.com/videos/550e8400-e29b-41d4-a716-446655440000/my_video_1080p.mp4",
      "file_size": 209715200,
      "bitrate": 8000,
      "resolution_width": 1920,
      "resolution_height": 1080,
      "codec": "h264",
      "container": "mp4",
      "duration": 3600,
      "is_default": false,
      "status": "ready",
      "created_at": "2024-01-01T00:00:00.000Z",
      "updated_at": "2024-01-01T00:00:00.000Z"
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440002",
      "video_id": "550e8400-e29b-41d4-a716-446655440000",
      "quality": "original",
      "url": "https://lam-brk.s3.ap-south-1.amazonaws.com/videos/550e8400-e29b-41d4-a716-446655440000/my_video.mp4",
      "file_size": 524288000,
      "bitrate": 12000,
      "resolution_width": 1920,
      "resolution_height": 1080,
      "codec": "h264",
      "container": "mp4",
      "duration": 3600,
      "is_default": false,
      "status": "ready",
      "created_at": "2024-01-01T00:00:00.000Z",
      "updated_at": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Invalid video_id format"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "Error fetching video qualities: [error details]"
}
```

---

#### 4. Get Video Status

**Method:** `GET`  
**URL:** `http://localhost:4500/api/compression/video/{video_id}/status`  
**Description:** Get the compression status for a video and all its quality versions.

**URL Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_id` | string (UUID) | Yes | UUID of the video |

**Full cURL Request:**
```bash
curl -X GET "http://localhost:4500/api/compression/video/550e8400-e29b-41d4-a716-446655440000/status"
```

**Success Response (200 OK):**
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
    "1080p": "ready",
    "original": "ready"
  }
}
```

**Response with Processing Status:**
```json
{
  "success": true,
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_status": "processing",
  "qualities": {
    "144p": "ready",
    "240p": "ready",
    "360p": "ready",
    "480p": "ready",
    "720p": "ready",
    "1080p": "processing",
    "original": "processing"
  }
}
```

**Response with Failed Qualities:**
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
    "1080p": "failed",
    "original": "ready"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Invalid video_id format"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Video not found"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "Error fetching video status: [error details]"
}
```

---

#### 5. Health Check

**Method:** `GET`  
**URL:** `http://localhost:4500/api/compression/health`  
**Description:** Check the health status of the service, database connection, and directory access.

**Full cURL Request:**
```bash
curl -X GET "http://localhost:4500/api/compression/health"
```

**Success Response (200 OK) - Healthy:**
```json
{
  "status": "healthy",
  "database": "connected",
  "pending_dir": "/Volumes/Expansion/Lambrk/pending",
  "completed_dir": "/Volumes/Expansion/Lambrk/completed"
}
```

**Response (200 OK) - Unhealthy:**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "Connection refused"
}
```

---

## Complete Data Models

### CompressionRequest

```typescript
interface CompressionRequest {
  video_id: string;              // UUID format: "550e8400-e29b-41d4-a716-446655440000"
  filename: string;               // Example: "my_video.mp4"
  video_url_base?: string;        // Optional, default: "https://example.com/videos"
}
```

**Example:**
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "my_video.mp4",
  "video_url_base": "https://example.com/videos"
}
```

---

### CompressionResponse

```typescript
interface CompressionResponse {
  success: boolean;
  message: string;
  video_id?: string;
  error?: string;
}
```

**Example:**
```json
{
  "success": true,
  "message": "Compression job started",
  "video_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### BatchCompressionRequest

```typescript
interface BatchCompressionRequest {
  videos: CompressionRequest[];
  max_workers?: number;           // Default: 4, range: 1-10 recommended
}
```

**Example:**
```json
{
  "videos": [
    {
      "video_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "video1.mp4"
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

---

### BatchCompressionResponse

```typescript
interface BatchCompressionResponse {
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

**Example:**
```json
{
  "success": true,
  "total": 2,
  "success_count": 0,
  "failed_count": 0,
  "results": []
}
```

---

### VideoQualityResponse

```typescript
interface VideoQualityResponse {
  id: string;                     // UUID
  video_id: string;               // UUID
  quality: '144p' | '240p' | '360p' | '480p' | '720p' | '1080p' | '1440p' | '2160p' | 'original';
  url: string;                    // S3 URL or local URL
  file_size?: number;             // Bytes
  bitrate?: number;                // kbps
  resolution_width?: number;       // Pixels
  resolution_height?: number;      // Pixels
  codec?: string;                 // e.g., "h264"
  container?: string;             // e.g., "mp4"
  duration?: number;               // Seconds
  is_default: boolean;
  status: 'processing' | 'ready' | 'failed';
  created_at: string;             // ISO 8601 format
  updated_at: string;              // ISO 8601 format
}
```

**Example:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "quality": "720p",
  "url": "https://lam-brk.s3.ap-south-1.amazonaws.com/videos/550e8400-e29b-41d4-a716-446655440000/my_video_720p.mp4",
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
```

---

### VideoQualitiesResponse

```typescript
interface VideoQualitiesResponse {
  success: boolean;
  qualities: VideoQualityResponse[];
}
```

**Example:**
```json
{
  "success": true,
  "qualities": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "video_id": "550e8400-e29b-41d4-a716-446655440000",
      "quality": "720p",
      "url": "https://lam-brk.s3.ap-south-1.amazonaws.com/videos/550e8400-e29b-41d4-a716-446655440000/my_video_720p.mp4",
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

---

## HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request successful |
| `400` | Bad Request | Invalid request parameters or format |
| `404` | Not Found | Resource (video/file) not found |
| `500` | Internal Server Error | Server error occurred |

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Examples:**

**400 Bad Request:**
```json
{
  "detail": "Invalid video_id format"
}
```

**404 Not Found:**
```json
{
  "detail": "Video not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error starting compression: Database connection failed"
}
```

---

## Complete Workflow Example

### Step 1: Compress a Video

**Request:**
```bash
curl -X POST "http://localhost:4500/api/compression/compress" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "my_video.mp4"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Compression job started",
  "video_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Step 2: Check Status

**Request:**
```bash
curl "http://localhost:4500/api/compression/video/550e8400-e29b-41d4-a716-446655440000/status"
```

**Response (Processing):**
```json
{
  "success": true,
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_status": "processing",
  "qualities": {
    "144p": "processing",
    "240p": "processing",
    "360p": "ready",
    "480p": "ready",
    "720p": "ready"
  }
}
```

### Step 3: Get All Qualities

**Request:**
```bash
curl "http://localhost:4500/api/compression/video/550e8400-e29b-41d4-a716-446655440000/qualities"
```

**Response:**
```json
{
  "success": true,
  "qualities": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "video_id": "550e8400-e29b-41d4-a716-446655440000",
      "quality": "720p",
      "url": "https://lam-brk.s3.ap-south-1.amazonaws.com/videos/550e8400-e29b-41d4-a716-446655440000/my_video_720p.mp4",
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

---

## Notes

- All compression jobs run **asynchronously** in the background
- Video files must be placed in the `PENDING_DIR` before starting compression
- Compressed videos are uploaded to **AWS S3** and saved locally to `COMPLETED_DIR/{video_id}/`
- S3 URLs are automatically stored in the database
- The service automatically selects a default quality (prefers 720p, then 1080p, 480p, 360p)
- Processing status can be checked using the status endpoint
- Videos are organized in S3 by video_id: `s3://lam-brk/videos/{video_id}/{filename}_{quality}.mp4`

---

## Rate Limiting

Currently, there is no rate limiting implemented. Consider adding rate limiting for production use.

---

## Interactive API Documentation

Access interactive API documentation at:
- **Swagger UI**: http://localhost:4500/docs
- **ReDoc**: http://localhost:4500/redoc
