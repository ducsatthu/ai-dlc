import * as React from 'react';

/** Numbered section label above an h2 in documents ("01 · Đội hình"), with a rule filling the line. */
export interface EyebrowProps extends React.HTMLAttributes<HTMLDivElement> {
  /** draw the hairline rule to the right of the label */
  rule?: boolean;
  children?: React.ReactNode;
}
export declare function Eyebrow(props: EyebrowProps): JSX.Element;
