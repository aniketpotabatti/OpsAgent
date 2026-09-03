export default function StepTracker({ steps, agent }: { steps: any[]; agent: any }) {
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);

  const toggleStep = (stepIndex: number) => {
    setCompletedSteps(prev =>
      prev.includes(stepIndex)
        ? prev.filter((i) => i !== stepIndex)
        : [...prev, stepIndex]
    );
  };

  return (
    <div>
      {steps.map((step, index) => (
        <div key={index} className="flex items-start mb-2">
          <input
            type="checkbox"
            checked={completedSteps.includes(index)}
            onChange={() => toggleStep(index)}
            className="mr-2 h-4 w-4"
          />
          <span className={completedSteps.includes(index) ? 'line-through text-gray-500' : ''}>
            {step}
          </span>
        </div>
      ))}
    </div>
  );
}