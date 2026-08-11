import React from 'react';

const CDN = 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js';
let loader = null;

function loadMermaid() {
  if (window.mermaid) return Promise.resolve(window.mermaid);
  if (!loader) {
    loader = new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = CDN;
      s.onload = () => resolve(window.mermaid);
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }
  return loader;
}

function tokens() {
  const cs = getComputedStyle(document.documentElement);
  const v = n => (cs.getPropertyValue(n) || '').trim();
  return {
    ink: v('--ink') || '#18222C', muted: v('--muted') || '#5B6874', line: v('--line') || '#CFD7DE',
    surface: v('--surface') || '#FFFFFF', surface2: v('--surface-2') || '#E9EDF1', bg: v('--bg') || '#F2F4F6',
    accent: v('--accent') || '#B96E00', blue: v('--blue') || '#33689E', ok: v('--ok') || '#2E7D4F',
    mono: v('--mono') || 'ui-monospace, monospace'
  };
}

/* Brand theme: flat surfaces, hairline borders, mono labels, amber = human decision. */
function themeConfig(t) {
  return {
    startOnLoad: false,
    securityLevel: 'loose',
    fontFamily: t.mono,
    theme: 'base',
    themeVariables: {
      background: 'transparent',
      primaryColor: t.surface2, primaryTextColor: t.ink, primaryBorderColor: t.line,
      secondaryColor: t.surface, secondaryTextColor: t.ink, secondaryBorderColor: t.line,
      tertiaryColor: t.surface, tertiaryTextColor: t.muted, tertiaryBorderColor: t.line,
      lineColor: t.muted, textColor: t.ink, mainBkg: t.surface2, nodeBorder: t.line,
      clusterBkg: t.bg, clusterBorder: t.line, titleColor: t.muted,
      edgeLabelBackground: t.surface, fontSize: '13px',
      actorBkg: t.surface2, actorBorder: t.line, actorTextColor: t.ink, actorLineColor: t.line,
      signalColor: t.ink, signalTextColor: t.muted, labelBoxBkg: t.surface2, labelBoxBorderColor: t.accent,
      labelTextColor: t.ink, loopTextColor: t.muted, noteBkgColor: t.surface, noteBorderColor: t.accent, noteTextColor: t.ink,
      sequenceNumberColor: t.surface,
      transitionColor: t.muted, stateBkg: t.surface2, stateLabelColor: t.ink, altBackground: t.bg,
      compositeBackground: t.bg, compositeBorder: t.line, innerEndBackground: t.ink,
      pie1: t.accent, pie2: t.blue, pie3: t.ok
    },
    flowchart: { curve: 'basis', padding: 12, nodeSpacing: 34, rankSpacing: 46, useMaxWidth: false },
    sequence: { useMaxWidth: false, actorMargin: 46, boxMargin: 8, mirrorActors: false, messageFontSize: 12, noteFontSize: 12 }
  };
}

/* Mermaid's classDef parser rejects var(--x); resolve token references to literal colours first. */
function toHex(v) {
  const m = /^rgba?\(([^)]+)\)$/i.exec(v.trim());
  if (!m) return v;
  const p = m[1].split(/[\s,\/]+/).filter(Boolean);
  const h = n => Math.round(parseFloat(n)).toString(16).padStart(2, '0');
  const a = p[3] === undefined ? '' : Math.round(parseFloat(p[3]) * 255).toString(16).padStart(2, '0');
  return '#' + h(p[0]) + h(p[1]) + h(p[2]) + a;
}

function resolveVars(src) {
  const cs = getComputedStyle(document.documentElement);
  return String(src).replace(/var\(\s*(--[\w-]+)\s*\)/g, (m, name) => {
    const v = (cs.getPropertyValue(name) || '').trim();
    return v ? toHex(v) : m;
  });
}

let seq = 0;

export function MermaidDiagram({ chart, caption, scroll = true, style, ...rest }) {
  const ref = React.useRef(null);
  const [err, setErr] = React.useState(null);
  const id = React.useRef('mmd-' + (++seq));

  React.useEffect(() => {
    let alive = true;
    loadMermaid().then(m => {
      if (!alive || !chart) return;
      const t = tokens();
      m.initialize(themeConfig(t));
      return m.render(id.current, resolveVars(chart.trim())).then(({ svg }) => {
        if (!alive || !ref.current) return;
        ref.current.innerHTML = svg;
        const el = ref.current.querySelector('svg');
        // Natural size only: forcing width/height rescales text away from the document's type sizes.
        if (el) { el.style.display = 'block'; }
      });
    }).catch(e => alive && setErr(String(e && e.message || e)));
    return () => { alive = false; };
  }, [chart]);

  return (
    <figure style={{
      margin: '24px 0 8px', background: 'var(--surface)', border: '1px solid var(--line)',
      borderRadius: 'var(--radius-xl)', padding: 20, overflowX: scroll ? 'auto' : 'visible', ...style
    }} {...rest}>
      <div ref={ref} />
      {err && <div style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--danger)' }}>Diagram lỗi: {err}</div>}
      {caption && <figcaption style={{ fontSize: 13.5, color: 'var(--muted)', marginTop: 14, maxWidth: '80ch' }}>{caption}</figcaption>}
    </figure>
  );
}
