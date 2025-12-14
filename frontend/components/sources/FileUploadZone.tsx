"use client";

import { useState, useCallback } from "react";
import { Upload, FileText, Image, Music, Video, Loader2 } from "lucide-react";
import { SourceType } from "@/lib/types";
import { cn } from "@/lib/utils";

interface FileUploadZoneProps {
  onFileSelect: (file: File, sourceType: SourceType) => void;
  isUploading?: boolean;
  className?: string;
}

const acceptedFileTypes = {
  [SourceType.PDF]: {
    mimeTypes: ["application/pdf"],
    extensions: [".pdf"],
    icon: FileText,
    label: "PDF",
  },
  [SourceType.IMAGE]: {
    mimeTypes: ["image/jpeg", "image/png", "image/gif", "image/webp"],
    extensions: [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    icon: Image,
    label: "Image",
  },
  [SourceType.AUDIO]: {
    mimeTypes: ["audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4"],
    extensions: [".mp3", ".wav", ".ogg", ".m4a"],
    icon: Music,
    label: "Audio",
  },
  [SourceType.VIDEO]: {
    mimeTypes: ["video/mp4", "video/webm", "video/ogg", "video/quicktime"],
    extensions: [".mp4", ".webm", ".ogg", ".mov"],
    icon: Video,
    label: "Video",
  },
};

function getSourceTypeFromFile(file: File): SourceType | null {
  const mimeType = file.type.toLowerCase();
  
  for (const [sourceType, config] of Object.entries(acceptedFileTypes)) {
    if (config.mimeTypes.some((type) => mimeType.includes(type.split("/")[1]))) {
      return sourceType as SourceType;
    }
  }
  
  // Fallback to extension check
  const extension = file.name.toLowerCase().match(/\.[^.]+$/)?.[0];
  if (!extension) return null;
  
  for (const [sourceType, config] of Object.entries(acceptedFileTypes)) {
    if (config.extensions.includes(extension)) {
      return sourceType as SourceType;
    }
  }
  
  return null;
}

export function FileUploadZone({ onFileSelect, isUploading, className }: FileUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      setError(null);

      const files = Array.from(e.dataTransfer.files);
      if (files.length === 0) return;

      const file = files[0]; // Only handle first file
      const sourceType = getSourceTypeFromFile(file);

      if (!sourceType) {
        setError("Unsupported file type. Please upload a PDF, image, audio, or video file.");
        return;
      }

      onFileSelect(file, sourceType);
    },
    [onFileSelect]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setError(null);
      const files = e.target.files;
      if (!files || files.length === 0) return;

      const file = files[0];
      const sourceType = getSourceTypeFromFile(file);

      if (!sourceType) {
        setError("Unsupported file type. Please upload a PDF, image, audio, or video file.");
        return;
      }

      onFileSelect(file, sourceType);
      
      // Reset input
      e.target.value = "";
    },
    [onFileSelect]
  );

  const allExtensions = Object.values(acceptedFileTypes)
    .flatMap((config) => config.extensions)
    .join(",");

  return (
    <div className={cn("space-y-4", className)}>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "relative border-2 border-dashed rounded-lg p-8 text-center transition-colors",
          isDragging
            ? "border-blue-500 bg-blue-500/10"
            : "border-gray-600 bg-gray-800/50 hover:border-gray-500",
          isUploading && "opacity-50 pointer-events-none"
        )}
      >
        <input
          type="file"
          id="file-upload"
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          accept={allExtensions}
          onChange={handleFileInput}
          disabled={isUploading}
        />

        <div className="flex flex-col items-center gap-3">
          {isUploading ? (
            <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
          ) : (
            <Upload className="w-12 h-12 text-gray-400" />
          )}

          <div>
            <p className="text-base font-medium text-gray-200">
              {isUploading ? "Uploading..." : "Drag & drop files here"}
            </p>
            <p className="text-sm text-gray-400 mt-1">or click to browse</p>
          </div>

          <div className="flex gap-2 text-xs text-gray-500">
            <span>Supports: PDF, Image, Audio, Video</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Supported file types */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {Object.entries(acceptedFileTypes).map(([sourceType, config]) => {
          const Icon = config.icon;
          return (
            <div
              key={sourceType}
              className="flex items-center gap-2 p-2 bg-gray-800 rounded-lg border border-gray-700"
            >
              <Icon className="w-4 h-4 text-gray-400" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-gray-300">{config.label}</p>
                <p className="text-xs text-gray-500 truncate">
                  {config.extensions.join(", ")}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
