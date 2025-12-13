'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { generateVideo, getVideoUrl } from '@/lib/api';
import type { ScriptResponse, VideoGenerationFullResponse } from '@/lib/types';
import { Loader2, Download, Play, Pause, Video, CheckCircle2 } from 'lucide-react';

interface VideoStepProps {
  script: ScriptResponse;
  onBack: () => void;
}

type VideoStage = 
  | 'extracting' 
  | 'scenes' 
  | 'videos' 
  | 'audio' 
  | 'stitching' 
  | 'syncing' 
  | 'done' 
  | 'error';

export function VideoStep({ script, onBack }: VideoStepProps) {
  const [loading, setLoading] = useState(true);
  const [stage, setStage] = useState<VideoStage>('extracting');
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [playing, setPlaying] = useState(false);
  const [video, setVideo] = useState<HTMLVideoElement | null>(null);
  const [progress, setProgress] = useState<VideoGenerationFullResponse | null>(null);

  useEffect(() => {
    async function generate() {
      try {
        setLoading(true);
        setError(null);
        
        // Convert script to transcript format
        const transcript = script.full_script;
        
        // Start full pipeline
        setStage('extracting');
        const result = await generateVideo({
          transcript,
          transcript_format: 'plain',
          max_snippets: 5,
        });
        
        setProgress(result);
        
        // Simulate stage progression (the backend does this, but we show progress)
        // In reality, the backend returns the final result, but we can show intermediate stages
        setStage('videos');
        await new Promise(resolve => setTimeout(resolve, 500));
        setStage('audio');
        await new Promise(resolve => setTimeout(resolve, 500));
        setStage('stitching');
        await new Promise(resolve => setTimeout(resolve, 500));
        setStage('syncing');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Get the final video URL
        const finalVideoUrl = getVideoUrl(result.final_video_path);
        setVideoUrl(finalVideoUrl);
        
        // Create video element
        const videoElement = document.createElement('video');
        videoElement.src = finalVideoUrl;
        videoElement.controls = true;
        videoElement.addEventListener('play', () => setPlaying(true));
        videoElement.addEventListener('pause', () => setPlaying(false));
        videoElement.addEventListener('ended', () => setPlaying(false));
        setVideo(videoElement);
        
        setStage('done');
        setLoading(false);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to generate video. Please try again.');
        console.error(err);
        setStage('error');
        setLoading(false);
      }
    }

    generate();

    return () => {
      if (video) {
        video.pause();
        video.remove();
      }
    };
  }, [script]);

  const togglePlay = () => {
    if (!video) return;

    if (playing) {
      video.pause();
      setPlaying(false);
    } else {
      video.play();
      setPlaying(true);
    }
  };

  const handleDownload = async () => {
    if (!videoUrl || !progress) return;
    
    try {
      const response = await fetch(videoUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'podcast-video.mp4';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading video:', err);
      // Fallback: open in new tab
      window.open(videoUrl, '_blank');
    }
  };

  const getStageLabel = (currentStage: VideoStage): string => {
    const stages: Record<VideoStage, string> = {
      extracting: 'Extracting interesting snippets...',
      scenes: 'Generating scene descriptions...',
      videos: 'Generating video clips with Veo 3.1...',
      audio: 'Generating audio clips with ElevenLabs...',
      stitching: 'Stitching video clips together...',
      syncing: 'Synchronizing audio with video...',
      done: 'Video generation complete!',
      error: 'Error generating video',
    };
    return stages[currentStage] || 'Processing...';
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-16">
          <div className="text-center max-w-md">
            <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
            <p className="text-gray-600 font-medium mb-2">
              {getStageLabel(stage)}
            </p>
            <p className="text-sm text-gray-500">
              {stage === 'extracting' && 'Analyzing transcript for interesting moments...'}
              {stage === 'scenes' && 'Creating 8-second visual scenes...'}
              {stage === 'videos' && 'Generating cinematic video clips (this may take 5-10 minutes)...'}
              {stage === 'audio' && 'Creating natural voice audio...'}
              {stage === 'stitching' && 'Combining video clips...'}
              {stage === 'syncing' && 'Perfecting audio-video synchronization...'}
            </p>
            {progress && (
              <div className="mt-6 space-y-2 text-left">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  {progress.snippets.length > 0 && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                  <span>{progress.snippets.length} snippets extracted</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  {progress.scenes.length > 0 && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                  <span>{progress.scenes.length} scenes generated</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  {progress.video_scenes.length > 0 && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                  <span>{progress.video_scenes.length} video clips created</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  {progress.audio_scenes.length > 0 && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                  <span>{progress.audio_scenes.length} audio clips created</span>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-16">
          <div className="text-center">
            <p className="text-red-500 mb-4">{error}</p>
            <div className="flex gap-4 justify-center">
              <Button onClick={onBack} variant="outline">
                Back to Audio
              </Button>
              <Button onClick={() => window.location.reload()}>
                Try Again
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Video className="w-6 h-6 text-primary" />
            Your Video Podcast is Ready!
          </CardTitle>
          <CardDescription>
            Cinematic video generated with Google Veo 3.1 and ElevenLabs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-8">
            {videoUrl && (
              <div className="mb-6">
                <video
                  ref={(el) => {
                    if (el) {
                      el.src = videoUrl;
                      el.controls = true;
                      el.addEventListener('play', () => setPlaying(true));
                      el.addEventListener('pause', () => setPlaying(false));
                      el.addEventListener('ended', () => setPlaying(false));
                      if (!video) {
                        setVideo(el);
                      }
                    }
                  }}
                  className="w-full rounded-lg shadow-lg"
                  controls
                  onPlay={() => setPlaying(true)}
                  onPause={() => setPlaying(false)}
                />
              </div>
            )}
            
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold mb-2">Video Podcast Episode</h3>
              {progress && (
                <p className="text-gray-600">
                  Duration: ~{Math.round(progress.total_duration / 60)} minutes
                </p>
              )}
            </div>

            <div className="flex justify-center gap-4">
              <Button size="lg" onClick={togglePlay} disabled={!video}>
                {playing ? (
                  <>
                    <Pause className="w-5 h-5 mr-2" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 mr-2" />
                    Play
                  </>
                )}
              </Button>
              <Button size="lg" variant="outline" onClick={handleDownload} disabled={!videoUrl}>
                <Download className="w-5 h-5 mr-2" />
                Download MP4
              </Button>
            </div>

            {progress && (
              <div className="mt-6 p-4 bg-white/50 rounded-lg">
                <h4 className="font-semibold mb-3">Generation Summary</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Snippets:</span>
                    <span className="ml-2 font-medium">{progress.snippets.length}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Scenes:</span>
                    <span className="ml-2 font-medium">{progress.scenes.length}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Video Clips:</span>
                    <span className="ml-2 font-medium">{progress.video_scenes.length}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Audio Clips:</span>
                    <span className="ml-2 font-medium">{progress.audio_scenes.length}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-between">
        <Button onClick={onBack} variant="outline">
          Back to Audio
        </Button>
        <Button onClick={() => (window.location.href = '/')} variant="secondary">
          Create New Podcast
        </Button>
      </div>
    </div>
  );
}

