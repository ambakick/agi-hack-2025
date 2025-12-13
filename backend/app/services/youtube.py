"""YouTube service for searching videos and retrieving transcripts."""
import logging
from typing import List, Optional
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from app.models.schemas import VideoInfo, VideoTranscript

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for interacting with YouTube API and transcripts."""
    
    def __init__(self, api_key: str):
        """Initialize YouTube service with API key."""
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    async def search_podcasts(
        self,
        query: str,
        max_results: int = 10,
        language: str = "en"
    ) -> List[VideoInfo]:
        """
        Search for podcast episodes on YouTube.
        
        Args:
            query: Search query/topic
            max_results: Maximum number of results to return
            language: Language code (default: en)
            
        Returns:
            List of VideoInfo objects
        """
        try:
            # Search for videos with podcast-related keywords
            search_query = f"{query} podcast"
            
            search_response = self.youtube.search().list(
                q=search_query,
                part='id,snippet',
                type='video',
                maxResults=max_results,
                relevanceLanguage=language,
                videoCaption='closedCaption',  # Only videos with captions
                videoDuration='medium',  # 4-20 minutes
                order='relevance'
            ).execute()
            
            videos = []
            video_ids = []
            
            # Collect video IDs for detailed info
            for item in search_response.get('items', []):
                video_ids.append(item['id']['videoId'])
            
            if not video_ids:
                return []
            
            # Get detailed video information
            videos_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()
            
            for item in videos_response.get('items', []):
                video_info = VideoInfo(
                    video_id=item['id'],
                    title=item['snippet']['title'],
                    channel_name=item['snippet']['channelTitle'],
                    thumbnail_url=item['snippet']['thumbnails']['high']['url'],
                    duration=item['contentDetails']['duration'],
                    view_count=int(item['statistics'].get('viewCount', 0)),
                    published_at=item['snippet']['publishedAt'],
                    description=item['snippet']['description'][:500]  # Truncate
                )
                videos.append(video_info)
            
            logger.info(f"Found {len(videos)} videos for query: {query}")
            return videos
            
        except Exception as e:
            logger.error(f"Error searching YouTube: {str(e)}")
            raise
    
    async def get_transcript(
        self,
        video_id: str,
        languages: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Fetch transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            languages: Preferred language codes (default: ['en'])
            
        Returns:
            Transcript text or None if not available
        """
        if languages is None:
            languages = ['en']
        
        try:
            # Fetch transcript using the correct API for v1.2.3+
            transcript_list = YouTubeTranscriptApi().get_transcript(
                video_id,
                languages=languages
            )
            
            # Combine all transcript segments
            transcript_text = ' '.join([item['text'] for item in transcript_list])
            
            logger.info(f"Retrieved transcript for video {video_id}")
            return transcript_text
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.warning(f"No transcript available for video {video_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching transcript for {video_id}: {str(e)}")
            return None
    
    async def get_transcripts_batch(
        self,
        video_ids: List[str],
        languages: Optional[List[str]] = None
    ) -> List[VideoTranscript]:
        """
        Fetch transcripts for multiple videos.
        
        Args:
            video_ids: List of YouTube video IDs
            languages: Preferred language codes
            
        Returns:
            List of VideoTranscript objects
        """
        transcripts = []
        
        # Get video details first
        try:
            videos_response = self.youtube.videos().list(
                part='snippet,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            video_details = {
                item['id']: {
                    'title': item['snippet']['title'],
                    'duration': item['contentDetails']['duration']
                }
                for item in videos_response.get('items', [])
            }
        except Exception as e:
            logger.error(f"Error fetching video details: {str(e)}")
            video_details = {}
        
        # Fetch transcripts for each video
        for video_id in video_ids:
            transcript_text = await self.get_transcript(video_id, languages)
            
            if transcript_text:
                # Parse duration to seconds (simplified)
                duration_seconds = 600.0  # Default 10 minutes
                
                video_transcript = VideoTranscript(
                    video_id=video_id,
                    title=video_details.get(video_id, {}).get('title', f'Video {video_id}'),
                    transcript=transcript_text,
                    language=languages[0] if languages else 'en',
                    duration_seconds=duration_seconds
                )
                transcripts.append(video_transcript)
        
        logger.info(f"Retrieved {len(transcripts)} transcripts out of {len(video_ids)} requested")
        return transcripts

