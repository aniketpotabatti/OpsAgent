'use client';

import React, { useState } from 'react';
import APIKeyModal from '../settings/api-key-modal';

export default function Shell({ children }: { children: React.ReactNode }) {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#0f1117] flex flex-col">
      {/* Header */}
      <header className="h-16 flex-shrink-0 bg-[#161b27] border-b border-slate-700/50 flex items-center px-6 justify-between shadow-lg">
        {/* Left: Brand */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-white-600 flex items-center justify-center text-sm font-bold text-white shadow-lg shadow-indigo-500/30">
           🛡️
          </div>
          <div>
            <span className="text-base font-bold text-white">OpsAgent</span>
            <span className="ml-2 text-[10px] text-slate-400 font-medium tracking-wider uppercase">Incident Triage</span>
          </div>
          <div className="ml-3 flex items-center gap-1.5 bg-green-500/10 border border-green-500/30 rounded-full px-2.5 py-1">
            <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
            <span className="text-[10px] text-green-400 font-medium">Agent Online</span>
          </div>
        </div>

        {/* Center: Nav */}
        <nav className="hidden md:flex items-center gap-1">
          {[
            { label: 'Dashboard', icon: '⊞', active: true },
            { label: 'Runbooks', icon: '📋', active: false },
          ].map(({ label, icon, active }) => (
            <a
              key={label}
              href="#"
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                active
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              <span>{icon}</span>
              {label}
            </a>
          ))}
        </nav>

        {/* Right: Settings + Status */}
        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 text-[10px] text-slate-500">
            <span className="px-2 py-0.5 bg-slate-800 rounded border border-slate-700 text-slate-400">
              LangGraph v0.0.20
            </span>
          </div>
          <button
            id="settings-btn"
            onClick={() => setIsSettingsOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-600/50 transition-all"
          >
            <span>⚙️</span>
            API Keys
          </button>
        </div>
      </header>

      {/* Body */}
      <div className="flex-1 overflow-hidden">
        {children}
      </div>

      {/* Settings Modal */}
      <APIKeyModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </div>
  );
}