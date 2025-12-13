"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PodcastFormat } from "@/lib/types";
import { Mic, Users } from "lucide-react";

interface TopicStepProps {
  initialTopic: string;
  onNext: (topic: string, format: PodcastFormat) => void;
}

export function TopicStep({ initialTopic, onNext }: TopicStepProps) {
  const [topic, setTopic] = useState(initialTopic);
  const [format, setFormat] = useState<PodcastFormat>(
    PodcastFormat.SINGLE_HOST
  );

  const handleNext = () => {
    if (topic.trim()) {
      onNext(topic, format);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Podcast Topic</CardTitle>
          <CardDescription>
            Enter your podcast topic and choose the format
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <label htmlFor="topic" className="block text-sm font-medium mb-2">
              Topic
            </label>
            <input
              id="topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="e.g., The Future of Artificial Intelligence"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-3">Format</label>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => setFormat(PodcastFormat.SINGLE_HOST)}
                className={`p-6 rounded-lg border-2 transition-all ${
                  format === PodcastFormat.SINGLE_HOST
                    ? "border-primary bg-primary/5"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <Mic className="w-8 h-8 mx-auto mb-2 text-primary" />
                <h3 className="font-semibold mb-1">Single Host</h3>
                <p className="text-xs text-gray-500">
                  One narrator presents the content
                </p>
              </button>

              <button
                onClick={() => setFormat(PodcastFormat.MULTI_HOST)}
                className={`p-6 rounded-lg border-2 transition-all ${
                  format === PodcastFormat.MULTI_HOST
                    ? "border-primary bg-primary/5"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <Users className="w-8 h-8 mx-auto mb-2 text-primary" />
                <h3 className="font-semibold mb-1">Two Hosts</h3>
                <p className="text-xs text-gray-500">
                  Conversational dialogue between two hosts
                </p>
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleNext} size="lg" disabled={!topic.trim()}>
          Continue to References
        </Button>
      </div>
    </div>
  );
}
