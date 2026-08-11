import * as React from 'react';

/**
 * Action control. Mono, uppercase, hairline border — matches the console's label styling.
 */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** primary = amber (the human decision), ok = approve, danger = reject */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'ok';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  /** stretch to container width */
  full?: boolean;
  children?: React.ReactNode;
}
export declare function Button(props: ButtonProps): JSX.Element;
