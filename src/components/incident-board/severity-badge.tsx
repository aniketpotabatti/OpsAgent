type SeverityProps = {
  severity: 'low' | 'medium' | 'high' | 'critical';
};

export default function SeverityBadge({ severity }: SeverityProps) {
  const colorMap: Record<string, string> = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  };

  return (
    <span className={`px-2 py-1 text-xs rounded-full ${colorMap[severity]}`}>
      {severity.toUpperCase()}
    </span>
  );
}