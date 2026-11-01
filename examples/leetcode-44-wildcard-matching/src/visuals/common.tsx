import React from 'react';
import {C, MONO, Tok, TokState, ramp} from '../theme';
import {Ctx} from '../timeline';

export const fade = (c: Ctx, beat: number, dur = 14) => {
  const t = ramp(c.since(beat), 0, dur);
  return {opacity: t, transform: `translateY(${(1 - t) * 22}px)`} as React.CSSProperties;
};

export type Mark = {side: 'top' | 'bottom'; idx: number; label: string; color: string; level?: number};
export type Link = {si: number; pj: number; color: string; opacity?: number; dash?: boolean};

const ROW_GAP = 76;   // vertical room for match links between the two rows
const S_TOP = 96;     // room above row s for pointer marks (two levels)
const NAME_W = 64;    // left column with the names "s" and "p"

export const alignHeight = (w: number) => S_TOP + w + ROW_GAP + w + 6 + 88 + 12;

/** Two aligned rows (string s above, pattern p below) with pointer marks and match links. */
export const Align: React.FC<{
  s: string; p: string; sStates?: TokState[]; pStates?: TokState[]; marks?: Mark[]; links?: Link[];
  w?: number; endBox?: {label: string; show: boolean};
}> = ({s, p, sStates = [], pStates = [], marks = [], links = [], w = 120, endBox}) => {
  const gap = Math.round(w * 0.13);
  const step = w + gap;
  const x0 = NAME_W;
  const P_TOP = S_TOP + w + ROW_GAP;
  const cx = (idx: number) => x0 + idx * step + w / 2;
  const H = alignHeight(w);
  const size = Math.round(w * 0.52);
  return (
    <div style={{position: 'relative', width: x0 + Math.max(s.length, p.length + 1) * step + 20, height: H}}>
      <div style={{position: 'absolute', left: 0, top: S_TOP, height: w, width: NAME_W - 14, display: 'grid', placeItems: 'center', color: C.muted, fontFamily: MONO, fontSize: 40, fontWeight: 800}}>s</div>
      <div style={{position: 'absolute', left: x0, top: S_TOP, display: 'flex', gap}}>
        {s.split('').map((ch, k) => <Tok key={k} ch={ch} w={w} h={w} size={size} state={sStates[k] ?? 'idle'} />)}
      </div>
      <div style={{position: 'absolute', left: 0, top: P_TOP, height: w, width: NAME_W - 14, display: 'grid', placeItems: 'center', color: C.muted, fontFamily: MONO, fontSize: 40, fontWeight: 800}}>p</div>
      <div style={{position: 'absolute', left: x0, top: P_TOP, display: 'flex', gap}}>
        {p.split('').map((ch, k) => <Tok key={k} ch={ch} w={w} h={w} size={size} state={pStates[k] ?? 'idle'} />)}
      </div>
      {endBox?.show && (
        <div style={{position: 'absolute', left: x0 + p.length * step, top: P_TOP, width: w + 30, height: w, border: `3px dashed ${C.bad}`, borderRadius: 20, boxSizing: 'border-box',
          display: 'grid', placeItems: 'center', color: C.bad, fontSize: 28, fontWeight: 700, textAlign: 'center', lineHeight: 1.15}}>{endBox.label}</div>
      )}
      <svg width="100%" height={H} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
        {links.map((l, k) => (
          <line key={k} x1={cx(l.si)} y1={S_TOP + w + 4} x2={cx(l.pj)} y2={P_TOP - 4} stroke={l.color} strokeWidth={5} strokeLinecap="round"
            strokeDasharray={l.dash ? '10 8' : undefined} opacity={l.opacity ?? 1} />
        ))}
      </svg>
      {marks.map((m, k) => {
        const lvl = m.level ?? 0;
        const top = m.side === 'top' ? S_TOP - 46 - lvl * 44 : P_TOP + w + 6 + lvl * 44;
        return (
          <div key={k} style={{position: 'absolute', left: cx(m.idx) - 70, width: 140, top, textAlign: 'center', color: m.color, fontFamily: MONO, fontWeight: 800, fontSize: 30, lineHeight: '40px', whiteSpace: 'nowrap'}}>
            {m.side === 'top' ? <>{m.label}▼</> : <>▲{m.label}</>}
          </div>
        );
      })}
    </div>
  );
};

export const Banner: React.FC<{ok: boolean; text: string; style?: React.CSSProperties}> = ({ok, text, style}) => (
  <div style={{borderRadius: 22, padding: '18px 30px', border: `3px solid ${ok ? C.good : C.bad}`, background: ok ? 'rgba(88,225,164,0.14)' : 'rgba(255,123,142,0.14)',
    color: ok ? C.good : C.bad, fontSize: 38, fontWeight: 800, ...style}}>{text}</div>
);
