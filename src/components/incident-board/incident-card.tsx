import SeverityBadge from './severity-badge';
import { useState } from 'react';

export default function IncidentCard({ incident, agent }: { incident: any; agent: any }) {
  const [expanded, setExpanded] = useState(false);

  const handleAction = async (action: string) => {
    // In a real app, we would call agent.setState or use a CopilotKit action
    console.log(`Performing ${action} on incident ${incident.id}`);
    // For now, just update local state for demo
    if (action === 'resolve') {
      // Simulate resolving
      incident.status = 'resolved';
    }
  };

  return (
    <div className="p-4 mb-4 border rounded-lg">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-bold">{incident.title}</h3>
          <p className="text-sm text-gray-600">{incident.description}</p>
        </div>
        <SeverityBadge severity={incident.severity} />
      </div>
      <div className="mt-2 flex space-x-2">
        <button
          onClick={() => handleAction('acknowledge')}
          className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Acknowledge
        </button>
        <button
          onClick={() => handleAction('escalate')}
          className="px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-600"
        >
          Escalate
        </button>
        <button
          onClick={() => handleAction('resolve')}
          className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Resolve
        </button>
        <button
          onClick={() => setExpanded(!expanded)}
          className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          {expanded ? 'Hide' : 'Show'} Details
        </button>
      </div>
      {expanded && (
        <div className="mt-4 p-3 bg-gray-50 rounded">
          <p className="text-sm">{incident.details || 'No additional details.'}</p>
        </div>
      )}
    </div>
  );
}