'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { VideoCard } from '@/components/VideoCard';
import { discoverVideos } from '@/lib/api';
import type { VideoInfo } from '@/lib/types';
import { Loader2 } from 'lucide-react';

interface ReferencesStepProps {
  topic: string;
  onNext: (selectedVideos: VideoInfo[]) => void;
  onBack: () => void;
}

export function ReferencesStep({ topic, onNext, onBack }: ReferencesStepProps) {
  const [videos, setVideos] = useState<VideoInfo[]>([]);
  const [selectedVideos, setSelectedVideos] = useState<VideoInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchVideos() {
      try {
        setLoading(true);
        const results = await discoverVideos(topic, 12);
        setVideos(results);
      } catch (err) {
        setError('Failed to fetch videos. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchVideos();
  }, [topic]);

  const toggleVideo = (video: VideoInfo) => {
    if (selectedVideos.find((v) => v.video_id === video.video_id)) {
      setSelectedVideos(selectedVideos.filter((v) => v.video_id !== video.video_id));
    } else if (selectedVideos.length < 5) {
      setSelectedVideos([...selectedVideos, video]);
    }
  };

  const handleNext = () => {
    if (selectedVideos.length > 0) {
      onNext(selectedVideos);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-16">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
            <p className="text-gray-600">Searching for relevant podcasts...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-16">
          <div className="text-center">
            <p className="text-red-500 mb-4">{error}</p>
            <Button onClick={onBack}>Go Back</Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Select Reference Podcasts</CardTitle>
          <CardDescription>
            Choose 1-5 podcast episodes to use as reference material (
            {selectedVideos.length}/5 selected)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {videos.map((video) => (
              <VideoCard
                key={video.video_id}
                video={video}
                selected={!!selectedVideos.find((v) => v.video_id === video.video_id)}
                onToggle={() => toggleVideo(video)}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-between">
        <Button onClick={onBack} variant="outline">
          Back
        </Button>
        <Button
          onClick={handleNext}
          size="lg"
          disabled={selectedVideos.length === 0}
        >
          Continue to Analysis ({selectedVideos.length} selected)
        </Button>
      </div>
    </div>
  );
}

