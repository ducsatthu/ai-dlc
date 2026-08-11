import * as React from 'react';

/** Smallest status atom: an 8-stage step, a task status, a filter token. Mono, 10.5px, 4px radius. */
export interface ChipProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** done=green · active=amber · here=solid amber · agent=blue · blocked=red · pending=outline */
  tone?: 'pending' | 'done' | 'active' | 'agent' | 'blocked' | 'here' | 'neutral';
  children?: React.ReactNode;
}
export declare function Chip(props: ChipProps): JSX.Element;
