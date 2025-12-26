# S3 Service Documentation

Detailed documentation for the AWS S3 integration service.

## Overview

The S3 service (`services/s3_service.py`) handles uploading compressed videos to AWS S3 and managing S3 URLs in the database.

## Features

- Automatic upload to S3 after compression
- Public-read ACL for video files
- Organized folder structure by video_id
- Fallback to local URLs if S3 upload fails
- File existence checking
- File deletion support

## S3 Structure

Videos are organized in S3 with the following structure:

```
s3://lam-brk/videos/{video_id}/{filename}_{quality}.mp4
```

**Example:**
- Video ID: `550e8400-e29b-41d4-a716-446655440000`
- Filename: `my_video.mp4`
- Quality: `720p`
- S3 Key: `videos/550e8400-e29b-41d4-a716-446655440000/my_video_720p.mp4`
- Public URL: `https://lam-brk.s3.ap-south-1.amazonaws.com/videos/550e8400-e29b-41d4-a716-446655440000/my_video_720p.mp4`

## Configuration

S3 configuration is done through environment variables:

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (default: `ap-south-1`)
- `AWS_S3_BUCKET`: S3 bucket name (default: `lam-brk`)
- `AWS_S3_BASE_URL`: Base URL for public access (default: `https://lam-brk.s3.ap-south-1.amazonaws.com`)
- `AWS_S3_VIDEOS_PREFIX`: S3 prefix/folder (default: `videos`)

## Methods

### `upload_file()`

Uploads a video file to S3.

**Parameters:**
- `local_file_path` (str): Path to local file
- `video_id` (UUID): Video UUID
- `filename` (str): Original filename
- `quality` (str): Quality level

**Returns:**
- `str`: S3 public URL if successful
- `None`: If upload fails

**Process:**
1. Validates file exists locally
2. Generates S3 key: `videos/{video_id}/{filename}_{quality}.mp4`
3. Uploads with `public-read` ACL
4. Returns public URL

### `delete_file()`

Deletes a file from S3.

**Parameters:**
- `video_id` (UUID): Video UUID
- `filename` (str): Original filename
- `quality` (str): Quality level

**Returns:**
- `bool`: True if successful

### `file_exists()`

Checks if a file exists in S3.

**Parameters:**
- `video_id` (UUID): Video UUID
- `filename` (str): Original filename
- `quality` (str): Quality level

**Returns:**
- `bool`: True if file exists

## Integration with Compression Service

The S3 service is automatically called by the compression service:

1. Video is compressed to local file
2. Compressed file is uploaded to S3
3. S3 URL is stored in database
4. If S3 upload fails, local URL is used as fallback

## Error Handling

- **Missing credentials**: Logs warning, uploads fail gracefully
- **Upload failures**: Falls back to local URLs
- **Network errors**: Retries not implemented (can be added)
- **Permission errors**: Logged and handled gracefully

## Best Practices

1. **Configure credentials**: Set AWS credentials before starting service
2. **Bucket permissions**: Ensure bucket allows public-read for video files
3. **CORS configuration**: Configure CORS if accessing from web browsers
4. **Monitoring**: Monitor S3 upload success rates
5. **Cost optimization**: Consider lifecycle policies for old videos
6. **Backup**: Keep local copies until S3 upload is confirmed

## S3 Bucket Setup

### Required Permissions

The IAM user/role needs:
- `s3:PutObject` - Upload files
- `s3:PutObjectAcl` - Set public-read ACL
- `s3:GetObject` - Read files (for verification)
- `s3:DeleteObject` - Delete files (optional)

### Bucket Policy Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::lam-brk/videos/*"
    }
  ]
}
```

### CORS Configuration

If accessing videos from web browsers:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

## Troubleshooting

### Upload Failures

1. Check AWS credentials are correct
2. Verify bucket exists and is accessible
3. Check IAM permissions
4. Verify network connectivity
5. Check bucket region matches configuration

### Permission Errors

1. Verify IAM user has required permissions
2. Check bucket policy allows operations
3. Ensure ACL can be set (bucket may block ACLs)

### URL Access Issues

1. Verify bucket is configured for public access
2. Check bucket policy allows public reads
3. Verify CORS is configured if needed
4. Check file actually exists in S3

## Future Enhancements

- Multipart uploads for large files
- Upload progress tracking
- Retry mechanism with exponential backoff
- CloudFront CDN integration
- Lifecycle policies for automatic cleanup
- Upload queue management
- Parallel uploads for multiple qualities

