import React from 'react';
import {C, Card, Glass, MONO, TokState, vn, t} from '../theme';
import {Ctx, trace} from '../timeline';
import {Align, Link, Mark, fade} from './common';

const CW = 142, CH = 80, HW = 150;

/** Scene 15: the 2-D DP table for s = "adceb", p = "*a*b" (values from trace.main.dp, cross-checked in tests). */
export const DP: React.FC<{c: Ctx}> = ({c}) => {
  const M = trace.main;
  const dp = M.dp;
  const rows = M.s.length + 1, cols = M.p.length + 1;
  const key = (i: number, j: number) => `${i},${j}`;
  const ex3 = new Set([key(1, 2), key(0, 1)]);
  const ex4 = new Set([key(2, 1), key(1, 1), key(2, 0)]);
  const all = rows * cols;
  const fillCount = c.beat < 5 ? 0 : c.beat === 5 ? Math.floor(c.bp * (all - cols) * 1.08) : all;
  const revealed = (i: number, j: number) => {
    if (c.beat >= 6) return true;
    if (c.beat >= 2 && i === 0) return true;
    if (c.beat >= 3 && ex3.has(key(i, j))) return true;
    if (c.beat >= 4 && ex4.has(key(i, j))) return true;
    if (c.beat === 5 && i >= 1 && (i - 1) * cols + j < fillCount) return true;
    return false;
  };
  const target = c.beat === 1 ? key(2, 2) : c.beat === 3 ? key(1, 2) : c.beat === 4 ? key(2, 1) : c.beat >= 6 ? key(rows - 1, cols - 1) : '';
  const sources = c.beat === 3 ? new Set([key(0, 1)]) : c.beat === 4 ? new Set([key(1, 1), key(2, 0)]) : new Set<string>();
  const headerP = [t('rỗng', 'empty'), ...M.p.split('')];
  const headerS = [t('rỗng', 'empty'), ...M.s.split('')];
  const rules: [string, React.ReactNode, string, number][] = [
    [t('Ô dp[i][j]', 'CELL dp[i][j]'), t(<>s[:i] khớp p[:j]?</>, <>does s[:i] match p[:j]?</>), C.cyanLight, 1],
    [t('CƠ SỞ', 'BASE'), t(<>dp[0][0] = true · hàng 0: chỉ đúng khi p[:j] toàn *</>, <>dp[0][0] = true · row 0: true only if p[:j] is all *</>), C.good, 2],
    [t('CHỮ CÁI / ?', 'LETTER / ?'), t(<>dp[i-1][j-1] và hai ký tự khớp</>, <>dp[i-1][j-1] and the characters match</>), C.cyanLight, 3],
    [t('DẤU *', 'STAR *'), <>dp[i-1][j] <b style={{color: C.warn}}>{t('HOẶC', 'OR')}</b> dp[i][j-1]</>, C.warn, 4],
  ];
  const activeRule = c.beat <= 1 ? 0 : Math.min(3, c.beat - 1);
  return (
    <div style={{display: 'flex', gap: 50, height: '100%'}}>
      <div style={{width: HW + cols * CW + 10, ...fade(c, 0)}}>
        <div style={{display: 'flex', marginLeft: HW}}>
          {headerP.map((h, j) => <div key={j} style={{width: CW, textAlign: 'center', fontFamily: MONO, fontSize: j === 0 ? 24 : 38, fontWeight: 800, color: h === '*' ? C.warn : C.cyanLight, height: 56, lineHeight: '56px'}}>{h}</div>)}
        </div>
        {Array.from({length: rows}).map((_, i) => (
          <div key={i} style={{display: 'flex', height: CH + 4}}>
            <div style={{width: HW, textAlign: 'right', paddingRight: 18, fontFamily: MONO, fontSize: i === 0 ? 24 : 38, fontWeight: 800, color: C.cyanLight, lineHeight: `${CH}px`}}>{headerS[i]}</div>
            {Array.from({length: cols}).map((__, j) => {
              const k = key(i, j);
              const isT = k === target, isS = sources.has(k);
              const show = revealed(i, j);
              const v = dp[i][j];
              const last = i === rows - 1 && j === cols - 1;
              return (
                <div key={j} style={{width: CW - 6, height: CH - 4, margin: '2px 3px', borderRadius: 14, boxSizing: 'border-box', display: 'grid', placeItems: 'center',
                  border: `3px solid ${isT ? C.cyanLight : isS ? C.warn : last && c.beat >= 6 ? C.good : C.line}`,
                  background: show ? (v ? 'rgba(88,225,164,0.20)' : 'rgba(255,123,142,0.10)') : 'rgba(20,44,67,0.55)',
                  boxShadow: isT ? `0 0 26px ${C.cyan}` : undefined, fontFamily: MONO, fontSize: 40, fontWeight: 800, color: v ? C.good : C.bad}}>
                  {show ? (v ? 'T' : 'F') : ''}
                </div>
              );
            })}
          </div>
        ))}
        <div style={{marginLeft: HW, color: C.muted, fontSize: 24, marginTop: 6}}>{t('T = true · F = false · hàng = i ký tự đầu của s · cột = j ký tự đầu của p', 'T = true · F = false · row = first i characters of s · column = first j characters of p')}</div>
      </div>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 14}}>
        {c.beat <= 5 && rules.map(([t, body, col, minBeat], k) => (
          <Card key={t} title={t} accent={col} active={c.beat >= minBeat && k === activeRule} style={{padding: '12px 26px', opacity: c.beat >= minBeat ? (k === activeRule ? 1 : 0.55) : 0.12}}>
            <div style={{fontFamily: MONO, fontSize: 30, fontWeight: 700, lineHeight: 1.3}}>{body}</div>
          </Card>
        ))}
        {c.beat >= 6 && (
          <Card title={t('Ô CUỐI', 'LAST CELL')} accent={C.good} style={fade(c, 6)}>
            <div style={{fontFamily: MONO, fontSize: 36, fontWeight: 800}}>dp[{rows - 1}][{cols - 1}] = <span style={{color: C.good}}>true</span></div>
          </Card>
        )}
        {c.beat >= 7 && (
          <Glass style={{...fade(c, 7), padding: '14px 26px', borderColor: C.warn}}>
            <div style={{fontFamily: MONO, fontSize: 28, lineHeight: 1.45}}>
              2001 × 2001 ≈ <b style={{color: C.warn}}>{vn(2001 * 2001)}</b>{t(' ô', ' cells')}<br />
              {t('thời gian ', 'time ')}<b>O(m × n)</b>{t(' · bộ nhớ ', ' · memory ')}<b style={{color: C.bad}}>O(m × n)</b>
            </div>
          </Glass>
        )}
      </div>
    </div>
  );
};

