'use client';

import { useState, useRef, useEffect } from 'react';

interface Incident {
  id: string;
  title: string;
  severity: string;
  status: string;
}

interface Message {
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
}

const AGENT_RESPONSES: Record<string, string> = {
  default: "I'm monitoring all active incidents. You can ask me to acknowledge, escalate, or resolve any incident by name or ID.",
  help: "Available commands:\n• 'resolve low severity' — resolves all low-severity incidents\n• 'escalate [incident ID]' — escalates an incident\n• 'summarize' — gives a status summary\n• 'acknowledge all' — acknowledges all open incidents",
  summary: '',
  resolve: "✅ Resolving low-severity incidents now. Board updated.",
  escalate: "⚡ Incident escalated and oncall notified via PagerDuty.",
  acknowledge: "✔️ Acknowledging all open incidents...",
};

function formatChatTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default function Chat({
  incidents,
  activeIncident,
}: {
  incidents: Incident[];
  activeIncident: Incident | null;
}) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'agent',
      content: `👋 OpsAgent online. ${incidents.length} incidents active — ${incidents.filter(i => i.severity === 'critical').length} critical. How can I help?`,
      timestamp: formatChatTime(),
    },
  ]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getAgentReply = (userMsg: string): string => {
    const lower = userMsg.toLowerCase();
    if (lower.includes('help') || lower.includes('command')) return AGENT_RESPONSES.help;
    if (lower.includes('summarize') || lower.includes('summary') || lower.includes('status')) {
      const open = incidents.filter((i) => i.status === 'open').length;
      const critical = incidents.filter((i) => i.severity === 'critical').length;
      const resolved = incidents.filter((i) => i.status === 'resolved').length;
      return `📊 Status Summary:\n• Total incidents: ${incidents.length}\n• Open: ${open}\n• Critical: ${critical}\n• Resolved: ${resolved}`;
    }
    if (lower.includes('resolve low') || lower.includes('resolve all low')) return AGENT_RESPONSES.resolve;
    if (lower.includes('escalate')) return AGENT_RESPONSES.escalate;
    if (lower.includes('acknowledge')) return AGENT_RESPONSES.acknowledge;
    if (activeIncident && lower.includes(activeIncident.id.toLowerCase())) {
      return `Incident ${activeIncident.id} is ${activeIncident.status} with ${activeIncident.severity} severity. Runbook steps loaded in the panel.`;
    }
    return AGENT_RESPONSES.default;
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: text, timestamp: formatChatTime() }]);
    setTyping(true);
    await new Promise((r) => setTimeout(r, 800 + Math.random() * 600));
    setTyping(false);
    setMessages((prev) => [...prev, { role: 'agent', content: getAgentReply(text), timestamp: formatChatTime() }]);
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50 flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">OpsAgent Chat</h2>
        </div>
        <p className="text-[10px] text-slate-500 mt-0.5">Ask me to triage, escalate, or resolve</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
            {msg.role === 'agent' && (
              <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-[10px] font-bold flex-shrink-0 mt-0.5">
                AI
              </div>
            )}
            <div className={`max-w-[85%] rounded-xl px-3 py-2 text-xs leading-relaxed whitespace-pre-wrap ${
              msg.role === 'user'
                ? 'bg-indigo-600 text-white rounded-tr-sm'
                : 'bg-slate-800 text-slate-200 border border-slate-700/50 rounded-tl-sm'
            }`}>
              {msg.content}
              <div className={`text-[9px] mt-1 ${msg.role === 'user' ? 'text-indigo-200' : 'text-slate-500'}`}>
                {msg.timestamp}
              </div>
            </div>
          </div>
        ))}
        {typing && (
          <div className="flex gap-2 items-start">
            <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-[10px] font-bold flex-shrink-0">
              AI
            </div>
            <div className="bg-slate-800 border border-slate-700/50 rounded-xl rounded-tl-sm px-3 py-2.5 flex items-center gap-1">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"
                  style={{ animationDelay: `${i * 150}ms` }}
                />
              ))}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-slate-700/50 flex-shrink-0">
        <div className="flex gap-2 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask about incidents…"
            rows={2}
            className="flex-1 resize-none bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim()}
            className="px-3 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 disabled:cursor-not-allowed text-white rounded-lg text-xs font-medium transition-colors flex-shrink-0"
          >
            ↑ Send
          </button>
        </div>
      </div>
    </div>
  );
}