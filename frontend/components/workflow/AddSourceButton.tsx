"use client";

import { useState } from "react";
import { Plus, FileText, Image, Music, Video, ChevronDown } from "lucide-react";
import { SourceType } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface AddSourceButtonProps {
  onAddSource: (sourceType: SourceType) => void;
  onContinue: () => void;
  isVisible: boolean;
}

const sourceOptions = [
  {
    type: SourceType.PDF,
    label: "PDF Document",
    icon: FileText,
    color: "text-blue-500",
    bgColor: "hover:bg-blue-500/10",
  },
  {
    type: SourceType.IMAGE,
    label: "Image",
    icon: Image,
    color: "text-green-500",
    bgColor: "hover:bg-green-500/10",
  },
  {
    type: SourceType.AUDIO,
    label: "Audio File",
    icon: Music,
    color: "text-purple-500",
    bgColor: "hover:bg-purple-500/10",
  },
  {
    type: SourceType.VIDEO,
    label: "Video File",
    icon: Video,
    color: "text-orange-500",
    bgColor: "hover:bg-orange-500/10",
  },
];

export function AddSourceButton({
  onAddSource,
  onContinue,
  isVisible,
}: AddSourceButtonProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  if (!isVisible) return null;

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl border border-gray-700 p-4 min-w-[280px]">
      {/* Add Source Menu */}
      <div className="space-y-2">
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="w-full flex items-center justify-between px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-white font-medium"
        >
          <div className="flex items-center gap-2">
            <Plus className="w-5 h-5" />
            <span>Add Additional Source</span>
          </div>
          <ChevronDown
            className={cn(
              "w-4 h-4 transition-transform",
              isMenuOpen && "rotate-180"
            )}
          />
        </button>

        {/* Source Type Options */}
        {isMenuOpen && (
          <div className="space-y-1 animate-in fade-in slide-in-from-top-2 duration-200">
            {sourceOptions.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.type}
                  onClick={() => {
                    onAddSource(option.type);
                    setIsMenuOpen(false);
                  }}
                  className={cn(
                    "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors text-left",
                    "bg-gray-700/50 hover:bg-gray-700",
                    option.bgColor
                  )}
                >
                  <Icon className={cn("w-5 h-5", option.color)} />
                  <span className="text-white font-medium">{option.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Continue Button */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <Button onClick={onContinue} className="w-full" size="lg">
          Continue to Outline →
        </Button>
      </div>

      <p className="text-xs text-gray-400 mt-2 text-center">
        Add sources or continue to generate outline
      </p>
    </div>
  );
}
