import subprocess
import json
import os
import platform
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def is_apple_silicon() -> bool:
    """Check if running on Apple Silicon (M1/M2/M3)."""
    return platform.system() == 'Darwin' and platform.machine() == 'arm64'


def get_hardware_encoder() -> Tuple[str, str]:
    """Get the best hardware encoder for the current platform."""
    if is_apple_silicon():
        return 'h264_videotoolbox', 'videotoolbox'
    return 'libx264', 'software'


def get_video_info(video_path: str) -> Optional[Dict]:
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        data = json.loads(result.stdout)
        
        video_stream = None
        audio_stream = None
        
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video' and not video_stream:
                video_stream = stream
            elif stream.get('codec_type') == 'audio' and not audio_stream:
                audio_stream = stream
        
        if not video_stream:
            return None
        
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        duration = float(data.get('format', {}).get('duration', 0))
        bitrate = int(data.get('format', {}).get('bit_rate', 0))
        codec = video_stream.get('codec_name', '')
        container = os.path.splitext(video_path)[1].lstrip('.')
        
        fps_str = video_stream.get('r_frame_rate', '0/1')
        if '/' in fps_str:
            num, den = map(int, fps_str.split('/'))
            fps = num / den if den > 0 else 0
        else:
            fps = float(fps_str) if fps_str else 0
        
        pixel_format = video_stream.get('pix_fmt', '')
        color_space = video_stream.get('color_space', '')
        color_range = video_stream.get('color_range', '')
        
        aspect_ratio_str = video_stream.get('display_aspect_ratio', '')
        if not aspect_ratio_str or aspect_ratio_str == '0:1':
            aspect_ratio = f"{width}:{height}"
        else:
            aspect_ratio = aspect_ratio_str
        
        nb_frames = video_stream.get('nb_frames')
        if nb_frames:
            frame_count = int(nb_frames)
        elif fps > 0 and duration > 0:
            frame_count = int(fps * duration)
        else:
            frame_count = None
        
        audio_codec = None
        audio_bitrate = None
        audio_sample_rate = None
        audio_channels = None
        
        if audio_stream:
            audio_codec = audio_stream.get('codec_name', '')
            audio_bitrate_str = audio_stream.get('bit_rate')
            if audio_bitrate_str:
                audio_bitrate = int(audio_bitrate_str) // 1000
            audio_sample_rate = audio_stream.get('sample_rate')
            if audio_sample_rate:
                audio_sample_rate = int(audio_sample_rate)
            audio_channels = audio_stream.get('channels')
            if audio_channels:
                audio_channels = int(audio_channels)
        
        return {
            'width': width,
            'height': height,
            'duration': int(duration),
            'bitrate': bitrate // 1000 if bitrate else None,
            'codec': codec,
            'container': container,
            'file_size': os.path.getsize(video_path),
            'fps': round(fps, 2) if fps > 0 else None,
            'pixel_format': pixel_format,
            'color_space': color_space,
            'color_range': color_range,
            'aspect_ratio': aspect_ratio,
            'frame_count': frame_count,
            'audio_codec': audio_codec,
            'audio_bitrate': audio_bitrate,
            'audio_sample_rate': audio_sample_rate,
            'audio_channels': audio_channels
        }
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return None


QUALITY_CONFIGS = {
    '144p': {
        'height': 144,
        'bitrate': '200k',
        'maxrate': '300k',
        'bufsize': '400k'
    },
    '240p': {
        'height': 240,
        'bitrate': '400k',
        'maxrate': '600k',
        'bufsize': '800k'
    },
    '360p': {
        'height': 360,
        'bitrate': '800k',
        'maxrate': '1200k',
        'bufsize': '1600k'
    },
    '480p': {
        'height': 480,
        'bitrate': '1500k',
        'maxrate': '2250k',
        'bufsize': '3000k'
    },
    '720p': {
        'height': 720,
        'bitrate': '3000k',
        'maxrate': '4500k',
        'bufsize': '6000k'
    },
    '1080p': {
        'height': 1080,
        'bitrate': '6000k',
        'maxrate': '9000k',
        'bufsize': '12000k'
    },
    '1440p': {
        'height': 1440,
        'bitrate': '12000k',
        'maxrate': '18000k',
        'bufsize': '24000k'
    },
    '2160p': {
        'height': 2160,
        'bitrate': '25000k',
        'maxrate': '37500k',
        'bufsize': '50000k'
    }
}


def get_quality_config(quality: str) -> Optional[Dict]:
    return QUALITY_CONFIGS.get(quality)


def get_supported_qualities(original_height: int, original_width: int) -> list:
    """
    Get supported qualities up to the original video resolution.
    Only creates qualities that are equal to or lower than the original.
    Maintains aspect ratio and orientation.
    """
    supported = []
    # Determine the maximum quality based on original resolution
    max_quality_height = min(original_height, 2160)  # Cap at 4K max
    
    # Quality order from lowest to highest
    quality_order = ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p']
    
    for quality in quality_order:
        config = QUALITY_CONFIGS[quality]
        # Only add qualities that are <= original resolution
        if config['height'] <= original_height:
            supported.append(quality)
    
    return supported


def calculate_resolution(width: int, height: int, target_height: int) -> Tuple[int, int]:
    """
    Calculate resolution maintaining aspect ratio and orientation.
    Never upscales - if original is smaller, returns original dimensions.
    Ensures dimensions are even numbers (required by most codecs).
    """
    # Never upscale - if target is larger than original, use original
    if target_height >= height:
        # Ensure even dimensions
        final_width = width if width % 2 == 0 else width + 1
        final_height = height if height % 2 == 0 else height + 1
        return final_width, final_height
    
    # Calculate new dimensions maintaining aspect ratio
    aspect_ratio = width / height
    new_height = target_height
    new_width = int(new_height * aspect_ratio)
    
    # Ensure dimensions are even (required by H.264 and most codecs)
    if new_width % 2 != 0:
        new_width += 1
    if new_height % 2 != 0:
        new_height += 1
    
    return new_width, new_height

