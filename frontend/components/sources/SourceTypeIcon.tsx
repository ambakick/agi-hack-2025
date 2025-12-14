"use client";

import { FileText, Image, Music, Video, Youtube, LucideIcon } from "lucide-react";
import { SourceType } from "@/lib/types";
import { cn } from "@/lib/utils";

interface SourceTypeIconProps {
  type: SourceType;
  className?: string;
}

const iconMap: Record<SourceType, LucideIcon> = {
  [SourceType.YOUTUBE]: Youtube,
  [SourceType.PDF]: FileText,
  [SourceType.IMAGE]: Image,
  [SourceType.AUDIO]: Music,
  [SourceType.VIDEO]: Video,
};

export function SourceTypeIcon({ type, className }: SourceTypeIconProps) {
  const Icon = iconMap[type];
  return <Icon className={cn("w-4 h-4", className)} />;
}
