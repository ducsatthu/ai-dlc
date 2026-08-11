import * as React from 'react';

/** Narrative step in a flow walkthrough: a lane-coloured node, an actor chip, a heading and prose. Wrap items in `Timeline`. */
export interface TimelineItemProps extends React.HTMLAttributes<HTMLDivElement> {
  /** agent id(s) or role, shown as a chip */
  actor?: React.ReactNode;
  /** agent = blue hollow node · human = solid amber node */
  lane?: 'agent' | 'human';
  heading?: React.ReactNode;
  /** suppress bottom spacing on the final item */
  last?: boolean;
  children?: React.ReactNode;
}
export declare function TimelineItem(props: TimelineItemProps): JSX.Element;
export interface TimelineProps extends React.HTMLAttributes<HTMLDivElement> { children?: React.ReactNode }
export declare function Timeline(props: TimelineProps): JSX.Element;
