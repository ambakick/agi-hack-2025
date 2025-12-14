"use client";

import { useState } from "react";
import { NodeProps, Handle, Position } from "reactflow";
import {
  Plus,
  FileText,
  Image,
  Music,
  Video,
  ChevronDown,
  FolderPlus,
  ArrowRight,
  X,
} from "lucide-react";
import { WorkflowNodeData } from "@/lib/workflowState";
import { Source, SourceType } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { FileUploadZone } from "@/components/sources/FileUploadZone";
import { uploadSource } from "@/lib/api";

interface AddSourceNodeProps extends NodeProps {
  data: WorkflowNodeData & {
    onContinue?: (sources: Source[]) => void;
  };
}

const sourceOptions = [
  {
    type: SourceType.PDF,
    label: "PDF Document",
    icon: FileText,
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
  },
  {
    type: SourceType.IMAGE,
    label: "Image",
    icon: Image,
    color: "text-green-500",
    bgColor: "bg-green-500/10",
  },
  {
    type: SourceType.AUDIO,
    label: "Audio File",
    icon: Music,
    color: "text-purple-500",
    bgColor: "bg-purple-500/10",
  },
  {
    type: SourceType.VIDEO,
    label: "Video File",
    icon: Video,
    color: "text-orange-500",
    bgColor: "bg-orange-500/10",
  },
];

const getSourceIcon = (type: SourceType) => {
  const option = sourceOptions.find((opt) => opt.type === type);
  return option?.icon || FileText;
};

const getSourceColor = (type: SourceType) => {
  const option = sourceOptions.find((opt) => opt.type === type);
  return option?.color || "text-gray-500";
};

const getSourceBgColor = (type: SourceType) => {
  const option = sourceOptions.find((opt) => opt.type === type);
  return option?.bgColor || "bg-gray-500/10";
};

export function AddSourceNode({ id, data }: AddSourceNodeProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [sources, setSources] = useState<Source[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [showUploadZone, setShowUploadZone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelectSourceType = (sourceType: SourceType) => {
    setIsMenuOpen(false);
    setShowUploadZone(true);
    setError(null);
  };

  const handleFileSelect = async (file: File, sourceType: SourceType) => {
    try {
      setIsUploading(true);
      setError(null);

      const uploadedSource = await uploadSource(file, sourceType);
      setSources((prev) => [...prev, uploadedSource]);
      setShowUploadZone(false);
    } catch (err) {
      console.error("Failed to upload source:", err);
      setError("Failed to upload file. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveSource = (sourceId: string) => {
    setSources((prev) => prev.filter((s) => s.id !== sourceId));
  };

  const handleContinue = () => {
    if (data.onContinue) {
      data.onContinue(sources);
    }
  };

  return (
    <div
      className="bg-gray-800 rounded-xl border-l-4 shadow-lg"
      style={{
        borderLeftColor: "#6366f1",
        width: "280px",
        minHeight: "120px",
      }}
    >
      {/* Handles for ReactFlow connections */}
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 !bg-gray-400"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 !bg-gray-400"
      />

      {/* Header */}
      <div className="p-4 flex items-center gap-3">
        <div
          className="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: "#6366f120", color: "#6366f1" }}
        >
          <FolderPlus className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white text-sm">Add Sources</h3>
          <p className="text-xs text-gray-400 mt-0.5">
            {sources.length > 0
              ? `${sources.length} source${sources.length > 1 ? "s" : ""} added`
              : "Optional: add more sources"}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 pb-4 space-y-3">
        {/* Uploaded Sources List */}
        {sources.length > 0 && (
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {sources.map((source) => {
              const Icon = getSourceIcon(source.type);
              const color = getSourceColor(source.type);
              const bgColor = getSourceBgColor(source.type);

              return (
                <div
                  key={source.id}
                  className="flex items-center gap-2 p-2 bg-gray-700 rounded-lg group hover:bg-gray-600 transition-colors"
                >
                  <div className={cn("p-1.5 rounded", bgColor)}>
                    <Icon className={cn("w-3.5 h-3.5", color)} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white font-medium truncate">
                      {source.name}
                    </p>
                    {source.metadata?.file_size && (
                      <p className="text-xs text-gray-400">
                        {(
                          (source.metadata.file_size || 0) /
                          1024 /
                          1024
                        ).toFixed(1)}{" "}
                        MB
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveSource(source.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-500 rounded transition-opacity"
                  >
                    <X className="w-3.5 h-3.5 text-gray-300" />
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {/* Upload Zone */}
        {showUploadZone && (
          <div className="space-y-2">
            <FileUploadZone
              onFileSelect={handleFileSelect}
              isUploading={isUploading}
              className="scale-90"
            />
            <Button
              onClick={() => setShowUploadZone(false)}
              variant="outline"
              size="sm"
              className="w-full"
            >
              Cancel
            </Button>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="p-2 bg-red-900/30 border border-red-700 rounded-lg">
            <p className="text-xs text-red-400">{error}</p>
          </div>
        )}

        {/* Add Source Button */}
        {!showUploadZone && (
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="w-full flex items-center justify-between px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-white text-sm font-medium"
          >
            <div className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              <span>Add Source</span>
            </div>
            <ChevronDown
              className={cn(
                "w-4 h-4 transition-transform",
                isMenuOpen && "rotate-180"
              )}
            />
          </button>
        )}

        {/* Source Type Options */}
        {isMenuOpen && !showUploadZone && (
          <div className="space-y-1 animate-in fade-in slide-in-from-top-2 duration-200">
            {sourceOptions.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.type}
                  onClick={() => handleSelectSourceType(option.type)}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-left text-sm",
                    "bg-gray-700/50 hover:bg-gray-700"
                  )}
                >
                  <div className={cn("p-1 rounded", option.bgColor)}>
                    <Icon className={cn("w-4 h-4", option.color)} />
                  </div>
                  <span className="text-white">{option.label}</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Continue Button */}
        {!showUploadZone && (
          <Button onClick={handleContinue} className="w-full" size="sm">
            <span>Continue to Outline</span>
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        )}
      </div>
    </div>
  );
}
