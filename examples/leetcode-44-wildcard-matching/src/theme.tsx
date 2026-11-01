import React from 'react';
import {Easing, interpolate, staticFile} from 'remotion';
import {loadFont} from '@remotion/fonts';
import timelineJson from './timeline.json';

/** UI language: scripts/build_timeline.py stamps KIEU_LANG into timeline.json. */
export const EN = (timelineJson as unknown as {lang?: string}).lang === 'en';
export const t = <V,>(vi: V, en: V): V => (EN ? en : vi);

/** Kieu Studio palette (kieu-studio data/brand.yaml) + semantic colours for match / mismatch. */
export const C = {
  bg: '#071321',
  bg2: '#102338',
  surface: '#142c43',
  glass: 'rgba(20,44,67,0.74)',
  line: 'rgba(115,237,240,0.28)',
  cyan: '#31C4CF',
  cyanLight: '#73EDF0',
  text: '#F3FAFF',
  muted: '#9EB7C8',
  warn: '#F5BA68',
  good: '#58E1A4',
  bad: '#FF7B8E',
  blue: '#6AA9FF',
};
// Noto Sans has no arrows/math signs (→ ≈ ≠ ≤ ≥ ▲ ▼); the vendored JetBrains Mono does, so it is the deterministic fallback
// (never a system font). scripts/check_visual_glyphs.py enforces that every character is covered by this stack.
export const FONT = '"Noto Sans EP03","JetBrains Mono EP03",Arial,sans-serif';
export const MONO = '"JetBrains Mono EP03","JetBrains Mono",Menlo,Consolas,monospace';

let fontsLoaded = false;
export function ensureFonts() {
  if (fontsLoaded) return;
  fontsLoaded = true;
  loadFont({family: 'Noto Sans EP03', url: staticFile('fonts/NotoSans-Variable.ttf'), weight: '100 900'});
  loadFont({family: 'JetBrains Mono EP03', url: staticFile('fonts/JetBrainsMono-Variable.ttf'), weight: '100 800'});
}

export const easeOut = Easing.out(Easing.cubic);
export const easeInOut = Easing.inOut(Easing.cubic);

/** 0 → 1 over `dur` frames starting at `start` (eased, clamped). */
export function ramp(frame: number, start: number, dur = 14, ease: (t: number) => number = easeOut) {
  return interpolate(frame, [start, start + dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
}

export const glass: React.CSSProperties = {
  background: C.glass,
  border: `2px solid ${C.line}`,
  borderRadius: 26,
  boxShadow: '0 18px 50px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06)',
};

export const Glass: React.FC<{style?: React.CSSProperties; children?: React.ReactNode}> = ({style, children}) => (
  <div style={{...glass, ...style}}>{children}</div>
);

export const Pill: React.FC<{color?: string; children: React.ReactNode; size?: number; style?: React.CSSProperties}> = ({color = C.cyan, children, size = 26, style}) => (
  <span style={{display: 'inline-block', padding: '6px 18px', borderRadius: 999, border: `2px solid ${color}`, color, fontSize: size, fontWeight: 700, letterSpacing: 0.5, whiteSpace: 'nowrap', ...style}}>
    {children}
  </span>
);

export type TokState = 'idle' | 'match' | 'eaten' | 'bad' | 'cursor' | 'dim';
const tokColors: Record<TokState, {bg: string; border: string; fg: string}> = {
  idle: {bg: 'rgba(20,44,67,0.9)', border: C.line, fg: C.text},
  match: {bg: 'rgba(88,225,164,0.18)', border: C.good, fg: C.good},
  eaten: {bg: 'rgba(245,186,104,0.20)', border: C.warn, fg: C.warn},
  bad: {bg: 'rgba(255,123,142,0.20)', border: C.bad, fg: C.bad},
  cursor: {bg: 'rgba(49,196,207,0.22)', border: C.cyanLight, fg: C.cyanLight},
  dim: {bg: 'rgba(20,44,67,0.45)', border: 'rgba(115,237,240,0.12)', fg: C.muted},
};

/** One character tile (string character or pattern symbol). */
export const Tok: React.FC<{ch: string; state?: TokState; w?: number; h?: number; size?: number; label?: string; style?: React.CSSProperties}> = ({
  ch, state = 'idle', w = 104, h = 104, size = 62, label, style,
}) => {
  const k = tokColors[state];
  return (
    <div style={{position: 'relative', width: w, height: h, borderRadius: 20, border: `3px solid ${k.border}`, background: k.bg, color: k.fg,
      display: 'grid', placeItems: 'center', fontFamily: MONO, fontSize: size, fontWeight: 800, boxSizing: 'border-box', ...style}}>
      {ch}
      {label ? <div style={{position: 'absolute', top: -34, left: 0, right: 0, textAlign: 'center', fontFamily: MONO, fontSize: 22, color: C.muted, fontWeight: 600}}>{label}</div> : null}
    </div>
  );
};

export const Card: React.FC<{title?: string; accent?: string; active?: boolean; children?: React.ReactNode; style?: React.CSSProperties}> = ({
  title, accent = C.cyan, active = true, children, style,
}) => (
  <Glass style={{padding: '22px 30px', borderColor: active ? accent : C.line, opacity: active ? 1 : 0.5, ...style}}>
    {title ? <div style={{color: accent, fontSize: 26, fontWeight: 800, letterSpacing: 1, marginBottom: 10}}>{title}</div> : null}
    {children}
  </Glass>
);

/** Thousands grouping: 967654 → "967.654" (vi) or "967,654" (en). */
export const vn = (n: number) => (EN ? n.toLocaleString('en-US') : n.toLocaleString('en-US').replace(/,/g, '.'));
