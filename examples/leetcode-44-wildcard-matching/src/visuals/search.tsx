import React from 'react';
import {C, Card, Glass, MONO, Pill, TokState, ramp, vn, t} from '../theme';
import {Ctx, TreeNode, trace} from '../timeline';
import {Align, Banner, Link, Mark, fade} from './common';

/** Tidy layout: x by leaf order, y by depth. Computed from the real call tree in trace.json. */
function layout(nodes: TreeNode[]) {
  const pos: Record<number, {x: number; y: number}> = {};
  let leaf = 0;
  const walk = (id: number, depth: number): number => {
    const n = nodes[id];
    if (!n.children.length) { const x = leaf++; pos[id] = {x, y: depth}; return x; }
    const xs = n.children.map((ch) => walk(ch, depth + 1));
    const x = (xs[0] + xs[xs.length - 1]) / 2;
    pos[id] = {x, y: depth};
    return x;
  };
  walk(0, 0);
  return {pos, leaves: leaf};
}

const HOW: Record<string, {color: string; label: string}> = {
  skip: {color: C.cyanLight, label: t('nhảy qua *', 'skip *')},
  eat: {color: C.warn, label: t('nuốt thêm 1 ký tự', 'swallow 1 more')},
  match: {color: C.good, label: t('khớp 1 ký tự', 'match 1 char')},
};

/** Scene 12: the decision tree of the brute-force recursion (s = "aaa", p = "*a*b"). */
export const Tree: React.FC<{c: Ctx}> = ({c}) => {
  const T = trace.tree;
  const {pos, leaves} = layout(T.nodes);
  const DX = 150, DY = 104, X0 = 70, Y0 = 50, R = 36;
  const shown = c.beat < 1 ? 1 : c.beat === 1 ? Math.min(T.nodes.length, 1 + Math.floor(c.bp * (T.nodes.length - 1) * 1.15)) : T.nodes.length;
  const px = (id: number) => X0 + pos[id].x * DX;
  const py = (id: number) => Y0 + pos[id].y * DY;
  const fail = c.beat >= 2, dup = c.beat >= 3;
  return (
    <div style={{display: 'flex', gap: 30, height: '100%'}}>
      <div style={{position: 'relative', width: X0 * 2 + (leaves - 1) * DX + 40, height: '100%'}}>
        <svg width="100%" height="100%" style={{position: 'absolute', inset: 0}}>
          {T.nodes.slice(1).map((n) => {
            const parent = T.nodes.find((q) => q.children.includes(n.id))!;
            if (n.id >= shown) return null;
            return <line key={n.id} x1={px(parent.id)} y1={py(parent.id)} x2={px(n.id)} y2={py(n.id)} stroke={HOW[n.how].color} strokeWidth={4} opacity={0.85} />;
          })}
        </svg>
        {T.nodes.map((n) => {
          if (n.id >= shown) return null;
          const leafFail = n.children.length === 0 && fail;
          const border = leafFail ? C.bad : dup && n.dup ? C.warn : C.line;
          const bg = dup && n.repeat ? 'rgba(245,186,104,0.34)' : leafFail ? 'rgba(255,123,142,0.16)' : C.glass;
          return (
            <div key={n.id} style={{position: 'absolute', left: px(n.id) - R, top: py(n.id) - R, width: R * 2, height: R * 2, borderRadius: R, background: bg,
              border: `4px solid ${border}`, display: 'grid', placeItems: 'center', fontFamily: MONO, fontWeight: 800, fontSize: 25, boxSizing: 'border-box', color: C.text}}>
              {n.i},{n.j}
            </div>
          );
        })}
      </div>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 18}}>
        <Card title={t('BÀI TOÁN NHỎ', 'SMALL EXAMPLE')} accent={C.cyanLight} style={{padding: '14px 24px'}}>
          <div style={{fontFamily: MONO, fontSize: 30, lineHeight: 1.4}}>s = "{T.s}"<br />p = "{T.p}"  →  <span style={{color: C.bad}}>false</span></div>
        </Card>
        <Glass style={{padding: '14px 24px'}}>
          <div style={{color: C.muted, fontSize: 24, fontWeight: 800, letterSpacing: 1, marginBottom: 6}}>{t('NÚT = (i, j)', 'NODE = (i, j)')}</div>
          {Object.entries(HOW).map(([k, v]) => (
            <div key={k} style={{display: 'flex', alignItems: 'center', gap: 12, fontSize: 26, lineHeight: 1.6}}>
              <div style={{width: 34, height: 6, borderRadius: 3, background: v.color}} />{v.label}
            </div>
          ))}
        </Glass>
        {fail && <Banner ok={false} text={t('Lá thất bại → quay lui', 'Failed leaf → backtrack')} style={{...fade(c, 2), fontSize: 30, padding: '12px 22px'}} />}
        {dup && (
          <Card title={t('CÂU HỎI LẶP LẠI', 'REPEATED QUESTIONS')} accent={C.warn} style={{...fade(c, 3), padding: '12px 24px'}}>
            <div style={{fontSize: 26, lineHeight: 1.35}}>{t('Viền vàng: cặp (i, j) xuất hiện nhiều lần. Nền vàng: lần xuất hiện thứ 2 trở đi.', 'Yellow border: a pair (i, j) that appears more than once. Yellow fill: its 2nd appearance onwards.')}</div>
          </Card>
        )}
        {c.beat >= 4 && (
          <Glass style={{...fade(c, 4), padding: '14px 24px', borderColor: C.warn, display: 'flex', gap: 28, alignItems: 'center'}}>
            <div><div style={{fontFamily: MONO, fontSize: 64, fontWeight: 800, color: C.bad, lineHeight: 1}}>{T.calls}</div><div style={{fontSize: 24, color: C.muted}}>{t('lần gọi hàm', 'function calls')}</div></div>
            <div><div style={{fontFamily: MONO, fontSize: 64, fontWeight: 800, color: C.good, lineHeight: 1}}>{T.distinctStates}</div><div style={{fontSize: 24, color: C.muted}}>{t('câu hỏi khác nhau', 'distinct questions')}</div></div>
          </Glass>
        )}
      </div>
    </div>
  );
};

