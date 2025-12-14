"use client";

import { useEffect } from "react";

interface KeyboardShortcutsOptions {
  onEscape?: () => void;
  onEnter?: () => void;
  onCtrlEnter?: () => void;
}

export function useKeyboardShortcuts({
  onEscape,
  onEnter,
  onCtrlEnter,
}: KeyboardShortcutsOptions) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Escape key
      if (event.key === "Escape" && onEscape) {
        event.preventDefault();
        onEscape();
      }

      // Enter key
      if (event.key === "Enter" && !event.ctrlKey && !event.metaKey && onEnter) {
        event.preventDefault();
        onEnter();
      }

      // Ctrl/Cmd + Enter
      if (
        (event.ctrlKey || event.metaKey) &&
        event.key === "Enter" &&
        onCtrlEnter
      ) {
        event.preventDefault();
        onCtrlEnter();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [onEscape, onEnter, onCtrlEnter]);
}

