"use client";

import { AlertCircle } from "lucide-react";

interface EditModeIndicatorProps {
  show: boolean;
}

export function EditModeIndicator({ show }: EditModeIndicatorProps) {
  if (!show) return null;

  return (
    <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 animate-in fade-in slide-in-from-top-2 duration-300">
      <div className="bg-amber-900/30 border-2 border-amber-600 rounded-lg shadow-lg px-4 py-2 flex items-center gap-2">
        <AlertCircle className="w-4 h-4 text-amber-400" />
        <p className="text-sm font-medium text-amber-200">
          Edit Mode: Future steps will be regenerated
        </p>
      </div>
    </div>
  );
}
