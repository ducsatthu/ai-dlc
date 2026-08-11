import * as React from 'react';

/**
 * The 8-stage AI-DLC flow as chips: done (green) → current (amber, marked ◇<gate> when a gate is open) → pending (grey).
 */
export interface StageStripProps extends React.HTMLAttributes<HTMLDivElement> {
  /** 1–8, the stage the intent is sitting in */
  current?: number;
  /** open gate letter A–G shown on the current chip */
  gate?: string;
  /** render stage names instead of numbers */
  labels?: boolean;
  compact?: boolean;
}
export declare function StageStrip(props: StageStripProps): JSX.Element;
export declare const STAGES: string[];
