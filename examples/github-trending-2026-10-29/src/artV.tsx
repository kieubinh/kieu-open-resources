import React from 'react';
import {C, accent, sans, mono, clamp, ease, seg, stagger, fmt, box} from './theme';
import {Icon, IconG} from './art';

/**
 * Portrait (9:16) illustrations for the one-minute shorts. Area: 920 x 740 px inside a 1080 x 1920 frame, kept clear of
 * the YouTube Shorts UI (right 120 px, bottom 345 px). Text is sized for a phone: body >= 28 px, labels >= 24 px.
 */
export const VW = 920, VH = 740;
export type Lang = 'vi' | 'en';
const langOf = (data: any): Lang => (data && data.lang === 'en' ? 'en' : 'vi');
/** Static strings of the illustrations: Vietnamese by default, English for KIEU_LANG=en. */
const pick = (lang: Lang, vi: string, en: string) => (lang === 'en' ? en : vi);

type P = {p: number; col: string; lang: Lang};
const Svg: React.FC<{children: React.ReactNode; h?: number}> = ({children, h = VH}) => (
  <svg width={VW} height={h} viewBox={`0 0 ${VW} ${h}`} style={{display: 'block', fontFamily: sans}}>{children}</svg>
);
const T: React.FC<{x: number; y: number; size?: number; color?: string; anchor?: 'start' | 'middle' | 'end'; weight?: number; mono?: boolean; opacity?: number; children: React.ReactNode}> =
  ({x, y, size = 30, color = C.white, anchor = 'start', weight = 600, mono: m, opacity = 1, children}) => (
    <text x={x} y={y} fontSize={size} fill={color} textAnchor={anchor} fontWeight={weight} fontFamily={m ? mono : sans} opacity={opacity}>{children}</text>);
const wrap = (text: string, max: number): string[] => {
  const words = text.split(' '); const out: string[] = []; let cur = '';
  words.forEach((w) => { if ((cur + ' ' + w).trim().length > max && cur) { out.push(cur); cur = w; } else cur = (cur + ' ' + w).trim(); });
  if (cur) out.push(cur); return out;
};
const Robot: React.FC<{x: number; y: number; size?: number; color?: string}> = ({x, y, size = 110, color = C.white}) => <IconG name="robot" x={x} y={y} size={size} color={color} sw={1.5} />;

