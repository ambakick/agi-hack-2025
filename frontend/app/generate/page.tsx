'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { TopicStep } from './components/TopicStep';
import { ReferencesStep } from './components/ReferencesStep';
import { OutlineStep } from './components/OutlineStep';
import { ScriptStep } from './components/ScriptStep';
import { AudioStep } from './components/AudioStep';
import { VideoStep } from './components/VideoStep';
import { Progress } from '@/components/ui/progress';
import { PodcastFormat } from '@/lib/types';
import type {
  VideoInfo,
  VideoTranscript,
  AnalysisResponse,
  OutlineResponse,
  ScriptResponse,
  GenerationState,
} from '@/lib/types';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

type Step = 'topic' | 'references' | 'outline' | 'script' | 'audio' | 'video';

function GenerateContent() {
  const searchParams = useSearchParams();
  const initialTopic = searchParams.get('topic') || '';

  const [step, setStep] = useState<Step>('topic');
  const [state, setState] = useState<GenerationState>({
    topic: initialTopic,
    format: PodcastFormat.SINGLE_HOST,
    selectedVideos: [],
    transcripts: [],
    analysis: null,
    outline: null,
    script: null,
    audioUrl: null,
    videoUrl: null,
  });

  const steps: { id: Step; label: string }[] = [
    { id: 'topic', label: 'Topic' },
    { id: 'references', label: 'References' },
    { id: 'outline', label: 'Outline' },
    { id: 'script', label: 'Script' },
    { id: 'audio', label: 'Audio' },
    { id: 'video', label: 'Video' },
  ];

  const currentStepIndex = steps.findIndex((s) => s.id === step);
  const progress = ((currentStepIndex + 1) / steps.length) * 100;

  const handleTopicNext = (topic: string, format: PodcastFormat) => {
    setState({ ...state, topic, format });
    setStep('references');
  };

  const handleReferencesNext = (selectedVideos: VideoInfo[]) => {
    setState({ ...state, selectedVideos });
    setStep('outline');
  };

  const handleOutlineNext = (
    transcripts: VideoTranscript[],
    analysis: AnalysisResponse,
    outline: OutlineResponse
  ) => {
    setState({ ...state, transcripts, analysis, outline });
    setStep('script');
  };

  const handleScriptNext = (script: ScriptResponse) => {
    setState({ ...state, script });
    setStep('audio');
  };

  const handleAudioNext = () => {
    setStep('video');
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/"
            className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>

          <h1 className="text-3xl font-bold mb-2">Generate Podcast</h1>
          <p className="text-gray-600 mb-6">
            Follow the steps to create your AI-powered podcast episode
          </p>

          {/* Progress Bar */}
          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
            <div className="flex justify-between mb-2">
              {steps.map((s, idx) => (
                <div
                  key={s.id}
                  className={`flex-1 text-center ${
                    idx === currentStepIndex
                      ? 'text-primary font-semibold'
                      : idx < currentStepIndex
                      ? 'text-gray-700'
                      : 'text-gray-400'
                  }`}
                >
                  <div className="text-sm">{s.label}</div>
                </div>
              ))}
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        </div>

        {/* Step Content */}
        <div>
          {step === 'topic' && (
            <TopicStep initialTopic={state.topic} onNext={handleTopicNext} />
          )}

          {step === 'references' && (
            <ReferencesStep
              topic={state.topic}
              onNext={handleReferencesNext}
              onBack={() => setStep('topic')}
            />
          )}

          {step === 'outline' && (
            <OutlineStep
              topic={state.topic}
              format={state.format}
              selectedVideos={state.selectedVideos}
              onNext={handleOutlineNext}
              onBack={() => setStep('references')}
            />
          )}

          {step === 'script' && state.outline && (
            <ScriptStep
              topic={state.topic}
              format={state.format}
              outline={state.outline}
              onNext={handleScriptNext}
              onBack={() => setStep('outline')}
            />
          )}

          {step === 'audio' && state.script && (
            <AudioStep 
              script={state.script} 
              onBack={() => setStep('script')}
              onNext={handleAudioNext}
            />
          )}

          {step === 'video' && state.script && (
            <VideoStep 
              script={state.script} 
              onBack={() => setStep('audio')}
            />
          )}
        </div>
      </div>
    </main>
  );
}

export default function GeneratePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      }
    >
      <GenerateContent />
    </Suspense>
  );
}

