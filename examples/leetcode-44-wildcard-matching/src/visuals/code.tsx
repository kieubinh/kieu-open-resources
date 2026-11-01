import React from 'react';
import {C, Card, Glass, MONO, TokState, t} from '../theme';
import {Ctx, EventRow, trace} from '../timeline';
import {Align, Banner, Link, Mark, fade} from './common';
import {nz, replay} from './greedy';

const KW = new Set(['class', 'def', 'while', 'if', 'elif', 'else', 'return', 'and', 'or', 'not', 'True', 'False', 'len', 'self']);

function colorize(line: string): React.ReactNode[] {
  const out: React.ReactNode[] = [];
  const re = /("[^"]*")|(\b\d+\b)|([A-Za-z_][A-Za-z_0-9]*)|(\s+)|(.)/g;
  let m: RegExpExecArray | null;
  let k = 0;
  while ((m = re.exec(line))) {
    const [t, str, num, id, ws] = m;
    let col: string = C.text;
    if (str) col = '#F5BA68';
    else if (num) col = '#FF9E7A';
    else if (id) col = KW.has(id) ? (id === 'self' ? C.muted : '#C792EA') : ['i', 'j', 'star', 'mark'].includes(id) ? C.cyanLight : C.text;
    else if (!ws) col = '#89DDFF';
    out.push(<span key={k++} style={{color: col, fontWeight: id && KW.has(id) && id !== 'self' && id !== 'len' ? 800 : 500}}>{t}</span>);
  }
  return out;
}

const LH = 34;

/** Python source panel; `hi` is the inclusive [from, to] range of 0-based lines to light up (null = none dimmed). */
export const CodePanel: React.FC<{hi: [number, number] | null; width?: number; fontSize?: number}> = ({hi, width = 1000, fontSize = 25}) => {
  const lines = trace.source.lines;
  return (
    <Glass style={{width, padding: '16px 0', overflow: 'hidden', flex: 'none'}}>
      {lines.map((ln, idx) => {
        const on = hi ? idx >= hi[0] && idx <= hi[1] : false;
        return (
          <div key={idx} style={{display: 'flex', height: LH, alignItems: 'center', background: on ? 'rgba(49,196,207,0.24)' : 'transparent', borderLeft: `6px solid ${on ? C.cyanLight : 'transparent'}`,
            opacity: hi === null || on ? 1 : 0.42}}>
            <div style={{width: 62, textAlign: 'right', paddingRight: 18, color: C.muted, fontFamily: MONO, fontSize: fontSize - 4}}>{idx + 1}</div>
            <div style={{fontFamily: MONO, fontSize, whiteSpace: 'pre'}}>{colorize(ln)}</div>
          </div>
        );
      })}
    </Glass>
  );
};

const NOTES = [
  [t('TOÀN BỘ', 'WHOLE'), t('Khoảng 20 dòng, bộ nhớ O(1)', 'About 20 lines, O(1) memory'), C.cyanLight],
  [t('KHỞI TẠO', 'SETUP'), t('i = j = 0 · star = -1 (chưa có *) · mark = 0', 'i = j = 0 · star = -1 (no * yet) · mark = 0'), C.good],
  [t('VÒNG LẶP CHÍNH', 'MAIN LOOP'), t('chạy khi i < len(s)', 'runs while i < len(s)'), C.blue],
  [t('NHÁNH 1', 'BRANCH 1'), t('khớp hoặc ? → i, j cùng tiến', 'match or ? → i, j advance together'), C.good],
  [t('NHÁNH 2', 'BRANCH 2'), t('gặp * → nhớ star, mark; tiến j', 'meet * → save star, mark; advance j'), C.warn],
  [t('NHÁNH 3 + CUỐI', 'BRANCH 3 + LAST'), t('có * → nuốt thêm, quay j · chưa có * → False', 'have * → swallow more, reset j · no * → False'), C.bad],
  [t('SAU VÒNG LẶP', 'AFTER THE LOOP'), t('bỏ * cuối mẫu · return j == len(p)', 'skip trailing * · return j == len(p)'), C.cyanLight],
];

/** Scene 20: the whole solution, with the line range of the narrated part highlighted. */
export const Code1: React.FC<{c: Ctx}> = ({c}) => {
  const b = c.scene.beats[c.beat];
  const hi = b && Array.isArray(b.cue) ? (b.cue as [number, number]) : null;
  const all = c.beat === 0;
  return (
    <div style={{display: 'flex', gap: 40, height: '100%', alignItems: 'flex-start'}}>
      <CodePanel hi={all ? null : hi} width={1060} />
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 8}}>
        {NOTES.map(([t, body, col], k) => (
          <Card key={t} title={t} accent={col} active={c.beat === k} style={{padding: '8px 22px', opacity: c.beat === k ? 1 : 0.4}}>
            <div style={{fontSize: 23, fontWeight: 700, lineHeight: 1.25}}>{body}</div>
          </Card>
        ))}
      </div>
    </div>
  );
};

