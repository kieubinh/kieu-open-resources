import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile} from 'remotion';
import {C, EN, FONT, ramp} from './theme';
import {Ctx, SceneRow, timeline} from './timeline';

const CODE_MODES = new Set(['code1', 'code2']);

export const Header: React.FC = () => (
  <div style={{position: 'absolute', left: 80, right: 80, top: 26, height: 72, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 18}}>
      <div style={{width: 66, height: 66, borderRadius: 16, background: '#F3F8FF', display: 'grid', placeItems: 'center', overflow: 'hidden'}}>
        <Img src={staticFile('brand/kieu-studio-mark.png')} style={{height: 62, width: 'auto'}} />
      </div>
      <div style={{fontSize: 30, fontWeight: 800, letterSpacing: 1}}>
        <span style={{color: C.cyan}}>KIEU STUDIO</span>
        <span style={{color: C.muted, fontWeight: 500}}> · THE ART OF CODING</span>
      </div>
    </div>
    <div style={{display: 'flex', alignItems: 'center', gap: 26}}>
      <span style={{color: C.warn, fontSize: 27, fontWeight: 800, letterSpacing: 0.5}}>LEETCODE #44 · HARD</span>
      <span style={{color: C.cyanLight, fontSize: 30, fontWeight: 700}}>kieu.app</span>
    </div>
  </div>
);

export const Subtitle: React.FC<{c: Ctx}> = ({c}) => {
  const beats = c.scene.beats;
  const b = c.beat >= 0 ? beats[c.beat] : null;
  if (!b || c.f >= b.endFrame || c.f < b.startFrame) return null;
  const fadeIn = interpolate(c.f - b.startFrame, [0, 8], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: EN ? 150 : 120, right: EN ? 340 : 120, bottom: 50, display: 'flex', justifyContent: 'center', opacity: fadeIn}}>
      <div style={{background: 'rgba(5,14,25,0.86)', border: `1.5px solid ${C.line}`, borderRadius: 20, padding: '14px 32px', maxWidth: 1640, textAlign: 'center',
        fontSize: 38, lineHeight: 1.32, fontWeight: 600, color: C.text, textWrap: 'balance' as React.CSSProperties['textWrap']}}>
        {b.text}
      </div>
    </div>
  );
};

export const SceneFrame: React.FC<{c: Ctx; children: React.ReactNode}> = ({c, children}) => {
  const s: SceneRow = c.scene;
  const code = CODE_MODES.has(s.mode);
  const enter = ramp(c.f, 0, 18);
  const out = interpolate(c.f, [s.frames - 18, s.frames], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const stageTop = code ? 118 : 262;
  const progress = (s.fromFrame + c.f) / timeline.totalFrames;
  return (
    <AbsoluteFill style={{background: `radial-gradient(1200px 700px at 78% 8%, rgba(49,196,207,0.13), transparent 60%), linear-gradient(180deg, ${C.bg} 0%, ${C.bg2} 100%)`,
      color: C.text, fontFamily: FONT, fontVariantLigatures: 'none', fontFeatureSettings: '"liga" 0, "calt" 0'}}>
      <Header />
      <div style={{position: 'absolute', left: 80, right: 80, top: 104, height: 2, background: C.line}} />
      {!code && (
        <div style={{position: 'absolute', left: 80, right: 80, top: 122, opacity: enter * out, transform: `translateY(${(1 - enter) * 18}px)`}}>
          <div style={{color: C.cyan, fontSize: 26, fontWeight: 800, letterSpacing: 2}}>{s.phase}</div>
          <div style={{fontSize: 60, fontWeight: 800, lineHeight: 1.12, marginTop: 6}}>{s.title}</div>
        </div>
      )}
      <div style={{position: 'absolute', left: 80, right: 80, top: stageTop, bottom: 190, opacity: enter * out, transform: EN ? 'scale(0.88)' : undefined, transformOrigin: 'top left'}}>{children}</div>
      <div style={{opacity: out}}><Subtitle c={c} /></div>
      <div style={{position: 'absolute', left: 0, bottom: 0, height: 5, width: `${progress * 100}%`, background: C.cyan, opacity: 0.8}} />
    </AbsoluteFill>
  );
};
