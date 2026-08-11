import * as React from 'react';

/** Inline emphasis block in prose — a finding, a caveat, a "phát hiện quan trọng". Left rule only, no full border. */
export interface CalloutProps extends React.HTMLAttributes<HTMLDivElement> {
  tone?: 'agent' | 'gate' | 'done';
  children?: React.ReactNode;
}
export declare function Callout(props: CalloutProps): JSX.Element;
