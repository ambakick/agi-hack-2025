"""Service for generating videos using Veo 3.1."""

import logging
import time
import asyncio
from pathlib import Path
from typing import List, Optional
from google import genai
from google.genai import types
from app.models.schemas import SceneDescription, VideoScene, VideoGenerationResponse
from app.core.config import settings
from app.utils.video_utils import ensure_directory, get_output_path

logger = logging.getLogger(__name__)


class VeoService:
    """Service for generating videos using Veo 3.1."""
    
    def __init__(self, api_key: str):
        """Initialize Veo service with API key."""
        try:
            self.client = genai.Client(api_key=api_key)
            self.model_name = "veo-3.1-generate-preview"
            self.output_dir = settings.video_output_dir
            logger.info(f"VeoService initialized with model: {self.model_name}")
            
            # Test API access
            try:
                models = self.client.models.list()
                logger.info(f"API client initialized successfully. Available models: {len(list(models))}")
            except Exception as e:
                logger.warning(f"Could not list models (this may be normal): {str(e)}")
        except Exception as e:
            logger.error(f"Failed to initialize Veo client: {str(e)}")
            raise
    
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
        
        logger.info(f"Operation completed after {time.time() - start_time:.1f}s")
        
        # Check if operation has an error
        if hasattr(operation, 'error') and operation.error:
            logger.error(f"Operation completed with error: {operation.error}")
            raise RuntimeError(f"Video generation failed: {operation.error}")
        
        return operation
    
    def _upload_video_to_genai(self, video_path: str):
        """
        Upload a video file to GenAI and return the file reference.
        
        Args:
            video_path: Path to video file
            
        Returns:
            GenAI file reference
        """
        try:
            uploaded_file = self.client.files.upload(path=video_path)
            logger.info(f"Uploaded video {video_path} to GenAI")
            return uploaded_file
        except Exception as e:
            logger.error(f"Error uploading video to GenAI: {str(e)}")
            raise
    
    def _get_video_file_from_operation(self, operation) -> genai.types.File:
        """
        Get the video file reference from a completed operation.
        
        Args:
            operation: Completed Veo operation
            
        Returns:
            GenAI file reference to the generated video
        """
        try:
            logger.info(f"Operation done: {operation.done}")
            logger.info(f"Operation has response: {hasattr(operation, 'response')}")
            
            if not operation.response:
                logger.error("Operation response is None or missing")
                logger.error(f"Operation error: {operation.error if hasattr(operation, 'error') else 'No error attr'}")
                logger.error(f"Operation metadata: {operation.metadata if hasattr(operation, 'metadata') else 'No metadata'}")
                raise ValueError("Operation response is None")
            
            logger.info(f"Response type: {type(operation.response)}")
            logger.info(f"Response has generated_videos: {hasattr(operation.response, 'generated_videos')}")
            
            if not hasattr(operation.response, 'generated_videos'):
                logger.error(f"Response attributes: {dir(operation.response)}")
                raise ValueError("Operation response does not contain generated_videos")
            
            videos = operation.response.generated_videos
            logger.info(f"Generated videos count: {len(videos) if videos else 0}")
            
            if not videos or len(videos) == 0:
                logger.error("⚠️  VEO API ACCESS REQUIRED ⚠️")
                logger.error("The Veo API completed the operation but returned no videos.")
                logger.error("This typically means:")
                logger.error("1. Your Google Cloud project is not allowlisted for Veo 3.1")
                logger.error("2. Apply for access at: https://ai.google.dev/gemini-api/docs/video-generation")
                logger.error("3. Or check if your API key has Veo permissions enabled")
                raise ValueError("Veo API access required: No generated videos returned. Please apply for Veo 3.1 access at https://ai.google.dev/gemini-api/docs/video-generation")
            
            generated_video = videos[0]
            logger.info(f"Video file retrieved successfully")
            return generated_video.video
            
        except Exception as e:
            logger.error(f"Error getting video file from operation: {str(e)}")
            raise
    
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
            
            # Download the video file (returns bytes)
            logger.info(f"Downloading video from Veo...")
            video_bytes = self.client.files.download(file=generated_video.video)
            
            # Save bytes to output path
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write bytes directly to file
            with open(output_file, 'wb') as f:
                f.write(video_bytes)
            
            logger.info(f"Video saved to {output_path} ({len(video_bytes)} bytes)")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise
    
    async def generate_video(
        self,
        scene: SceneDescription,
        output_filename: str = None,
        previous_video_file: Optional[genai.types.File] = None
    ) -> VideoScene:
        """
        Generate a single video clip from scene description.
        
        Args:
            scene: Scene description with visual prompt
            output_filename: Optional output filename
            previous_video_file: Optional GenAI file reference to previous video to extend from
            
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
            logger.info(f"Prompt length: {len(veo_prompt)} characters")
            logger.info(f"Using model: {self.model_name}")
            
            # Generate video (this is a blocking operation, so we run it in executor)
            loop = asyncio.get_event_loop()
            
            try:
                # If we have a previous video file, extend from it
                if previous_video_file:
                    logger.info(f"Extending from previous video file...")
                    operation = await loop.run_in_executor(
                        None,
                        lambda: self.client.models.generate_videos(
                            model=self.model_name,
                            video=previous_video_file,
                            prompt=veo_prompt,
                        )
                    )
                else:
                    # Generate new video - match notebook exactly (no config)
                    logger.info(f"Calling Veo API to generate new video (no config, matching notebook)...")
                    operation = await loop.run_in_executor(
                        None,
                        lambda: self.client.models.generate_videos(
                            model=self.model_name,
                            prompt=veo_prompt,
                        )
                    )
                    logger.info(f"Veo API call successful, operation created: {operation.name if hasattr(operation, 'name') else 'unknown'}")
            except Exception as api_error:
                logger.error(f"Veo API call failed: {type(api_error).__name__}: {str(api_error)}")
                raise
            
            # Poll for completion
            operation = await loop.run_in_executor(
                None,
                lambda: self._poll_operation(operation)
            )
            
            # Get video file reference from operation (for potential extension)
            video_file = await loop.run_in_executor(
                None,
                lambda: self._get_video_file_from_operation(operation)
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
            
            # Store video file reference for potential extension
            video_scene.video_file = video_file
            
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
        Generate videos for all scenes by extending a single video.
        
        Instead of generating independent videos, this method:
        1. Generates the first video normally
        2. For subsequent scenes, extends the previous video using frame interpolation
        
        Args:
            scenes: List of scene descriptions
            
        Returns:
            VideoGenerationResponse with all generated videos (actually one extended video)
        """
        try:
            if not scenes:
                raise ValueError("No scenes provided")
            
            logger.info(f"Generating extended video from {len(scenes)} scenes...")
            
            # Generate first video normally
            first_scene = scenes[0]
            logger.info(f"Generating initial video for scene {first_scene.scene_number}...")
            first_video = await self.generate_video(first_scene)
            current_video_file = getattr(first_video, 'video_file', None)
            video_scenes = [first_video]
            total_duration = first_video.duration
            
            # For subsequent scenes, extend the video using the previous video file
            for i, scene in enumerate(scenes[1:], start=2):
                logger.info(f"Extending video for scene {scene.scene_number} ({i}/{len(scenes)})...")
                
                if not current_video_file:
                    raise ValueError(f"No video file reference available from previous video for scene {scene.scene_number}")
                
                # Generate extended video using the previous video file reference
                # This extends the video seamlessly using Veo's extension feature
                extended_video = await self.generate_video(
                    scene,
                    previous_video_file=current_video_file,
                    output_filename=f"extended_scene_{scene.scene_number}.mp4"
                )
                
                # The extended video continues from where the previous one left off
                video_scenes.append(extended_video)
                total_duration += extended_video.duration
                
                # Update current video file reference for next iteration
                current_video_file = getattr(extended_video, 'video_file', None)
            
            # When extending videos, the final video contains all previous content
            # So we only return the final extended video to avoid duplication
            if len(video_scenes) > 1:
                logger.info(f"Extended video created with {len(scenes)} scenes. Using final extended video only.")
                final_video = video_scenes[-1]
                # Update the scene number to reflect it's the complete video
                final_video.scene_number = 1
                return VideoGenerationResponse(
                    video_scenes=[final_video],
                    total_duration=total_duration
                )
            else:
                logger.info(f"Generated video with duration: {total_duration}s")
                return VideoGenerationResponse(
                    video_scenes=video_scenes,
                    total_duration=total_duration
                )
            
        except Exception as e:
            logger.error(f"Error generating videos: {str(e)}")
            raise

