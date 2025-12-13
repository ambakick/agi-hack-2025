'use client';

import { ReactNode, useEffect } from 'react';
import { Handle, Position } from 'reactflow';
import { X, Check, Loader2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useKeyboardShortcuts } from '@/lib/useKeyboardShortcuts';

interface NodeWrapperProps {
  id: string;
  icon: ReactNode;
  title: string;
  summary?: string;
  color: string;
  isExpanded: boolean;
  isCompleted: boolean;
  isLoading: boolean;
  error?: string | null;
  children?: ReactNode;
  onExpand?: () => void;
  onCollapse?: () => void;
  canEdit?: boolean;
  hasSourceHandle?: boolean;
  hasTargetHandle?: boolean;
}

export function NodeWrapper({
  id,
  icon,
  title,
  summary,
  color,
  isExpanded,
  isCompleted,
  isLoading,
  error,
  children,
  onExpand,
  onCollapse,
  canEdit = true,
  hasSourceHandle = true,
  hasTargetHandle = true,
}: NodeWrapperProps) {
  const handleClick = () => {
    if (isExpanded && onCollapse) {
      onCollapse();
    } else if (!isExpanded && onExpand && canEdit) {
      onExpand();
    }
  };

  // Keyboard shortcuts for active expanded node
  useKeyboardShortcuts({
    onEscape: isExpanded && onCollapse ? onCollapse : undefined,
  });

  return (
    <div
      className={cn(
        'bg-white rounded-xl border-l-4 shadow-lg transition-all duration-300',
        isExpanded ? 'shadow-2xl' : 'shadow-md hover:shadow-xl',
        isLoading && 'animate-pulse-border',
        error && 'border-red-500',
        !error && !isLoading && `border-[${color}]`
      )}
      style={{
        borderLeftColor: error ? '#ef4444' : color,
        width: isExpanded ? '600px' : '280px',
        minHeight: isExpanded ? '400px' : '120px',
      }}
    >
      {/* Handles for ReactFlow connections */}
      {hasTargetHandle && (
        <Handle
          type="target"
          position={Position.Left}
          className="w-3 h-3 !bg-gray-400"
        />
      )}
      {hasSourceHandle && (
        <Handle
          type="source"
          position={Position.Right}
          className="w-3 h-3 !bg-gray-400"
        />
      )}

      {/* Header */}
      <div
        className={cn(
          'p-4 flex items-center justify-between cursor-pointer',
          !isExpanded && 'hover:bg-gray-50',
          'group'
        )}
        onClick={!isExpanded ? handleClick : undefined}
        title={!isExpanded ? 'Click to expand' : undefined}
      >
        <div className="flex items-center gap-3 flex-1">
          <div
            className="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110"
            style={{ backgroundColor: `${color}20`, color }}
          >
            {icon}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 text-sm truncate">
              {title}
            </h3>
            {!isExpanded && summary && (
              <p className="text-xs text-gray-500 truncate mt-0.5">{summary}</p>
            )}
          </div>
        </div>

        {/* Status indicators */}
        <div className="flex items-center gap-2">
          {isLoading && (
            <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
          )}
          {isCompleted && !isExpanded && (
            <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
              <Check className="w-4 h-4 text-white" />
            </div>
          )}
          {error && (
            <div className="w-6 h-6 rounded-full bg-red-500 flex items-center justify-center">
              <AlertCircle className="w-4 h-4 text-white" />
            </div>
          )}
          {isExpanded && onCollapse && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onCollapse();
              }}
              className="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4 text-gray-600" />
            </button>
          )}
        </div>
      </div>

      {/* Error message */}
      {error && !isExpanded && (
        <div className="px-4 pb-3">
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}

      {/* Expanded content */}
      {isExpanded && (
        <div className="px-4 pb-4">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
          <div className="workflow-node-content">{children}</div>
        </div>
      )}
    </div>
  );
}

