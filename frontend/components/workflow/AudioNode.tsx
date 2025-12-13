"use client";

import { useState, useEffect } from "react";
import { NodeProps } from "reactflow";
import { NodeWrapper } from "./NodeWrapper";
import { Button } from "@/components/ui/button";
import { WorkflowNodeData } from "@/lib/workflowState";
import { convertToSpeech } from "@/lib/api";
import type { ScriptResponse } from "@/lib/types";
import { Volume2, Loader2, Download, Play, Pause } from "lucide-react";

interface AudioNodeProps extends NodeProps {
  data: WorkflowNodeData & {
    script?: ScriptResponse;
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

  useEffect(() => {
    if (data.isExpanded && !audioUrl && data.script) {
      generateAudio();
    }
  }, [data.isExpanded]);

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

  const summary = audioUrl ? "Audio ready!" : "Generate audio";

  return (
    <NodeWrapper
      id={id}
      icon={<Volume2 className="w-5 h-5" />}
      title="Podcast Audio"
      summary={summary}
      color="#10b981"
      isExpanded={data.isExpanded}
      isCompleted={data.isCompleted}
      isLoading={data.isLoading || loading}
      error={data.error || error}
      onExpand={data.onExpand}
      onCollapse={data.onCollapse}
      hasSourceHandle={false}
    >
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-green-500 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-200 mb-1">
              Converting script to audio with ElevenLabs...
            </p>
            <p className="text-xs text-gray-400">This may take 2-3 minutes</p>
          </div>
        </div>
      ) : audioUrl ? (
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
      ) : error ? (
        <div className="text-center py-8">
          <p className="text-red-400 mb-3">{error}</p>
          <Button onClick={generateAudio} variant="outline" size="sm">
            Try Again
          </Button>
        </div>
      ) : null}
    </NodeWrapper>
  );
}
