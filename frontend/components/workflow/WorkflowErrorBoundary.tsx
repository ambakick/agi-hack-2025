'use client';

import React, { Component, ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import { AlertCircle } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class WorkflowErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Workflow error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center border border-red-200">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Something went wrong
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              We encountered an error in the workflow. Please try refreshing the page.
            </p>
            <div className="flex gap-3 justify-center">
              <Button onClick={() => window.location.reload()} size="lg">
                Refresh Page
              </Button>
              <Button
                onClick={() => (window.location.href = '/')}
                variant="outline"
                size="lg"
              >
                Go Home
              </Button>
            </div>
            {this.state.error && (
              <details className="mt-4 text-left">
                <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                  Error details
                </summary>
                <pre className="mt-2 text-xs text-red-600 overflow-auto p-2 bg-red-50 rounded">
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