/** Scene 13: measured number of calls, log-scale bars (data: trace.blowup, measured by running the real recursion). */
export const Blowup: React.FC<{c: Ctx}> = ({c}) => {
  const B = trace.blowup;
  const maxLog = Math.log10(B.rows[B.rows.length - 1].calls) + 0.15;
  const BW = 1000;
  const rowsShown = c.beat < 1 ? 0 : c.beat === 1 ? c.bp * (B.rows.length + 0.4) : B.rows.length;
  return (
    <div style={{display: 'flex', gap: 40, height: '100%'}}>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 26}}>
        {B.rows.map((r, k) => {
          const t = Math.max(0, Math.min(1, rowsShown - k));
          const w = (Math.log10(r.calls) / maxLog) * BW * t;
          const hot = k === B.rows.length - 1;
          return (
            <div key={r.k} style={{display: 'flex', alignItems: 'center', gap: 22, opacity: t > 0 ? 1 : 0.15}}>
              <div style={{width: 170, fontFamily: MONO, fontSize: 30, fontWeight: 800, color: C.muted}}>k = {r.k}</div>
              <div style={{height: 56, width: Math.max(8, w), borderRadius: 14, background: hot ? C.bad : C.cyan, opacity: 0.9}} />
              <div style={{fontFamily: MONO, fontSize: 36, fontWeight: 800, color: hot ? C.bad : C.text, opacity: t > 0.6 ? 1 : 0}}>{vn(Math.round(r.calls * Math.min(1, t * 1.2)))}</div>
            </div>
          );
        })}
        <div style={{color: C.muted, fontSize: 24}}>{t('Trục độ dài theo thang logarit. Số lần gọi đã đo bằng cách chạy thật đệ quy.', 'Bar length on a log scale. Call counts measured by actually running the recursion.')}</div>
      </div>
      <div style={{width: 560, display: 'flex', flexDirection: 'column', gap: 22}}>
        <Card title={t('THÍ NGHIỆM', 'EXPERIMENT')} accent={C.cyanLight}>
          <div style={{fontFamily: MONO, fontSize: 28, lineHeight: 1.5}}>s = "a" × {B.n}<br />p = "*a" × k + "b"</div>
        </Card>
        {c.beat >= 2 && (
          <Card title={t('VỚI ĐỘ DÀI 2000', 'AT LENGTH 2000')} accent={C.bad} style={fade(c, 2)}>
            <div style={{fontSize: 36, fontWeight: 800, lineHeight: 1.3}}>{t(<>Thử hết mọi nhánh là <span style={{color: C.bad}}>không thể</span>.</>, <>Trying every branch is <span style={{color: C.bad}}>impossible</span>.</>)}</div>
          </Card>
        )}
      </div>
    </div>
  );
};

