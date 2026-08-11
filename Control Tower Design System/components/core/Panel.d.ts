import * as React from 'react';

/**
 * The console's only container: hairline border, 12px radius, sunken mono uppercase header. Never shadowed.
 */
export interface PanelProps extends React.HTMLAttributes<HTMLElement> {
  /** uppercase mono header label; omit for a bare bordered surface */
  title?: React.ReactNode;
  /** right-aligned mono meta in the header (counts, timestamps) */
  meta?: React.ReactNode;
  /** false = zero body padding, for tables and row lists */
  pad?: boolean;
  /** square corners, for panels flush inside a grid */
  flush?: boolean;
  children?: React.ReactNode;
}
export declare function Panel(props: PanelProps): JSX.Element;
