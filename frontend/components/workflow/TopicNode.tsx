'use client';

import { useState, useEffect } from 'react';
import { NodeProps } from 'reactflow';
import { NodeWrapper } from './NodeWrapper';
import { Button } from '@/components/ui/button';
import { PodcastFormat } from '@/lib/types';
import { WorkflowNodeData } from '@/lib/workflowState';
import { Lightbulb, Mic, Users } from 'lucide-react';

interface TopicNodeProps extends NodeProps {
  data: WorkflowNodeData & {
    onComplete?: (topic: string, format: PodcastFormat) => void;
    onExpand?: () => void;
    onCollapse?: () => void;
  };
}

export function TopicNode({ id, data }: TopicNodeProps) {
  const [topic, setTopic] = useState(data.topic || '');
  const [format, setFormat] = useState<PodcastFormat>(
    data.format || PodcastFormat.SINGLE_HOST
  );

  useEffect(() => {
    if (data.topic) setTopic(data.topic);
    if (data.format) setFormat(data.format);
  }, [data.topic, data.format]);

  const handleNext = () => {
    if (topic.trim() && data.onComplete) {
      data.onComplete(topic, format);
    }
  };

  const summary = data.topic
    ? `${data.topic} (${data.format === PodcastFormat.MULTI_HOST ? 'Two Hosts' : 'Single Host'})`
    : 'Click to start';

  return (
    <NodeWrapper
      id={id}
      icon={<Lightbulb className="w-5 h-5" />}
      title="Topic & Format"
      summary={summary}
      color="#3b82f6"
      isExpanded={data.isExpanded}
      isCompleted={data.isCompleted}
      isLoading={data.isLoading}
      error={data.error}
      onExpand={data.onExpand}
      onCollapse={data.onCollapse}
      hasTargetHandle={false}
    >
      <div className="space-y-4">
        <div>
          <label htmlFor="topic-input" className="block text-sm font-medium mb-2">
            What's your podcast about?
          </label>
          <input
            id="topic-input"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., The Future of Artificial Intelligence"
            disabled={data.isCompleted && !data.isExpanded}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-3">Choose Format</label>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setFormat(PodcastFormat.SINGLE_HOST)}
              className={`p-4 rounded-lg border-2 transition-all ${
                format === PodcastFormat.SINGLE_HOST
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <Mic className="w-6 h-6 mx-auto mb-2 text-blue-500" />
              <h4 className="font-semibold text-sm mb-1">Single Host</h4>
              <p className="text-xs text-gray-500">One narrator</p>
            </button>

            <button
              onClick={() => setFormat(PodcastFormat.MULTI_HOST)}
              className={`p-4 rounded-lg border-2 transition-all ${
                format === PodcastFormat.MULTI_HOST
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <Users className="w-6 h-6 mx-auto mb-2 text-blue-500" />
              <h4 className="font-semibold text-sm mb-1">Two Hosts</h4>
              <p className="text-xs text-gray-500">Conversational dialogue</p>
            </button>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <Button
            onClick={handleNext}
            disabled={!topic.trim() || data.isLoading}
            size="lg"
          >
            Continue to References
          </Button>
        </div>
      </div>
    </NodeWrapper>
  );
}

