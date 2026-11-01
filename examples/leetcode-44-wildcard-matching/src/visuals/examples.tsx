import React from 'react';
import {C, Card, Glass, MONO, Pill, TokState, t} from '../theme';
import {Ctx, trace} from '../timeline';
import {Align, Banner, Link, Mark, fade} from './common';

const Side: React.FC<{c: Ctx; expected: boolean; resultBeat: number; lessonBeat: number; lesson: React.ReactNode; extra?: React.ReactNode}> = ({c, expected, resultBeat, lessonBeat, lesson, extra}) => (
  <div style={{width: 520, display: 'flex', flexDirection: 'column', gap: 12, maxHeight: '100%'}}>
    <Card title={t('OUTPUT CỦA ĐỀ', 'EXPECTED OUTPUT')} accent={expected ? C.good : C.bad} style={{padding: '12px 24px'}}>
      <div style={{fontFamily: MONO, fontSize: 42, fontWeight: 800, color: expected ? C.good : C.bad}}>{String(expected)}</div>
    </Card>
    {c.beat >= resultBeat && <Banner ok={expected} text={expected ? t('Kết quả: true', 'Result: true') : t('Kết quả: false', 'Result: false')} style={fade(c, resultBeat)} />}
    {extra}
    {c.beat >= lessonBeat && (
      <Card title={t('BÀI HỌC', 'LESSON')} accent={C.warn} style={{...fade(c, lessonBeat), flex: 1}}>
        <div style={{fontSize: 27, fontWeight: 700, lineHeight: 1.25}}>{lesson}</div>
      </Card>
    )}
  </div>
);

const Frame: React.FC<{left: React.ReactNode; right: React.ReactNode}> = ({left, right}) => (
  <div style={{display: 'flex', gap: 50, height: '100%'}}>
    <div style={{flex: 1}}>{left}</div>
    {right}
  </div>
);

/** Example 1: s = "aa", p = "a" → false. Events come from the real run (trace.official[0]). */
export const Example1: React.FC<{c: Ctx}> = ({c}) => {
  const ev = trace.official[0].events; // match, fail
  const moved = c.beat >= 2 || (c.beat === 1 && c.since(1) > 22);
  const i = (moved ? ev[0].after.i : ev[0].before.i) as number;
  const j = (moved ? ev[0].after.j : ev[0].before.j) as number;
  const sSt: TokState[] = [c.beat >= 1 ? 'match' : 'idle', c.beat >= 2 ? 'bad' : 'idle'];
  const pSt: TokState[] = [c.beat >= 1 ? 'match' : 'idle'];
  const links: Link[] = c.beat >= 1 ? [{si: 0, pj: 0, color: C.good}] : [];
  const marks: Mark[] = [{side: 'top', idx: i, label: 'i', color: C.cyanLight}, {side: 'bottom', idx: j, label: 'j', color: C.warn}];
  return (
    <Frame
      left={<Align s="aa" p="a" sStates={sSt} pStates={pSt} links={links} marks={marks} w={160} endBox={{label: t('hết mẫu', 'pattern ends'), show: c.beat >= 2}} />}
      right={<Side c={c} expected={false} resultBeat={2} lessonBeat={3} lesson={t(<>Luôn kiểm tra <span style={{color: C.warn}}>điều kiện kết thúc</span> của cả hai phía.</>, <>Always check the <span style={{color: C.warn}}>ending condition</span> on both sides.</>)}
        extra={c.beat >= 2 ? <Card title={t('VÌ SAO FALSE?', 'WHY FALSE?')} accent={C.bad} style={fade(c, 2)}><div style={{fontSize: 30, lineHeight: 1.35}}>{t('p đã hết, nhưng s còn dư một ký tự ', 'p has ended, but s still has one extra ')}<span style={{fontFamily: MONO, color: C.bad}}>a</span></div></Card> : null} />}
    />
  );
};

/** Example 2: s = "aa", p = "*" → true. The star eats one more character each backtrack event. */
export const Example2: React.FC<{c: Ctx}> = ({c}) => {
  const eaten = c.beat < 1 ? 0 : c.beat === 1 ? Math.min(2, Math.floor(c.bp * 2.6)) : 2;
  const sSt: TokState[] = [0, 1].map((k) => (k < eaten ? 'eaten' : 'idle'));
  const pSt: TokState[] = [c.beat >= 1 ? 'eaten' : 'idle'];
  const links: Link[] = Array.from({length: eaten}, (_, k) => ({si: k, pj: 0, color: C.warn}));
  const marks: Mark[] = [{side: 'top', idx: eaten, label: 'i', color: C.cyanLight}, {side: 'bottom', idx: c.beat >= 1 ? 1 : 0, label: 'j', color: C.warn}];
  const chips = [t('rỗng', 'empty'), 'a', 'aa', '…'];
  return (
    <Frame
      left={<Align s="aa" p="*" sStates={sSt} pStates={pSt} links={links} marks={marks} w={160} />}
      right={<Side c={c} expected resultBeat={2} lessonBeat={3} lesson={t(<>Một ký hiệu có thể tạo ra <span style={{color: C.warn}}>nhiều lựa chọn</span>.</>, <>One symbol can create <span style={{color: C.warn}}>many choices</span>.</>)}
        extra={c.beat >= 3 ? (
          <Glass style={{...fade(c, 3), padding: '16px 20px'}}>
            <div style={{color: C.muted, fontSize: 24, marginBottom: 8}}>{t('* có thể nuốt:', '* can swallow:')}</div>
            <div style={{display: 'flex', gap: 10, flexWrap: 'wrap'}}>{chips.map((t) => <Pill key={t} color={C.warn} size={26}>{t}</Pill>)}</div>
          </Glass>) : null} />}
    />
  );
};

