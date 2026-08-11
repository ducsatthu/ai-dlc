import * as React from 'react';

/** Mono-initial disc identifying one of the 17 agents; ring colour encodes the agent's lane. No photos, no illustration. */
export interface AgentAvatarProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** agent id, e.g. "be-dev", "tech-lead-reviewer" */
  name?: string;
  lane?: 'pipeline' | 'review' | 'human' | 'learning';
  /** diameter in px, default 22 */
  size?: number;
  /** show the agent id next to the disc */
  withName?: boolean;
}
export declare function AgentAvatar(props: AgentAvatarProps): JSX.Element;
