import axios from 'axios';
import type {
  VideoInfo,
  VideoTranscript,
  AnalysisResponse,
  OutlineResponse,
  ScriptResponse,
  PodcastFormat,
  TranscriptSegment,
  VideoGenerationRequest,
  VideoGenerationFullResponse,
  SnippetExtractionResponse,
  SceneGenerationResponse,
  VideoGenerationResponse,
  AudioGenerationResponse,
  VideoStitchRequest,
  VideoStitchResponse,
  AudioSyncRequest,
  AudioSyncResponse,
  Snippet,
  SceneDescription,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Discovery API
export async function discoverVideos(topic: string, maxResults: number = 10): Promise<VideoInfo[]> {
  const response = await api.post('/discover', {
    topic,
    max_results: maxResults,
    language: 'en',
  });
  return response.data.videos;
}

// Transcripts API
export async function getTranscripts(videoIds: string[]): Promise<VideoTranscript[]> {
  const response = await api.post('/transcripts', {
    video_ids: videoIds,
  });
  return response.data.transcripts;
}

// Analysis API
export async function analyzeContent(
  transcripts: VideoTranscript[],
  topic: string
): Promise<AnalysisResponse> {
  const response = await api.post('/analyze', {
    transcripts,
    topic,
  });
  return response.data;
}

// Outline API
export async function generateOutline(
  analysis: AnalysisResponse,
  topic: string,
  format: PodcastFormat,
  targetDuration: number
): Promise<OutlineResponse> {
  const response = await api.post('/outline', {
    analysis,
    topic,
    format,
    target_duration_minutes: targetDuration,
  });
  return response.data;
}

// Script API
export async function generateScript(
  outline: OutlineResponse,
  topic: string,
  format: PodcastFormat
): Promise<ScriptResponse> {
  const response = await api.post('/script', {
    outline,
    topic,
    format,
  });
  return response.data;
}

// TTS API
export async function convertToSpeech(script: ScriptResponse): Promise<Blob> {
  const response = await api.post(
    '/tts',
    {
      script,
    },
    {
      responseType: 'blob',
    }
  );
  return response.data;
}

// Video Generation APIs

/**
 * Extract interesting snippets from transcript
 */
export async function extractSnippets(
  transcript: string | TranscriptSegment[],
  format: 'plain' | 'json' = 'plain',
  maxSnippets: number = 5
): Promise<SnippetExtractionResponse> {
  const response = await api.post('/extract-snippets', {
    transcript,
    format,
    max_snippets: maxSnippets,
  });
  return response.data;
}

/**
 * Generate 8-second scene descriptions from snippets
 */
export async function generateScenes(snippets: Snippet[]): Promise<SceneGenerationResponse> {
  const response = await api.post('/generate-scenes', snippets);
  return response.data;
}

/**
 * Generate video clips using Veo 3.1
 */
export async function generateVideos(scenes: SceneDescription[]): Promise<VideoGenerationResponse> {
  const response = await api.post('/generate-videos', scenes);
  return response.data;
}

/**
 * Generate audio clips using ElevenLabs
 */
export async function generateAudio(
  scenes: SceneDescription[],
  voiceId?: string
): Promise<AudioGenerationResponse> {
  const response = await api.post('/generate-audio', scenes, {
    params: voiceId ? { voice_id: voiceId } : {},
  });
  return response.data;
}

/**
 * Stitch multiple video clips into a single video
 */
export async function stitchVideos(
  videoPaths: string[],
  outputPath?: string
): Promise<VideoStitchResponse> {
  const response = await api.post('/stitch-videos', {
    video_paths: videoPaths,
    output_path: outputPath,
  });
  return response.data;
}

/**
 * Add audio to video with perfect synchronization
 */
export async function addAudio(
  videoPath: string,
  audioPath: string,
  outputPath?: string
): Promise<AudioSyncResponse> {
  const response = await api.post('/add-audio', {
    video_path: videoPath,
    audio_path: audioPath,
    output_path: outputPath,
  });
  return response.data;
}

/**
 * Full pipeline: Extract snippets, generate scenes, create videos and audio, stitch, and sync
 */
export async function generateVideo(
  request: VideoGenerationRequest
): Promise<VideoGenerationFullResponse> {
  const response = await api.post('/generate-video', request);
  return response.data;
}

/**
 * Download a file from the backend
 */
export async function downloadFile(filePath: string): Promise<Blob> {
  // The backend should serve files, but for now we'll construct a URL
  // In production, you'd want a proper file serving endpoint
  const response = await axios.get(`${API_URL}${filePath}`, {
    responseType: 'blob',
  });
  return response.data;
}

/**
 * Get the full URL for a video file
 */
export function getVideoUrl(filePath: string): string {
  // Remove leading ./ if present
  let cleanPath = filePath.startsWith('./') ? filePath.slice(2) : filePath;
  
  // If path contains video_output, use the mounted static route
  if (cleanPath.includes('video_output')) {
    // Extract just the filename and subdirectory from video_output
    const parts = cleanPath.split('video_output');
    cleanPath = parts.length > 1 ? `video_output${parts[1]}` : cleanPath;
  } else if (cleanPath.includes('audio_output')) {
    // Extract just the filename and subdirectory from audio_output
    const parts = cleanPath.split('audio_output');
    cleanPath = parts.length > 1 ? `audio_output${parts[1]}` : cleanPath;
  }
  
  // Ensure path starts with /
  if (!cleanPath.startsWith('/')) {
    cleanPath = `/${cleanPath}`;
  }
  
  // Construct full URL
  return `${API_URL}${cleanPath}`;
}

