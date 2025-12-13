"use client";

import { useState, useEffect } from "react";
import { NodeProps } from "reactflow";
import { NodeWrapper } from "./NodeWrapper";
import { Button } from "@/components/ui/button";
import { WorkflowNodeData } from "@/lib/workflowState";
import { getTranscripts, analyzeContent, generateOutline } from "@/lib/api";
import type {
  VideoInfo,
  VideoTranscript,
  AnalysisResponse,
  OutlineResponse,
  PodcastFormat,
  OutlineSection,
} from "@/lib/types";
import { FileText, Clock, Loader2 } from "lucide-react";

interface OutlineNodeProps extends NodeProps {
  data: WorkflowNodeData & {
    topic?: string;
    format?: PodcastFormat;
    videos?: VideoInfo[];
    onComplete?: (
      transcripts: VideoTranscript[],
      analysis: AnalysisResponse,
      outline: OutlineResponse
    ) => void;
    onExpand?: () => void;
    onCollapse?: () => void;
  };
}

export function OutlineNode({ id, data }: OutlineNodeProps) {
  console.log("OutlineNode rendered with data:", {
    id,
    isExpanded: data.isExpanded,
    hasVideos: !!data.videos,
    videosCount: data.videos?.length,
    topic: data.topic,
    format: data.format,
  });

  const [stage, setStage] = useState<
    "idle" | "transcripts" | "analysis" | "outline" | "done"
  >("idle");
  const [transcripts, setTranscripts] = useState<VideoTranscript[]>(
    data.transcripts || []
  );
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(
    data.analysis || null
  );
  const [outline, setOutline] = useState<OutlineResponse | null>(
    data.outline || null
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log("OutlineNode useEffect triggered", {
      isExpanded: data.isExpanded,
      stage,
      hasVideos: !!data.videos,
      videosCount: data.videos?.length,
      topic: data.topic,
      format: data.format,
    });

    // Auto-start processing when node is expanded and has all required data
    if (
      data.isExpanded &&
      stage === "idle" &&
      data.videos &&
      data.videos.length > 0 &&
      data.topic &&
      data.format
    ) {
      console.log("Starting processOutline automatically...");
      processOutline();
    }
  }, [data.isExpanded, data.videos, data.topic, data.format]);

  // Separate effect to start processing when stage becomes idle with all data
  useEffect(() => {
    if (
      stage === "idle" &&
      data.isExpanded &&
      data.videos?.length &&
      data.topic &&
      data.format
    ) {
      console.log("Re-triggering processOutline due to stage change");
      processOutline();
    }
  }, [stage]);

  const processOutline = async () => {
    console.log("processOutline called");
    if (!data.videos || !data.topic || !data.format) {
      console.error("Missing required data:", {
        hasVideos: !!data.videos,
        hasTopic: !!data.topic,
        hasFormat: !!data.format,
      });
      return;
    }

    try {
      // Fetch transcripts
      console.log("Fetching transcripts for", data.videos.length, "videos");
      setStage("transcripts");
      const videoIds = data.videos.map((v) => v.video_id);
      const transcriptResults = await getTranscripts(videoIds);
      console.log("Transcripts fetched:", transcriptResults.length);
      setTranscripts(transcriptResults);

      // Analyze content
      setStage("analysis");
      const analysisResults = await analyzeContent(
        transcriptResults,
        data.topic
      );
      setAnalysis(analysisResults);

      // Generate outline
      setStage("outline");
      const outlineResults = await generateOutline(
        analysisResults,
        data.topic,
        data.format,
        15
      );
      setOutline(outlineResults);

      setStage("done");
    } catch (err) {
      setError("Failed to generate outline. Please try again.");
      console.error(err);
      setStage("idle");
    }
  };

  const handleNext = () => {
    if (transcripts && analysis && outline && data.onComplete) {
      data.onComplete(transcripts, analysis, outline);
    }
  };

  const summary = outline
    ? `Outline ready (~${outline.total_duration_minutes}min)`
    : "Generate outline";

  const isLoading = ["transcripts", "analysis", "outline"].includes(stage);

  return (
    <NodeWrapper
      id={id}
      icon={<FileText className="w-5 h-5" />}
      title="Analysis & Outline"
      summary={summary}
      color="#14b8a6"
      isExpanded={data.isExpanded}
      isCompleted={data.isCompleted}
      isLoading={data.isLoading || isLoading}
      error={data.error || error}
      onExpand={data.onExpand}
      onCollapse={data.onCollapse}
    >
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-teal-500 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-200 mb-1">
              {stage === "transcripts" && "Fetching video transcripts..."}
              {stage === "analysis" && "Analyzing content with Gemini..."}
              {stage === "outline" && "Generating episode outline..."}
            </p>
            <p className="text-xs text-gray-400">This may take a minute</p>
          </div>
        </div>
      ) : stage === "done" && analysis && outline ? (
        <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
          {/* Analysis Summary */}
          <div className="bg-teal-900/30 rounded-lg p-3 border border-teal-700">
            <h4 className="font-semibold text-sm mb-2 text-teal-300">
              Content Analysis
            </h4>
            <p className="text-xs text-gray-300 mb-3">{analysis.summary}</p>
            <div>
              <p className="text-xs font-medium text-teal-400 mb-1">
                Key Themes:
              </p>
              <ul className="space-y-1">
                {analysis.themes.slice(0, 3).map((theme, idx) => (
                  <li key={idx} className="text-xs text-gray-400">
                    <span className="font-medium">{theme.theme}:</span>{" "}
                    {theme.description}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Outline Sections */}
          <div>
            <h4 className="font-semibold text-sm mb-2 text-white">
              Episode Outline ({outline.total_duration_minutes} minutes)
            </h4>
            <div className="space-y-2">
              {outline.sections.map((section: OutlineSection, idx) => (
                <div
                  key={section.id}
                  className="border border-gray-600 rounded-lg p-3 bg-gray-700"
                >
                  <div className="flex items-start justify-between mb-1">
                    <h5 className="font-medium text-sm text-white">
                      {idx + 1}. {section.title}
                    </h5>
                    <div className="flex items-center text-xs text-gray-400">
                      <Clock className="w-3 h-3 mr-1" />
                      {section.duration_minutes}m
                    </div>
                  </div>
                  <p className="text-xs text-gray-300 mb-2">
                    {section.description}
                  </p>
                  <ul className="text-xs text-gray-400 list-disc list-inside space-y-0.5">
                    {section.key_points.slice(0, 2).map((point, pidx) => (
                      <li key={pidx}>{point}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <Button onClick={handleNext} size="lg">
              Generate Script
            </Button>
          </div>
        </div>
      ) : error ? (
        <div className="text-center py-8">
          <p className="text-red-400 mb-3">{error}</p>
          <Button onClick={processOutline} variant="outline" size="sm">
            Try Again
          </Button>
        </div>
      ) : (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <p className="text-sm text-gray-300 mb-2">Initializing...</p>
            <p className="text-xs text-gray-500">
              {!data.videos ? "Waiting for videos..." : ""}
              {!data.topic ? "Waiting for topic..." : ""}
              {!data.format ? "Waiting for format..." : ""}
              {data.videos && data.topic && data.format && stage === "idle" ? (
                <Button onClick={processOutline} size="sm" className="mt-2">
                  Start Analysis
                </Button>
              ) : null}
            </p>
          </div>
        </div>
      )}
    </NodeWrapper>
  );
}
