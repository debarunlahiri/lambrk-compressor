# Lambrk Compression Service

A high-performance video compression REST API service built with Python, FastAPI, FFmpeg, and PostgreSQL. Optimized for Apple Silicon M2 Pro with hardware acceleration support.

## Features

- **Multiple Quality Encoding**: Automatically generates multiple video quality versions (144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p, original)
- **Hardware Acceleration**: Optimized for Apple Silicon M2 Pro using VideoToolbox hardware encoder
- **Batch Processing**: Process multiple videos in parallel with configurable worker threads
- **Comprehensive Metadata**: Stores detailed video and audio metadata (fps, codec, bitrate, resolution, etc.)
- **PostgreSQL Integration**: Stores video quality information in PostgreSQL database
- **REST API**: Full REST API with FastAPI for easy integration
- **Auto Migrations**: Automatic database schema migrations on startup

## Requirements

- Python 3.8+
- PostgreSQL 12+
- FFmpeg with FFprobe
- Apple Silicon (M1/M2/M3) for hardware acceleration (optional, falls back to software encoding)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd lambrk-compression
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### 4. Configure environment variables

Create a `.env` file or set environment variables:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=debarunlahiri
POSTGRES_PASSWORD=
POSTGRES_DB=lambrk

PENDING_DIR=/Volumes/Expansion/Lambrk/pending
COMPLETED_DIR=/Volumes/Expansion/Lambrk/completed

API_HOST=0.0.0.0
API_PORT=4500

LOG_LEVEL=INFO
```

### 5. Run database migrations

```bash
python3 scripts/migrate.py
```

## Quick Start

### Using the startup script (Recommended)

```bash
./run.sh
```

This script will:
- Check all dependencies (Python, pip, FFmpeg, PostgreSQL)
- Create virtual environment if needed
- Install dependencies
- Run database migrations
- Start the service

### Manual startup

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4500
```

### Stop the service

```bash
./stop.sh
```

## API Documentation

Once the service is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:4500/docs
- **ReDoc**: http://localhost:4500/redoc

For detailed API documentation, see the [docs](./docs/) folder.

## Project Structure

```
lambrk-compression/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   └── main.py            # FastAPI application entry point
├── api/
│   ├── __init__.py
│   └── routes.py          # API route handlers
├── models/
│   ├── __init__.py
│   └── video.py           # Database models
├── services/
│   ├── __init__.py
│   ├── database.py        # PostgreSQL database service
│   └── compression.py     # Video compression service
├── utils/
│   ├── __init__.py
│   └── video_utils.py     # Video utility functions
├── migrations/
│   ├── 001_initial_schema.sql
│   ├── 002_create_video_qualities_table.sql
│   └── 003_add_video_metadata_fields.sql
├── scripts/
│   ├── migrate.py         # Database migration script
│   └── __init__.py
├── docs/                  # API documentation
├── run.sh                 # Startup script
├── stop.sh                # Shutdown script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Usage Examples

### Compress a single video

```bash
curl -X POST "http://localhost:4500/api/compression/compress" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "my_video.mp4",
    "video_url_base": "https://example.com/videos"
  }'
```

### Batch compress multiple videos

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
        "filename": "video2.mp4",
        "video_url_base": "https://example.com/videos"
      }
    ],
    "max_workers": 4
  }'
```

### Get video qualities

```bash
curl "http://localhost:4500/api/compression/video/{video_id}/qualities"
```

### Check video status

```bash
curl "http://localhost:4500/api/compression/video/{video_id}/status"
```

## Video Quality Configuration

The service automatically generates quality versions based on the original video resolution:

- **144p**: 200k bitrate, 144px height
- **240p**: 400k bitrate, 240px height
- **360p**: 800k bitrate, 360px height
- **480p**: 1500k bitrate, 480px height
- **720p**: 3000k bitrate, 720px height (default)
- **1080p**: 6000k bitrate, 1080px height
- **1440p**: 12000k bitrate, 1440px height
- **2160p**: 25000k bitrate, 2160px height
- **original**: Uncompressed original file

Only qualities equal to or lower than the original resolution are created.

## Hardware Acceleration

On Apple Silicon (M1/M2/M3), the service automatically uses:

- **VideoToolbox Hardware Encoder**: `h264_videotoolbox`
- **GPU Acceleration**: `-hwaccel videotoolbox`
- **Faster Encoding**: Significantly faster than software encoding

On other platforms, it falls back to software encoding using `libx264`.

## Database Schema

The service uses PostgreSQL with the following main tables:

- **videos**: Main video records (managed by Node.js backend)
- **video_qualities**: Multiple quality versions for each video (managed by this service)

**Note**: The `videos` table is created and managed by the Node.js backend service. This compression service only manages the `video_qualities` table and reads from the `videos` table.

See [Database Schema Documentation](./docs/database-schema.md) for detailed schema information.

## Configuration

All configuration is done through environment variables. See [Configuration Documentation](./docs/configuration.md) for details.

## API Endpoints

See [API Documentation](./docs/api-reference.md) for complete API reference.

## Development

### Running tests

```bash
pytest
```

### Code style

```bash
black .
flake8 .
```

## Troubleshooting

### FFmpeg not found

Ensure FFmpeg is installed and in your PATH:
```bash
ffmpeg -version
ffprobe -version
```

### Database connection errors

Check PostgreSQL is running and credentials are correct:
```bash
psql -h localhost -U debarunlahiri -d lambrk
```

### Permission errors

Ensure the pending and completed directories exist and are writable:
```bash
mkdir -p /Volumes/Expansion/Lambrk/pending
mkdir -p /Volumes/Expansion/Lambrk/completed
chmod 755 /Volumes/Expansion/Lambrk/pending
chmod 755 /Volumes/Expansion/Lambrk/completed
```

## License

[Your License Here]

## Support

For issues and questions, please open an issue on the repository.