/* ───────────── intro: radar + hook question + repo + facts ───────────── */
export const IntroV: React.FC<{data: any; p: number}> = ({data, p}) => {
  const col = accent(data.color); const q: string = data.q;
  const typed = q.slice(0, Math.ceil(q.length * seg(p, 0.02, 0.3)));
  const sweep = (p * 900) % 360; const blip = seg(p, 0.35, 0.5);
  const cx = 150, cy = 150, R = 135;
  return <div>
    <div style={{display: 'flex', gap: 28, alignItems: 'center', height: 320}}>
      <svg width={300} height={300} viewBox="0 0 300 300" style={{flex: '0 0 300px'}}>
        <defs><radialGradient id="rgv" cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor={col} stopOpacity="0.2" /><stop offset="100%" stopColor={col} stopOpacity="0" /></radialGradient></defs>
        <circle cx={cx} cy={cy} r={R} fill="url(#rgv)" />
        {[R, R * 0.66, R * 0.33].map((r) => <circle key={r} cx={cx} cy={cy} r={r} fill="none" stroke={C.border} strokeWidth={2} />)}
        <line x1={cx - R} y1={cy} x2={cx + R} y2={cy} stroke={C.border} /><line x1={cx} y1={cy - R} x2={cx} y2={cy + R} stroke={C.border} />
        <g transform={`rotate(${sweep} ${cx} ${cy})`}>
          <path d={`M${cx} ${cy} L${cx + R} ${cy} A${R} ${R} 0 0 0 ${cx + R * Math.cos(-0.7)} ${cy + R * Math.sin(-0.7)} Z`} fill={col} opacity={0.24} />
          <line x1={cx} y1={cy} x2={cx + R} y2={cy} stroke={col} strokeWidth={3} />
        </g>
        <circle cx={cx + 66} cy={cy - 50} r={8 + blip * 5 + Math.sin(p * 40) * 2 * blip} fill={C.red} opacity={blip} />
        <circle cx={cx + 66} cy={cy - 50} r={20 + blip * 14} fill="none" stroke={C.red} strokeWidth={2} opacity={blip * 0.6} />
      </svg>
      <div style={{flex: 1, fontSize: 64, fontWeight: 800, lineHeight: 1.12, minHeight: 240, display: 'flex', alignItems: 'center'}}>
        <span>{typed}<span style={{color: col, opacity: Math.floor(p * 20) % 2 ? 0 : 1}}>▌</span></span>
      </div>
    </div>
    <div style={{marginTop: 22, display: 'flex', alignItems: 'center', gap: 16, opacity: blip, transform: `translateX(${(1 - blip) * 30}px)`,
      background: C.panel, border: `3px solid ${col}`, borderRadius: 22, padding: '16px 26px'}}>
      <Icon name={data.art === 'palette' ? 'palette' : data.art === 'memory' ? 'db' : 'shield'} size={56} color={col} />
      <span style={{fontFamily: mono, fontSize: 35, fontWeight: 800, color: col}}>{data.repo}</span>
    </div>
    <div style={{display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 16, marginTop: 22}}>
      {(data.chips as string[][]).map(([icon, label, value], i) => {
        const a = stagger(p, i, 0.08, 0.2) * seg(p, 0.45, 0.6);
        return <div key={label} style={{...box, display: 'flex', alignItems: 'center', gap: 16, padding: '18px 22px', opacity: a, transform: `translateY(${(1 - a) * 24}px)`}}>
          <Icon name={icon} size={52} color={col} />
          <div><div style={{fontSize: 25, color: C.muted}}>{label}</div><div style={{fontSize: 37, fontWeight: 800}}>{value}</div></div>
        </div>;
      })}
    </div>
  </div>;
};

