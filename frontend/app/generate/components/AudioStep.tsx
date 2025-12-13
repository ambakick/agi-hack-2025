'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { convertToSpeech } from '@/lib/api';
import type { ScriptResponse } from '@/lib/types';
import { Loader2, Download, Play, Pause, Volume2 } from 'lucide-react';

interface AudioStepProps {
  script: ScriptResponse;
  onBack: () => void;
}

export function AudioStep({ script, onBack }: AudioStepProps) {
  const [loading, setLoading] = useState(true);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [playing, setPlaying] = useState(false);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);

  useEffect(() => {
    async function generate() {
      try {
        setLoading(true);
        const audioBlob = await convertToSpeech(script);
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        
        const audioElement = new Audio(url);
        setAudio(audioElement);
        
        audioElement.addEventListener('ended', () => setPlaying(false));
      } catch (err) {
        setError('Failed to generate audio. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    generate();

    return () => {
      if (audio) {
        audio.pause();
        audio.remove();
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [script]);

  const togglePlay = () => {
    if (!audio) return;

    if (playing) {
      audio.pause();
      setPlaying(false);
    } else {
      audio.play();
      setPlaying(true);
    }
  };

  const handleDownload = () => {
    if (audioUrl) {
      const a = document.createElement('a');
      a.href = audioUrl;
      a.download = 'podcast.mp3';
      a.click();
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-16">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
            <p className="text-gray-600 font-medium mb-2">
              Converting script to audio with ElevenLabs...
            </p>
            <p className="text-sm text-gray-500">This may take 2-3 minutes</p>
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
          <CardTitle className="flex items-center gap-2">
            <Volume2 className="w-6 h-6 text-primary" />
            Your Podcast is Ready!
          </CardTitle>
          <CardDescription>
            High-quality audio generated with ElevenLabs TTS
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-8 text-center">
            <div className="mb-6">
              <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Volume2 className="w-12 h-12 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Podcast Episode</h3>
              <p className="text-gray-600">
                Duration: ~{Math.round(script.total_duration_seconds / 60)} minutes
              </p>
            </div>

            <div className="flex justify-center gap-4">
              <Button size="lg" onClick={togglePlay}>
                {playing ? (
                  <>
                    <Pause className="w-5 h-5 mr-2" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 mr-2" />
                    Play
                  </>
                )}
              </Button>
              <Button size="lg" variant="outline" onClick={handleDownload}>
                <Download className="w-5 h-5 mr-2" />
                Download MP3
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-between">
        <Button onClick={onBack} variant="outline">
          Back to Script
        </Button>
        <Button onClick={() => (window.location.href = '/')} variant="secondary">
          Create New Podcast
        </Button>
      </div>
    </div>
  );
}

