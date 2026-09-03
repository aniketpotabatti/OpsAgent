import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Shell from '@/components/layout/shell';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'OpsAgent — AI-Powered Incident Triage',
  description: 'AI-powered incident triage and runbook assistant powered by LangGraph',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body className="bg-[#0f1117] text-slate-100 min-h-screen">
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}