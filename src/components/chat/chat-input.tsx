import { useAgent } from '@copilotkit/react-agent';
import { useState } from 'react';

export default function ChatInput({ agent }: { agent: any }) {
  const [input, setInput] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // In a real app, we would use CopilotKit to send a message to the agent
    // For now, we simulate by updating agent state
    const newMessage = { role: 'user' as const, content: input };
    // We would normally do: await agent.sendMessage(input);
    // But for demo, we just add to state
    agent.state = {
      ...agent.state,
      messages: [...(agent.state?.messages || []), newMessage],
    };

    // Simulate agent response after a short delay
    setTimeout(() => {
      const response = {
        role: 'assistant' as const,
        content: `I received: "${input}". How can I help further?`,
      };
      agent.state = {
        ...agent.state,
        messages: [...(agent.state?.messages || []), response],
      };
    }, 1000);

    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="flex space-x-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type a message..."
        className="flex-1 rounded border px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        className="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
      >
        Send
      </button>
    </form>
  );
}