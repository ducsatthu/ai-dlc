import * as React from 'react';

/** One line of the live feed: time · id · from → to · type badge · one-line summary. Mono throughout — this is a traceable record, not chat. */
export interface FeedItemProps extends React.HTMLAttributes<HTMLDivElement> {
  /** "14:22" */
  time?: string;
  /** "MSG-0058" */
  id?: string;
  from?: string;
  to?: string;
  type?: 'review-request' | 'finding' | 'question' | 'answer' | 'clarification' | 'handoff' | 'note' | 'decision' | 'escalation';
  summary?: React.ReactNode;
  /** just-arrived row: amber left rule */
  isNew?: boolean;
  onClick?: React.MouseEventHandler<HTMLDivElement>;
}
export declare function FeedItem(props: FeedItemProps): JSX.Element;