/** Scene 16: why only the nearest star matters (exchange argument, shown on the adceb / *a*b example). */
export const Insight: React.FC<{c: Ctx}> = ({c}) => {
  const sSt: TokState[] = ['idle', 'idle', 'idle', 'idle', 'idle'];
  const pSt: TokState[] = ['idle', 'idle', 'idle', 'idle'];
  const links: Link[] = [];
  const marks: Mark[] = [];
  if (c.beat >= 1) { pSt[0] = 'dim'; pSt[2] = 'eaten'; marks.push({side: 'bottom', idx: 2, label: t('gần nhất', 'latest'), color: C.warn}); }
  if (c.beat >= 2) { pSt[1] = 'match'; sSt[0] = 'match'; links.push({si: 0, pj: 1, color: C.good}); }
  if (c.beat >= 3) { pSt[3] = 'bad'; sSt[1] = 'bad'; pSt[2] = 'cursor'; links.push({si: 1, pj: 3, color: C.bad, dash: true}); }
  const cards: [string, string, string][] = [
    [t('QUAN SÁT', 'OBSERVE'), t('Mỗi ô của bảng chỉ cần hàng trên và ô bên cạnh', 'Each cell only needs the row above and the cell beside it'), C.cyanLight],
    [t('* GẦN NHẤT', 'LATEST *'), t('Dấu * gần nhất là lựa chọn linh hoạt nhất', 'The most recent * is the most flexible choice'), C.warn],
    [t('KHỚP SỚM', 'MATCH EARLY'), t('Đoạn giữa hai dấu *: khớp ở vị trí sớm nhất để chừa nhiều ký tự nhất', 'Between two *: match as early as possible to leave the most characters'), C.good],
    [t('KHI LỆCH', 'ON MISMATCH'), t('Chỉ quay về dấu * gần nhất. Các dấu * cũ hơn không cần thử lại', 'Go back only to the most recent *. Older * never need retrying'), C.bad],
  ];
  return (
    <div style={{display: 'flex', gap: 40, height: '100%'}}>
      <div style={{width: 760}}>
        <Align s="adceb" p="*a*b" sStates={sSt} pStates={pSt} links={links} marks={marks} />
      </div>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 14}}>
        {cards.map(([t, body, col], k) => (
          <Card key={t} title={t} accent={col} active={c.beat === k} style={{flex: 1, padding: '12px 26px', opacity: c.beat >= k ? (c.beat === k ? 1 : 0.55) : 0.12}}>
            <div style={{fontSize: 31, fontWeight: 700, lineHeight: 1.3}}>{body}</div>
          </Card>
        ))}
      </div>
    </div>
  );
};
