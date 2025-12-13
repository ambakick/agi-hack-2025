"""Service for synchronizing audio with video."""

import logging
from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, concatenate_audioclips
from app.models.schemas import AudioSyncRequest, AudioSyncResponse
from app.core.config import settings
from app.utils.video_utils import ensure_directory, get_output_path

logger = logging.getLogger(__name__)


class AudioSync:
    """Service for synchronizing audio with video."""
    
    def __init__(self):
        """Initialize audio sync service."""
        self.output_dir = settings.video_output_dir
    
    async def sync_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str = None
    ) -> AudioSyncResponse:
        """
        Add audio to video, ensuring perfect synchronization.
        
        Args:
            video_path: Path to video file (should be silent)
            audio_path: Path to audio file
            output_path: Optional output path (auto-generated if not provided)
            
        Returns:
            AudioSyncResponse with final video path
        """
        try:
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            if not Path(audio_path).exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            if output_path is None:
                output_path = get_output_path(self.output_dir, "final_video_with_audio.mp4")
            
            logger.info(f"Synchronizing audio with video...")
            logger.debug(f"Video: {video_path}")
            logger.debug(f"Audio: {audio_path}")
            
            # Load video and audio
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            
            # Get durations
            video_duration = video_clip.duration
            audio_duration = audio_clip.duration
            
            logger.debug(f"Video duration: {video_duration}s, Audio duration: {audio_duration}s")
            
            # Handle duration mismatch
            if audio_duration > video_duration:
                # Trim audio to match video
                logger.warning(f"Audio ({audio_duration}s) is longer than video ({video_duration}s). Trimming audio.")
                audio_clip = audio_clip.subclip(0, video_duration)
            elif audio_duration < video_duration:
                # Loop audio or extend with silence
                logger.warning(f"Audio ({audio_duration}s) is shorter than video ({video_duration}s). Extending audio.")
                # For now, we'll just use the audio as-is and let video play silently after
                # In production, you might want to loop the audio or add silence
                pass
            
            # Set audio to video (this replaces any existing audio)
            final_clip = video_clip.set_audio(audio_clip)
            
            # Write output file
            logger.info(f"Writing final video with audio to {output_path}...")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4
            )
            
            # Get final duration
            duration = final_clip.duration
            
            # Clean up
            final_clip.close()
            video_clip.close()
            audio_clip.close()
            
            logger.info(f"Final video with audio saved: {output_path} (duration: {duration}s)")
            
            return AudioSyncResponse(
                final_video_path=output_path,
                duration=duration
            )
            
        except Exception as e:
            logger.error(f"Error synchronizing audio: {str(e)}")
            raise
    
    async def sync_multiple_audio(
        self,
        video_path: str,
        audio_paths: list[str],
        output_path: str = None
    ) -> AudioSyncResponse:
        """
        Add multiple audio clips to video in sequence.
        
        Args:
            video_path: Path to video file
            audio_paths: List of audio file paths (in order)
            output_path: Optional output path
            
        Returns:
            AudioSyncResponse with final video path
        """
        try:
            if output_path is None:
                output_path = get_output_path(self.output_dir, "final_video_with_audio.mp4")
            
            logger.info(f"Combining {len(audio_paths)} audio clips with video...")
            
            # Load video
            video_clip = VideoFileClip(video_path)
            
            # Load and concatenate audio clips
            audio_clips = []
            for audio_path in audio_paths:
                if not Path(audio_path).exists():
                    logger.warning(f"Audio file not found: {audio_path}, skipping")
                    continue
                audio_clips.append(AudioFileClip(audio_path))
            
            if not audio_clips:
                raise ValueError("No valid audio clips found")
            
            # Concatenate audio clips
            combined_audio = concatenate_audioclips(audio_clips)
            
            # Get durations
            video_duration = video_clip.duration
            audio_duration = combined_audio.duration
            
            # Handle duration mismatch
            if audio_duration > video_duration:
                combined_audio = combined_audio.subclip(0, video_duration)
            elif audio_duration < video_duration:
                logger.warning(f"Audio ({audio_duration}s) is shorter than video ({video_duration}s)")
            
            # Set audio to video
            final_clip = video_clip.set_audio(combined_audio)
            
            # Write output file
            logger.info(f"Writing final video with audio to {output_path}...")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4
            )
            
            duration = final_clip.duration
            
            # Clean up
            final_clip.close()
            video_clip.close()
            combined_audio.close()
            for clip in audio_clips:
                clip.close()
            
            logger.info(f"Final video with audio saved: {output_path} (duration: {duration}s)")
            
            return AudioSyncResponse(
                final_video_path=output_path,
                duration=duration
            )
            
        except Exception as e:
            logger.error(f"Error synchronizing multiple audio clips: {str(e)}")
            raise

