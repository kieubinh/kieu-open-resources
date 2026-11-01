import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {C, FONT, MONO, Tok, TokState, ensureFonts, t} from './theme';

ensureFonts();

/** 1280×720 YouTube thumbnail: question hook + the three symbols of the problem. */
type ThumbProps = {ep?: string; tag?: string; l1?: string; l2?: string; hook?: string; row?: [string, TokState][]; code?: string; note?: string};

export const Thumbnail: React.FC<ThumbProps> = ({ep = 'EP03', tag = 'HARD · #44', l1 = 'Wildcard', l2 = 'Matching', hook, code, note,
  row = [['a', 'match'], ['?', 'cursor'], ['*', 'eaten'], ['e', 'match']]}) => {
  return (
    <AbsoluteFill style={{background: `radial-gradient(900px 520px at 85% 10%, rgba(49,196,207,0.28), transparent 60%), linear-gradient(135deg, ${C.bg} 0%, #0c2a40 100%)`, fontFamily: FONT, color: C.text}}>
      <div style={{position: 'absolute', left: 54, top: 40, display: 'flex', alignItems: 'center', gap: 16}}>
        <div style={{width: 64, height: 64, borderRadius: 16, background: '#F3F8FF', display: 'grid', placeItems: 'center'}}>
          <Img src={staticFile('brand/kieu-studio-mark.png')} style={{height: 60, width: 'auto'}} />
        </div>
        <div style={{fontSize: 30, fontWeight: 800, color: C.cyan, letterSpacing: 1}}>KIEU STUDIO · {ep}</div>
      </div>
      <div style={{position: 'absolute', right: 54, top: 44, padding: '8px 26px', borderRadius: 999, border: `3px solid ${C.bad}`, color: C.bad, fontSize: 38, fontWeight: 800}}>{tag}</div>
      <div style={{position: 'absolute', left: 54, top: 150, width: 1170}}>
        <div style={{fontSize: 118, fontWeight: 800, lineHeight: 1.0, letterSpacing: -1}}>{l1}</div>
        <div style={{fontSize: 118, fontWeight: 800, lineHeight: 1.0, letterSpacing: -1, color: C.cyanLight}}>{l2}</div>
        <div style={{fontSize: 52, fontWeight: 800, marginTop: 22, color: C.warn}}>{hook ?? t('Dấu * nên nuốt bao nhiêu ký tự?', 'How many characters should * swallow?')}</div>
      </div>
      <div style={{position: 'absolute', left: 54, bottom: 58, display: 'flex', gap: 18}}>
        {row.map(([ch, st], k) => <Tok key={k} ch={ch} state={st} w={118} h={118} size={72} />)}
      </div>
      <div style={{position: 'absolute', right: 54, bottom: 62, textAlign: 'right'}}>
        <div style={{fontFamily: MONO, fontSize: 40, fontWeight: 800, color: C.good}}>{code ?? t('Python 3 · O(1) bộ nhớ', 'Python 3 · O(1) memory')}</div>
        <div style={{fontSize: 34, fontWeight: 700, color: C.muted, marginTop: 6}}>{note ?? t('10 giây tự nghĩ trước lời giải', '10-second challenge inside')}</div>
      </div>
    </AbsoluteFill>
  );
};
