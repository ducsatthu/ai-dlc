import * as React from 'react';

/**
 * One task on a Bolt's task board — the claim/approver/dependency rules are visible in the meta line, not hidden.
 */
export interface TaskRowProps extends React.HTMLAttributes<HTMLDivElement> {
  /** "TSK-02" */
  id?: string;
  title?: React.ReactNode;
  status?: 'todo' | 'claimed' | 'in-progress' | 'blocked' | 'review' | 'done';
  /** agent that claimed it */
  claimedBy?: string;
  /** pre-assigned approver */
  approver?: string;
  /** e.g. "TSK-01" */
  dependsOn?: string;
  msgCount?: number;
  onClick?: React.MouseEventHandler<HTMLDivElement>;
}
export declare function TaskRow(props: TaskRowProps): JSX.Element;
