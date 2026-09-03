'use client';

import React, { useState, useEffect } from 'react';

interface APIKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PROVIDERS = [
  { id: 'openai', label: 'OpenAI', models: 'GPT-4o / GPT-3.5-turbo', icon: '🤖', placeholder: 'sk-...' },
  { id: 'anthropic', label: 'Anthropic', models: 'Claude 3.5 / Claude 3 Haiku', icon: '🧠', placeholder: 'sk-ant-...' },
  { id: 'gemini', label: 'Google Gemini', models: 'Gemini 1.5 Flash / Pro', icon: '✨', placeholder: 'AIzaSy...' },
] as const;

type ProviderId = 'openai' | 'anthropic' | 'gemini';

export default function APIKeyModal({ isOpen, onClose }: APIKeyModalProps) {
  const [provider, setProvider] = useState<ProviderId>('openai');
  const [keys, setKeys] = useState({ openai: '', anthropic: '', gemini: '' });
  const [showKey, setShowKey] = useState({ openai: false, anthropic: false, gemini: false });
  const [savedMessage, setSavedMessage] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined' && isOpen) {
      const stored = localStorage.getItem('opsagent_llm_provider') as ProviderId;
      if (stored) setProvider(stored);
      setKeys({
        openai: localStorage.getItem('opsagent_openai_key') || '',
        anthropic: localStorage.getItem('opsagent_anthropic_key') || '',
        gemini: localStorage.getItem('opsagent_gemini_key') || '',
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('opsagent_llm_provider', provider);
      localStorage.setItem('opsagent_openai_key', keys.openai);
      localStorage.setItem('opsagent_anthropic_key', keys.anthropic);
      localStorage.setItem('opsagent_gemini_key', keys.gemini);
    }
    setSavedMessage(true);
    setTimeout(() => {
      setSavedMessage(false);
      onClose();
    }, 1400);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)' }}
    >
      <div className="bg-[#1a2033] border border-slate-700/60 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/50">
          <div className="flex items-center gap-2">
            <span className="text-indigo-400">⚙️</span>
            <h3 className="text-sm font-bold text-slate-200">API Key Configuration</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-300 text-xl leading-none w-6 h-6 flex items-center justify-center rounded hover:bg-slate-700 transition-colors"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-5">
          {savedMessage && (
            <div className="flex items-center gap-2 p-3 bg-green-500/15 border border-green-500/30 rounded-lg">
              <span className="text-green-400 text-sm">✓</span>
              <span className="text-green-400 text-xs font-medium">Configuration saved successfully!</span>
            </div>
          )}

          {/* Active Provider Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Active LLM Provider
            </label>
            <div className="grid grid-cols-3 gap-2">
              {PROVIDERS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setProvider(p.id as ProviderId)}
                  className={`flex flex-col items-center gap-1 p-3 rounded-xl border text-xs font-medium transition-all ${
                    provider === p.id
                      ? 'bg-indigo-600/20 border-indigo-500/60 text-indigo-300 shadow-lg shadow-indigo-500/10'
                      : 'bg-slate-800/50 border-slate-700/50 text-slate-400 hover:text-slate-200 hover:border-slate-600'
                  }`}
                >
                  <span className="text-lg">{p.icon}</span>
                  <span>{p.label}</span>
                </button>
              ))}
            </div>
            <p className="text-[10px] text-slate-500 mt-1.5">
              Active: {PROVIDERS.find(p => p.id === provider)?.models}
            </p>
          </div>

          <div className="border-t border-slate-700/40 pt-4 space-y-4">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">
              API Keys (store all, switch via provider above)
            </p>
            {PROVIDERS.map((p) => {
              const key = keys[p.id as ProviderId];
              const show = showKey[p.id as ProviderId];
              return (
                <div key={p.id}>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                      <span>{p.icon}</span> {p.label}
                    </label>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium border ${
                      key
                        ? 'bg-green-500/15 text-green-400 border-green-500/30'
                        : 'bg-slate-700/50 text-slate-500 border-slate-600/50'
                    }`}>
                      {key ? 'Configured' : 'Not set'}
                    </span>
                  </div>
                  <div className="relative">
                    <input
                      type={show ? 'text' : 'password'}
                      value={key}
                      onChange={(e) => setKeys((prev) => ({ ...prev, [p.id]: e.target.value }))}
                      placeholder={p.placeholder}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors pr-16"
                    />
                    <button
                      type="button"
                      onClick={() => setShowKey((prev) => ({ ...prev, [p.id]: !prev[p.id as ProviderId] }))}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-indigo-400 hover:text-indigo-300 font-medium"
                    >
                      {show ? 'Hide' : 'Show'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-700/50 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-lg transition-colors shadow-lg shadow-indigo-500/20"
          >
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
}