/* ───────────── growth: honest 2–3 point chart + rate cards ───────────── */
export const GrowthV: React.FC<{data: any; note: string; p: number}> = ({data, note, p}) => {
  const lang = langOf(data); const nf = (n: number) => (lang === 'en' ? Math.round(n).toLocaleString('en-US') : fmt(n));
  const col = accent(data.color); const pts = data.pts as [string, number][];
  const X0 = 110, X1 = 790, Y0 = 296, H = 138; const max = data.total * 1.06;
  const days = pts.length === 3 ? [30, 7, 0] : [30, 0];
  const xs = days.map((d) => X0 + ((30 - d) / 30) * (X1 - X0));
  const ys = pts.map(([, v]) => Y0 - (v / max) * H);
  const line = xs.map((x, i) => `${i ? 'L' : 'M'}${x} ${ys[i]}`).join(' ');
  const area = `${line} L${xs[xs.length - 1]} ${Y0} L${xs[0]} ${Y0} Z`;
  const draw = seg(p, 0.12, 0.62);
  const total = data.total * ease(p * 1.6);
  const star = 1 + Math.sin(p * 60) * 0.06;
  return <div>
    <div style={{...box, padding: 0}}>
      <svg width={VW} height={348} viewBox={`0 0 ${VW} 348`} style={{fontFamily: sans}}>
        <defs><linearGradient id="arv" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={col} stopOpacity="0.45" /><stop offset="100%" stopColor={col} stopOpacity="0.02" /></linearGradient>
          <clipPath id="revealv"><rect x="0" y="0" width={X0 + (X1 - X0) * draw + 40} height="348" /></clipPath></defs>
        <T x={32} y={44} size={28} color={C.muted}>{pick(lang, 'Số sao tích lũy', 'Stars so far')}</T>
        <T x={32} y={112} size={72} color={C.white} weight={900}>{nf(total)}</T>
        <g transform={`translate(${VW - 90},50) scale(${star})`}><IconG name="star" size={58} color={col} sw={2} /></g>
        <line x1={X0} x2={X1} y1={Y0} y2={Y0} stroke={C.border} strokeWidth={2} />
        <T x={X0 - 14} y={Y0 + 8} size={22} color={C.muted} anchor="end">0</T>
        <g clipPath="url(#revealv)"><path d={area} fill="url(#arv)" /><path d={line} fill="none" stroke={col} strokeWidth={7} strokeLinejoin="round" strokeLinecap="round" /></g>
        {xs.map((x, i) => {
          const at = i / (xs.length - 1);
          return <g key={i} opacity={i === 0 ? 1 : clamp((draw - at + 0.08) / 0.08)}>
            <circle cx={x} cy={ys[i]} r={12} fill={C.bg} stroke={col} strokeWidth={5} />
            <T x={x} y={ys[i] - 24} size={31} color={C.white} anchor="middle" weight={800}>{nf(pts[i][1])}</T>
            <T x={x} y={Y0 + 36} size={25} color={C.muted} anchor="middle">{pts[i][0]}</T>
          </g>;
        })}
        {data.segs && data.segs.map((r: number, i: number) => {
          const a = seg(p, 0.55 + i * 0.12, 0.7 + i * 0.12);
          const mx = (xs[i] + xs[i + 1]) / 2, my = Y0 - 14;
          return <g key={i} opacity={a} transform={`translate(0,${(1 - a) * 12})`}>
            <rect x={mx - 140} y={my - 40} width={280} height={46} rx={23} fill={i ? col : C.border} />
            <T x={mx} y={my - 7} size={25} color={i ? C.bg : C.white} anchor="middle" weight={800}>≈ {nf(r)} {pick(lang, 'sao / ngày', 'stars / day')}</T>
          </g>;
        })}
      </svg>
    </div>
    <div style={{...box, marginTop: 14, padding: '16px 28px', borderLeft: `10px solid ${col}`, opacity: seg(p, 0.5, 0.65)}}>
      <div style={{fontSize: 26, color: C.muted}}>{pick(lang, 'Cứ khoảng', 'About every')}</div>
      <div style={{fontSize: 70, fontWeight: 900, color: col, lineHeight: 1.05}}>{data.tick.replace('≈ ', '')}</div>
      <div style={{fontSize: 25, color: C.muted, marginTop: 4}}>{pick(lang, 'có thêm một sao · ', 'one more star · ')}{data.tick_basis}</div>
    </div>
    <div style={{display: 'flex', gap: 14, marginTop: 14}}>
      {[[pick(lang, '30 ngày', '30 days'), '+' + nf(data.month)], data.week != null ? [pick(lang, '7 ngày', '7 days'), '+' + nf(data.week)] : [pick(lang, 'Hôm nay', 'Today'), '+' + nf(data.today)]].map(([l, v], i) => (
        <div key={l} style={{...box, flex: 1, padding: '10px 18px', textAlign: 'center', opacity: seg(p, 0.62 + i * 0.08, 0.78 + i * 0.08)}}>
          <div style={{fontSize: 25, color: C.muted}}>{l}</div><div style={{fontSize: 48, fontWeight: 900, color: col, lineHeight: 1.1}}>{v}</div></div>))}
    </div>
    <div style={{marginTop: 10, fontSize: 23, color: C.muted, lineHeight: 1.3, opacity: seg(p, 0.7, 0.85)}}>{note}</div>
  </div>;
};

