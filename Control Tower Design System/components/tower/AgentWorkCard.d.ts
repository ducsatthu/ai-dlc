import * as React from 'react';

/** Answers "agent này đang làm gì, nói gì với ai" for one running task: current action, step checklist, latest messages, and who it is waiting on. */
export interface WorkStep { label: string; state: 'done' | 'doing' | 'todo' }
export interface WorkMessage { id: string; from: string; to: string; type: string; body: string }
export interface AgentWorkCardProps extends React.HTMLAttributes<HTMLElement> {
  /** "TSK-02" */
  taskId?: string;
  title?: React.ReactNode;
  /** agent id currently holding the task */
  agent?: string;
  lane?: 'pipeline' | 'review' | 'human' | 'learning';
  status?: 'in-progress' | 'review' | 'blocked' | 'done' | 'claimed';
  /** "18 phút" */
  elapsed?: string;
  /** one line: what the agent is doing right now */
  doing?: React.ReactNode;
  /** file or artifact being touched */
  target?: string;
  steps?: WorkStep[];
  /** last 2–3 messages on this task */
  messages?: WorkMessage[];
  /** what blocks completion, e.g. "backend-reviewer ký TSK-02" */
  waitingOn?: string;
  onOpenTask?: () => void;
}
export declare function AgentWorkCard(props: AgentWorkCardProps): JSX.Element;
