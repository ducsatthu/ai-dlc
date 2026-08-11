import * as React from 'react';

/** Document-side counterpart of GateCard: the "◇ GATE A — DỪNG, CHỜ ANH/CHỊ" block inside a narrative timeline. */
export interface GateStopProps extends React.HTMLAttributes<HTMLDivElement> {
  /** e.g. "◇ GATE A — DỪNG, CHỜ ANH/CHỊ (lần confirm #1)" */
  label?: React.ReactNode;
  children?: React.ReactNode;
}
export declare function GateStop(props: GateStopProps): JSX.Element;
