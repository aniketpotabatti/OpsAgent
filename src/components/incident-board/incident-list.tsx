import IncidentCard from './incident-card';

export default function IncidentList({ agent }: { agent: any }) {
  // In a real app, we would get incidents from agent.state
  const incidents = agent.state?.incidents || [];

  return (
    <div>
      {incidents.map((incident: any) => (
        <IncidentCard key={incident.id} incident={incident} agent={agent} />
      ))}
    </div>
  );
}