/** Last body line (0-based) of the branch that each trace event belongs to. */
const BODY_END: Record<string, number> = {match: 8, star: 12, backtrack: 16};

/** Scene 21: line-by-line execution. The highlighted line, and the values shown AFTER it has run, come from the sys.settrace run (trace.main.steps). */
export const Code2: React.FC<{c: Ctx}> = ({c}) => {
  const M = trace.main;
  const steps = M.steps;
  const lastStep = steps.length - 1;
  const beats = c.scene.beats;
  const endStep = (e: EventRow) => {
    for (let k = e.step; k < steps.length; k++) if (steps[k].line === BODY_END[e.kind]) return k;
    return e.step;
  };
  const targets = beats.map((b, k) => {
    if (k === beats.length - 1) return lastStep - 1; // the 'return' line; step lastStep is the pseudo 'returned' marker
    const cue = b.cue as number;
    const ei = M.events.findIndex((e) => e.step === cue);
    if (ei < 0) return cue;
    return endStep(M.events[ei === 4 ? 5 : ei]);
  });
  let idx = 0;
  if (c.beat >= 0) {
    const prev = c.beat === 0 ? 0 : targets[c.beat - 1];
    const span = Math.max(1, beats[c.beat].audioEndFrame - beats[c.beat].startFrame);
    const t = Math.min(1, c.bf / (span * 0.8));
    idx = Math.round(prev + (targets[c.beat] - prev) * t);
  }
  idx = Math.min(idx, lastStep - 1);
  const step = steps[idx];                       // line about to be highlighted (values before it runs)
  const after = steps[Math.min(idx + 1, lastStep)]; // values once that line has run
  const doneEvents = M.events.filter((e) => endStep(e) <= idx).length;
  const rp = replay(M.events, doneEvents, M.s.length);
  const sSt: TokState[] = M.s.split('').map((_, x) => (rp.owner[x] === undefined ? 'idle' : M.p[rp.owner[x] as number] === '*' ? 'eaten' : 'match'));
  const jj = after.j ?? 0;
  const pSt: TokState[] = M.p.split('').map((ch, x) => (x < jj ? (ch === '*' ? 'eaten' : 'match') : 'idle'));
  const links: Link[] = [];
  rp.owner.forEach((o, x) => { if (o !== undefined) links.push({si: x, pj: o, color: M.p[o] === '*' ? C.warn : C.good}); });
  const marks: Mark[] = [];
  if (after.i !== null) marks.push({side: 'top', idx: after.i, label: 'i', color: C.cyanLight});
  if (after.j !== null) marks.push({side: 'bottom', idx: after.j, label: 'j', color: C.warn});
  const vars: ['i' | 'j' | 'star' | 'mark', string][] = [['i', C.cyanLight], ['j', C.warn], ['star', C.good], ['mark', C.blue]];
  return (
    <div style={{display: 'flex', gap: 36, height: '100%', alignItems: 'flex-start'}}>
      <CodePanel hi={[step.line, step.line]} width={960} fontSize={23} />
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 14}}>
        <div style={{width: 700, height: 420, position: 'relative'}}>
          <div style={{transform: 'scale(0.76)', transformOrigin: 'top left', position: 'absolute', left: 0, top: -10}}>
            <Align s={M.s} p={M.p} sStates={sSt} pStates={pSt} links={links} marks={marks} />
          </div>
        </div>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12}}>
          {vars.map(([k, col]) => {
            const changed = step[k] !== after[k];
            return (
              <Glass key={k} style={{padding: '10px 16px', textAlign: 'center', borderColor: changed ? col : C.line, background: changed ? 'rgba(49,196,207,0.2)' : undefined}}>
                <div style={{fontFamily: MONO, fontSize: 24, color: col, fontWeight: 800}}>{k}</div>
                <div style={{fontFamily: MONO, fontSize: 46, fontWeight: 800}}>{nz(after[k])}</div>
              </Glass>
            );
          })}
        </div>
        <div style={{color: C.muted, fontSize: 22}}>{t('Giá trị biến sau khi dòng đang tô sáng chạy xong.', 'Variable values after the highlighted line runs.')}</div>
        {after.ret && <Banner ok text="return True" style={{...fade(c, c.beat), fontSize: 34, padding: '10px 24px'}} />}
      </div>
    </div>
  );
};
