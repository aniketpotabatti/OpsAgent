import { CopilotKitNextJSAdapter } from '@copilotkit/next';
import { CopilotKitRuntime } from '@copilotkit/runtime';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req: Request, res: Response) {
  const { handleRequest } = new CopilotKitNextJSAdapter({
    endpoint: '/api/copilotkit',
  });

  return handleRequest(req, res);
}