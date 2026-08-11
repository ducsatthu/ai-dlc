import * as React from 'react';

/** One intent on the pipeline board: id · name · 8 stage chips · the agent currently holding the ball. */
export interface PipelineRowProps extends React.HTMLAttributes<HTMLDivElement> {
  /** e.g. "INT-001" */
  id?: string;
  name?: React.ReactNode;
  current?: number;
  gate?: string;
  /** agent id holding the ball */
  holder?: string;
  holderLane?: 'pipeline' | 'review' | 'human' | 'learning';
  onClick?: React.MouseEventHandler<HTMLDivElement>;
}
export declare function PipelineRow(props: PipelineRowProps): JSX.Element;
