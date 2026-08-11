import * as React from 'react';

/** Labels which lane an actor belongs to: PIPELINE · REVIEW BOARD · HUMAN · LEARNING. */
export interface TagProps extends React.HTMLAttributes<HTMLSpanElement> {
  kind?: 'pipeline' | 'review' | 'human' | 'learning';
  children?: React.ReactNode;
}
export declare function Tag(props: TagProps): JSX.Element;
