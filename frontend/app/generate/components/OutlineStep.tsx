'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { getTranscripts, analyzeContent, generateOutline } from '@/lib/api';
import type {
  VideoInfo,
  VideoTranscript,
  AnalysisResponse,
  OutlineResponse,
  PodcastFormat,
  OutlineSection,
} from '@/lib/types';
import { Loader2, FileText, Clock } from 'lucide-react';

interface OutlineStepProps {
  topic: string;
  format: PodcastFormat;
  selectedVideos: VideoInfo[];
  onNext: (
    transcripts: VideoTranscript[],
    analysis: AnalysisResponse,
    outline: OutlineResponse
  ) => void;
  onBack: () => void;
}

export function OutlineStep({
  topic,
  format,
  selectedVideos,
  onNext,
  onBack,
}: OutlineStepProps) {
  const [loading, setLoading] = useState(true);
  const [stage, setStage] = useState<'transcripts' | 'analysis' | 'outline' | 'done'>(
    'transcripts'
  );
  const [transcripts, setTranscripts] = useState<VideoTranscript[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [outline, setOutline] = useState<OutlineResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function process() {
      try {
        // Fetch transcripts
        setStage('transcripts');
        const videoIds = selectedVideos.map((v) => v.video_id);
        const transcriptResults = await getTranscripts(videoIds);
        setTranscripts(transcriptResults);

        // Analyze content
        setStage('analysis');
        const analysisResults = await analyzeContent(transcriptResults, topic);
        setAnalysis(analysisResults);

        // Generate outline
        setStage('outline');
        const outlineResults = await generateOutline(analysisResults, topic, format, 15);
        setOutline(outlineResults);

        setStage('done');
        setLoading(false);
      } catch (err) {
        setError('Failed to generate outline. Please try again.');
        console.error(err);
        setLoading(false);
      }
    }

    process();
  }, [topic, format, selectedVideos]);

  const handleNext = () => {
    if (transcripts && analysis && outline) {
      onNext(transcripts, analysis, outline);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-16">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
            <p className="text-gray-600 font-medium mb-2">
              {stage === 'transcripts' && 'Fetching video transcripts...'}
              {stage === 'analysis' && 'Analyzing content with Gemini...'}
              {stage === 'outline' && 'Generating episode outline...'}
            </p>
            <p className="text-sm text-gray-500">This may take a minute</p>
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
      {/* Analysis Summary */}
      {analysis && (
        <Card>
          <CardHeader>
            <CardTitle>Content Analysis</CardTitle>
            <CardDescription>Key themes identified from reference podcasts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Summary</h4>
                <p className="text-sm text-gray-600">{analysis.summary}</p>
              </div>
              <div>
                <h4 className="font-medium mb-2">Major Themes</h4>
                <ul className="space-y-2">
                  {analysis.themes.map((theme, idx) => (
                    <li key={idx} className="text-sm">
                      <span className="font-medium">{theme.theme}:</span>{' '}
                      {theme.description}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Outline */}
      {outline && (
        <Card>
          <CardHeader>
            <CardTitle>Episode Outline</CardTitle>
            <CardDescription>
              Structured plan for your podcast episode (~{Math.round(outline.total_duration_minutes)}{' '}
              minutes)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {outline.sections.map((section: OutlineSection, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold">
                      {idx + 1}. {section.title}
                    </h4>
                    <div className="flex items-center text-sm text-gray-500">
                      <Clock className="w-4 h-4 mr-1" />
                      {Math.round(section.duration_minutes)}m
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{section.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex justify-between">
        <Button onClick={onBack} variant="outline">
          Back
        </Button>
        <Button onClick={handleNext} size="lg">
          Generate Script
        </Button>
      </div>
    </div>
  );
}
