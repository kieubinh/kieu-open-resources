import React from 'react';
import {C, Card, Glass, MONO, TokState, t} from '../theme';
import {Ctx, EventRow, Vars, trace} from '../timeline';
import {Align, Banner, Link, Mark, fade} from './common';

const cueOf = (c: Ctx): number | null => {
  const b = c.scene.beats[c.beat];
  return b && typeof b.cue === 'number' ? b.cue : null;
};

/** Replay the first `n` real events of a run: final variables + which pattern index consumed each character. */
export function replay(events: EventRow[], n: number, sLen: number) {
  const owner: (number | undefined)[] = Array(sLen).fill(undefined);
  let vars: Vars = {i: 0, j: 0, star: -1, mark: 0};
  for (let k = 0; k < Math.min(n, events.length); k++) {
    const e = events[k];
    if (e.kind === 'match') owner[e.before.i as number] = e.before.j as number;
    if (e.kind === 'backtrack') {
      owner[e.before.mark as number] = e.before.star as number;
      for (let x = e.after.i as number; x < sLen; x++) owner[x] = undefined;
    }
    vars = e.after;
  }
  return {owner, vars};
}

export const nz = (v: number | null | undefined) => (v === null || v === undefined ? '–' : String(v));

const VAR_INFO: [keyof Vars, string, string, string][] = [
  ['i', 'i', t('vị trí trên chuỗi s', 'position in string s'), C.cyanLight],
  ['j', 'j', t('vị trí trên mẫu p', 'position in pattern p'), C.warn],
  ['star', 'star', t('dấu * gần nhất (-1 = chưa có)', 'most recent * (-1 = none yet)'), C.good],
  ['mark', 'mark', t('chỗ trên s mà * đã nuốt tới', 'how far * has swallowed in s'), C.blue],
];

