"use client";

import { useState, useEffect } from "react";
import { NodeProps } from "reactflow";
import { NodeWrapper } from "./NodeWrapper";
import { Button } from "@/components/ui/button";
import { WorkflowNodeData } from "@/lib/workflowState";
import { generateScript } from "@/lib/api";
import { PodcastFormat } from "@/lib/types";
import type { OutlineResponse, ScriptResponse } from "@/lib/types";
import { ScrollText, Loader2 } from "lucide-react";

interface ScriptNodeProps extends NodeProps {
  data: WorkflowNodeData & {
    topic?: string;
    format?: PodcastFormat;
    outline?: OutlineResponse;
    onComplete?: (script: ScriptResponse) => void;
    onExpand?: () => void;
    onCollapse?: () => void;
  };
}

export function ScriptNode({ id, data }: ScriptNodeProps) {
  const [loading, setLoading] = useState(false);
  const [script, setScript] = useState<ScriptResponse | null>(
    data.script || null
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (
      data.isExpanded &&
      !script &&
      data.outline &&
      data.topic &&
      data.format
    ) {
      generateScriptContent();
    }
  }, [data.isExpanded]);

  const generateScriptContent = async () => {
    if (!data.outline || !data.topic || !data.format) return;

    try {
      setLoading(true);
      setError(null);
      const result = await generateScript(
        data.outline,
        data.topic,
        data.format
      );
      setScript(result);
    } catch (err) {
      setError("Failed to generate script. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (script && data.onComplete) {
      data.onComplete(script);
    }
  };

  const summary = script
    ? `Script generated (~${Math.round(script.total_duration_seconds / 60)}min)`
    : "Generate script";

  return (
    <NodeWrapper
      id={id}
      icon={<ScrollText className="w-5 h-5" />}
      title="Podcast Script"
      summary={summary}
      color="#f97316"
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
            <Loader2 className="w-8 h-8 animate-spin text-orange-500 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-200 mb-1">
              Generating podcast script with Gemini...
            </p>
            <p className="text-xs text-gray-400">This may take 1-2 minutes</p>
          </div>
        </div>
      ) : script ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>
              {data.format === PodcastFormat.TWO_HOSTS
                ? "Two-host dialogue"
                : "Single narrator"}
            </span>
            <span>
              ~{Math.round(script.total_duration_seconds / 60)} minutes
            </span>
          </div>

          <div className="bg-gray-700 rounded-lg p-4 max-h-80 overflow-y-auto">
            {data.format === PodcastFormat.TWO_HOSTS ? (
              <div className="space-y-3">
                {script.segments.map((segment, idx) => (
                  <div key={idx} className="flex gap-2">
                    <div className="flex-shrink-0">
                      {segment.speaker === "HOST_1" ? (
                        <div className="w-7 h-7 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-medium">
                          H1
                        </div>
                      ) : (
                        <div className="w-7 h-7 rounded-full bg-purple-500 flex items-center justify-center text-white text-xs font-medium">
                          H2
                        </div>
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-xs font-medium text-gray-200 mb-0.5">
                        {segment.speaker === "HOST_1" ? "Host 1" : "Host 2"}
                      </p>
                      <p className="text-xs text-gray-300">{segment.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="prose prose-sm max-w-none">
                <p className="whitespace-pre-wrap text-xs text-gray-200">
                  {script.full_script}
                </p>
              </div>
            )}
          </div>

          <div className="flex justify-end pt-2">
            <Button onClick={handleNext} size="lg">
              Generate Audio
            </Button>
          </div>
        </div>
      ) : error ? (
        <div className="text-center py-8">
          <p className="text-red-400 mb-3">{error}</p>
          <Button onClick={generateScriptContent} variant="outline" size="sm">
            Try Again
          </Button>
        </div>
      ) : null}
    </NodeWrapper>
  );
}
