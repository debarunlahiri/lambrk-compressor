-- Add additional video metadata fields to video_qualities table
-- For comprehensive video information storage

ALTER TABLE video_qualities 
ADD COLUMN IF NOT EXISTS fps DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS pixel_format VARCHAR(20),
ADD COLUMN IF NOT EXISTS color_space VARCHAR(20),
ADD COLUMN IF NOT EXISTS color_range VARCHAR(20),
ADD COLUMN IF NOT EXISTS audio_codec VARCHAR(50),
ADD COLUMN IF NOT EXISTS audio_bitrate INTEGER,
ADD COLUMN IF NOT EXISTS audio_sample_rate INTEGER,
ADD COLUMN IF NOT EXISTS audio_channels INTEGER,
ADD COLUMN IF NOT EXISTS aspect_ratio VARCHAR(20),
ADD COLUMN IF NOT EXISTS frame_count BIGINT,
ADD COLUMN IF NOT EXISTS encoding_time INTEGER,
ADD COLUMN IF NOT EXISTS processing_started_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS processing_completed_at TIMESTAMP;

-- Add index for processing times
CREATE INDEX IF NOT EXISTS idx_video_qualities_processing_times 
ON video_qualities(processing_started_at, processing_completed_at);

