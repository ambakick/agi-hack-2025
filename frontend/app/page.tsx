'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Mic, Sparkles, Youtube, Zap } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const [topic, setTopic] = useState('');

  const handleStart = () => {
    if (topic.trim()) {
      router.push(`/generate?topic=${encodeURIComponent(topic)}`);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center mb-6">
            <div className="bg-primary/10 p-4 rounded-full">
              <Mic className="w-12 h-12 text-primary" />
            </div>
          </div>
          <h1 className="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
            AI Podcast Generator
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Create professional podcast episodes from any topic using advanced AI.
            Research, script, and produce in minutes.
          </p>
        </div>

        {/* Main Input */}
        <div className="max-w-3xl mx-auto mb-16">
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
            <label htmlFor="topic" className="block text-lg font-semibold mb-4 text-gray-700">
              What topic would you like to create a podcast about?
            </label>
            <div className="flex gap-4">
              <input
                id="topic"
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleStart()}
                placeholder="e.g., The Future of Artificial Intelligence"
                className="flex-1 px-6 py-4 text-lg border-2 border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-colors"
              />
              <button
                onClick={handleStart}
                disabled={!topic.trim()}
                className="px-8 py-4 bg-primary text-white rounded-xl font-semibold hover:bg-primary/90 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                <Sparkles className="w-5 h-5" />
                Generate
              </button>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">
          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
            <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Youtube className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Research from YouTube</h3>
            <p className="text-gray-600">
              Automatically finds and analyzes relevant podcast episodes to gather insights.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
            <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">AI Script Generation</h3>
            <p className="text-gray-600">
              Gemini 3 creates engaging, conversational scripts with natural flow.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
            <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Natural Voice Synthesis</h3>
            <p className="text-gray-600">
              ElevenLabs converts your script to podcast-quality audio instantly.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-16 text-gray-500">
          <p>Powered by Google Gemini 3, ElevenLabs, and YouTube</p>
        </div>
      </div>
    </main>
  );
}

