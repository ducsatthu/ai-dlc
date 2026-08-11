import * as React from 'react';

/**
 * The gate queue's unit of work: an amber card carrying a decision brief and Approve / Reject / Discuss. Reject requires a reason.
 */
export interface GateCardProps extends React.HTMLAttributes<HTMLElement> {
  /** gate letter A–G (ignored when kind="escalation") */
  gate?: string;
  /** what the gate is about, e.g. "INT-001" or "UOW-03" */
  target?: string;
  title?: React.ReactNode;
  /** 2–3 line context line from ba-reviewer */
  brief?: React.ReactNode;
  /** the options and their trade-offs */
  options?: React.ReactNode[];
  recommendation?: React.ReactNode;
  /** artifact / verdict ids backing the brief, e.g. ["RV-010","units/UOW-01/spec.md"] */
  evidence?: string[];
  /** escalation renders △ instead of ◇ */
  kind?: 'gate' | 'escalation';
  /** controlled expansion; omit to let the card manage it */
  expanded?: boolean;
  defaultExpanded?: boolean;
  onApprove?: () => void;
  /** receives the required rejection reason */
  onReject?: (reason: string) => void;
  onDiscuss?: () => void;
}
export declare function GateCard(props: GateCardProps): JSX.Element;
