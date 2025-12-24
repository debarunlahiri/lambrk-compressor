# Database Service Documentation

Detailed documentation for the database service module.

## Overview

The database service (`services/database.py`) provides a connection pool and database operations for the compression service using PostgreSQL and psycopg2.

## Architecture

### DatabaseService Class

Singleton-style class managing database connections and operations.

#### Connection Pooling

Uses `ThreadedConnectionPool` from psycopg2:

- **Min connections**: 1
- **Max connections**: 10
- **Thread-safe**: Safe for concurrent access
- **Automatic management**: Connections reused efficiently

#### Connection Lifecycle

1. **Get connection**: `get_connection()`
2. **Use connection**: Execute queries
3. **Return connection**: `put_connection(conn)`
4. **Close all**: `close_all()` on shutdown

## Methods

### Connection Management

#### `get_pool()`

Returns the connection pool, creating it if necessary.

**Returns:**
- `ThreadedConnectionPool`: Connection pool instance

#### `get_connection()`

Gets a connection from the pool.

**Returns:**
- `psycopg2.connection`: Database connection

#### `put_connection(conn)`

Returns a connection to the pool.

**Parameters:**
- `conn`: Connection to return

#### `close_all()`

Closes all connections in the pool. Called on service shutdown.

### Video Operations

#### `get_video_by_id(video_id)`

Retrieves a video record by ID.

**Parameters:**
- `video_id` (UUID): Video identifier

**Returns:**
- `Video` object or `None` if not found

**SQL:**
```sql
SELECT id, title, description, url, thumbnail_url, duration, 
       user_id, views, likes, status, created_at, updated_at
FROM videos
WHERE id = %s
```

#### `update_video_status(video_id, status)`

Updates the status of a video.

**Parameters:**
- `video_id` (UUID): Video identifier
- `status` (str): New status ('draft', 'published', 'processing')

**Returns:**
- `bool`: True if update successful

### Video Quality Operations

#### `create_video_quality()`

Creates a new video quality record.

**Parameters:**
- `video_id` (UUID): Video identifier
- `quality` (str): Quality level
- `url` (str): Video file URL
- `file_size` (int, optional): File size in bytes
- `bitrate` (int, optional): Video bitrate in kbps
- `resolution_width` (int, optional): Video width
- `resolution_height` (int, optional): Video height
- `codec` (str, optional): Video codec
- `container` (str, optional): Container format
- `duration` (int, optional): Duration in seconds
- `is_default` (bool): Whether this is default quality
- `status` (str): Processing status
- `processing_started_at` (datetime, optional): Processing start time

**Returns:**
- `VideoQuality` object or `None` on error

#### `update_video_quality()`

Updates a video quality record with metadata.

**Parameters:**
- `quality_id` (UUID): Quality record identifier
- Various optional metadata fields (see method signature)

**Returns:**
- `bool`: True if update successful

**Updates:**
- File size, bitrate, resolution
- Codec, container, duration
- FPS, pixel format, color space
- Audio metadata
- Aspect ratio, frame count
- Encoding time
- Processing completion time

#### `update_video_quality_status()`

Quickly updates only the status field.

**Parameters:**
- `quality_id` (UUID): Quality record identifier
- `status` (str): New status

**Returns:**
- `bool`: True if update successful

#### `get_video_qualities()`

Retrieves all quality versions for a video.

**Parameters:**
- `video_id` (UUID): Video identifier

**Returns:**
- `List[VideoQuality]`: List of quality records

**Ordering:**
Qualities are ordered by resolution (highest first):
1. 2160p
2. 1440p
3. 1080p
4. 720p
5. 480p
6. 360p
7. 240p
8. 144p
9. original

#### `set_default_quality()`

Sets a quality as the default for a video.

**Parameters:**
- `video_id` (UUID): Video identifier
- `quality_id` (UUID): Quality record identifier

**Returns:**
- `bool`: True if successful

**Process:**
1. Unsets any existing default quality
2. Sets the specified quality as default
3. Uses transaction to ensure atomicity

## Error Handling

### Connection Errors

- Connection failures are logged
- Operations return `None` or `False` on error
- Transactions are rolled back on error
- Connections are always returned to pool

### Transaction Management

- Each operation uses its own transaction
- Commits on success
- Rollbacks on error
- No nested transactions

## Performance Considerations

### Connection Pooling

- Reuses connections efficiently
- Reduces connection overhead
- Handles concurrent requests
- Limits maximum connections

### Query Optimization

- Uses parameterized queries (prevents SQL injection)
- Indexes on frequently queried columns
- Efficient WHERE clauses
- Minimal data transfer

### Batch Operations

- Individual updates per quality
- Could be optimized with batch inserts
- Consider bulk updates for status changes

## Thread Safety

All operations are thread-safe:
- Connection pool handles concurrent access
- Each operation gets its own connection
- No shared state between operations
- Safe for use with ThreadPoolExecutor

## Best Practices

1. **Always return connections**: Use try/finally blocks
2. **Handle errors gracefully**: Check return values
3. **Use transactions**: For multi-step operations
4. **Close on shutdown**: Call `close_all()` on exit
5. **Monitor pool size**: Adjust max connections if needed
6. **Log errors**: Include context in error messages

## Example Usage

```python
from services.database import DatabaseService
from uuid import UUID

# Get video
video = DatabaseService.get_video_by_id(UUID("..."))
if video:
    print(f"Video: {video.title}")

# Create quality
quality = DatabaseService.create_video_quality(
    video_id=video.id,
    quality="720p",
    url="https://example.com/video_720p.mp4",
    status="processing"
)

# Update with metadata
DatabaseService.update_video_quality(
    quality_id=quality.id,
    file_size=104857600,
    bitrate=5000,
    resolution_width=1280,
    resolution_height=720,
    status="ready"
)

# Get all qualities
qualities = DatabaseService.get_video_qualities(video.id)
for q in qualities:
    print(f"{q.quality}: {q.status}")
```

## Future Enhancements

- Batch insert operations
- Query result caching
- Connection health monitoring
- Automatic retry on connection errors
- Read replicas support
- Connection metrics

