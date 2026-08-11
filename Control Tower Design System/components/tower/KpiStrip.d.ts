import * as React from 'react';

/** The thin top strip of Mission Control: 3–5 counts, mono numerals, divided by hairlines. */
export interface KpiItem {
  value: React.ReactNode;
  label: string;
  /** colours the numeral; gate = amber (needs you) */
  tone?: 'gate' | 'agent' | 'done' | 'neutral';
}
export interface KpiStripProps extends React.HTMLAttributes<HTMLDivElement> {
  items?: KpiItem[];
}
export declare function KpiStrip(props: KpiStripProps): JSX.Element;
