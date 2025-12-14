"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { generateScript } from "@/lib/api";
import { PodcastFormat } from "@/lib/types";
import type { OutlineResponse, ScriptResponse } from "@/lib/types";
import { Loader2, User, Users } from "lucide-react";

interface ScriptStepProps {
  topic: string;
  format: PodcastFormat;
  outline: OutlineResponse;
  onNext: (script: ScriptResponse) => void;
  onBack: () => void;
}

export function ScriptStep({
  topic,
  format,
  outline,
  onNext,
  onBack,
}: ScriptStepProps) {
  const [loading, setLoading] = useState(true);
  const [script, setScript] = useState<ScriptResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function generate() {
      try {
        setLoading(true);
        const result = await generateScript(outline, topic, format);
        setScript(result);
      } catch (err) {
        setError("Failed to generate script. Please try again.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    generate();
  }, [topic, format, outline]);

  const handleNext = () => {
    if (script) {
      onNext(script);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-16">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
            <p className="text-gray-600 font-medium mb-2">
              Generating podcast script with Gemini 3...
            </p>
            <p className="text-sm text-gray-500">This may take 1-2 minutes</p>
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
      {script && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Podcast Script</CardTitle>
                <CardDescription>
                  {format === PodcastFormat.TWO_HOSTS
                    ? "Conversational script with two hosts"
                    : "Single narrator script"}
                </CardDescription>
              </div>
              <div className="text-sm text-gray-500">
                ~{Math.round(script.total_duration_seconds / 60)} minutes
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 rounded-lg p-6 max-h-96 overflow-y-auto">
              {format === PodcastFormat.TWO_HOSTS ? (
                <div className="space-y-4">
                  {script.segments.map((segment, idx) => (
                    <div key={idx} className="flex gap-3">
                      <div className="flex-shrink-0">
                        {segment.speaker === "HOST_1" ? (
                          <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm">
                            H1
                          </div>
                        ) : (
                          <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center text-white text-sm">
                            H2
                          </div>
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-700 mb-1">
                          {segment.speaker === "HOST_1" ? "Host 1" : "Host 2"}
                        </p>
                        <p className="text-sm text-gray-600">{segment.text}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="prose prose-sm max-w-none">
                  <p className="whitespace-pre-wrap text-gray-700">
                    {script.full_script}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex justify-between">
        <Button onClick={onBack} variant="outline">
          Back
        </Button>
        <Button onClick={handleNext} size="lg">
          Generate Audio
        </Button>
      </div>
    </div>
  );
}