/** Scene 17: the two-pointer algorithm, one rule per narration beat (cue = rule index). */
export const Greedy: React.FC<{c: Ctx}> = ({c}) => {
  const cue = cueOf(c);
  const lit = c.beat === 0 ? Math.min(3, Math.floor(c.bp * 4.4)) : 3;
  const rules: [string, string, React.ReactNode, string][] = [
    ['1', t('KHỚP HOẶC ?', 'MATCH OR ?'), <>i += 1 · j += 1</>, C.good],
    ['2', t('GẶP *', 'MEET *'), <>star = j · mark = i · j += 1</>, C.warn],
    ['3', t('LỆCH, ĐÃ CÓ *', 'MISMATCH, HAVE *'), <>mark += 1 · i = mark · j = star + 1</>, C.cyanLight],
    ['4', t('LỆCH, CHƯA CÓ *', 'MISMATCH, NO *'), <>return False</>, C.bad],
    ['5', t('HẾT CHUỖI', 'STRING ENDS'), t(<>bỏ các * cuối p · true khi j == len(p)</>, <>skip trailing * in p · true when j == len(p)</>), C.blue],
  ];
  return (
    <div style={{display: 'flex', gap: 40, height: '100%'}}>
      <div style={{width: 700, display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr', gap: 20}}>
        {VAR_INFO.map(([k, name, desc, col], idx) => (
          <Glass key={k} style={{padding: '22px 26px', borderColor: idx <= lit && c.beat >= 0 ? col : C.line, opacity: c.beat < 0 ? 0.2 : idx <= lit ? 1 : 0.25, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
            <div style={{fontFamily: MONO, fontSize: 64, fontWeight: 800, color: col}}>{name}</div>
            <div style={{fontSize: 27, color: C.muted, lineHeight: 1.3, marginTop: 4}}>{desc}</div>
          </Glass>
        ))}
      </div>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 14}}>
        {rules.map(([n, t, body, col], k) => {
          const on = cue === k + 1;
          return (
            <Card key={n} title={`${n} · ${t}`} accent={col} active={on} style={{flex: 1, padding: '10px 28px', opacity: c.beat < 1 ? 0.25 : on ? 1 : 0.45}}>
              <div style={{fontFamily: MONO, fontSize: 31, fontWeight: 700}}>{body}</div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

const EVENT_TEXT: Record<string, [string, string]> = {
  star: [t('GẶP *', 'MEET *'), 'star = j · mark = i · j += 1'],
  match: [t('KHỚP', 'MATCH'), 'i += 1 · j += 1'],
  backtrack: [t('LỆCH, ĐÃ CÓ *', 'MISMATCH, HAVE *'), 'mark += 1 · i = mark · j = star + 1'],
};

/** Scene 18: step-by-step run on adceb / *a*b; every state comes from the real event list. */
export const Trace: React.FC<{c: Ctx}> = ({c}) => {
  const M = trace.main;
  const cue = cueOf(c);
  let e = cue === null ? -1 : cue;
  if (cue === 4) e = c.bp < 0.5 ? 4 : 5;
  const applied = e >= 0 && (cue === 4 ? c.bf > 12 : c.bf > 16);
  const prior = replay(M.events, e < 0 ? 0 : applied ? e + 1 : e, M.s.length);
  const ev = e >= 0 ? M.events[e] : null;
  const vars = prior.vars;
  const sSt: TokState[] = M.s.split('').map((_, x) => {
    const o = prior.owner[x];
    if (o === undefined) return 'idle';
    return M.p[o] === '*' ? 'eaten' : 'match';
  });
  const pSt: TokState[] = M.p.split('').map((ch, x) => (x < (vars.j as number) ? (ch === '*' ? 'eaten' : 'match') : 'idle'));
  const links: Link[] = [];
  prior.owner.forEach((o, x) => { if (o !== undefined) links.push({si: x, pj: o, color: M.p[o] === '*' ? C.warn : C.good}); });
  let bad = false;
  if (ev && !applied && ev.kind === 'backtrack') {
    bad = true;
    sSt[vars.i as number] = 'bad';
    pSt[vars.j as number] = 'bad';
  }
  if (!bad && (vars.i as number) < M.s.length) sSt[vars.i as number] = sSt[vars.i as number] === 'idle' ? 'cursor' : sSt[vars.i as number];
  const marks: Mark[] = [
    {side: 'top', idx: vars.i as number, label: 'i', color: C.cyanLight},
    {side: 'bottom', idx: vars.j as number, label: 'j', color: C.warn},
  ];
  if ((vars.star as number) >= 0) marks.push({side: 'bottom', idx: vars.star as number, label: 'star', color: C.good, level: 1});
  if ((vars.star as number) >= 0) marks.push({side: 'top', idx: vars.mark as number, label: 'mark', color: C.blue, level: 1});
  const done = cue === 6 && applied;
  const [title, rule] = ev ? EVENT_TEXT[ev.kind] : ['', ''];
  return (
    <div style={{display: 'flex', gap: 30, height: '100%'}}>
      <div style={{width: 800}}>
        <Align s={M.s} p={M.p} sStates={sSt} pStates={pSt} links={links} marks={marks} />
      </div>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 16}}>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14}}>
          {VAR_INFO.map(([k, name, , col]) => {
            const changed = ev && applied && ev.before[k] !== ev.after[k];
            return (
              <Glass key={k} style={{padding: '12px 22px', borderColor: changed ? col : C.line, background: changed ? 'rgba(49,196,207,0.2)' : undefined}}>
                <span style={{fontFamily: MONO, fontSize: 30, color: col, fontWeight: 800}}>{name} = </span>
                <span style={{fontFamily: MONO, fontSize: 44, fontWeight: 800}}>{nz(vars[k])}</span>
              </Glass>
            );
          })}
        </div>
        {ev && (
          <Card title={title} accent={ev.kind === 'backtrack' ? C.cyanLight : ev.kind === 'match' ? C.good : C.warn} style={{padding: '12px 26px'}}>
            <div style={{fontFamily: MONO, fontSize: 28, fontWeight: 700, lineHeight: 1.4}}>{rule}</div>
            {bad && <div style={{fontSize: 26, color: C.bad, marginTop: 6, fontWeight: 700}}>{t('p[j] ≠ s[i] → lệch', 'p[j] ≠ s[i] → mismatch')}</div>}
          </Card>
        )}
        {done && <Banner ok text={t('Hết s, j = len(p) → true', 's ends, j = len(p) → true')} style={{...fade(c, c.beat), fontSize: 32}} />}
      </div>
    </div>
  );
};

/** Scene 19: the logic in words, revealed with the narration. */
export const Pseudocode: React.FC<{c: Ctx}> = ({c}) => {
  const lines: [number, string, number][] = [
    [0, t('Lặp khi chuỗi s còn ký tự:', 'While s has characters:'), 1],
    [1, t('khớp / ? → tiến i, j', 'match / ? → advance i, j'), 1],
    [1, t('* → nhớ vị trí, tiến j', '* → remember position, advance j'), 1],
    [1, t('lệch + có * → nuốt thêm một ký tự, quay j', 'mismatch + have * → swallow one more, reset j'), 1],
    [1, t('lệch + chưa có * → trả về false', 'mismatch + no * → return false'), 1],
    [0, t('Bỏ các * dư ở cuối mẫu', 'Skip trailing * in the pattern'), 2],
    [0, t('Trả về: j đã tới cuối mẫu', 'Return: j reached the end of the pattern'), 2],
  ];
  const group1 = c.beat < 1 ? 0 : c.beat === 1 ? 5 * Math.min(1, c.bp * 1.15) : 5;
  const group2 = c.beat < 2 ? 0 : 2 * Math.min(1, c.bp * 1.15);
  return (
    <div style={{display: 'flex', gap: 40, height: '100%'}}>
      <Glass style={{flex: 1, padding: '30px 44px', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 16}}>
        {lines.map(([ind, text, g], k) => {
          const t = g === 1 ? Math.max(0, Math.min(1, group1 - k)) : Math.max(0, Math.min(1, group2 - (k - 5)));
          return (
            <div key={k} style={{paddingLeft: ind * 56, fontSize: 40, fontWeight: 700, opacity: 0.12 + 0.88 * t, transform: `translateX(${(1 - t) * -24}px)`}}>
              <span style={{color: C.cyanLight}}>{ind === 0 ? '' : '›  '}</span>{text}
            </div>
          );
        })}
      </Glass>
    </div>
  );
};
