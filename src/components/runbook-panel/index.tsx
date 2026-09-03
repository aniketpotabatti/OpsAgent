'use client';

import { useState } from 'react';

interface Incident {
  id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  source: string;
  category: string;
  timestamp: string;
  runbook_id: string;
}

interface Runbook {
  title: string;
  steps: string[];
}

export default function RunbookPanel({
  incident,
  runbook,
}: {
  incident: Incident | null;
  runbook: Runbook | null;
}) {
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const toggleStep = (idx: number) => {
    setCompletedSteps((prev) => {
      const next = new Set(prev);
      next.has(idx) ? next.delete(idx) : next.add(idx);
      return next;
    });
  };

  if (!incident || !runbook) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[300px] text-slate-500 gap-3 p-8">
        <div className="text-5xl opacity-30">📋</div>
        <p className="text-sm font-medium">Select an incident to view the matched runbook</p>
        <p className="text-xs text-slate-600">Agent will surface the most relevant runbook steps</p>
      </div>
    );
  }

  const progress = runbook.steps.length > 0
    ? Math.round((completedSteps.size / runbook.steps.length) * 100)
    : 0;

  const categoryColors: Record<string, string> = {
    hardware: 'text-orange-400 bg-orange-400/10 border-orange-400/20',
    database: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    software: 'text-purple-400 bg-purple-400/10 border-purple-400/20',
    network: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20',
    security: 'text-red-400 bg-red-400/10 border-red-400/20',
    general: 'text-slate-400 bg-slate-400/10 border-slate-400/20',
  };
  const catColor = categoryColors[incident.category] || categoryColors['general'];

  return (
    <div className="p-6 h-full">
      {/* Incident context header */}
      <div className="mb-5 p-4 rounded-xl bg-slate-800/60 border border-slate-700/50">
        <div className="flex items-start justify-between gap-3 mb-2">
          <h3 className="text-sm font-semibold text-slate-200 leading-snug">{incident.title}</h3>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded border flex-shrink-0 ${catColor}`}>
            {incident.category.toUpperCase()}
          </span>
        </div>
        <p className="text-xs text-slate-400 mb-3">{incident.description}</p>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Runbook progress:</span>
          <div className="flex-1 bg-slate-700 rounded-full h-1.5">
            <div
              className="bg-indigo-500 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="text-xs font-semibold text-indigo-400">{progress}%</span>
        </div>
      </div>

      {/* Runbook title */}
      <h2 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
        <span className="text-indigo-400">📋</span>
        {runbook.title}
      </h2>

      {/* Steps */}
      <div className="space-y-2">
        {runbook.steps.map((step, idx) => {
          const done = completedSteps.has(idx);
          return (
            <div
              key={idx}
              onClick={() => toggleStep(idx)}
              className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all border ${
                done
                  ? 'bg-green-500/10 border-green-500/30 opacity-70'
                  : 'bg-slate-800/40 border-slate-700/40 hover:bg-slate-800/80 hover:border-slate-600'
              }`}
            >
              <div className={`flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center mt-0.5 transition-all ${
                done ? 'border-green-500 bg-green-500' : 'border-slate-500 hover:border-indigo-400'
              }`}>
                {done && (
                  <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none">
                    <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <span className="text-[11px] text-slate-400 font-medium mr-2">Step {idx + 1}</span>
                <p className={`text-sm mt-0.5 font-mono leading-snug ${done ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                  {step}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {progress === 100 && (
        <div className="mt-5 p-4 rounded-xl bg-green-500/15 border border-green-500/30 text-center">
          <p className="text-green-400 font-semibold text-sm">✅ All runbook steps completed!</p>
          <p className="text-green-500/70 text-xs mt-1">Incident can now be resolved.</p>
        </div>
      )}
    </div>
  );
}