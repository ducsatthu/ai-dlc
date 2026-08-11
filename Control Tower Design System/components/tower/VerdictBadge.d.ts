import * as React from 'react';

/** A review verdict (RV) rendered as one mono badge: id · reviewer · verdict. */
export interface VerdictBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** e.g. "RV-012" */
  id?: string;
  /** e.g. "tech-lead" */
  reviewer?: string;
  verdict?: 'approve' | 'approve-with-notes' | 'request-changes';
}
export declare function VerdictBadge(props: VerdictBadgeProps): JSX.Element;
