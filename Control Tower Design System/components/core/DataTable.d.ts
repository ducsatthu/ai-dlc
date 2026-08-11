import * as React from 'react';

/**
 * Dense reference table: mono uppercase headers on a 2px ink rule, hairline row separators, no zebra, no outer border.
 */
export interface DataTableProps extends React.TableHTMLAttributes<HTMLTableElement> {
  columns?: React.ReactNode[];
  /** row-major cells */
  rows?: React.ReactNode[][];
  /** render the first column in mono (IDs) — default true */
  monoFirst?: boolean;
}
export declare function DataTable(props: DataTableProps): JSX.Element;
