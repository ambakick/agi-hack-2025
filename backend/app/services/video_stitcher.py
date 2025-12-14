"""Service for stitching video clips together."""

import logging
from pathlib import Path
from typing import List

# MoviePy API differs across major versions:
# - MoviePy 1.x: clip.resize(...), clip.crop(...)
# - MoviePy 2.x: clip.resized(...), clip.cropped(...)
# Imports also differ depending on install.
try:
    # MoviePy 1.x common import path
    from moviepy.editor import VideoFileClip, concatenate_videoclips  # type: ignore
except Exception:  # pragma: no cover
    from moviepy import VideoFileClip, concatenate_videoclips  # type: ignore

from app.models.schemas import VideoStitchRequest, VideoStitchResponse
from app.core.config import settings
from app.utils.video_utils import ensure_directory, get_output_path

logger = logging.getLogger(__name__)

def _resize_clip(clip, **kwargs):
    """Version-tolerant resize helper for MoviePy."""
    if hasattr(clip, "resize"):
        return clip.resize(**kwargs)
    if hasattr(clip, "resized"):
        return clip.resized(**kwargs)
    raise AttributeError("MoviePy clip has neither resize() nor resized()")

def _crop_clip(clip, **kwargs):
    """Version-tolerant crop helper for MoviePy."""
    if hasattr(clip, "crop"):
        return clip.crop(**kwargs)
    if hasattr(clip, "cropped"):
        return clip.cropped(**kwargs)
    raise AttributeError("MoviePy clip has neither crop() nor cropped()")


class VideoStitcher:
    """Service for stitching video clips together."""
    
    def __init__(self):
        """Initialize video stitcher."""
        self.output_dir = settings.video_output_dir
    
    async def stitch_videos(
        self,
        video_paths: List[str],
        output_path: str = None
    ) -> VideoStitchResponse:
        """
        Stitch multiple video clips into a single video.
        
        Args:
            video_paths: List of paths to video files
            output_path: Optional output path (auto-generated if not provided)
            
        Returns:
            VideoStitchResponse with stitched video path
        """
        try:
            if not video_paths:
                raise ValueError("No video paths provided")
            
            if output_path is None:
                output_path = get_output_path(self.output_dir, "stitched_video.mp4")
            
            logger.info(f"Stitching {len(video_paths)} video clips...")
            
            # Load all video clips
            clips = []
            for i, video_path in enumerate(video_paths):
                if not Path(video_path).exists():
                    raise FileNotFoundError(f"Video file not found: {video_path}")
                
                logger.debug(f"Loading clip {i+1}/{len(video_paths)}: {video_path}")
                clip = VideoFileClip(video_path)
                
                # Resize to ensure consistent dimensions (9:16 aspect ratio)
                # Target: 1080x1920 for vertical format
                target_width = 1080
                target_height = 1920
                
                if clip.w != target_width or clip.h != target_height:
                    # Resize maintaining aspect ratio, then crop to exact size
                    clip = _resize_clip(clip, height=target_height)
                    if clip.w != target_width:
                        # Crop horizontally to center
                        x_center = clip.w / 2
                        clip = _crop_clip(clip, x_center=x_center, width=target_width)
                
                clips.append(clip)
            
            # Concatenate clips
            logger.info("Concatenating video clips...")
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Write output file
            logger.info(f"Writing stitched video to {output_path}...")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4
            )
            
            # Get actual duration
            duration = final_clip.duration
            
            # Clean up
            final_clip.close()
            for clip in clips:
                clip.close()
            
            logger.info(f"Stitched video saved: {output_path} (duration: {duration}s)")
            
            return VideoStitchResponse(
                stitched_video_path=output_path,
                duration=duration
            )
            
        except Exception as e:
            logger.error(f"Error stitching videos: {str(e)}")
            raise

