"""Service for generating videos using Veo 3.1."""

import logging
import time
import asyncio
from pathlib import Path
from typing import List
from google import genai
from app.models.schemas import SceneDescription, VideoScene, VideoGenerationResponse
from app.core.config import settings
from app.utils.video_utils import ensure_directory, get_output_path

logger = logging.getLogger(__name__)


class VeoService:
    """Service for generating videos using Veo 3.1."""
    
    def __init__(self, api_key: str):
        """Initialize Veo service with API key."""
        self.client = genai.Client(api_key=api_key)
        self.model_name = "veo-3.1-generate-preview"
        self.output_dir = settings.video_output_dir
    
    def _poll_operation(self, operation, max_wait_time: int = 600) -> genai.types.Operation:
        """
        Poll operation until complete.
        
        Args:
            operation: Veo operation object
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            Completed operation
        """
        start_time = time.time()
        poll_interval = 10  # seconds
        
        while not operation.done:
            elapsed = time.time() - start_time
            if elapsed > max_wait_time:
                raise TimeoutError(f"Video generation timed out after {max_wait_time} seconds")
            
            logger.info(f"Waiting for video generation... ({elapsed:.0f}s elapsed)")
            time.sleep(poll_interval)
            operation = self.client.operations.get(operation)
        
        return operation
    
    def _download_video(self, operation, output_path: str) -> str:
        """
        Download generated video from operation.
        
        Args:
            operation: Completed Veo operation
            output_path: Path to save video
            
        Returns:
            Path to downloaded video
        """
        try:
            if not operation.response or not hasattr(operation.response, 'generated_videos'):
                raise ValueError("Operation response does not contain generated_videos")
            
            if not operation.response.generated_videos:
                raise ValueError("No generated videos found in response")
            
            generated_video = operation.response.generated_videos[0]
            
            # Download the video file
            video_file = self.client.files.download(file=generated_video.video)
            
            # Save to output path
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            video_file.save(str(output_file))
            
            logger.info(f"Video saved to {output_path}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise
    
    async def generate_video(
        self,
        scene: SceneDescription,
        output_filename: str = None
    ) -> VideoScene:
        """
        Generate a single video clip from scene description.
        
        Args:
            scene: Scene description with visual prompt
            output_filename: Optional output filename
            
        Returns:
            VideoScene with file path and metadata
        """
        try:
            if output_filename is None:
                output_filename = f"scene_{scene.scene_number}.mp4"
            
            output_path = get_output_path(self.output_dir, output_filename)
            
            # Create Veo prompt with constraints
            veo_prompt = f"""
You are generating a short-form video clip to accompany an EXISTING audio track.

CRITICAL AUDIO CONSTRAINT (MUST FOLLOW):
- The audio for this video is PRE-RECORDED and comes DIRECTLY from the provided transcript.
- Do NOT generate any audio, vocals, speech, singing, rapping, narration, or sound effects.
- The video MUST be SILENT by itself.
- The transcript is NOT dialogue to be acted out — it is a fixed voiceover.

TRANSCRIPT (audio reference only; do not reinterpret):
\"\"\"{scene.transcript_text}\"\"\"

PRIMARY TASK:
Generate visuals that SHOW the SITUATION, actions, or scenario being described in the transcript, as if the viewer is watching what the speaker is talking about.

HARD CONSTRAINTS:
- Maximum duration: {scene.duration} seconds.
- No visible people speaking, singing, or facing the camera.
- No lip movement of any kind.
- No musical performance, rapping, or rhythmic vocalization.
- No on-screen text, subtitles, captions, or lyrics.
- No podcast studios, microphones, or interview setups.

VISUAL PROMPT:
{scene.visual_prompt}

VISUAL GUIDELINES:
- Translate spoken ideas into concrete visual scenes (environments, motion, events, symbolic actions).
- People may appear ONLY as background actors or performing actions, never speaking.
- Camera movement should feel cinematic and intentional.
- Maintain a consistent visual style and continuity.

STYLE & PACING:
- Designed for short-form social media (YouTube Shorts).
- Visually engaging within the first 2 seconds.
- Clear visual progression from start to finish.

OUTPUT REQUIREMENT:
- One continuous, silent video clip.
- The video must align temporally with the transcript audio when the audio is added externally.
"""
            
            logger.info(f"Generating video for scene {scene.scene_number}...")
            
            # Generate video (this is a blocking operation, so we run it in executor)
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_videos(
                    model=self.model_name,
                    prompt=veo_prompt,
                )
            )
            
            # Poll for completion
            operation = await loop.run_in_executor(
                None,
                lambda: self._poll_operation(operation)
            )
            
            # Download video
            video_path = await loop.run_in_executor(
                None,
                lambda: self._download_video(operation, output_path)
            )
            
            # Get actual video duration (we'll use the expected duration for now)
            video_scene = VideoScene(
                scene_number=scene.scene_number,
                file_path=video_path,
                duration=scene.duration,
                transcript_text=scene.transcript_text
            )
            
            logger.info(f"Video generated for scene {scene.scene_number}: {video_path}")
            return video_scene
            
        except Exception as e:
            logger.error(f"Error generating video for scene {scene.scene_number}: {str(e)}")
            raise
    
    async def generate_videos(
        self,
        scenes: List[SceneDescription]
    ) -> VideoGenerationResponse:
        """
        Generate videos for all scenes.
        
        Args:
            scenes: List of scene descriptions
            
        Returns:
            VideoGenerationResponse with all generated videos
        """
        try:
            logger.info(f"Generating {len(scenes)} video clips...")
            
            # Generate videos sequentially (Veo API may have rate limits)
            video_scenes = []
            for scene in scenes:
                video_scene = await self.generate_video(scene)
                video_scenes.append(video_scene)
            
            total_duration = sum(vs.duration for vs in video_scenes)
            
            logger.info(f"Generated {len(video_scenes)} video clips, total duration: {total_duration}s")
            return VideoGenerationResponse(
                video_scenes=video_scenes,
                total_duration=total_duration
            )
            
        except Exception as e:
            logger.error(f"Error generating videos: {str(e)}")
            raise

