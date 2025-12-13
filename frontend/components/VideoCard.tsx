'use client';

import Image from 'next/image';
import { Check } from 'lucide-react';
import type { VideoInfo } from '@/lib/types';
import { Card } from '@/components/ui/card';

interface VideoCardProps {
  video: VideoInfo;
  selected: boolean;
  onToggle: () => void;
}

export function VideoCard({ video, selected, onToggle }: VideoCardProps) {
  return (
    <Card
      className={`cursor-pointer transition-all ${
        selected ? 'ring-2 ring-primary shadow-lg' : 'hover:shadow-md'
      }`}
      onClick={onToggle}
    >
      <div className="relative">
        <Image
          src={video.thumbnail_url}
          alt={video.title}
          width={480}
          height={360}
          className="w-full h-48 object-cover rounded-t-lg"
        />
        {selected && (
          <div className="absolute top-2 right-2 bg-primary text-white rounded-full p-2">
            <Check className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-sm line-clamp-2 mb-2">
          {video.title}
        </h3>
        <p className="text-xs text-gray-500">{video.channel_name}</p>
        <p className="text-xs text-gray-400 mt-1">
          {video.view_count.toLocaleString()} views
        </p>
      </div>
    </Card>
  );
}

