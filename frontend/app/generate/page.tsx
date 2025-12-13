"use client";

import { Suspense, useCallback, useEffect } from "react";
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
import { OutlineNode } from "@/components/workflow/OutlineNode";
import { ScriptNode } from "@/components/workflow/ScriptNode";
import { AudioNode } from "@/components/workflow/AudioNode";
import { EditModeIndicator } from "@/components/workflow/EditModeIndicator";
import { ConfettiEffect } from "@/components/workflow/ConfettiEffect";
import { WorkflowErrorBoundary } from "@/components/workflow/WorkflowErrorBoundary";
import { PodcastFormat } from "@/lib/types";
import type {
  VideoInfo,
  VideoTranscript,
  AnalysisResponse,
  OutlineResponse,
  ScriptResponse,
} from "@/lib/types";

const nodeTypes = {
  topicNode: TopicNode,
  referencesNode: ReferencesNode,
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
  } = useWorkflowState(initialTopic);

  const [nodes, setNodes, onNodesChange] = useNodesState(state.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(state.edges);

  // Sync workflow state with ReactFlow state
  useEffect(() => {
    setNodes(state.nodes);
    setEdges(state.edges);
  }, [state.nodes, state.edges, setNodes, setEdges]);

  // Script node completion handler
  const handleScriptComplete = useCallback(
    (script: ScriptResponse) => {
      console.log("handleScriptComplete called");
      updateGenerationState({ script });
      completeNode("script", { script });

      // Add Audio node
      addNode(
        "audio",
        { x: 1500, y: 200 },
        {
          label: "Podcast Audio",
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
          topic: state.topic,
          format: state.format || PodcastFormat.SINGLE_HOST,
          outline,
          onComplete: handleScriptComplete,
          onExpand: () => expandNode("script"),
          onCollapse: () => collapseNode("script"),
        }
      );
    },
    [
      state.topic,
      state.format,
      updateGenerationState,
      completeNode,
      addNode,
      expandNode,
      collapseNode,
      handleScriptComplete,
    ]
  );

  // References node completion handler
  const handleReferencesComplete = useCallback(
    (selectedVideos: VideoInfo[]) => {
      console.log(
        "handleReferencesComplete called with",
        selectedVideos.length,
        "videos"
      );
      updateGenerationState({ selectedVideos });
      completeNode("references", { videos: selectedVideos });

      console.log("Adding outline node with state:", {
        topic: state.topic,
        format: state.format,
      });

      // Add Outline node
      addNode(
        "outline",
        { x: 800, y: 200 },
        {
          label: "Analysis & Outline",
          isExpanded: true,
          isCompleted: false,
          isLoading: false,
          topic: state.topic,
          format: state.format || PodcastFormat.SINGLE_HOST,
          videos: selectedVideos,
          onComplete: handleOutlineComplete,
          onExpand: () => expandNode("outline"),
          onCollapse: () => collapseNode("outline"),
        }
      );
    },
    [
      state.topic,
      state.format,
      updateGenerationState,
      completeNode,
      addNode,
      expandNode,
      collapseNode,
      handleOutlineComplete,
    ]
  );

  // Topic node completion handler
  const handleTopicComplete = useCallback(
    (topic: string, format: PodcastFormat) => {
      console.log("handleTopicComplete called with", { topic, format });
      updateGenerationState({ topic, format });
      completeNode("topic", { topic, format });

      console.log("Adding references node with handleReferencesComplete");
      // Add References node
      addNode(
        "references",
        { x: 450, y: 200 },
        {
          label: "Reference Videos",
          isExpanded: true,
          isCompleted: false,
          isLoading: false,
          topic,
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
    (n) => !n.data.isCompleted && n.id !== "topic"
  );

  // Check if audio is completed for confetti
  const audioNode = nodes.find((n) => n.id === "audio");
  const showConfetti = audioNode?.data.isCompleted || false;

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <EditModeIndicator show={hasEditedNode} />
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
          nodeColor={(node) => {
            const colors: Record<string, string> = {
              topicNode: "#3b82f6",
              referencesNode: "#8b5cf6",
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
              {["Topic", "References", "Outline", "Script", "Audio"].map(
                (label, idx) => {
                  const nodeId = label.toLowerCase();
                  const node = nodes.find((n) => n.id === nodeId);
                  const isCompleted = node?.data.isCompleted;
                  const isActive = node && !isCompleted;

                  return (
                    <div
                      key={label}
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
                      <span className="text-xs text-gray-300">{label}</span>
                    </div>
                  );
                }
              )}
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