/** Example 3: s = "cb", p = "?a" → false. */
export const Example3: React.FC<{c: Ctx}> = ({c}) => {
  const moved = c.beat >= 2 || (c.beat === 1 && c.since(1) > 22);
  const sSt: TokState[] = [c.beat >= 1 ? 'match' : 'idle', c.beat >= 2 ? 'bad' : 'idle'];
  const pSt: TokState[] = [c.beat >= 1 ? 'match' : 'idle', c.beat >= 2 ? 'bad' : 'idle'];
  const links: Link[] = [];
  if (c.beat >= 1) links.push({si: 0, pj: 0, color: C.good});
  if (c.beat >= 2) links.push({si: 1, pj: 1, color: C.bad, dash: true});
  const marks: Mark[] = [{side: 'top', idx: moved ? 1 : 0, label: 'i', color: C.cyanLight}, {side: 'bottom', idx: moved ? 1 : 0, label: 'j', color: C.warn}];
  return (
    <Frame
      left={<Align s="cb" p="?a" sStates={sSt} pStates={pSt} links={links} marks={marks} w={160} />}
      right={<Side c={c} expected={false} resultBeat={2} lessonBeat={3} lesson={t(<>Không có <span style={{color: C.warn}}>*</span> thì mọi thứ thẳng hàng 1–1; lệch một vị trí là hỏng.</>, <>Without <span style={{color: C.warn}}>*</span>, everything lines up 1–1; one position off breaks it.</>)}
        extra={c.beat >= 2 ? <Card title={t('SO SÁNH', 'COMPARE')} accent={C.bad} style={fade(c, 2)}><div style={{fontFamily: MONO, fontSize: 40, fontWeight: 800}}>a <span style={{color: C.bad}}>≠</span> b</div></Card> : null} />}
    />
  );
};

/** Scene 08: three habits + "the hard part is the star". */
export const Recap: React.FC<{c: Ctx}> = ({c}) => {
  const habits = [
    ['1', t('Kiểm tra điều kiện kết thúc', 'Check the ending condition'), t('Ví dụ 1 · aa với a', 'Example 1 · aa with a'), C.bad],
    ['2', t('Tìm nơi phát sinh lựa chọn', 'Find where choices appear'), t('Ví dụ 2 · aa với *', 'Example 2 · aa with *'), C.warn],
    ['3', t('Biết khi nào mọi thứ ép thẳng hàng', 'Know when everything is forced into line'), t('Ví dụ 3 · cb với ?a', 'Example 3 · cb with ?a'), C.cyanLight],
  ];
  const shown = c.beat === 0 ? Math.min(3, Math.floor(c.bp * 3.6) + 1) : 3;
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 28, height: '100%'}}>
      <div style={{display: 'flex', gap: 28, flex: 1}}>
        {habits.map(([n, t, e, col], k) => (
          <Glass key={n} style={{flex: 1, padding: '30px 34px', borderColor: k < shown ? col : C.line, opacity: k < shown ? (c.beat === 1 && k !== 1 ? 0.55 : 1) : 0.15,
            transform: `scale(${c.beat === 1 && k === 1 ? 1.04 : 1})`}}>
            <div style={{fontFamily: MONO, fontSize: 90, fontWeight: 800, color: col}}>{n}</div>
            <div style={{fontSize: 44, fontWeight: 800, lineHeight: 1.2, margin: '10px 0 16px'}}>{t}</div>
            <div style={{fontSize: 28, color: C.muted}}>{e}</div>
          </Glass>
        ))}
      </div>
      <div style={{...fade(c, 1), height: 150, display: 'flex', alignItems: 'center', gap: 30, padding: '0 40px', borderRadius: 26, border: `3px solid ${C.warn}`, background: 'rgba(245,186,104,0.12)'}}>
        <div style={{fontFamily: MONO, fontSize: 100, fontWeight: 800, color: C.warn, lineHeight: 1}}>*</div>
        <div style={{fontSize: 42, fontWeight: 800}}>{t('Chỗ khó của bài nằm ở dấu sao.', 'The hard part of the problem is the star.')}</div>
      </div>
    </div>
  );
};
