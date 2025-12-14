"use client";

import { X, FileText, Image as ImageIcon, Music, Video, Youtube } from "lucide-react";
import { Source, SourceType } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface SourceCardProps {
  source: Source;
  onRemove?: () => void;
  className?: string;
}

const sourceTypeConfig = {
  [SourceType.YOUTUBE]: {
    icon: Youtube,
    color: "bg-red-500",
    textColor: "text-red-500",
    bgLight: "bg-red-500/10",
    label: "YouTube",
  },
  [SourceType.PDF]: {
    icon: FileText,
    color: "bg-blue-500",
    textColor: "text-blue-500",
    bgLight: "bg-blue-500/10",
    label: "PDF",
  },
  [SourceType.IMAGE]: {
    icon: ImageIcon,
    color: "bg-green-500",
    textColor: "text-green-500",
    bgLight: "bg-green-500/10",
    label: "Image",
  },
  [SourceType.AUDIO]: {
    icon: Music,
    color: "bg-purple-500",
    textColor: "text-purple-500",
    bgLight: "bg-purple-500/10",
    label: "Audio",
  },
  [SourceType.VIDEO]: {
    icon: Video,
    color: "bg-orange-500",
    textColor: "text-orange-500",
    bgLight: "bg-orange-500/10",
    label: "Video",
  },
};

function formatFileSize(bytes?: number): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function SourceCard({ source, onRemove, className }: SourceCardProps) {
  const config = sourceTypeConfig[source.type];
  const Icon = config.icon;

  const getMetadataLine = () => {
    if (source.type === SourceType.YOUTUBE) {
      const views = source.metadata?.view_count
        ? `${source.metadata.view_count.toLocaleString()} views`
        : "";
      const duration = source.metadata?.duration || "";
      return [duration, views].filter(Boolean).join(" • ");
    } else {
      const size = formatFileSize(source.metadata?.file_size);
      const pages = source.metadata?.page_count
        ? `${source.metadata.page_count} pages`
        : "";
      return [size, pages].filter(Boolean).join(" • ");
    }
  };

  return (
    <Card
      className={cn(
        "relative group bg-gray-800 border-gray-700 overflow-hidden transition-all hover:border-gray-600",
        className
      )}
    >
      {/* Thumbnail/Preview */}
      <div className="relative h-32 bg-gray-900 flex items-center justify-center overflow-hidden">
        {source.thumbnail_url ? (
          <img
            src={source.thumbnail_url}
            alt={source.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className={cn("w-12 h-12 rounded-full flex items-center justify-center", config.bgLight)}>
            <Icon className={cn("w-6 h-6", config.textColor)} />
          </div>
        )}
        
        {/* Type Badge */}
        <div className={cn("absolute top-2 left-2 px-2 py-1 rounded-md flex items-center gap-1", config.color)}>
          <Icon className="w-3 h-3 text-white" />
          <span className="text-xs font-medium text-white">{config.label}</span>
        </div>

        {/* Remove Button */}
        {onRemove && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRemove();
            }}
            className="absolute top-2 right-2 w-6 h-6 rounded-full bg-gray-900/80 hover:bg-red-500 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
            title="Remove source"
          >
            <X className="w-4 h-4 text-white" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="p-3">
        <h3 className="font-medium text-sm text-white line-clamp-2 mb-1">
          {source.name}
        </h3>
        
        {source.type === SourceType.YOUTUBE && source.metadata?.channel_name && (
          <p className="text-xs text-gray-400 mb-1">{source.metadata.channel_name}</p>
        )}
        
        {getMetadataLine() && (
          <p className="text-xs text-gray-500">{getMetadataLine()}</p>
        )}
      </div>
    </Card>
  );
}
