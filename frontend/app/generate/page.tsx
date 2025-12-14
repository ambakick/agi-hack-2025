"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Panel,
  ReactFlowProvider,
} from "reactflow";
import "reactflow/dist/style.css";
import { useWorkflowState } from "@/lib/workflowState";
import { TopicNode } from "@/components/workflow/TopicNode";
import { ReferencesNode } from "@/components/workflow/ReferencesNode";
import { PDFSourceNode } from "@/components/workflow/PDFSourceNode";
import { ImageSourceNode } from "@/components/workflow/ImageSourceNode";
import { AudioSourceNode } from "@/components/workflow/AudioSourceNode";
import { VideoSourceNode } from "@/components/workflow/VideoSourceNode";
import { AddSourceNode } from "@/components/workflow/AddSourceNode";
import { OutlineNode } from "@/components/workflow/OutlineNode";
import { ScriptNode } from "@/components/workflow/ScriptNode";
import { AudioNode } from "@/components/workflow/AudioNode";
import { EditModeIndicator } from "@/components/workflow/EditModeIndicator";
import { ConfettiEffect } from "@/components/workflow/ConfettiEffect";
import { WorkflowErrorBoundary } from "@/components/workflow/WorkflowErrorBoundary";
import { PodcastFormat, SourceType } from "@/lib/types";
import type {
  VideoInfo,
  VideoTranscript,
  AnalysisResponse,
  OutlineResponse,
  ScriptResponse,
  Source,
} from "@/lib/types";

const nodeTypes = {
  topicNode: TopicNode,
  referencesNode: ReferencesNode,
  "pdf-sourceNode": PDFSourceNode,
  "image-sourceNode": ImageSourceNode,
  "audio-sourceNode": AudioSourceNode,
  "video-sourceNode": VideoSourceNode,
  addSourceNode: AddSourceNode,
  outlineNode: OutlineNode,
  scriptNode: ScriptNode,
  audioNode: AudioNode,
};