/* ───────────── flow: vertical pipeline with a travelling packet ───────────── */
export const FlowV: React.FC<{data: any; note?: string; p: number}> = ({data, note, p}) => {
  const col = accent(data.color); const steps = data.steps as string[][]; const n = steps.length;
  const x = 72, y0 = 54, pitch = 108; const ys = steps.map((_, i) => y0 + i * pitch); const yEnd = ys[n - 1];
  const travel = seg(p, 0.08, 0.86); const py = y0 + (yEnd - y0) * travel;
  return <Svg>
    <line x1={x} y1={y0} x2={x} y2={yEnd} stroke={C.border} strokeWidth={6} strokeLinecap="round" />
    <line x1={x} y1={y0} x2={x} y2={py} stroke={col} strokeWidth={6} strokeLinecap="round" />
    {ys.map((y, i) => {
      const lit = py >= y - 4; const a = stagger(p, i, 0.07, 0.16);
      const [icon, title, sub] = steps[i]; const lines = wrap(sub, 26);
      return <g key={i} opacity={a} transform={`translate(${(1 - a) * 30},0)`}>
        <circle cx={x} cy={y} r={44} fill={lit ? C.panel : C.deep} stroke={lit ? col : C.border} strokeWidth={lit ? 5 : 3} />
        <IconG name={icon} x={x - 22} y={y - 22} size={44} color={lit ? col : C.muted} sw={1.7} />
        <circle cx={x - 36} cy={y - 36} r={16} fill={col} /><T x={x - 36} y={y - 29} size={20} color={C.bg} anchor="middle" weight={900}>{i + 1}</T>
        <T x={148} y={y - (lines.length > 1 ? 2 : 0) + (lines.length ? 0 : 12)} size={38} weight={800} color={lit ? C.white : C.muted}>{title}</T>
        {lines.map((l, k) => <T key={k} x={148} y={y + 32 + k * 30 - (lines.length > 1 ? 8 : 0)} size={27} color={C.muted} weight={500}>{l}</T>)}
      </g>;
    })}
    <g opacity={1 - seg(p, 0.86, 0.95)}><circle cx={x} cy={py} r={13} fill={C.white} /><circle cx={x} cy={py} r={26} fill={col} opacity={0.35} /></g>
    {note && wrap(note, 44).map((l, k) => <T key={k} x={VW / 2} y={yEnd + 96 + k * 34} size={28} color={col} anchor="middle" weight={700} opacity={seg(p, 0.75, 0.92)}>{l}</T>)}
  </Svg>;
};

/* ───────────── story illustrations (why) ───────────── */
const ArtCtxV: React.FC<P> = ({p, col, lang}) => {
  const fill = seg(p, 0.1, 0.62); const cols = 12, rows = 5, total = cols * rows; const scanned = Math.floor(seg(p, 0.1, 0.62) * 22);
  const full = fill > 0.97;
  return <Svg>
    <rect x={0} y={0} width={VW} height={292} rx={32} fill={C.panel} stroke={full ? C.red : C.border} strokeWidth={4} />
    <T x={36} y={56} size={30} color={C.muted}>{pick(lang, 'Ngữ cảnh của agent', "The agent's context")}</T>
    <rect x={36} y={78} width={848} height={44} rx={22} fill={C.deep} stroke={C.border} />
    <rect x={36} y={78} width={Math.max(0, 848 * fill)} height={44} rx={22} fill={full ? C.red : col} />
    <T x={460} y={110} size={28} color={C.white} anchor="middle" weight={800}>{Math.round(fill * 100)}%</T>
    <Robot x={44} y={150} size={118} color={col} />
    <g opacity={seg(p, 0.25, 0.4)}><rect x={190} y={176} width={330} height={68} rx={34} fill={C.deep} stroke={col} strokeWidth={3} /><T x={355} y={221} size={30} anchor="middle" color={C.white}>{pick(lang, '1 giả thuyết / lúc', '1 hypothesis at a time')}</T></g>
    {full && <g transform={`translate(0,${Math.sin(p * 50) * 3})`}><rect x={560} y={176} width={320} height={68} rx={34} fill={C.red} /><T x={720} y={221} size={30} anchor="middle" color={C.bg} weight={900}>{pick(lang, 'Ngữ cảnh đầy', 'Context full')}</T></g>}
    <T x={460} y={352} size={30} color={C.muted} anchor="middle">{pick(lang, 'Một repo thật', 'A real repo')}</T>
    {Array.from({length: total}).map((_, i) => {
      const cx = 16 + (i % cols) * 74, cy = 376 + Math.floor(i / cols) * 58; const on = i < scanned;
      return <rect key={i} x={cx} y={cy} width={62} height={46} rx={10} fill={on ? col : C.dim} opacity={on ? 1 : 0.9} />;
    })}
    {(() => { const i = Math.min(scanned, total - 1); return <IconG name="search" x={16 + (i % cols) * 74 + 10} y={376 + Math.floor(i / cols) * 58 + 2} size={44} color={C.white} sw={2.4} />; })()}
    <T x={460} y={700} size={34} color={C.white} anchor="middle" weight={700} opacity={seg(p, 0.68, 0.82)}>{pick(lang, 'Mới đọc được một phần nhỏ', 'Only a small part read')}</T>
  </Svg>;
};

