# Compression Service Documentation

Detailed documentation for the video compression service module.

## Overview

The compression service (`services/compression.py`) handles video compression using FFmpeg, creating multiple quality versions of videos similar to YouTube's multi-quality system.

## Features

- Multi-quality encoding (144p to 2160p)
- Hardware acceleration support (Apple Silicon VideoToolbox)
- Batch processing with parallel execution
- Comprehensive metadata extraction
- Automatic quality selection based on original resolution
- Default quality assignment

## Architecture

### CompressionService Class

Main service class that handles all compression operations.

#### Methods

##### `compress_video()`

Compresses a single video to a specific quality.

**Parameters:**
- `input_path` (str): Path to input video file
- `output_path` (str): Path for output compressed video
- `quality` (str): Target quality ('144p', '240p', etc.)
- `width` (int): Original video width
- `height` (int): Original video height
- `start_time` (datetime, optional): Processing start time

**Returns:**
- `Dict` with compression results including:
  - `success`: Boolean indicating success
  - `output_path`: Path to compressed file
  - `width`, `height`: Resolution
  - `file_size`: File size in bytes
  - `bitrate`: Video bitrate in kbps
  - `codec`: Video codec
  - `container`: Container format
  - `fps`: Frames per second
  - `pixel_format`: Pixel format
  - `color_space`: Color space
  - `color_range`: Color range
  - `audio_codec`: Audio codec
  - `audio_bitrate`: Audio bitrate
  - `audio_sample_rate`: Audio sample rate
  - `audio_channels`: Number of audio channels
  - `aspect_ratio`: Aspect ratio
  - `frame_count`: Total frames
  - `encoding_time`: Encoding time in seconds

**FFmpeg Command (Apple Silicon):**
```bash
ffmpeg -hwaccel videotoolbox \
  -i input.mp4 \
  -c:v h264_videotoolbox \
  -b:v {bitrate} \
  -maxrate {maxrate} \
  -bufsize {bufsize} \
  -vf scale={width}:{height} \
  -allow_sw 1 \
  -c:a aac \
  -b:a 128k \
  -movflags +faststart \
  -y output.mp4
```

**FFmpeg Command (Other Platforms):**
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -preset fast \
  -crf 23 \
  -vf scale={width}:{height} \
  -b:v {bitrate} \
  -maxrate {maxrate} \
  -bufsize {bufsize} \
  -c:a aac \
  -b:a 128k \
  -movflags +faststart \
  -threads 0 \
  -y output.mp4
```

##### `process_video_qualities()`

Processes a video to create all supported quality versions.

**Parameters:**
- `video_id` (UUID): Video database ID
- `input_path` (str): Path to input video
- `video_url_base` (str): Base URL for video file URLs

**Returns:**
- `Dict` with processing results

**Process:**
1. Extracts video information
2. Determines supported qualities based on resolution
3. Creates database records for each quality
4. Compresses to each quality
5. Updates database with metadata
6. Sets default quality

##### `process_pending_video()`

Main entry point for processing a video from the pending directory.

**Parameters:**
- `video_id` (UUID): Video database ID
- `filename` (str): Video filename in pending directory
- `video_url_base` (str): Base URL for video files

**Returns:**
- `Dict` with processing results

**Process:**
1. Validates input file exists
2. Processes all quality versions
3. Copies original to completed directory
4. Creates original quality record
5. Updates video status

##### `process_batch()`

Processes multiple videos in parallel.

**Parameters:**
- `video_tasks` (List[Dict]): List of video processing tasks
  - Each task contains: `video_id`, `filename`, `video_url_base`
- `max_workers` (int): Maximum parallel workers (default: 4)

**Returns:**
- `Dict` with batch results:
  - `total`: Total videos processed
  - `success`: Number of successful compressions
  - `failed`: Number of failed compressions
  - `results`: List of individual results

**Implementation:**
Uses `ThreadPoolExecutor` for parallel processing.

## Quality Configuration

Quality settings are defined in `utils/video_utils.py`:

```python
QUALITY_CONFIGS = {
    '144p': {
        'height': 144,
        'bitrate': '200k',
        'maxrate': '300k',
        'bufsize': '400k'
    },
    # ... other qualities
}
```

### Quality Selection Logic

1. Only creates qualities equal to or lower than original resolution
2. Default quality selection priority:
   - 720p (preferred)
   - 1080p
   - 480p
   - 360p
   - First available quality

## Hardware Acceleration

### Apple Silicon Detection

The service automatically detects Apple Silicon using:
```python
platform.system() == 'Darwin' and platform.machine() == 'arm64'
```

### VideoToolbox Encoder

On Apple Silicon, uses:
- **Hardware encoder**: `h264_videotoolbox`
- **Hardware acceleration**: `-hwaccel videotoolbox`
- **Software fallback**: `-allow_sw 1` (if hardware encoding fails)

### Performance Benefits

- **3-5x faster** encoding compared to software
- **Lower CPU usage** (offloads to GPU)
- **Better battery life** on laptops
- **Higher quality** at same bitrate

## Error Handling

### Compression Failures

- Individual quality failures don't stop entire process
- Failed qualities marked as 'failed' in database
- Video status set to 'draft' only if all qualities fail
- Errors logged with full context

### Common Errors

1. **File not found**: Video file missing from pending directory
2. **FFmpeg errors**: Invalid video format or corrupted file
3. **Database errors**: Connection issues or constraint violations
4. **Disk space**: Insufficient storage for output files

## Performance Optimization

### Parallel Processing

- Multiple videos processed simultaneously
- Configurable worker count
- Thread-safe database operations
- Efficient resource utilization

### Quality Processing

Currently processes qualities sequentially. Can be optimized to:
- Process multiple qualities in parallel
- Use separate threads for each quality
- Balance CPU/GPU load

### Resource Management

- Connection pooling for database
- Efficient file I/O operations
- Memory management for large videos
- Disk space monitoring

## Monitoring

### Metrics Tracked

- Encoding time per quality
- File size reduction
- Processing start/end times
- Success/failure rates
- Bitrate achieved vs target

### Logging

All operations are logged with appropriate levels:
- `DEBUG`: Detailed FFmpeg commands and responses
- `INFO`: Processing status and progress
- `WARNING`: Non-critical issues
- `ERROR`: Compression failures

## Best Practices

1. **Pre-validate videos**: Check format and integrity before processing
2. **Monitor disk space**: Ensure sufficient storage
3. **Optimize worker count**: Balance between speed and resource usage
4. **Handle failures gracefully**: Don't stop batch on single failure
5. **Clean up failed files**: Remove incomplete compressions
6. **Monitor encoding times**: Track performance trends

## Future Enhancements

- Parallel quality processing
- Adaptive bitrate selection
- H.265/HEVC support
- WebM format support
- Thumbnail generation
- Progress callbacks
- Retry mechanisms
- Queue management system

