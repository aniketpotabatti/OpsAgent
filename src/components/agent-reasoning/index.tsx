'use client';

import { useState, useEffect, useRef } from 'react';

export default function AgentReasoning({ thoughts }: { thoughts: string[] }) {
  const [visible, setVisible] = useState<string[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const timers = useRef<NodeJS.Timeout[]>([]);

  useEffect(() => {
    setVisible([]);
    timers.current.forEach(clearTimeout);
    timers.current = [];
    thoughts.forEach((thought, idx) => {
      const t = setTimeout(() => {
        setVisible((prev) => [...prev, thought]);
      }, idx * 900 + 400);
      timers.current.push(t);
    });
    return () => timers.current.forEach(clearTimeout);
  }, []);

  const display = isExpanded ? visible : visible.slice(-2);

  return (
    <div className="px-4 py-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="relative">
            <span className="w-2 h-2 bg-indigo-400 rounded-full inline-block animate-pulse" />
          </div>
          <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Agent Reasoning</h2>
          {visible.length > 0 && (
            <span className="text-[10px] bg-indigo-600/30 text-indigo-300 px-1.5 py-0.5 rounded-full border border-indigo-500/30">
              {visible.length} steps
            </span>
          )}
        </div>
        {thoughts.length > 2 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-[10px] text-indigo-400 hover:text-indigo-300 font-medium"
          >
            {isExpanded ? 'Show less ▲' : `Show all ${thoughts.length} ▼`}
          </button>
        )}
      </div>

      <div className="space-y-1">
        {display.length === 0 && (
          <div className="flex items-center gap-2 text-xs text-slate-500 italic py-1">
            <span className="animate-pulse">▸</span> Agent is analyzing incidents…
          </div>
        )}
        {display.map((thought, idx) => (
          <div
            key={idx}
            className="flex items-start gap-2 text-xs text-slate-300 py-1 px-2 rounded bg-slate-800/30 animate-fadeIn"
          >
            <span className="text-indigo-400 mt-0.5 flex-shrink-0">▸</span>
            <span>{thought}</span>
          </div>
        ))}
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.4s ease-out;
        }
      `}</style>
    </div>
  );
}