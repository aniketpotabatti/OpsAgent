'use client';

import IncidentBoard from '@/components/incident-board';
import RunbookPanel from '@/components/runbook-panel';
import AgentReasoning from '@/components/agent-reasoning';
import Chat from '@/components/chat';
import { useState } from 'react';

const MOCK_INCIDENTS = [
  {
    id: 'inc-001',
    title: 'High CPU Usage — prod-api-03',
    description: 'CPU utilization at 94% for >15 mins. Service degradation likely.',
    severity: 'critical' as const,
    status: 'open' as const,
    source: 'Prometheus',
    category: 'hardware',
    timestamp: '2026-09-03T16:01:00Z',
    runbook_id: 'high-cpu-runbook',
  },
  {
    id: 'inc-002',
    title: 'DB Connection Pool Exhausted — postgres-primary',
    description: 'All 100 connections in use. New requests timing out after 30s.',
    severity: 'high' as const,
    status: 'open' as const,
    source: 'Alertmanager',
    category: 'database',
    timestamp: '2026-09-03T16:05:00Z',
    runbook_id: 'db-pool-runbook',
  },
  {
    id: 'inc-003',
    title: 'Pod CrashLoopBackOff — payments-service',
    description: 'payments-service-7d9f has been restarting every 2 min for last 30 min.',
    severity: 'high' as const,
    status: 'acknowledged' as const,
    source: 'Kubernetes',
    category: 'software',
    timestamp: '2026-09-03T15:55:00Z',
    runbook_id: 'crashloop-runbook',
  },
  {
    id: 'inc-004',
    title: 'Network Latency Spike — us-east-1',
    description: 'P99 latency jumped from 120ms to 780ms. Possible packet loss upstream.',
    severity: 'medium' as const,
    status: 'open' as const,
    source: 'Datadog',
    category: 'network',
    timestamp: '2026-09-03T16:10:00Z',
    runbook_id: 'network-latency-runbook',
  },
  {
    id: 'inc-005',
    title: 'SSL Certificate Expiring — api.example.com',
    description: 'TLS certificate expires in 3 days. Auto-renewal failed.',
    severity: 'low' as const,
    status: 'open' as const,
    source: 'CertBot',
    category: 'security',
    timestamp: '2026-09-03T14:00:00Z',
    runbook_id: 'cert-expiry-runbook',
  },
];

const MOCK_RUNBOOKS: Record<string, { title: string; steps: string[] }> = {
  'high-cpu-runbook': {
    title: 'High CPU Runbook',
    steps: [
      'SSH into affected node: ssh prod-api-03',
      'Run `top` to identify high-CPU processes',
      'Check for runaway threads: `ps aux --sort=-%cpu | head -20`',
      'If a single process, check for memory leak with `valgrind`',
      'Scale horizontally if load-driven: `kubectl scale deploy api --replicas=6`',
      'Notify #sre-oncall if unresolved after 10 min',
    ],
  },
  'db-pool-runbook': {
    title: 'DB Connection Pool Runbook',
    steps: [
      'Check active connections: `SELECT count(*) FROM pg_stat_activity`',
      'Identify long-running queries: `SELECT pid, query, duration FROM pg_stat_activity ORDER BY duration DESC`',
      'Kill blocking query if safe: `SELECT pg_terminate_backend(pid)`',
      'Increase pool size in app config if needed (MAX_DB_CONNECTIONS)',
      'Restart connection pooler (PgBouncer) if hung: `systemctl restart pgbouncer`',
    ],
  },
  'crashloop-runbook': {
    title: 'CrashLoopBackOff Runbook',
    steps: [
      'Check pod logs: `kubectl logs payments-service-7d9f --previous`',
      'Describe pod for events: `kubectl describe pod payments-service-7d9f`',
      'Check resource limits — OOMKill is common cause',
      'If config error, update ConfigMap and redeploy',
      'If image error, rollback: `kubectl rollout undo deploy/payments-service`',
    ],
  },
  'network-latency-runbook': {
    title: 'Network Latency Runbook',
    steps: [
      'Run traceroute to identify hop with latency: `traceroute api.example.com`',
      'Check AWS status page for us-east-1 anomalies',
      'Verify no route table / SG changes in last 1 hour (CloudTrail)',
      'Switch traffic to us-west-2 if latency persists >15 min',
    ],
  },
  'cert-expiry-runbook': {
    title: 'SSL Certificate Renewal Runbook',
    steps: [
      'Check cert expiry: `openssl s_client -connect api.example.com:443 | openssl x509 -noout -dates`',
      'Run certbot manually: `certbot renew --force-renewal`',
      'Reload nginx after renewal: `systemctl reload nginx`',
      'Verify cert updated: re-run openssl check above',
    ],
  },
};

const MOCK_THOUGHTS = [
  '🔍 Ingested 5 alerts from Prometheus, Alertmanager, and Kubernetes.',
  '⚡ Critical: inc-001 (High CPU) escalated. Matching runbook "high-cpu-runbook".',
  '📋 inc-002 matched to DB Connection Pool runbook. 3 steps recommended.',
  '🔄 inc-003 (CrashLoopBackOff) status: acknowledged. Runbook loaded.',
  '✅ Low-severity incidents queued. No immediate escalation needed.',
];

export default function Home() {
  const [incidents, setIncidents] = useState(MOCK_INCIDENTS);
  const [activeIncidentId, setActiveIncidentId] = useState<string | null>('inc-001');

  const activeIncident = incidents.find((i) => i.id === activeIncidentId) || null;
  const activeRunbook = activeIncident ? MOCK_RUNBOOKS[activeIncident.runbook_id] : null;

  const updateIncidentStatus = (id: string, status: 'open' | 'acknowledged' | 'in_progress' | 'resolved') => {
    setIncidents((prev) => prev.map((inc) => inc.id === id ? { ...inc, status } : inc));
  };

  return (
    <div className="flex h-[calc(100vh-64px)] overflow-hidden">
      {/* Left Panel — Incident Board */}
      <aside className="w-80 flex-shrink-0 bg-[#161b27] border-r border-slate-700/50 flex flex-col overflow-hidden">
        <IncidentBoard
          incidents={incidents}
          activeIncidentId={activeIncidentId}
          onSelect={setActiveIncidentId}
          onStatusChange={updateIncidentStatus}
        />
      </aside>

      {/* Center — Agent Reasoning + Runbook Panel */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Agent Reasoning - top */}
        <div className="flex-shrink-0 border-b border-slate-700/50 bg-[#161b27]">
          <AgentReasoning thoughts={MOCK_THOUGHTS} />
        </div>
        {/* Runbook Panel - bottom, scrollable */}
        <div className="flex-1 overflow-y-auto bg-[#0f1117]">
          <RunbookPanel incident={activeIncident} runbook={activeRunbook} />
        </div>
      </main>

      {/* Right Panel — Chat */}
      <aside className="w-80 flex-shrink-0 bg-[#161b27] border-l border-slate-700/50 flex flex-col overflow-hidden">
        <Chat incidents={incidents} activeIncident={activeIncident} />
      </aside>
    </div>
  );
}