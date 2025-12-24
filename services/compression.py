import subprocess
import os
import logging
from typing import Optional, List, Dict
from uuid import UUID
import shutil
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.config import settings
from services.database import DatabaseService
from utils.video_utils import (
    get_video_info, 
    get_quality_config, 
    get_supported_qualities,
    calculate_resolution,
    get_hardware_encoder
)

logger = logging.getLogger(__name__)


class CompressionService:
    
    @staticmethod
    def compress_video(input_path: str, output_path: str, quality: str, 
                      width: int, height: int, start_time: Optional[datetime] = None) -> Optional[Dict]:
        config = get_quality_config(quality)
        if not config:
            logger.error(f"Unsupported quality: {quality}")
            return None
        
        target_width, target_height = calculate_resolution(width, height, config['height'])
        
        # Check if this is original quality (dimensions match)
        is_original_quality = (target_width == width and target_height == height) or quality == 'original'
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        encoder, encoder_type = get_hardware_encoder()
        
        # Build scale filter that maintains aspect ratio and orientation
        # Only scale if dimensions are different
        if target_width == width and target_height == height:
            # No scaling needed - maintain original dimensions
            scale_filter = None
        else:
            # Scale maintaining aspect ratio - never upscale
            # This preserves portrait/landscape orientation
            scale_filter = f'scale={target_width}:{target_height}'
        
        if encoder_type == 'videotoolbox':
            cmd = ['ffmpeg', '-hwaccel', 'videotoolbox', '-i', input_path]
            
            if is_original_quality:
                # Higher quality settings for original quality
                adaptive_bitrate = max(int(width * height * 0.15), 5000)  # Minimum 5Mbps
                cmd.extend([
                    '-c:v', encoder,
                    '-b:v', f'{adaptive_bitrate}k',
                    '-maxrate', f'{int(adaptive_bitrate * 1.5)}k',
                    '-bufsize', f'{int(adaptive_bitrate * 2)}k',
                    '-c:a', 'aac',
                    '-b:a', '192k'
                ])
            else:
                cmd.extend([
                    '-c:v', encoder,
                    '-b:v', config['bitrate'],
                    '-maxrate', config['maxrate'],
                    '-bufsize', config['bufsize'],
                    '-c:a', 'aac',
                    '-b:a', '128k'
                ])
            
            if scale_filter:
                cmd.extend(['-vf', scale_filter])
            
            cmd.extend(['-allow_sw', '1', '-movflags', '+faststart', '-y', output_path])
        else:
            cmd = ['ffmpeg', '-i', input_path]
            
            if is_original_quality:
                # Higher quality settings for original quality
                cmd.extend([
                    '-c:v', encoder,
                    '-preset', 'slow',
                    '-crf', '18',  # Higher quality (lower CRF = better)
                    '-c:a', 'aac',
                    '-b:a', '192k'
                ])
            else:
                cmd.extend([
                    '-c:v', encoder,
                    '-preset', 'fast',
                    '-crf', '23',
                    '-b:v', config['bitrate'],
                    '-maxrate', config['maxrate'],
                    '-bufsize', config['bufsize'],
                    '-c:a', 'aac',
                    '-b:a', '128k'
                ])
            
            if scale_filter:
                cmd.extend(['-vf', scale_filter])
            
            cmd.extend(['-movflags', '+faststart', '-threads', '0', '-y', output_path])
        
        encoding_start = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            encoding_time = int(time.time() - encoding_start)
            
            if os.path.exists(output_path):
                info = get_video_info(output_path)
                return {
                    'success': True,
                    'output_path': output_path,
                    'width': target_width,
                    'height': target_height,
                    'file_size': os.path.getsize(output_path),
                    'bitrate': info.get('bitrate') if info else None,
                    'codec': 'h264',
                    'container': 'mp4',
                    'fps': info.get('fps') if info else None,
                    'pixel_format': info.get('pixel_format') if info else None,
                    'color_space': info.get('color_space') if info else None,
                    'color_range': info.get('color_range') if info else None,
                    'aspect_ratio': info.get('aspect_ratio') if info else None,
                    'frame_count': info.get('frame_count') if info else None,
                    'audio_codec': info.get('audio_codec') if info else None,
                    'audio_bitrate': info.get('audio_bitrate') if info else None,
                    'audio_sample_rate': info.get('audio_sample_rate') if info else None,
                    'audio_channels': info.get('audio_channels') if info else None,
                    'encoding_time': encoding_time
                }
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error for {quality}: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Error compressing video to {quality}: {e}")
            return None
    
    @staticmethod
    def process_video_qualities(video_id: UUID, input_path: str, 
                                video_url_base: str) -> Dict:
        video_info = get_video_info(input_path)
        if not video_info:
            logger.error(f"Could not get video info for {input_path}")
            return {'success': False, 'error': 'Could not read video file'}
        
        original_width = video_info['width']
        original_height = video_info['height']
        supported_qualities = get_supported_qualities(original_height, original_width)
        
        video = DatabaseService.get_video_by_id(video_id)
        if not video:
            return {'success': False, 'error': 'Video not found'}
        
        input_filename = os.path.basename(input_path)
        base_name = os.path.splitext(input_filename)[0]
        
        results = []
        
        processing_start = datetime.now()
        
        for quality in supported_qualities:
            output_filename = f"{base_name}_{quality}.mp4"
            output_path = os.path.join(settings.COMPLETED_DIR, str(video_id), output_filename)
            
            video_quality_url = f"{video_url_base}/{str(video_id)}/{output_filename}"
            
            quality_record = DatabaseService.create_video_quality(
                video_id=video_id,
                quality=quality,
                url=video_quality_url,
                status='processing',
                processing_started_at=processing_start
            )
            
            if not quality_record:
                logger.error(f"Failed to create quality record for {quality}")
                continue
            
            compression_result = CompressionService.compress_video(
                input_path=input_path,
                output_path=output_path,
                quality=quality,
                width=original_width,
                height=original_height,
                start_time=processing_start
            )
            
            if compression_result and compression_result.get('success'):
                DatabaseService.update_video_quality(
                    quality_id=quality_record.id,
                    file_size=compression_result['file_size'],
                    bitrate=compression_result['bitrate'],
                    resolution_width=compression_result['width'],
                    resolution_height=compression_result['height'],
                    codec=compression_result['codec'],
                    container=compression_result['container'],
                    duration=video_info.get('duration'),
                    status='ready',
                    fps=compression_result.get('fps'),
                    pixel_format=compression_result.get('pixel_format'),
                    color_space=compression_result.get('color_space'),
                    color_range=compression_result.get('color_range'),
                    audio_codec=compression_result.get('audio_codec'),
                    audio_bitrate=compression_result.get('audio_bitrate'),
                    audio_sample_rate=compression_result.get('audio_sample_rate'),
                    audio_channels=compression_result.get('audio_channels'),
                    aspect_ratio=compression_result.get('aspect_ratio'),
                    frame_count=compression_result.get('frame_count'),
                    encoding_time=compression_result.get('encoding_time'),
                    processing_completed_at=datetime.now()
                )
                results.append({
                    'quality': quality,
                    'status': 'ready',
                    'file_size': compression_result['file_size']
                })
            else:
                DatabaseService.update_video_quality_status(
                    quality_id=quality_record.id,
                    status='failed'
                )
                results.append({
                    'quality': quality,
                    'status': 'failed'
                })
        
        ready_qualities = [r for r in results if r.get('status') == 'ready']
        if ready_qualities:
            preferred_defaults = ['720p', '1080p', '480p', '360p']
            default_quality_name = None
            for pref in preferred_defaults:
                if pref in supported_qualities:
                    default_quality_name = pref
                    break
            if not default_quality_name and supported_qualities:
                default_quality_name = supported_qualities[0]
            
            if default_quality_name:
                default_qualities = DatabaseService.get_video_qualities(video_id)
                for vq in default_qualities:
                    if vq.quality == default_quality_name and vq.status == 'ready':
                        DatabaseService.set_default_quality(video_id, vq.id)
                        break
        
        all_failed = all(r.get('status') == 'failed' for r in results)
        if all_failed:
            DatabaseService.update_video_status(video_id, 'draft')
            return {'success': False, 'error': 'All compressions failed', 'results': results}
        else:
            DatabaseService.update_video_status(video_id, 'published')
            return {'success': True, 'results': results}
    
    @staticmethod
    def process_pending_video(video_id: UUID, filename: str, video_url_base: str) -> Dict:
        input_path = os.path.join(settings.PENDING_DIR, filename)
        
        if not os.path.exists(input_path):
            return {'success': False, 'error': f'Video file not found: {input_path}'}
        
        try:
            result = CompressionService.process_video_qualities(
                video_id=video_id,
                input_path=input_path,
                video_url_base=video_url_base
            )
            
            if result.get('success'):
                completed_dir = os.path.join(settings.COMPLETED_DIR, str(video_id))
                os.makedirs(completed_dir, exist_ok=True)
                original_output = os.path.join(completed_dir, filename)
                
                if not os.path.exists(original_output):
                    shutil.copy2(input_path, original_output)
                
                original_info = get_video_info(original_output)
                if original_info:
                    original_quality = DatabaseService.create_video_quality(
                        video_id=video_id,
                        quality='original',
                        url=f"{video_url_base}/{str(video_id)}/{filename}",
                        file_size=original_info.get('file_size'),
                        bitrate=original_info.get('bitrate'),
                        resolution_width=original_info.get('width'),
                        resolution_height=original_info.get('height'),
                        codec=original_info.get('codec'),
                        container=original_info.get('container'),
                        duration=original_info.get('duration'),
                        status='ready',
                        processing_started_at=datetime.now()
                    )
                    if original_quality:
                        DatabaseService.update_video_quality(
                            quality_id=original_quality.id,
                            fps=original_info.get('fps'),
                            pixel_format=original_info.get('pixel_format'),
                            color_space=original_info.get('color_space'),
                            color_range=original_info.get('color_range'),
                            audio_codec=original_info.get('audio_codec'),
                            audio_bitrate=original_info.get('audio_bitrate'),
                            audio_sample_rate=original_info.get('audio_sample_rate'),
                            audio_channels=original_info.get('audio_channels'),
                            aspect_ratio=original_info.get('aspect_ratio'),
                            frame_count=original_info.get('frame_count'),
                            processing_completed_at=datetime.now()
                        )
            
            return result
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")
            DatabaseService.update_video_status(video_id, 'draft')
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def process_batch(video_tasks: List[Dict], max_workers: int = 4) -> Dict:
        """
        Process multiple videos in parallel using batch processing.
        
        Args:
            video_tasks: List of dicts with keys: video_id, filename, video_url_base
            max_workers: Maximum number of parallel workers (default: 4)
        
        Returns:
            Dict with success count, failed count, and results
        """
        results = {
            'total': len(video_tasks),
            'success': 0,
            'failed': 0,
            'results': []
        }
        
        def process_single(task):
            try:
                result = CompressionService.process_pending_video(
                    video_id=task['video_id'],
                    filename=task['filename'],
                    video_url_base=task.get('video_url_base', 'https://example.com/videos')
                )
                return {
                    'video_id': str(task['video_id']),
                    'filename': task['filename'],
                    'success': result.get('success', False),
                    'error': result.get('error'),
                    'qualities': result.get('results', [])
                }
            except Exception as e:
                logger.error(f"Error processing {task['filename']}: {e}")
                return {
                    'video_id': str(task['video_id']),
                    'filename': task['filename'],
                    'success': False,
                    'error': str(e),
                    'qualities': []
                }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {
                executor.submit(process_single, task): task 
                for task in video_tasks
            }
            
            for future in as_completed(future_to_task):
                result = future.result()
                results['results'].append(result)
                if result['success']:
                    results['success'] += 1
                else:
                    results['failed'] += 1
        
        return results