/** Scene 14: a "never come back" greedy idea and its counter-example (events from trace.noBacktrack). */
export const GreedyFail: React.FC<{c: Ctx}> = ({c}) => {
  const N = trace.noBacktrack;
  const ev = N.events; // star-empty, match, star-empty, fail
  const upto = c.beat < 1 ? 0 : c.beat === 1 ? Math.min(3, Math.floor(c.bp * 3.4) + 1) : c.beat === 2 ? 4 : 4;
  const pos = upto === 0 ? {i: 0, j: 0} : ev[Math.min(upto, 4) - 1].after;
  const truth = c.beat >= 3;
  let sSt: TokState[] = ['idle', 'idle', 'idle', 'idle', 'idle'];
  let pSt: TokState[] = ['idle', 'idle', 'idle', 'idle'];
  const links: Link[] = [];
  if (!truth) {
    if (upto >= 1) pSt[0] = 'eaten';
    if (upto >= 2) { sSt[0] = 'match'; pSt[1] = 'match'; links.push({si: 0, pj: 1, color: C.good}); }
    if (upto >= 3) pSt[2] = 'eaten';
    if (upto >= 4 && c.beat >= 2) { sSt[1] = 'bad'; pSt[3] = 'bad'; links.push({si: 1, pj: 3, color: C.bad, dash: true}); }
  } else {
    sSt = ['match', 'eaten', 'eaten', 'eaten', 'match'];
    pSt = ['eaten', 'match', 'eaten', 'match'];
    links.push({si: 0, pj: 1, color: C.good}, {si: 1, pj: 2, color: C.warn}, {si: 2, pj: 2, color: C.warn}, {si: 3, pj: 2, color: C.warn}, {si: 4, pj: 3, color: C.good});
  }
  const marks: Mark[] = truth ? [] : [{side: 'top', idx: pos.i, label: 'i', color: C.cyanLight}, {side: 'bottom', idx: pos.j, label: 'j', color: C.warn}];
  return (
    <div style={{display: 'flex', gap: 40, height: '100%'}}>
      <div style={{flex: 1}}>
        <Align s={N.s} p={N.p} sStates={sSt} pStates={pSt} links={links} marks={marks} />
      </div>
      <div style={{width: 560, display: 'flex', flexDirection: 'column', gap: 12}}>
        <Card title={t('Ý TƯỞNG THỬ', 'IDEA TO TRY')} accent={C.warn} style={fade(c, 0)}>
          <div style={{fontSize: 27, fontWeight: 700, lineHeight: 1.25}}>{t(<>Gặp <span style={{fontFamily: MONO, color: C.warn}}>*</span> thì nuốt rỗng, <b>không bao giờ quay lại</b>.</>, <>On a <span style={{fontFamily: MONO, color: C.warn}}>*</span>, swallow nothing and <b>never look back</b>.</>)}</div>
        </Card>
        {c.beat >= 2 && <Banner ok={false} text={t('Kết luận: false', 'Conclusion: false')} style={{...fade(c, 2), fontSize: 30}} />}
        {truth && (
          <Card title={t('ĐÁP ÁN ĐÚNG: TRUE', 'CORRECT ANSWER: TRUE')} accent={C.good} style={fade(c, 3)}>
            <div style={{fontSize: 25, lineHeight: 1.3}}>
              {t(<><span style={{fontFamily: MONO, color: C.warn}}>*</span> đầu nuốt rỗng, <span style={{fontFamily: MONO, color: C.good}}>a</span> khớp a,<br />
              <span style={{fontFamily: MONO, color: C.warn}}>*</span> thứ hai nuốt <span style={{fontFamily: MONO}}>dce</span>, rồi <span style={{fontFamily: MONO, color: C.good}}>b</span> khớp b.</>,
              <>The first <span style={{fontFamily: MONO, color: C.warn}}>*</span> swallows nothing, <span style={{fontFamily: MONO, color: C.good}}>a</span> matches a,<br />
              the second <span style={{fontFamily: MONO, color: C.warn}}>*</span> swallows <span style={{fontFamily: MONO}}>dce</span>, then <span style={{fontFamily: MONO, color: C.good}}>b</span> matches b.</>)}
            </div>
          </Card>
        )}
        {c.beat >= 4 && (
          <Card title={t('BÀI HỌC', 'LESSON')} accent={C.cyanLight} style={fade(c, 4)}>
            <div style={{fontSize: 26, fontWeight: 700, lineHeight: 1.25}}>{t(<>Giả thuyết hay vẫn có thể sai. <span style={{color: C.cyanLight}}>Phản ví dụ</span> cho ta biết.</>, <>A good hypothesis can still be wrong. A <span style={{color: C.cyanLight}}>counterexample</span> tells us.</>)}</div>
          </Card>
        )}
        {c.beat < 4 && <Pill color={C.muted} size={22} style={{alignSelf: 'flex-start'}}>{t('chạy thật: kết quả ', 'real run: result ')}{String(N.result)}{t(' vs đáp án ', ' vs answer ')}{String(trace.main.result)}</Pill>}
      </div>
    </div>
  );
};

export {ramp};
