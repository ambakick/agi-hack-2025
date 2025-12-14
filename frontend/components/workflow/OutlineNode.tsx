"use client";

import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
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
import { FileText, Clock, Loader2, Eye, X } from "lucide-react";

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
  const [showModal, setShowModal] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

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

  // Single useEffect to auto-start processing when node is expanded with required data
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
  }, [data.isExpanded, data.videos, data.topic, data.format, stage]);

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
        <div className="space-y-3">
          {/* Preview Card */}
          <div className="bg-teal-900/20 rounded-lg p-4 border border-teal-700/50">
            <h4 className="font-semibold text-sm mb-2 text-teal-300">
              Content Analysis Complete
            </h4>
            <p className="text-xs text-gray-400 mb-3 line-clamp-2">
              {analysis.summary}
            </p>
            <div className="flex items-center justify-between text-xs text-gray-300">
              <span>{analysis.themes.length} themes identified</span>
              <span>{outline.sections.length} sections • {outline.total_duration_minutes} min</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button 
              onClick={() => setShowModal(true)} 
              variant="outline"
              size="sm"
              className="flex-1"
            >
              <Eye className="w-4 h-4 mr-2" />
              View Full Details
            </Button>
            <Button onClick={handleNext} size="sm" className="flex-1">
              Generate Script →
            </Button>
          </div>

          {/* Modal rendered via Portal */}
          {mounted && showModal && createPortal(
            <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/70 backdrop-blur-sm animate-in fade-in duration-200" onClick={() => setShowModal(false)}>
              <div className="bg-gray-800 rounded-xl border border-gray-700 w-[90vw] max-w-4xl max-h-[85vh] overflow-hidden shadow-2xl animate-in zoom-in-95 duration-200" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-gray-900/50">
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-teal-400" />
                    <h3 className="font-semibold text-lg text-white">Analysis & Outline</h3>
                  </div>
                  <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-white transition">
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[calc(85vh-80px)]">
                  {/* Analysis Section */}
                  <div className="mb-6">
                    <div className="bg-teal-900/30 rounded-lg p-4 border border-teal-700">
                      <h4 className="font-semibold text-base mb-3 text-teal-300">
                        Content Analysis
                      </h4>
                      <p className="text-sm text-gray-300 mb-4">{analysis.summary}</p>
                      <div>
                        <p className="text-sm font-medium text-teal-400 mb-2">
                          Key Themes:
                        </p>
                        <ul className="space-y-2">
                          {analysis.themes.map((theme, idx) => (
                            <li key={idx} className="text-sm text-gray-300 pl-4 border-l-2 border-teal-600">
                              <span className="font-medium text-teal-400">{theme.theme}:</span>{" "}
                              {theme.description}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Outline Section */}
                  <div>
                    <h4 className="font-semibold text-base mb-3 text-white flex items-center gap-2">
                      Episode Outline
                      <span className="text-sm font-normal text-gray-400">
                        ({outline.total_duration_minutes} minutes)
                      </span>
                    </h4>
                    <div className="space-y-3">
                      {outline.sections.map((section: OutlineSection, idx) => (
                        <div
                          key={section.id}
                          className="border border-gray-600 rounded-lg p-4 bg-gray-700/50 hover:bg-gray-700 transition"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h5 className="font-medium text-base text-white">
                              {idx + 1}. {section.title}
                            </h5>
                            <div className="flex items-center text-sm text-gray-400">
                              <Clock className="w-4 h-4 mr-1" />
                              {section.duration_minutes}m
                            </div>
                          </div>
                          <p className="text-sm text-gray-300 mb-3">
                            {section.description}
                          </p>
                          <ul className="text-sm text-gray-400 space-y-1">
                            {section.key_points.map((point, pidx) => (
                              <li key={pidx} className="flex items-start gap-2">
                                <span className="text-teal-500 mt-1">•</span>
                                <span>{point}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-end gap-3 p-4 border-t border-gray-700 bg-gray-900/50">
                  <Button onClick={() => setShowModal(false)} variant="outline" size="sm">
                    Close
                  </Button>
                  <Button onClick={() => { setShowModal(false); handleNext(); }} size="sm">
                    Generate Script →
                  </Button>
                </div>
              </div>
            </div>,
            document.body
          )}
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
