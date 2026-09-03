'use client';

import { useState } from 'react';

type Severity = 'critical' | 'high' | 'medium' | 'low';
type Status = 'open' | 'acknowledged' | 'in_progress' | 'resolved';

interface Incident {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  status: Status;
  source: string;
  category: string;
  timestamp: string;
  runbook_id: string;
}

const SEVERITY_CONFIG: Record<Severity, { bg: string; text: string; dot: string; label: string }> = {
  critical: { bg: 'bg-red-500/20', text: 'text-red-400', dot: 'bg-red-500', label: 'CRITICAL' },
  high: { bg: 'bg-orange-500/20', text: 'text-orange-400', dot: 'bg-orange-500', label: 'HIGH' },
  medium: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', dot: 'bg-yellow-500', label: 'MEDIUM' },
  low: { bg: 'bg-green-500/20', text: 'text-green-400', dot: 'bg-green-500', label: 'LOW' },
};

const STATUS_LABELS: Record<Status, string> = {
  open: 'Open',
  acknowledged: 'Acknowledged',
  in_progress: 'In Progress',
  resolved: 'Resolved',
};

function formatTime(ts: string) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return ts;
  }
}

export default function IncidentBoard({
  incidents,
  activeIncidentId,
  onSelect,
  onStatusChange,
}: {
  incidents: Incident[];
  activeIncidentId: string | null;
  onSelect: (id: string) => void;
  onStatusChange: (id: string, status: Status) => void;
}) {
  const counts = { critical: 0, high: 0, medium: 0, low: 0 };
  incidents.forEach((i) => { counts[i.severity]++; });

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50">
        <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-3">
          Incident Board
        </h2>
        <div className="grid grid-cols-4 gap-1.5">
          {(Object.keys(counts) as Severity[]).map((sev) => (
            <div key={sev} className={`rounded-md p-1.5 text-center ${SEVERITY_CONFIG[sev].bg}`}>
              <div className={`text-lg font-bold ${SEVERITY_CONFIG[sev].text}`}>{counts[sev]}</div>
              <div className="text-[9px] text-slate-400 uppercase">{sev}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Incident list */}
      <div className="flex-1 overflow-y-auto py-2">
        {incidents.map((incident) => {
          const sc = SEVERITY_CONFIG[incident.severity];
          const isActive = incident.id === activeIncidentId;
          return (
            <div
              key={incident.id}
              onClick={() => onSelect(incident.id)}
              className={`mx-2 mb-1.5 p-3 rounded-lg cursor-pointer transition-all border ${
                isActive
                  ? 'bg-indigo-600/20 border-indigo-500/60 shadow-lg shadow-indigo-500/10'
                  : 'bg-slate-800/40 border-slate-700/40 hover:bg-slate-800/70 hover:border-slate-600/50'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-1.5 min-w-0">
                  <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${sc.dot} ${
                    incident.severity === 'critical' ? 'animate-pulse' : ''
                  }`} />
                  <span className="text-xs font-medium text-slate-200 truncate leading-tight">{incident.title}</span>
                </div>
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded flex-shrink-0 ${sc.bg} ${sc.text}`}>
                  {sc.label}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-tight mb-2 line-clamp-2">{incident.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-slate-500">{incident.source} · {formatTime(incident.timestamp)}</span>
                <select
                  value={incident.status}
                  onChange={(e) => {
                    e.stopPropagation();
                    onStatusChange(incident.id, e.target.value as Status);
                  }}
                  onClick={(e) => e.stopPropagation()}
                  className="text-[10px] bg-slate-700 text-slate-300 border border-slate-600 rounded px-1.5 py-0.5 cursor-pointer"
                >
                  {(Object.keys(STATUS_LABELS) as Status[]).map((s) => (
                    <option key={s} value={s}>{STATUS_LABELS[s]}</option>
                  ))}
                </select>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}