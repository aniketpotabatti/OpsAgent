import StepTracker from './step-tracker';

export default function RunbookViewer({ runbook, agent }: { runbook: any; agent: any }) {
  return (
    <div className="space-y-4">
      <h3 className="font-bold">{runbook.title}</h3>
      <p className="text-gray-600">{runbook.description}</p>
      <div className="border-t pt-4">
        <h4 className="font-semibold mb-2">Steps</h4>
        <StepTracker steps={runbook.steps} agent={agent} />
      </div>
    </div>
  );
}