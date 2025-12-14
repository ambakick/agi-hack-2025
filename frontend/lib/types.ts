// Podcast Format
export enum PodcastFormat {
  SINGLE_HOST = 'single',
  TWO_HOSTS = 'two_hosts',
}

// Video Discovery Types
export interface VideoInfo {
  video_id: string;
  title: string;
  channel_name: string;
  thumbnail_url: string;
  view_count: number;
  published_at: string;
  duration: string;
}

export interface VideoTranscript {
  video_id: string;
  transcript: string;
  segments?: TranscriptSegment[];
}

export interface TranscriptSegment {
  text: string;
  start: number;
  duration: number;
}

// Analysis Types
export interface ThemePoint {
  theme: string;
  description: string;
  sources: string[];
}

export interface AnalysisResponse {
  themes: ThemePoint[];
  key_anecdotes: string[];
  summary: string;
}

// Outline Types
export interface OutlineSection {
  id: string;
  title: string;
  description: string;
  duration_minutes: number;
  key_points: string[];
}

export interface OutlineResponse {
  sections: OutlineSection[];
  total_duration_minutes: number;
  format: PodcastFormat;
}

// Script Types
export interface ScriptSegment {
  section_id: string;
  speaker: string;
  text: string;
  timestamp_seconds: number;
}

export interface ScriptResponse {
  segments: ScriptSegment[];
  format: PodcastFormat;
  total_duration_seconds: number;
  full_script: string;
}

// Generation State
export interface GenerationState {
  topic: string;
  format: PodcastFormat;
  selectedVideos: VideoInfo[];
  transcripts: VideoTranscript[];
  analysis: AnalysisResponse | null;
  outline: OutlineResponse | null;
  script: ScriptResponse | null;
  audioUrl: string | null;
  videoUrl: string | null;
}

// Video Generation Types
export interface TranscriptInput {
  transcript: string | TranscriptSegment[];
  format: 'plain' | 'json';
}

export interface Snippet {
  text: string;
  start_time?: number;
  end_time?: number;
  context?: string;
  reason?: string;
}

export interface SnippetExtractionResponse {
  snippets: Snippet[];
  total_snippets: number;
}

export interface SceneDescription {
  scene_number: number;
  transcript_text: string;
  visual_prompt: string;
  duration: number;
  start_time?: number;
}

export interface SceneGenerationResponse {
  scenes: SceneDescription[];
  total_duration: number;
}

export interface VideoScene {
  scene_number: number;
  file_path: string;
  duration: number;
  transcript_text: string;
}

export interface VideoGenerationResponse {
  video_scenes: VideoScene[];
  total_duration: number;
}

export interface AudioScene {
  scene_number: number;
  file_path: string;
  duration: number;
  transcript_text: string;
}

export interface AudioGenerationResponse {
  audio_scenes: AudioScene[];
  total_duration: number;
  voice_id: string;
}

export interface VideoStitchRequest {
  video_paths: string[];
  output_path?: string;
}

export interface VideoStitchResponse {
  stitched_video_path: string;
  duration: number;
}

export interface AudioSyncRequest {
  video_path: string;
  audio_path: string;
  output_path?: string;
}

export interface AudioSyncResponse {
  final_video_path: string;
  duration: number;
}

export interface VideoGenerationRequest {
  transcript: string | TranscriptSegment[];
  transcript_format?: 'plain' | 'json';
  voice_id?: string;
  max_snippets?: number;
}

export interface VideoGenerationFullResponse {
  snippets: Snippet[];
  scenes: SceneDescription[];
  video_scenes: VideoScene[];
  audio_scenes: AudioScene[];
  stitched_video_path?: string;
  final_video_path: string;
  total_duration: number;
}

