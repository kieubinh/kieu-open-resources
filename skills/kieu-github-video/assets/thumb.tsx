import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {C, sans, mono} from './theme';
import {Icon} from './art';

/** YouTube thumbnail, 1280x720. Separate entry point (src/thumb-index.ts): `npx remotion still src/thumb-index.ts Thumb out.png --props='{...}'`. */
export type ThumbProps = {l1: string; l2: string; l3?: string; col: string; repo: string; stars: string; chip: string; badge: string; icon: string};
export const defaultThumb: ThumbProps = {l1: 'AI BÁO', l2: '20 LỖ HỔNG', l3: 'CÁI NÀO THẬT?', col: '#57ecd0', repo: 'cloudflare/security-audit-skill', stars: '52.530', chip: 'x2,2 trong 30 ngày', badge: 'GITHUB RADAR · TẬP 1', icon: 'shield'};

const fit = (t: string) => Math.min(118, Math.floor(700 / (t.length * 0.58)));   // keep each line on one row
export const Thumb: React.FC<Partial<ThumbProps>> = (raw) => {
  const p = {...defaultThumb, ...raw};
  return <AbsoluteFill style={{background: `radial-gradient(900px 700px at 80% 40%, ${p.col}33, transparent 70%), linear-gradient(135deg, #07101f, ${C.bg} 60%, #0d2a4a)`, fontFamily: sans, color: C.white, overflow: 'hidden'}}>
    <svg width={1280} height={720} style={{position: 'absolute', inset: 0, opacity: 0.35}}>
      {[160, 300, 440, 600].map((r) => <circle key={r} cx={1010} cy={330} r={r} fill="none" stroke={p.col} strokeOpacity={0.25} strokeWidth={2} />)}
      <line x1={1010} y1={0} x2={1010} y2={720} stroke={p.col} strokeOpacity={0.15} /><line x1={300} y1={330} x2={1280} y2={330} stroke={p.col} strokeOpacity={0.15} />
    </svg>
    <div style={{position: 'absolute', left: 56, top: 44, background: p.col, color: '#06101d', fontWeight: 900, fontSize: 30, letterSpacing: 1, padding: '10px 26px', borderRadius: 40}}>{p.badge}</div>
    <div style={{position: 'absolute', left: 56, top: 128, width: 760, lineHeight: 1.0, fontWeight: 900, letterSpacing: -2, textShadow: '0 6px 24px #000a'}}>
      <div style={{fontSize: fit(p.l1), whiteSpace: 'nowrap'}}>{p.l1}</div>
      <div style={{fontSize: fit(p.l2), color: p.col, whiteSpace: 'nowrap'}}>{p.l2}</div>
      {p.l3 && <div style={{fontSize: fit(p.l3), color: C.white, whiteSpace: 'nowrap'}}>{p.l3}</div>}
    </div>
    <div style={{position: 'absolute', left: 56, bottom: 48, display: 'flex', alignItems: 'center', gap: 16, background: '#0b1e36ee', border: `3px solid ${p.col}`, borderRadius: 22, padding: '12px 26px'}}>
      <Icon name={p.icon} size={48} color={p.col} />
      <span style={{fontFamily: mono, fontSize: 30, fontWeight: 800, color: p.col}}>{p.repo}</span>
    </div>
    <div style={{position: 'absolute', left: 820, top: 70, width: 400, height: 400, borderRadius: '50%', border: `12px solid ${p.col}`, overflow: 'hidden', background: '#071321',
      boxShadow: `0 0 80px ${p.col}aa, 0 20px 50px #000a`}}>
      <Img src={staticFile('brand/kieu-avatar.png')} style={{width: '100%', height: '100%', objectFit: 'cover', transform: 'scale(1.12)'}} />
    </div>
    <div style={{position: 'absolute', left: 800, top: 40, width: 120, height: 120, borderRadius: '50%', background: '#0b1e36', border: `5px solid ${p.col}`, display: 'grid', placeItems: 'center', boxShadow: '0 10px 30px #000a'}}>
      <Icon name={p.icon} size={70} color={p.col} />
    </div>
    <div style={{position: 'absolute', left: 800, top: 490, width: 440, background: '#0b1e36f2', border: `4px solid ${p.col}`, borderRadius: 28, padding: '14px 24px', textAlign: 'center', boxShadow: '0 12px 40px #000a'}}>
      <div style={{fontSize: 74, fontWeight: 900, lineHeight: 1.05}}><span style={{color: '#ffcc73'}}>★</span> {p.stars}</div>
      <div style={{fontSize: 36, fontWeight: 800, color: p.col}}>{p.chip}</div>
    </div>
    <div style={{position: 'absolute', right: 40, bottom: 18, fontSize: 28, fontWeight: 900, color: C.cyan}}>KIEU STUDIO</div>
  </AbsoluteFill>;
};
