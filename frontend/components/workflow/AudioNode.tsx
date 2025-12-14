"use client";

import { useState, useEffect } from "react";
import { NodeProps } from "reactflow";
import { NodeWrapper } from "./NodeWrapper";
import { Button } from "@/components/ui/button";
import { WorkflowNodeData } from "@/lib/workflowState";
import { convertToSpeech, generateVideo, getVideoUrl } from "@/lib/api";
import type { ScriptResponse, VideoGenerationRequest } from "@/lib/types";
import { Volume2, Loader2, Download, Play, Pause, Video } from "lucide-react";

interface AudioNodeProps extends NodeProps {
  data: WorkflowNodeData & {
    script?: ScriptResponse;
    transcript?: string;
    onExpand?: () => void;
    onCollapse?: () => void;
  };
}

export function AudioNode({ id, data }: AudioNodeProps) {
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(
    data.audioUrl || null
  );
  const [error, setError] = useState<string | null>(null);
  const [playing, setPlaying] = useState(false);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
  
  // Video generation state
  const [videoLoading, setVideoLoading] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [videoError, setVideoError] = useState<string | null>(null);

  // Removed auto-generation - now both audio and video only generate on button click

  useEffect(() => {
    return () => {
      if (audio) {
        audio.pause();
        audio.remove();
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audio, audioUrl]);

  const generateAudio = async () => {
    if (!data.script) return;

    try {
      setLoading(true);
      setError(null);
      const audioBlob = await convertToSpeech(data.script);
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

      const audioElement = new Audio(url);
      setAudio(audioElement);
      audioElement.addEventListener("ended", () => setPlaying(false));
    } catch (err) {
      setError("Failed to generate audio. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const togglePlay = () => {
    if (!audio) return;

    if (playing) {
      audio.pause();
      setPlaying(false);
    } else {
      audio.play();
      setPlaying(true);
    }
  };

  const handleDownload = () => {
    if (audioUrl) {
      const a = document.createElement("a");
      a.href = audioUrl;
      a.download = "podcast.mp3";
      a.click();
    }
  };

  const handleGenerateVideo = async () => {
    if (!data.script) return;

    try {
      setVideoLoading(true);
      setVideoError(null);

      // Build transcript from script
      const transcript = data.script.full_script || "";

      const request: VideoGenerationRequest = {
        transcript,
        max_snippets: 1,
      };

      const result = await generateVideo(request);
      const videoPath = result.final_video_path;
      const fullVideoUrl = getVideoUrl(videoPath);
      setVideoUrl(fullVideoUrl);
    } catch (err) {
      setVideoError("Failed to generate video. Please try again.");
      console.error(err);
    } finally {
      setVideoLoading(false);
    }
  };

  const summary = audioUrl ? "Audio ready!" : "Generate audio";

  return (
    <NodeWrapper
      id={id}
      icon={<Volume2 className="w-5 h-5" />}
      title="Podcast Media"
      summary={audioUrl || videoUrl ? "Media ready!" : "Generate media"}
      color="#10b981"
      isExpanded={data.isExpanded}
      isCompleted={data.isCompleted}
      isLoading={data.isLoading || loading || videoLoading}
      error={data.error || error || videoError}
      onExpand={data.onExpand}
      onCollapse={data.onCollapse}
      hasSourceHandle={false}
    >
      {/* Initial state: show both options */}
      {!audioUrl && !loading && !videoUrl && !videoLoading ? (
        <div className="space-y-4 py-4">
          <div className="grid grid-cols-2 gap-3">
            <Button onClick={handleGenerateVideo} className="h-auto py-4 flex flex-col gap-2">
              <Video className="w-6 h-6" />
              <span className="text-sm font-semibold">Generate Video</span>
              <span className="text-xs opacity-80">5-10 minutes</span>
            </Button>
            <Button onClick={generateAudio} variant="outline" className="h-auto py-4 flex flex-col gap-2">
              <Volume2 className="w-6 h-6" />
              <span className="text-sm font-semibold">Generate Audio</span>
              <span className="text-xs opacity-80">2-3 minutes</span>
            </Button>
          </div>
          <p className="text-xs text-center text-gray-400">
            Generate video for social media or audio for podcast listening
          </p>
        </div>
      ) : null}

      {/* Audio loading */}
      {loading && !audioUrl ? (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-green-500 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-200 mb-1">
              Converting script to audio with ElevenLabs...
            </p>
            <p className="text-xs text-gray-400">This may take 2-3 minutes</p>
          </div>
        </div>
      ) : null}

      {/* Audio ready */}
      {audioUrl ? (
        <div className="space-y-4">
          <div className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 rounded-lg p-6 text-center border border-green-700">
            <div className="w-16 h-16 bg-green-500 bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-3">
              <Volume2 className="w-8 h-8 text-green-400" />
            </div>
            <h3 className="text-base font-semibold text-white mb-1">
              Your Podcast is Ready!
            </h3>
            <p className="text-xs text-gray-300 mb-4">
              Duration: ~
              {Math.round(data.script?.total_duration_seconds || 0 / 60)}{" "}
              minutes
            </p>

            <div className="flex justify-center gap-3">
              <Button onClick={togglePlay} size="default">
                {playing ? (
                  <>
                    <Pause className="w-4 h-4 mr-2" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Play
                  </>
                )}
              </Button>
              <Button onClick={handleDownload} variant="outline" size="default">
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            </div>
          </div>

          {/* Video generation option when audio is ready */}
          {!videoUrl && !videoLoading && (
            <div className="border-t border-gray-700 pt-4">
              <Button
                onClick={handleGenerateVideo}
                variant="outline"
                className="w-full"
                disabled={videoLoading}
              >
                <Video className="w-4 h-4 mr-2" />
                Also Generate Video
              </Button>
            </div>
          )}

        </div>
      ) : null}

      {/* Video loading */}
      {videoLoading && !videoUrl ? (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-200 mb-1">
              Generating video with Veo 3.1...
            </p>
            <p className="text-xs text-gray-400">This may take 5-10 minutes</p>
          </div>
        </div>
      ) : null}

      {/* Video ready */}
      {videoUrl ? (
        <div className="space-y-4">
          <div className="bg-gradient-to-br from-blue-900/30 to-indigo-900/30 rounded-lg p-6 border border-blue-700">
            <div className="flex items-center justify-center mb-3">
              <div className="w-16 h-16 bg-blue-500 bg-opacity-20 rounded-full flex items-center justify-center">
                <Video className="w-8 h-8 text-blue-400" />
              </div>
            </div>
            <h3 className="text-base font-semibold text-white text-center mb-3">
              Your Video is Ready!
            </h3>
            <video
              src={videoUrl}
              controls
              className="w-full rounded-lg mb-3"
              style={{ maxHeight: "400px" }}
            >
              Your browser does not support the video tag.
            </video>
            <div className="flex justify-center gap-3">
              <Button
                onClick={() => window.open(videoUrl, "_blank")}
                variant="default"
                size="default"
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            </div>
          </div>

          {/* Audio generation option when video is ready */}
          {!audioUrl && !loading && (
            <div className="border-t border-gray-700 pt-4">
              <Button
                onClick={generateAudio}
                variant="outline"
                className="w-full"
                disabled={loading}
              >
                <Volume2 className="w-4 h-4 mr-2" />
                Also Generate Audio
              </Button>
            </div>
          )}

          <div className="text-center">
            <Button
              onClick={() => (window.location.href = "/generate")}
              variant="secondary"
              size="sm"
            >
              Create New Podcast
            </Button>
          </div>
        </div>
      ) : null}

      {/* Errors */}
      {error && !audioUrl ? (
        <div className="text-center py-8">
          <p className="text-red-400 mb-3">{error}</p>
          <Button onClick={generateAudio} variant="outline" size="sm">
            Try Again
          </Button>
        </div>
      ) : null}

      {videoError && !videoUrl ? (
        <div className="text-center py-8">
          <p className="text-red-400 mb-3">{videoError}</p>
          <Button onClick={handleGenerateVideo} variant="outline" size="sm">
            Try Again
          </Button>
        </div>
      ) : null}
    </NodeWrapper>
  );
}
