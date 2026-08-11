import * as React from 'react';

/** Visual answer to "truy vết một quyết định": the chain code → design → spec → DEC → RV → MSG → intent as typed, colour-coded cards instead of a line of text. */
export interface TraceStep {
  /** colours and labels the card */
  kind: 'code' | 'design' | 'spec' | 'task' | 'dec' | 'gate' | 'rv' | 'msg' | 'intent';
  /** the identifier or filename shown in mono */
  id: string;
  /** optional one-line explanation under the id */
  note?: string;
}
export interface TraceChainProps extends React.HTMLAttributes<HTMLDivElement> {
  steps?: TraceStep[];
  /** horizontal scrolls sideways; vertical stacks (better in a narrow drawer) */
  direction?: 'horizontal' | 'vertical';
  activeId?: string;
  onSelect?: (step: TraceStep) => void;
}
export declare function TraceChain(props: TraceChainProps): JSX.Element;
