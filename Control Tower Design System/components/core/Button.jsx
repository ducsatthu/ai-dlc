import React from 'react';

const SIZES = {
  sm: { padding: '5px 12px', fontSize: 'var(--fs-mono-xs)', letterSpacing: 'var(--ls-chip)' },
  md: { padding: '8px 16px', fontSize: 'var(--fs-sm)', letterSpacing: '0.04em' },
  lg: { padding: '10px 20px', fontSize: 'var(--fs-body-sm)', letterSpacing: '0.04em' }
};

const VARIANTS = {
  primary: { color: 'var(--on-accent)', background: 'var(--accent)', borderColor: 'var(--accent)' },
  secondary: { color: 'var(--ink)', background: 'var(--surface)', borderColor: 'var(--line)' },
  ghost: { color: 'var(--muted)', background: 'transparent', borderColor: 'transparent' },
  danger: { color: 'var(--danger)', background: 'var(--danger-bg)', borderColor: 'var(--danger)' },
  ok: { color: 'var(--ok)', background: 'var(--ok-bg)', borderColor: 'var(--ok)' }
};

export function Button({ variant = 'secondary', size = 'md', disabled = false, full = false, children, style, ...rest }) {
  const [hover, setHover] = React.useState(false);
  const v = VARIANTS[variant] || VARIANTS.secondary;
  return (
    <button
      type="button"
      disabled={disabled}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        fontFamily: 'var(--mono)',
        fontWeight: 'var(--fw-medium)',
        textTransform: 'uppercase',
        borderRadius: 'var(--radius-sm)',
        borderWidth: 1, borderStyle: 'solid',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.45 : hover ? 0.86 : 1,
        display: 'inline-flex', alignItems: 'center', gap: 'var(--sp-3)',
        width: full ? '100%' : undefined,
        justifyContent: 'center',
        transition: 'opacity var(--dur-fast) var(--ease-standard)',
        ...SIZES[size], ...v, ...style
      }}
      {...rest}
    >{children}</button>
  );
}