const MiniUiV: React.FC<{x: number; y: number; a: number}> = ({x, y, a}) => (
  <g opacity={a} transform={`translate(${x},${y + (1 - a) * 20}) scale(1.18)`}>
    <rect width={380} height={190} rx={14} fill="#f1eefb" /><defs><linearGradient id="slopv" x1="0" x2="1"><stop offset="0" stopColor="#8b5cf6" /><stop offset="1" stopColor="#3b82f6" /></linearGradient></defs>
    <rect width={380} height={62} rx={14} fill="url(#slopv)" /><rect y={30} width={380} height={32} fill="url(#slopv)" />
    <rect x={22} y={86} width={44} height={44} rx={12} fill="#c4b5fd" /><rect x={80} y={90} width={150} height={14} rx={7} fill="#1f2937" /><rect x={80} y={112} width={110} height={10} rx={5} fill="#9ca3af" />
    <rect x={22} y={140} width={336} height={38} rx={12} fill="#ffffff" /><rect x={34} y={150} width={140} height={10} rx={5} fill="#9ca3af" /><rect x={200} y={148} width={140} height={22} rx={11} fill="#e0e7ff" /><rect x={212} y={154} width={90} height={10} rx={5} fill="#a5b4fc" />
  </g>);
const ArtSlopV: React.FC<P> = ({p, col, lang}) => {
  const tells = lang === 'en' ? ['Inter for everything', 'Purple → blue gradient', 'Cards inside cards', 'Grey text on colour', 'Icon box above every heading']
    : ['Inter cho mọi thứ', 'Gradient tím → xanh', 'Thẻ lồng trong thẻ', 'Chữ xám trên nền màu', 'Ô icon trên mỗi tiêu đề'];
  return <Svg>
    {[0, 1, 2, 3].map((i) => <MiniUiV key={i} x={(i % 2) * 472} y={Math.floor(i / 2) * 238} a={stagger(p, i, 0.06, 0.14)} />)}
    <T x={460} y={500} size={31} color={C.white} weight={700} anchor="middle" opacity={seg(p, 0.45, 0.6)}>{pick(lang, 'Bốn trang, bốn dự án… giống hệt nhau?', 'Four pages, four projects… all identical?')}</T>
    {tells.map((t, i) => { const a = seg(p, 0.5 + i * 0.08, 0.62 + i * 0.08);
      const x = (i % 2) * 472, y = 522 + Math.floor(i / 2) * 74;
      return <g key={t} opacity={a} transform={`translate(${(1 - a) * 30},0)`}>
        <rect x={x} y={y} width={448} height={62} rx={31} fill={C.panel} stroke={col} strokeWidth={2} />
        <circle cx={x + 34} cy={y + 31} r={19} fill={col} /><T x={x + 34} y={y + 39} size={22} color={C.bg} weight={900} anchor="middle">{i + 1}</T>
        <T x={x + 66} y={y + 41} size={27} color={C.white} weight={600}>{t}</T></g>; })}
  </Svg>;
};

