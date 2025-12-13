"use client";

import { useState, useEffect } from "react";
import { NodeProps } from "reactflow";
import { NodeWrapper } from "./NodeWrapper";
import { Button } from "@/components/ui/button";
import { VideoCard } from "@/components/VideoCard";
import { WorkflowNodeData } from "@/lib/workflowState";
import { discoverVideos } from "@/lib/api";
import type { VideoInfo } from "@/lib/types";
import { Video, Loader2 } from "lucide-react";

interface ReferencesNodeProps extends NodeProps {
  data: WorkflowNodeData & {
    topic?: string;
    onComplete?: (selectedVideos: VideoInfo[]) => void;
    onExpand?: () => void;
    onCollapse?: () => void;
  };
}

export function ReferencesNode({ id, data }: ReferencesNodeProps) {
  const [videos, setVideos] = useState<VideoInfo[]>([]);
  const [selectedVideos, setSelectedVideos] = useState<VideoInfo[]>(
    data.videos || []
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (data.isExpanded && data.topic && videos.length === 0) {
      fetchVideos();
    }
  }, [data.isExpanded, data.topic]);

  const fetchVideos = async () => {
    if (!data.topic) return;

    try {
      setLoading(true);
      setError(null);
      const results = await discoverVideos(data.topic, 12);
      setVideos(results);
    } catch (err) {
      setError("Failed to fetch videos. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleVideo = (video: VideoInfo) => {
    if (selectedVideos.find((v) => v.video_id === video.video_id)) {
      setSelectedVideos(
        selectedVideos.filter((v) => v.video_id !== video.video_id)
      );
    } else if (selectedVideos.length < 5) {
      setSelectedVideos([...selectedVideos, video]);
    }
  };

  const handleNext = () => {
    console.log("ReferencesNode handleNext called", {
      selectedVideos: selectedVideos.length,
      hasOnComplete: !!data.onComplete,
    });
    if (selectedVideos.length > 0 && data.onComplete) {
      console.log("Calling onComplete with videos:", selectedVideos);
      data.onComplete(selectedVideos);
    } else {
      console.warn("Cannot proceed:", {
        videosSelected: selectedVideos.length,
        onCompleteExists: !!data.onComplete,
      });
    }
  };

  const summary = data.videos
    ? `${data.videos.length} video${
        data.videos.length !== 1 ? "s" : ""
      } selected`
    : "Select references";

  return (
    <NodeWrapper
      id={id}
      icon={<Video className="w-5 h-5" />}
      title="Reference Videos"
      summary={summary}
      color="#8b5cf6"
      isExpanded={data.isExpanded}
      isCompleted={data.isCompleted}
      isLoading={data.isLoading || loading}
      error={data.error || error}
      onExpand={data.onExpand}
      onCollapse={data.onCollapse}
    >
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-purple-500 mx-auto mb-3" />
            <p className="text-sm text-gray-300">
              Searching for relevant podcasts...
            </p>
          </div>
        </div>
      ) : error ? (
        <div className="text-center py-8">
          <p className="text-red-400 mb-3">{error}</p>
          <Button onClick={fetchVideos} variant="outline" size="sm">
            Try Again
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-gray-300">
            Select 1-5 podcast episodes ({selectedVideos.length}/5 selected)
          </p>

          <div className="grid grid-cols-2 gap-3 max-h-80 overflow-y-auto pr-2">
            {videos.map((video) => (
              <VideoCard
                key={video.video_id}
                video={video}
                selected={
                  !!selectedVideos.find((v) => v.video_id === video.video_id)
                }
                onToggle={() => toggleVideo(video)}
              />
            ))}
          </div>

          <div className="flex justify-end pt-2">
            <Button
              onClick={handleNext}
              disabled={selectedVideos.length === 0}
              size="lg"
            >
              Continue to Analysis ({selectedVideos.length} selected)
            </Button>
          </div>
        </div>
      )}
    </NodeWrapper>
  );
}