function WorkflowCanvas() {
  const searchParams = useSearchParams();
  const initialTopic = searchParams.get("topic") || "";

  const {
    state,
    updateNodeData,
    addNode,
    expandNode,
    collapseNode,
    completeNode,
    removeNodesAfter,
    updateGenerationState,
    addEdge,
    getSourceNodes,
  } = useWorkflowState(initialTopic);

  const [nodes, setNodes, onNodesChange] = useNodesState(state.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(state.edges);

  // Track additional sources uploaded in AddSourceNode
  const [additionalSources, setAdditionalSources] = useState<Source[]>([]);

  // Track latest state to avoid stale closure issues
  const stateRef = useRef(state);
  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  // Refs for handlers to avoid circular dependencies
  const handleContinueToOutlineRef = useRef<(sources: Source[]) => void>(
    () => {}
  );
  const additionalSourcesRef = useRef(additionalSources);

  // Keep refs in sync
  useEffect(() => {
    additionalSourcesRef.current = additionalSources;
  }, [additionalSources]);

  // Track previous state to prevent unnecessary updates
  const prevStateRef = useRef<{
    nodes: typeof state.nodes;
    edges: typeof state.edges;
  }>({
    nodes: state.nodes,
    edges: state.edges,
  });

  // Sync workflow state with ReactFlow state
  useEffect(() => {
    // Only update if state actually changed (by reference)
    const nodesChanged = prevStateRef.current.nodes !== state.nodes;
    const edgesChanged = prevStateRef.current.edges !== state.edges;

    if (nodesChanged) {
      setNodes(state.nodes);
      prevStateRef.current.nodes = state.nodes;
    }

    if (edgesChanged) {
      setEdges(state.edges);
      prevStateRef.current.edges = state.edges;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.nodes, state.edges]);

  // Script node completion handler
  const handleScriptComplete = useCallback(
    (script: ScriptResponse) => {
      console.log("handleScriptComplete called");
      updateGenerationState({ script });
      completeNode("script", { script });

      // Add Media node (Audio/Video)
      addNode(
        "audio",
        { x: 1500, y: 200 },
        {
          label: "Podcast Media",
          isExpanded: true,
          isCompleted: false,
          isLoading: false,
          script,
          onExpand: () => expandNode("audio"),
          onCollapse: () => collapseNode("audio"),
        }
      );
    },
    [updateGenerationState, completeNode, addNode, expandNode, collapseNode]
  );

  // Outline node completion handler
  const handleOutlineComplete = useCallback(
    (
      transcripts: VideoTranscript[],
      analysis: AnalysisResponse,
      outline: OutlineResponse
    ) => {
      // Use ref to get latest state (avoids stale closure)
      const currentState = stateRef.current;

      console.log("handleOutlineComplete called");
      updateGenerationState({ transcripts, analysis, outline });
      completeNode("outline", { transcripts, analysis, outline });

      // Add Script node
      addNode(
        "script",
        { x: 1150, y: 200 },
        {
          label: "Podcast Script",
          isExpanded: true,
          isCompleted: false,
          isLoading: false,
          topic: currentState.generationState.topic,
          format:
            currentState.generationState.format || PodcastFormat.SINGLE_HOST,
          outline,
          onComplete: handleScriptComplete,
          onExpand: () => expandNode("script"),
          onCollapse: () => collapseNode("script"),
        }
      );
    },
    [
      updateGenerationState,
      completeNode,
      addNode,
      expandNode,
      collapseNode,
      handleScriptComplete,
    ]
  );

  // Handle continuing to Outline
  const handleContinueToOutline = useCallback(
    (uploadedSources: Source[]) => {
      const currentState = stateRef.current;

      // Collect all sources
      const allSources: Source[] = [];

      // Add YouTube videos as sources
      const selectedVideos = currentState.generationState.selectedVideos || [];
      const youtubeSources: Source[] = selectedVideos.map((video) => ({
        id: video.video_id,
        type: SourceType.YOUTUBE,
        name: video.title,
        thumbnail_url: video.thumbnail_url,
        metadata: {
          video_id: video.video_id,
          channel_name: video.channel_name,
          duration: video.duration,
          view_count: video.view_count,
          published_at: video.published_at,
        },
      }));
      allSources.push(...youtubeSources);

      // Add additional uploaded sources from the AddSourceNode
      allSources.push(...uploadedSources);

      console.log(
        "Continuing to Outline with",
        allSources.length,
        "total sources"
      );

      updateGenerationState({ sources: allSources });

      // Mark addSource node as completed
      completeNode("addSource", { sources: uploadedSources });

      // Calculate average Y position for outline node
      const currentNodes = stateRef.current.nodes;
      const sourceNodes = currentNodes.filter(
        (n: any) => n.id === "references" || n.id === "addSource"
      );
      const avgY =
        sourceNodes.length > 0
          ? sourceNodes.reduce((sum: number, n: any) => sum + n.position.y, 0) /
            sourceNodes.length
          : 300;

      // Add Outline node
      addNode(
        "outline",
        { x: 800, y: avgY },
        {
          label: "Analysis & Outline",
          isExpanded: true,
          isCompleted: false,
          isLoading: false,
          topic: currentState.generationState.topic,
          format:
            currentState.generationState.format || PodcastFormat.SINGLE_HOST,
          videos: selectedVideos,
          sources: allSources,
          onComplete: handleOutlineComplete,
          onExpand: () => expandNode("outline"),
          onCollapse: () => collapseNode("outline"),
        }
      );

      // Add edges from source nodes to outline
      addEdge("references", "outline");
      addEdge("addSource", "outline");
    },
    [
      updateGenerationState,
      completeNode,
      addNode,
      addEdge,
      expandNode,
      collapseNode,
      handleOutlineComplete,
    ]
  );

  // Update refs when handlers change
  useEffect(() => {
    handleContinueToOutlineRef.current = handleContinueToOutline;
  }, [handleContinueToOutline]);

  // References node completion handler (YouTube videos)
  const handleReferencesComplete = useCallback(
    (selectedVideos: VideoInfo[]) => {
      console.log(
        "handleReferencesComplete called with",
        selectedVideos.length,
        "videos"
      );

      updateGenerationState({ selectedVideos });
      completeNode("references", { videos: selectedVideos });

      // Check if addSource node already exists to prevent duplicate edges
      const currentNodes = stateRef.current.nodes;
      const addSourceExists = currentNodes.some((n) => n.id === "addSource");

      // Add the AddSource node connected from Topic
      // Use wrapper function that calls ref to avoid circular dependencies
      addNode(
        "addSource",
        { x: 450, y: 450 },
        {
          label: "Add Sources",
          isExpanded: true,
          isCompleted: false,
          isLoading: false,
          onContinue: (sources: Source[]) =>
            handleContinueToOutlineRef.current(sources),
        },
        true // Skip automatic edge from references to addSource
      );

      // Only add edge if the node didn't already exist
      if (!addSourceExists) {
        addEdge("topic", "addSource");
      }
    },
    [updateGenerationState, completeNode, addNode, addEdge]
  );

  // Topic node completion handler
  const handleTopicComplete = useCallback(
    (topic: string, format: PodcastFormat) => {
      console.log("handleTopicComplete called with", { topic, format });
      updateGenerationState({ topic, format });
      completeNode("topic", { topic, format });

      console.log("Adding references node with handleReferencesComplete");
      // Add References node (YouTube)
      addNode(
        "references",
        { x: 450, y: 200 },
        {
          label: "Reference Videos",
          isExpanded: true,
          isCompleted: false,
          isLoading: false,
          topic,
          format,
          onComplete: handleReferencesComplete,
          onExpand: () => expandNode("references"),
          onCollapse: () => collapseNode("references"),
        }
      );
    },
    [
      updateGenerationState,
      completeNode,
      addNode,
      expandNode,
      collapseNode,
      handleReferencesComplete,
    ]
  );

  // Update initial topic node with handlers
  useEffect(() => {
    updateNodeData("topic", {
      onComplete: handleTopicComplete,
      onExpand: () => expandNode("topic"),
      onCollapse: () => collapseNode("topic"),
    });
  }, [handleTopicComplete, updateNodeData, expandNode, collapseNode]);

  const handleNodeClick = useCallback(
    (_: any, node: any) => {
      if (node.data.isCompleted && !node.data.isExpanded) {
        // Expand the node for viewing/editing
        expandNode(node.id);

        // Remove all nodes after this one to enable editing
        removeNodesAfter(node.id);

        // Reset the node to not completed so it can be edited
        updateNodeData(node.id, { isCompleted: false });
      }
    },
    [expandNode, removeNodesAfter, updateNodeData]
  );

  // Track if we're in edit mode (some completed nodes were removed)
  const hasEditedNode = nodes.some(
    (n: any) => !n.data.isCompleted && n.id !== "topic"
  );

  // Check if audio is completed for confetti
  const audioNode = nodes.find((n: any) => n.id === "audio");
  const showConfetti = audioNode?.data.isCompleted || false;

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* <EditModeIndicator show={hasEditedNode} /> */}
      <ConfettiEffect trigger={showConfetti} />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.2}
        maxZoom={1.5}
        defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
        proOptions={{ hideAttribution: true }}
        className="touch-pan-y"
        panOnScroll
        panOnDrag
        zoomOnScroll
        zoomOnPinch
      >
        <Background color="#374151" gap={16} />
        <Controls className="bg-gray-800 shadow-lg rounded-lg border border-gray-700 [&_button]:bg-gray-700 [&_button]:border-gray-600 [&_button:hover]:bg-gray-600 [&_button_svg]:text-gray-200" />
        <MiniMap
          className="bg-gray-800 shadow-lg rounded-lg border border-gray-700"
          maskColor="rgba(0, 0, 0, 0.5)"
          nodeColor={(node: any) => {
            const colors: Record<string, string> = {
              topicNode: "#3b82f6",
              referencesNode: "#8b5cf6",
              "pdf-sourceNode": "#3b82f6",
              "image-sourceNode": "#10b981",
              "audio-sourceNode": "#a855f7",
              "video-sourceNode": "#f97316",
              addSourceNode: "#6366f1",
              outlineNode: "#14b8a6",
              scriptNode: "#f97316",
              audioNode: "#10b981",
            };
            return colors[node.type || ""] || "#6b7280";
          }}
        />

        {/* Header Panel */}
        <Panel position="top-left" className="m-4">
          <div className="bg-gray-800 rounded-lg shadow-lg p-4 border border-gray-700 max-w-md">
            <h1 className="text-xl font-bold text-white">Podcast Generator</h1>
            <p className="text-xs text-gray-300 mt-1">
              Click nodes to expand • Use arrows to pan • Scroll to zoom
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Press ESC to collapse expanded nodes
            </p>
          </div>
        </Panel>

        {/* Progress Panel */}
        <Panel position="top-right" className="m-4">
          <div className="bg-gray-800 rounded-lg shadow-lg p-3 border border-gray-700">
            <div className="flex gap-2">
              {[
                { label: "Topic", id: "topic" },
                { label: "References", id: "references" },
                { label: "Outline", id: "outline" },
                { label: "Script", id: "script" },
                { label: "Audio", id: "audio" },
              ].map((step, idx) => {
                const node = nodes.find((n: any) => n.id === step.id);
                const isCompleted = node?.data.isCompleted;
                const isActive = node && !isCompleted;

                return (
                  <div
                    key={step.id}
                    className="flex flex-col items-center gap-1"
                  >
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium transition-colors ${
                        isCompleted
                          ? "bg-green-500 text-white"
                          : isActive
                          ? "bg-blue-500 text-white"
                          : "bg-gray-600 text-gray-300"
                      }`}
                    >
                      {idx + 1}
                    </div>
                    <span className="text-xs text-gray-300">{step.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}

function GenerateContent() {
  return (
    <WorkflowErrorBoundary>
      <ReactFlowProvider>
        <WorkflowCanvas />
      </ReactFlowProvider>
    </WorkflowErrorBoundary>
  );
}

export default function GeneratePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
          <div className="text-center">
            <p className="text-gray-300">Loading workflow...</p>
          </div>
        </div>
      }
    >
      <GenerateContent />
    </Suspense>
  );
}
