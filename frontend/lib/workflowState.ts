"use client";

import { useState, useCallback, useMemo } from "react";
import { Node, Edge } from "reactflow";
import type {
  GenerationState,
  VideoInfo,
  VideoTranscript,
  AnalysisResponse,
  OutlineResponse,
  ScriptResponse,
  PodcastFormat,
} from "./types";

export interface WorkflowNodeData {
  label: string;
  isExpanded: boolean;
  isCompleted: boolean;
  isLoading: boolean;
  topic?: string;
  format?: PodcastFormat;
  videos?: VideoInfo[];
  transcripts?: VideoTranscript[];
  analysis?: AnalysisResponse;
  outline?: OutlineResponse;
  script?: ScriptResponse;
  audioUrl?: string | null;
  videoUrl?: string | null;
  onComplete?: (...args: any[]) => void;
  onExpand?: () => void;
  onCollapse?: () => void;
  [key: string]: any; // Allow additional properties
}

interface WorkflowState {
  nodes: Node<WorkflowNodeData>[];
  edges: Edge[];
  generationState: GenerationState;
}

const createInitialNode = (
  id: string,
  position: { x: number; y: number },
  data: WorkflowNodeData
): Node<WorkflowNodeData> => ({
  id,
  type: `${id}Node`,
  position,
  data,
});

export function useWorkflowState(initialTopic: string = "") {
  const [generationState, setGenerationState] = useState<GenerationState>({
    topic: initialTopic,
    format: "single" as PodcastFormat,
    selectedVideos: [],
    transcripts: [],
    analysis: null,
    outline: null,
    script: null,
    audioUrl: null,
    videoUrl: null,
  });

  const [nodes, setNodes] = useState<Node<WorkflowNodeData>[]>([
    createInitialNode("topic", { x: 100, y: 200 }, {
      label: "Topic",
      isExpanded: true,
      isCompleted: false,
      isLoading: false,
      topic: initialTopic,
      format: "single" as PodcastFormat,
    }),
  ]);

  const [edges, setEdges] = useState<Edge[]>([]);

  const updateGenerationState = useCallback(
    (updates: Partial<GenerationState>) => {
      setGenerationState((prev) => ({ ...prev, ...updates }));
    },
    []
  );

  const updateNodeData = useCallback(
    (nodeId: string, updates: Partial<WorkflowNodeData>) => {
      setNodes((prevNodes) =>
        prevNodes.map((node) =>
          node.id === nodeId
            ? { ...node, data: { ...node.data, ...updates } }
            : node
        )
      );
    },
    []
  );

  const addNode = useCallback(
    (
      nodeId: string,
      position: { x: number; y: number },
      data: WorkflowNodeData
    ) => {
      const newNode = createInitialNode(nodeId, position, data);

      setNodes((prevNodes) => {
        // Check if node already exists
        if (prevNodes.find((n) => n.id === nodeId)) {
          return prevNodes.map((node) =>
            node.id === nodeId ? newNode : node
          );
        }
        
        // Store the last node before adding new one
        const lastNode = prevNodes[prevNodes.length - 1];
        const updatedNodes = [...prevNodes, newNode];
        
        // Add edge from previous node
        setEdges((prevEdges) => {
          if (prevEdges.length === 0) {
            return [{ id: `e-topic-${nodeId}`, source: "topic", target: nodeId }];
          }
          if (lastNode) {
            return [
              ...prevEdges,
              { id: `e-${lastNode.id}-${nodeId}`, source: lastNode.id, target: nodeId },
            ];
          }
          return prevEdges;
        });
        
        return updatedNodes;
      });
    },
    []
  );

  const expandNode = useCallback((nodeId: string) => {
    updateNodeData(nodeId, { isExpanded: true });
  }, [updateNodeData]);

  const collapseNode = useCallback((nodeId: string) => {
    updateNodeData(nodeId, { isExpanded: false });
  }, [updateNodeData]);

  const completeNode = useCallback(
    (nodeId: string, data?: Partial<WorkflowNodeData>) => {
      updateNodeData(nodeId, {
        isCompleted: true,
        isExpanded: false,
        isLoading: false,
        ...data,
      });
    },
    [updateNodeData]
  );

  const removeNodesAfter = useCallback((nodeId: string) => {
    setNodes((prevNodes) => {
      const nodeIndex = prevNodes.findIndex((n) => n.id === nodeId);
      if (nodeIndex === -1) return prevNodes;
      
      // Update edges based on the updated nodes
      setEdges((prevEdges) => {
        // Remove edges that connect to removed nodes
        const remainingNodeIds = new Set(
          prevNodes.slice(0, nodeIndex + 1).map((n) => n.id)
        );
        return prevEdges.filter(
          (edge) =>
            remainingNodeIds.has(edge.source) && remainingNodeIds.has(edge.target)
        );
      });
      
      return prevNodes.slice(0, nodeIndex + 1);
    });
  }, []);

  const state = useMemo<WorkflowState>(
    () => ({
      nodes,
      edges,
      generationState,
    }),
    [nodes, edges, generationState]
  );

  return {
    state,
    updateNodeData,
    addNode,
    expandNode,
    collapseNode,
    completeNode,
    removeNodesAfter,
    updateGenerationState,
  };
}

