'use client';

import { useEffect, useState } from 'react';

interface ConfettiEffectProps {
  trigger: boolean;
}

export function ConfettiEffect({ trigger }: ConfettiEffectProps) {
  const [particles, setParticles] = useState<Array<{ id: number; left: number; delay: number; color: string }>>([]);

  useEffect(() => {
    if (trigger) {
      const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f97316', '#ec4899'];
      const newParticles = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        left: Math.random() * 100,
        delay: Math.random() * 0.5,
        color: colors[Math.floor(Math.random() * colors.length)],
      }));
      setParticles(newParticles);

      // Clear particles after animation
      setTimeout(() => setParticles([]), 3000);
    }
  }, [trigger]);

  if (particles.length === 0) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="absolute w-2 h-2 animate-confetti"
          style={{
            left: `${particle.left}%`,
            top: '-10px',
            backgroundColor: particle.color,
            animationDelay: `${particle.delay}s`,
          }}
        />
      ))}
    </div>
  );
}

