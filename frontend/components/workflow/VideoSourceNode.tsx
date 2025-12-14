"use client";

import { useState } from "react";
import { NodeProps } from "reactflow";
import { NodeWrapper } from "./NodeWrapper";
import { FileUploadZone } from "@/components/sources/FileUploadZone";
import { WorkflowNodeData } from "@/lib/workflowState";
import { Source, SourceType } from "@/lib/types";
import { uploadSource } from "@/lib/api";
import { Video as VideoIcon, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface VideoSourceNodeProps extends NodeProps {
  data: WorkflowNodeData & {
    source?: Source;
    onComplete?: (source: Source) => void;
    onExpand?: () => void;
    onCollapse?: () => void;
  };
}

export function VideoSourceNode({ id, data }: VideoSourceNodeProps) {
  const [source, setSource] = useState<Source | null>(data.source || null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File, sourceType: SourceType) => {
    try {
      setIsUploading(true);
      setError(null);

      const uploadedSource = await uploadSource(file, sourceType);
      setSource(uploadedSource);
    } catch (err) {
      console.error("Failed to upload video:", err);
      setError("Failed to upload video. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleComplete = () => {
    if (source && data.onComplete) {
      data.onComplete(source);
    }
  };

  const summary = source
    ? `${source.name} (${(
        (source.metadata?.file_size || 0) /
        1024 /
        1024
      ).toFixed(1)} MB)`
    : "Upload Video";

  return (
    <NodeWrapper
      id={id}
      icon={<VideoIcon className="w-5 h-5" />}
      title="Video Source"
      summary={summary}
      color="#f97316"
      isExpanded={data.isExpanded}
      isCompleted={data.isCompleted}
      isLoading={data.isLoading || isUploading}
      error={data.error || error}
      onExpand={data.onExpand}
      onCollapse={data.onCollapse}
    >
      <div className="space-y-4">
        {!source ? (
          <>
            <p className="text-sm text-gray-300">Upload a video file</p>
            <FileUploadZone
              onFileSelect={handleFileSelect}
              isUploading={isUploading}
            />
          </>
        ) : (
          <>
            <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
              {source.file_url && (
                <video
                  controls
                  src={source.file_url}
                  className="w-full rounded-lg mb-3"
                  style={{ maxHeight: "200px" }}
                />
              )}
              <div className="flex items-start gap-3">
                <div className="w-12 h-12 rounded-lg bg-orange-500/10 flex items-center justify-center flex-shrink-0">
                  <VideoIcon className="w-6 h-6 text-orange-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-white truncate">
                    {source.name}
                  </h3>
                  <p className="text-sm text-gray-400 mt-1">
                    {((source.metadata?.file_size || 0) / 1024 / 1024).toFixed(
                      1
                    )}{" "}
                    MB
                  </p>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <Button
                onClick={() => setSource(null)}
                variant="outline"
                size="sm"
              >
                Change File
              </Button>
              <Button onClick={handleComplete} size="lg">
                Add to Podcast →
              </Button>
            </div>
          </>
        )}
      </div>
    </NodeWrapper>
  );
}
