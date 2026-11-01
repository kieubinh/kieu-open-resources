import React from 'react';
import {C, Card, Glass, MONO, Pill, Tok, TokState, ramp, t} from '../theme';
import {Ctx} from '../timeline';
import {Align, Mark, fade} from './common';

const cueOf = (c: Ctx): number | null => {
  const b = c.scene.beats[c.beat];
  return b && typeof b.cue === 'number' ? b.cue : null;
};

/** Scene 09: three hints revealed one by one, then a prompt for the silent pause. */
export const Hints: React.FC<{c: Ctx}> = ({c}) => {
  const hints = [
    [t('GỢI Ý 1', 'HINT 1'), t('Nhiều lựa chọn chỉ xuất hiện ở một ký hiệu.', 'Many choices come from just one symbol.'), t('Là ký hiệu nào?', 'Which one?'), C.warn],
    [t('GỢI Ý 2', 'HINT 2'), t('Thu nhỏ bài toán.', 'Shrink the problem.'), t('i ký tự đầu của s có khớp j ký tự đầu của p không?', 'Do the first i characters of s match the first j of p?'), C.cyanLight],
    [t('GỢI Ý 3', 'HINT 3'), t('Khi gặp lệch, cần quay lại…', 'On a mismatch, go back to…'), t('mọi dấu * đã qua, hay chỉ một vài dấu?', 'every * so far, or just one?'), C.good],
  ];
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 24, height: '100%'}}>
      <div style={{display: 'flex', gap: 26, flex: 1}}>
        {hints.map(([t, a, b2, col], k) => {
          const on = c.beat >= k + 1;
          const now = c.beat === k + 1;
          return (
            <Glass key={t} style={{flex: 1, padding: '30px 32px', borderColor: on ? col : C.line, opacity: on ? (now || c.beat >= 4 ? 1 : 0.7) : 0.18,
              transform: `translateY(${on ? 0 : 30}px) scale(${now ? 1.02 : 1})`}}>
              <div style={{color: col, fontSize: 30, fontWeight: 800, letterSpacing: 2}}>{t}</div>
              <div style={{fontSize: 46, fontWeight: 800, lineHeight: 1.22, margin: '18px 0 14px'}}>{a}</div>
              <div style={{fontSize: 36, color: C.muted, lineHeight: 1.3}}>{b2}</div>
            </Glass>
          );
        })}
      </div>
      <div style={{...fade(c, 4), height: 120, display: 'flex', alignItems: 'center', gap: 28, padding: '0 36px', borderRadius: 26, border: `3px solid ${C.cyanLight}`, background: 'rgba(49,196,207,0.14)'}}>
        <Pill color={C.cyanLight} size={34}>{t('10 GIÂY', '10 SECONDS')}</Pill>
        <div style={{fontSize: 40, fontWeight: 800}}>{t(<>Nếu gặp dấu <span style={{fontFamily: MONO, color: C.warn}}>*</span>, bạn sẽ thử lựa chọn nào trước?</>, <>When you meet a <span style={{fontFamily: MONO, color: C.warn}}>*</span>, which choice do you try first?</>)}</div>
      </div>
    </div>
  );
};