const ArtAmnesiaV: React.FC<P> = ({p, col, lang}) => <Svg>
  {[0, 1, 2].map((i) => { const a = stagger(p, i, 0.2, 0.25); const y = i * 215;
    return <g key={i} opacity={a} transform={`translate(0,${(1 - a) * 24})`}>
      <rect x={0} y={y} width={VW} height={190} rx={32} fill={C.panel} stroke={C.border} strokeWidth={3} />
      <IconG name="calendar" x={30} y={y + 22} size={44} color={C.muted} /><T x={86} y={y + 56} size={31} color={C.muted}>{pick(lang, 'Phiên ', 'Session ')}{i + 1}</T>
      <Robot x={50} y={y + 70} size={100} color={col} />
      <rect x={250} y={y + 36} width={640} height={118} rx={30} fill={C.deep} stroke={C.red} strokeWidth={3} />
      <T x={570} y={y + 108} size={36} anchor="middle" color={C.white}>{pick(lang, 'Dự án này cấu trúc thế nào?', 'How is this project structured?')}</T>
      {i < 2 && <g opacity={seg(p, 0.2 + i * 0.25, 0.32 + i * 0.25)}><circle cx={460} cy={y + 203} r={24} fill={C.bg} stroke={C.red} strokeWidth={3} /><IconG name="repeat" x={440} y={y + 183} size={40} color={C.red} sw={2.2} /></g>}
    </g>; })}
  <T x={460} y={688} size={32} color={C.white} anchor="middle" weight={700} opacity={seg(p, 0.75, 0.9)}>{pick(lang, 'Đóng phiên là quên sạch.', 'Close the session, forget everything.')}</T>
  <T x={460} y={728} size={32} color={C.white} anchor="middle" weight={700} opacity={seg(p, 0.78, 0.92)}>{pick(lang, 'Mỗi sáng lại giải thích từ đầu.', 'Every morning, explain it all again.')}</T>
</Svg>;

export const StoryV: React.FC<{data: any; p: number}> = ({data, p}) => {
  const col = accent(data.color); const k = data.art; const lang = langOf(data);
  return k === 'ctx' ? <ArtCtxV p={p} col={col} lang={lang} /> : k === 'slop' ? <ArtSlopV p={p} col={col} lang={lang} /> : <ArtAmnesiaV p={p} col={col} lang={lang} />;
};

/* ───────────── usage: terminal + compact result ───────────── */
const Verdict: React.FC<{x: number; y: number; icon: string; label: string; color: string; a: number; w: number}> = ({x, y, icon, label, color, a, w}) => (
  <g opacity={a} transform={`translate(0,${(1 - a) * 14})`}>
    <rect x={x} y={y} width={w} height={58} rx={29} fill={C.deep} stroke={color} strokeWidth={3} />
    <IconG name={icon} x={x + 14} y={y + 12} size={34} color={color} sw={2.4} /><T x={x + 58} y={y + 39} size={25} color={color} mono weight={800}>{label}</T>
  </g>);
