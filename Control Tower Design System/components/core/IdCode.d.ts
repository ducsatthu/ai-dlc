import * as React from 'react';

/** Every traceable identifier (INT-001, UOW-01, TSK-02, MSG-0058, RV-012, DEC-0018, LL-002) renders in mono through this. */
export interface IdCodeProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** plain = bare mono id · inline = code-style within prose · artifact = bordered file/artifact token */
  variant?: 'plain' | 'inline' | 'artifact';
  children?: React.ReactNode;
}
export declare function IdCode(props: IdCodeProps): JSX.Element;
