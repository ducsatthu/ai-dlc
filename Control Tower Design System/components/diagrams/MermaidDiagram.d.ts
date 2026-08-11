import * as React from 'react';

/**
 * Renders a Mermaid diagram inside the system's standard bordered figure, themed from the live CSS tokens
 * (so it follows light/dark automatically). Mermaid 11 is loaded from CDN on first use.
 */
export interface MermaidDiagramProps extends React.HTMLAttributes<HTMLElement> {
  /** Mermaid source: flowchart, sequenceDiagram, stateDiagram-v2, gantt … */
  chart: string;
  /** caption below the figure, 13.5px muted */
  caption?: React.ReactNode;
  /** horizontal scroll for wide diagrams (default true) — diagrams always render at natural size */
  scroll?: boolean;
}
export declare function MermaidDiagram(props: MermaidDiagramProps): JSX.Element;