const ResultV: React.FC<{kind: string; p: number; col: string; lang: Lang}> = ({kind, p, col, lang}) => {
  if (kind === 'ledger') {
    const n = Math.floor(seg(p, 0.35, 0.85) * 40);
    return <Svg h={250}>
      <T x={0} y={28} size={27} color={C.muted}>{pick(lang, 'Sổ coverage: phần đã được xem', 'Coverage ledger: what has been read')}</T>
      {Array.from({length: 60}).map((_, i) => <rect key={i} x={(i % 20) * 46} y={46 + Math.floor(i / 20) * 40} width={38} height={32} rx={8} fill={i < n * 1.5 ? col : C.dim} />)}
      <Verdict x={0} y={180} icon="check" label="confirmed" color={C.green} a={seg(p, 0.55, 0.7)} w={270} />
      <Verdict x={282} y={180} icon="clock" label="needs_validation" color={C.amber} a={seg(p, 0.65, 0.8)} w={350} />
      <Verdict x={644} y={180} icon="cross" label="rejected" color={C.red} a={seg(p, 0.75, 0.9)} w={250} />
    </Svg>;
  }
  if (kind === 'critique') {
    const a = (s: number) => seg(p, s, s + 0.12);
    return <Svg h={250}>
      <g opacity={seg(p, 0.3, 0.45)}><g transform="translate(0,6)"><MiniUiV x={0} y={0} a={1} /></g></g>
      {[['P0', 360, 120, C.red, 0.5], ['P1', 70, 20, C.amber, 0.6], ['P2', 300, 20, C.blue, 0.7]].map(([l, x, y, c, s]) => (
        <g key={l as string} opacity={a(s as number)}><circle cx={(x as number) + 20} cy={(y as number) + 20} r={30} fill={c as string} /><T x={(x as number) + 20} y={(y as number) + 30} size={25} color={C.bg} weight={900} anchor="middle">{l as string}</T></g>))}
      <T x={500} y={80} size={31} color={C.white} weight={700} opacity={a(0.75)}>critique:</T>
      <T x={500} y={122} size={29} color={C.white} weight={600} opacity={a(0.75)}>{pick(lang, 'xếp hạng việc cần sửa', 'ranks what to fix')}</T>
      <T x={500} y={160} size={29} color={C.white} weight={600} opacity={a(0.75)}>{pick(lang, 'trước', 'first')}</T>
      <T x={500} y={208} size={25} color={C.muted} opacity={a(0.8)}>{pick(lang, 'P0 chặn phát hành → P3 đánh bóng', 'P0 blocks release → P3 polish')}</T>
    </Svg>;
  }
  const items = lang === 'en' ? [['doc', 'Project structure'], ['check', 'Decisions made'], ['bug', 'Bugs already fixed']] : [['doc', 'Cấu trúc dự án'], ['check', 'Quyết định đã chốt'], ['bug', 'Lỗi đã sửa']];
  return <Svg h={250}>
    <g opacity={seg(p, 0.35, 0.5)}><Robot x={0} y={0} size={80} color={col} /><T x={96} y={52} size={32} weight={800}>{pick(lang, 'Phiên mới · đã nhớ:', 'New session · remembered:')}</T></g>
    {items.map(([ic, t], i) => { const a = seg(p, 0.5 + i * 0.12, 0.62 + i * 0.12);
      return <g key={t} opacity={a} transform={`translate(${(1 - a) * 30},0)`}><rect x={0} y={90 + i * 54} width={620} height={46} rx={23} fill={C.deep} stroke={C.border} /><IconG name={ic} x={14} y={95 + i * 54} size={36} color={col} sw={2.2} /><T x={64} y={124 + i * 54} size={28}>{t}</T></g>; })}
  </Svg>;
};
const wrapCmd = (l: string, max: number): string[] => {
  if (l.length <= max || l.startsWith('#')) return [l];
  const cut = l.lastIndexOf(' ', max); if (cut < 8) return [l];
  const tail = l.slice(cut + 1);
  return [l.slice(0, cut) + ' \\', ...wrapCmd('  ' + tail, max)];
};
export const UsageV: React.FC<{data: any; line: string; p: number}> = ({data, line, p}) => {
  const col = accent(data.color);
  const shown = (data.cmds as string[]).flatMap((l) => wrapCmd(l, 54));
  const total = shown.join('\n').length; let budget = Math.floor(total * clamp(p * 1.9));
  return <div>
    <div style={{...box, padding: 0, overflow: 'hidden', fontFamily: mono, background: '#071321'}}>
      <div style={{display: 'flex', gap: 10, padding: '10px 20px', background: C.deep}}>{['#ff6b6b', '#ffcc73', '#57ecd0'].map((c) => <div key={c} style={{width: 14, height: 14, borderRadius: '50%', background: c}} />)}</div>
      <div style={{padding: '12px 24px', fontSize: 26, lineHeight: 1.42}}>
        {shown.map((l, i) => { const s = l.slice(0, Math.max(0, budget)); budget -= l.length + 1;
          const comment = l.startsWith('#'), prompt = l.startsWith('>');
          return <div key={i} style={{color: comment ? C.muted : prompt ? col : C.white, whiteSpace: 'pre', minHeight: 37, fontFamily: comment ? sans : mono}}>{s}</div>; })}
      </div>
    </div>
    <div style={{marginTop: 12, fontSize: 28, color: C.amber, lineHeight: 1.28}}>{data.note}</div>
    <div style={{marginTop: 14}}><ResultV kind={data.art} p={p} col={col} lang={langOf(data)} /></div>
    {line ? <div style={{display: 'none'}}>{line}</div> : null}
  </div>;
};