/** Scene 10: exactly 10.0 s (300 frames) of silence. No audio, no subtitle; a countdown only. */
export const Think: React.FC<{c: Ctx}> = ({c}) => {
  const total = c.scene.frames; // 300
  const left = Math.max(1, Math.ceil((total - c.f) / 30));
  const R = 150, L = 2 * Math.PI * R;
  const prog = Math.min(1, c.f / total);
  const s = 'adceb', p = '*a*b';
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 70, height: '100%'}}>
      <div style={{width: 420, display: 'grid', placeItems: 'center'}}>
        <div style={{position: 'relative', width: 340, height: 340}}>
          <svg width={340} height={340} viewBox="0 0 340 340" style={{position: 'absolute', inset: 0}}>
            <circle cx={170} cy={170} r={R} fill="none" stroke="rgba(115,237,240,0.16)" strokeWidth={16} />
            <circle cx={170} cy={170} r={R} fill="none" stroke={C.cyanLight} strokeWidth={16} strokeLinecap="round" strokeDasharray={`${L * (1 - prog)} ${L}`} transform="rotate(-90 170 170)" />
          </svg>
          <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', fontFamily: MONO, fontSize: 170, fontWeight: 800, color: C.cyanLight}}>{left}</div>
        </div>
        <div style={{fontSize: 30, color: C.muted, marginTop: 16, fontWeight: 700}}>{t('giây suy nghĩ', 'seconds to think')}</div>
      </div>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 26}}>
        <div style={{fontSize: 52, fontWeight: 800, lineHeight: 1.2}}>{t('Đến lượt bạn. Hãy tự nghĩ.', 'Your turn. Think it through.')}</div>
        <div style={{fontSize: 36, color: C.muted, lineHeight: 1.35}}>{t(<>Nếu gặp dấu <span style={{fontFamily: MONO, color: C.warn}}>*</span>, bạn sẽ thử lựa chọn nào trước?</>, <>When you meet a <span style={{fontFamily: MONO, color: C.warn}}>*</span>, which choice do you try first?</>)}</div>
        <div>
          <div style={{fontFamily: MONO, color: C.muted, fontSize: 28, marginBottom: 8}}>s</div>
          <div style={{display: 'flex', gap: 14}}>{s.split('').map((ch, k) => <Tok key={k} ch={ch} w={100} h={100} size={56} />)}</div>
        </div>
        <div>
          <div style={{fontFamily: MONO, color: C.muted, fontSize: 28, marginBottom: 8}}>p</div>
          <div style={{display: 'flex', gap: 14}}>{p.split('').map((ch, k) => <Tok key={k} ch={ch} w={100} h={100} size={56} state={ch === '*' ? 'eaten' : 'idle'} />)}</div>
        </div>
      </div>
    </div>
  );
};

/** Scene 11: the simplest recursive idea, rule cards lit by cue. */
export const Rules: React.FC<{c: Ctx}> = ({c}) => {
  const cue = cueOf(c);
  const rules: [string, React.ReactNode, string][] = [
    [t('CÂU HỎI NHỎ', 'SMALL QUESTION'), t(<>f(i, j): s[i:] có khớp p[j:] không?</>, <>f(i, j): does s[i:] match p[j:]?</>), C.cyanLight],
    [t('CHỮ CÁI HOẶC ?', 'LETTER OR ?'), t(<>so s[i] với p[j], rồi gọi f(i+1, j+1)</>, <>compare s[i] with p[j], then call f(i+1, j+1)</>), C.good],
    [t('DẤU *', 'STAR *'), <>f(i, j+1) <b style={{color: C.warn}}>{t('HOẶC', 'OR')}</b> f(i+1, j)</>, C.warn],
    [t('HẾT MẪU', 'PATTERN ENDS'), t(<>j chạm cuối p → i phải chạm cuối s</>, <>j reaches the end of p → i must reach the end of s</>), C.bad],
  ];
  const skip = c.beat === 3, eat = c.beat === 4;
  const i = eat ? 1 : 0, j = skip ? 1 : 0;
  const marks: Mark[] = [{side: 'top', idx: i, label: 'i', color: C.cyanLight}, {side: 'bottom', idx: j, label: 'j', color: C.warn}];
  const sSt: TokState[] = eat ? ['eaten'] : [];
  const pSt: TokState[] = c.beat >= 3 ? ['eaten'] : [];
  return (
    <div style={{display: 'flex', gap: 40, height: '100%'}}>
      <div style={{width: 800, position: 'relative', ...fade(c, 1)}}>
        <Align s="adceb" p="*a*b" sStates={sSt} pStates={pSt} marks={c.beat >= 1 ? marks : []} />
        {(skip || eat) && (
          <div style={{position: 'absolute', left: 0, top: 524, fontFamily: MONO, fontSize: 34, fontWeight: 800, color: C.warn}}>
            {skip ? t('nuốt rỗng → (i, j+1)', 'swallow nothing → (i, j+1)') : t('nuốt thêm 1 ký tự → (i+1, j)', 'swallow 1 more → (i+1, j)')}
          </div>
        )}
      </div>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 16}}>
        {rules.map(([t, body, col], k) => (
          <Card key={t} title={t} accent={col} active={cue === null ? c.beat >= 1 && k === 0 : k === cue} style={{flex: 1, padding: '14px 28px', transition: 'none'}}>
            <div style={{fontFamily: MONO, fontSize: 32, fontWeight: 700, lineHeight: 1.3}}>{body}</div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export {ramp};
