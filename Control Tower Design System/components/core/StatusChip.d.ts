import * as React from 'react';

/** Pill-shaped document/page status marker (masthead, screen header). Larger and rounder than Chip. */
export interface StatusChipProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: 'gate' | 'agent' | 'done' | 'danger' | 'muted';
  /** leading status dot */
  dot?: boolean;
  children?: React.ReactNode;
}
export declare function StatusChip(props: StatusChipProps): JSX.Element;