/* ───────────── value: benefits vs cost + caveat ───────────── */
export const ValueV: React.FC<{data: any; caveat: string; p: number}> = ({data, caveat, p}) => {
  const col = accent(data.color); const pros = data.pros as string[][]; const cons = data.cons as string[][];
  const tilt = -6 * ease(seg(p, 0.15, 0.55)) + Math.sin(seg(p, 0.5, 0.75) * 9) * 0.8 * (1 - seg(p, 0.5, 0.9));
  const rad = (tilt * Math.PI) / 180; const L = 330; const cx = 460, cy = 38;
  const lY = cy + L * Math.sin(-rad), rY = cy + L * Math.sin(rad);
  const panel = (title: string, items: string[][], c: string, start: number, warn: boolean) => (
    <div style={{...box, marginTop: 12, padding: '14px 24px 10px', borderLeft: `10px solid ${c}`, background: warn ? '#2a2a22' : C.panel}}>
      <div style={{fontSize: 28, fontWeight: 900, color: c, letterSpacing: 1}}>{title}</div>
      {items.map(([ic, t], i) => { const a = seg(p, start + i * 0.1, start + 0.12 + i * 0.1);
        return <div key={t} style={{display: 'flex', alignItems: 'center', gap: 18, height: 64, opacity: a, transform: `translateY(${(1 - a) * 14}px)`}}>
          <Icon name={ic} size={44} color={c} sw={2.2} /><span style={{fontSize: 36, fontWeight: 650}}>{t}</span></div>; })}
    </div>);
  return <div>
    <svg width={VW} height={86} viewBox={`0 0 ${VW} 86`}>
      <polygon points={`${cx - 26},80 ${cx + 26},80 ${cx},${cy}`} fill={C.border} />
      <line x1={cx - L * Math.cos(rad)} y1={lY} x2={cx + L * Math.cos(rad)} y2={rY} stroke={C.white} strokeWidth={9} strokeLinecap="round" />
      <circle cx={cx} cy={cy} r={13} fill={col} />
      <circle cx={cx - L * Math.cos(rad)} cy={lY} r={11} fill={col} /><circle cx={cx + L * Math.cos(rad)} cy={rY} r={11} fill={C.amber} />
    </svg>
    {panel(pick(langOf(data), 'CÁI ĐƯỢC', 'THE GAINS'), pros, col, 0.25, false)}
    {panel(pick(langOf(data), 'CÁI GIÁ', 'THE COST'), cons, C.amber, 0.35, true)}
    <div style={{display: 'flex', gap: 14, alignItems: 'flex-start', marginTop: 12, padding: '14px 22px', borderRadius: 26, background: '#2a2a22', border: `2px solid ${C.amber}`, opacity: seg(p, 0.75, 0.9)}}>
      <Icon name="warn" size={40} color={C.amber} sw={2.2} /><div style={{fontSize: 27, color: C.amber, fontWeight: 600, lineHeight: 1.3}}>{caveat}</div>
    </div>
  </div>;
};

/* ───────────── outro: verdict actions + CTA ───────────── */
export const OutroV: React.FC<{data: any; p: number}> = ({data, p}) => {
  const col = accent(data.color);
  return <div style={{display: 'flex', flexDirection: 'column', gap: 14}}>
    {(data.chips as string[][]).map(([ic, t], i) => { const a = stagger(p, i, 0.12, 0.2);
      return <div key={t} style={{...box, display: 'flex', alignItems: 'center', gap: 22, padding: '18px 28px', opacity: a, transform: `translateX(${(1 - a) * 30}px)`, borderLeft: `12px solid ${col}`}}>
        <Icon name={ic} size={58} color={col} /><div style={{fontSize: 38, fontWeight: 700}}>{t}</div></div>; })}
    <div style={{...box, borderTop: `8px solid ${C.cyan}`, textAlign: 'center', padding: '18px 0 14px', marginTop: 8, opacity: seg(p, 0.4, 0.55)}}>
      <div style={{fontSize: 30, color: C.muted}}>Kieu Studio</div><div style={{fontSize: 84, fontWeight: 900, color: C.cyan, lineHeight: 1.1}}>{data.url}</div></div>
    <div style={{...box, display: 'flex', alignItems: 'center', gap: 18, padding: '16px 24px', opacity: seg(p, 0.55, 0.7)}}>
      <Icon name="arrow" size={46} color={col} /><div style={{fontSize: 30, color: C.white, lineHeight: 1.25}}>{data.teaser}</div></div>
  </div>;
};
