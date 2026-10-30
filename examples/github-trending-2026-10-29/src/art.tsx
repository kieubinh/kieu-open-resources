import React from 'react';
import {C, accent, sans, mono, clamp, ease, seg, stagger, fmt, box} from './theme';

/* ───────────── hand-drawn icon set (24×24, stroke) ───────────── */
const ICONS: Record<string, string[]> = {
  users: ['M9 11m-3.5 0a3.5 3.5 0 1 0 7 0a3.5 3.5 0 1 0-7 0', 'M2.5 20c.6-3.4 3.3-5 6.5-5s5.9 1.6 6.5 5', 'M17 8.5a3 3 0 0 1 0 5.8', 'M18 15.5c2 .5 3.3 2 3.5 4.5'],
  doc: ['M6 3H14L19 8V21H6Z', 'M14 3V8H19', 'M9 13H16', 'M9 17H16'],
  calendar: ['M4 6H20V20H4Z', 'M4 10H20', 'M8 3V7', 'M16 3V7'],
  branch: ['M6 3V15', 'M6 18m-3 0a3 3 0 1 0 6 0a3 3 0 1 0-6 0', 'M18 6m-3 0a3 3 0 1 0 6 0a3 3 0 1 0-6 0', 'M18 9C18 13 12 13 6 15'],
  shield: ['M12 3L20 6V12C20 17 16.5 20 12 21C7.5 20 4 17 4 12V6Z', 'M8.5 12L11 14.5L15.5 9.5'],
  search: ['M11 11m-7 0a7 7 0 1 0 14 0a7 7 0 1 0-14 0', 'M16.5 16.5L21 21'],
  map: ['M3 6L9 4L15 6L21 4V18L15 20L9 18L3 20Z', 'M9 4V18', 'M15 6V20'],
  eye: ['M2 12C5 6.5 8.5 4.5 12 4.5S19 6.5 22 12C19 17.5 15.5 19.5 12 19.5S5 17.5 2 12Z', 'M12 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0-6 0'],
  check: ['M5 12.5L10 17.5L19 7'],
  cross: ['M6 6L18 18', 'M18 6L6 18'],
  lock: ['M5 11H19V21H5Z', 'M8 11V8a4 4 0 0 1 8 0V11'],
  clock: ['M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0-18 0', 'M12 7V12L15.5 14'],
  repeat: ['M17 2L21 6L17 10', 'M3 12V10a4 4 0 0 1 4-4H21', 'M7 22L3 18L7 14', 'M21 12V14a4 4 0 0 1-4 4H3'],
  box: ['M3 8L12 3L21 8V16L12 21L3 16Z', 'M3 8L12 13L21 8', 'M12 13V21'],
  book: ['M4 5C7 4 10 4.5 12 6C14 4.5 17 4 20 5V19C17 18 14 18.5 12 20C10 18.5 7 18 4 19Z', 'M12 6V20'],
  rocket: ['M12 3C16 5 18 9 17 14L12 17L7 14C6 9 8 5 12 3Z', 'M12 10m-1.5 0a1.5 1.5 0 1 0 3 0a1.5 1.5 0 1 0-3 0', 'M7 14L4 17L8 17', 'M17 14L20 17L16 17', 'M10 19L12 22L14 19'],
  palette: ['M12 3a9 9 0 1 0 0 18c1.2 0 1.8-.8 1.4-1.8-.5-1.2.3-2.2 1.6-2.2H17a4 4 0 0 0 4-4C21 6.5 17 3 12 3Z', 'M7.5 11h.01', 'M10 7.5h.01', 'M14 7.5h.01'],
  sliders: ['M4 7H20', 'M4 12H20', 'M4 17H20', 'M9 5V9', 'M15 10V14', 'M8 15V19'],
  bug: ['M12 8c-2.5 0-4 1.8-4 4.5S9.5 18 12 18s4-2.8 4-5.5S14.5 8 12 8Z', 'M12 8V18', 'M8 11L4 9', 'M16 11L20 9', 'M8 15L4 17', 'M16 15L20 17', 'M10 6L9 4', 'M14 6L15 4'],
  hook: ['M12 3V14a4 4 0 1 1-4 4', 'M8 18L5.5 14.5', 'M8 18L11.5 15.5'],
  gear: ['M12 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0-6 0', 'M12 3V6', 'M12 18V21', 'M3 12H6', 'M18 12H21', 'M5.6 5.6L7.8 7.8', 'M16.2 16.2L18.4 18.4', 'M5.6 18.4L7.8 16.2', 'M16.2 7.8L18.4 5.6'],
  db: ['M4 6c0-1.7 3.6-3 8-3s8 1.3 8 3-3.6 3-8 3-8-1.3-8-3Z', 'M4 6V12c0 1.7 3.6 3 8 3s8-1.3 8-3V6', 'M4 12V18c0 1.7 3.6 3 8 3s8-1.3 8-3V12'],
  layers: ['M12 3L21 8L12 13L3 8Z', 'M3 12L12 17L21 12', 'M3 16L12 21L21 16'],
  robot: ['M5 8H19V19H5Z', 'M12 8V4', 'M12 3.5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0-2 0', 'M9 13h.01', 'M15 13h.01', 'M9.5 16.5H14.5'],
  star: ['M12 3L14.8 9L21 9.8L16.5 14.2L17.7 20.5L12 17.5L6.3 20.5L7.5 14.2L3 9.8L9.2 9Z'],
  warn: ['M12 4L21 20H3Z', 'M12 10V14', 'M12 17V17.5'],
  chat: ['M4 5H20V16H10L5 20V16H4Z'],
  arrow: ['M4 12H20', 'M14 6L20 12L14 18'],
};
export const IconG: React.FC<{name: string; x?: number; y?: number; size?: number; color?: string; sw?: number}> = ({name, x = 0, y = 0, size = 48, color = C.white, sw = 1.8}) => (
  <g transform={`translate(${x},${y}) scale(${size / 24})`} fill="none" stroke={color} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round">
    {(ICONS[name] || []).map((d, i) => <path key={i} d={d} />)}
  </g>
);
export const Icon: React.FC<{name: string; size?: number; color?: string; sw?: number}> = ({name, size = 48, color = C.white, sw = 1.8}) => (
  <svg width={size} height={size} viewBox="0 0 24 24"><IconG name={name} size={24} color={color} sw={sw} /></svg>
);

type P = {p: number; col: string};
const Svg: React.FC<{children: React.ReactNode; h?: number}> = ({children, h = 500}) => (
  <svg width="1768" height={h} viewBox={`0 0 1768 ${h}`} style={{display: 'block', fontFamily: sans}}>{children}</svg>
);
const T: React.FC<{x: number; y: number; size?: number; color?: string; anchor?: 'start' | 'middle' | 'end'; weight?: number; mono?: boolean; opacity?: number; children: React.ReactNode}> =
  ({x, y, size = 28, color = C.white, anchor = 'start', weight = 600, mono: m, opacity = 1, children}) => (
    <text x={x} y={y} fontSize={size} fill={color} textAnchor={anchor} fontWeight={weight} fontFamily={m ? mono : sans} opacity={opacity}>{children}</text>);
const wrap = (text: string, max: number): string[] => {
  const words = text.split(' '); const out: string[] = []; let cur = '';
  words.forEach((w) => { if ((cur + ' ' + w).trim().length > max && cur) { out.push(cur); cur = w; } else cur = (cur + ' ' + w).trim(); });
  if (cur) out.push(cur); return out;
};

/* ───────────── cold open: question + radar ───────────── */
export const RadarIntro: React.FC<{data: any; p: number}> = ({data, p}) => {
  const col = accent(data.color); const q: string = data.q;
  const typed = q.slice(0, Math.ceil(q.length * seg(p, 0.02, 0.3)));
  const sweep = (p * 900) % 360;
  const blip = seg(p, 0.35, 0.5);
  const cx = 270, cy = 205, R = 190;
  return <div>
    <div style={{display: 'flex', gap: 40, alignItems: 'center', height: 450}}>
      <div style={{flex: 1}}>
        <div style={{fontSize: 88, fontWeight: 800, lineHeight: 1.1, minHeight: 200}}>{typed}<span style={{color: col, opacity: Math.floor(p * 20) % 2 ? 0 : 1}}>▌</span></div>
        <div style={{marginTop: 24, display: 'inline-flex', alignItems: 'center', gap: 16, opacity: blip, transform: `translateX(${(1 - blip) * 30}px)`,
          background: C.panel, border: `2px solid ${col}`, borderRadius: 18, padding: '14px 30px'}}>
          <Icon name={data.art === 'palette' ? 'palette' : data.art === 'memory' ? 'db' : 'shield'} size={52} color={col} />
          <span style={{fontFamily: mono, fontSize: 40, fontWeight: 800, color: col}}>{data.repo}</span>
        </div>
      </div>
      <svg width={640} height={486} viewBox="0 0 540 410">
        <defs><radialGradient id="rg" cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor={col} stopOpacity="0.18" /><stop offset="100%" stopColor={col} stopOpacity="0" /></radialGradient></defs>
        <circle cx={cx} cy={cy} r={R} fill="url(#rg)" />
        {[R, R * 0.66, R * 0.33].map((r) => <circle key={r} cx={cx} cy={cy} r={r} fill="none" stroke={C.border} strokeWidth={2} />)}
        <line x1={cx - R} y1={cy} x2={cx + R} y2={cy} stroke={C.border} /><line x1={cx} y1={cy - R} x2={cx} y2={cy + R} stroke={C.border} />
        <g transform={`rotate(${sweep} ${cx} ${cy})`}>
          <path d={`M${cx} ${cy} L${cx + R} ${cy} A${R} ${R} 0 0 0 ${cx + R * Math.cos(-0.7)} ${cy + R * Math.sin(-0.7)} Z`} fill={col} opacity={0.22} />
          <line x1={cx} y1={cy} x2={cx + R} y2={cy} stroke={col} strokeWidth={3} />
        </g>
        <circle cx={cx + 95} cy={cy - 70} r={9 + blip * 6 + Math.sin(p * 40) * 2 * blip} fill={C.red} opacity={blip} />
        <circle cx={cx + 95} cy={cy - 70} r={26 + blip * 18} fill="none" stroke={C.red} strokeWidth={2} opacity={blip * 0.6} />
        <T x={cx} y={400} size={22} color={C.muted} anchor="middle" weight={700}>GITHUB RADAR</T>
      </svg>
    </div>
    <div style={{display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 20, marginTop: 24}}>
      {(data.chips as string[][]).map(([icon, label, value], i) => {
        const a = stagger(p, i, 0.08, 0.2) * seg(p, 0.45, 0.6);
        return <div key={label} style={{...box, display: 'flex', alignItems: 'center', gap: 16, padding: '20px 22px', opacity: a, transform: `translateY(${(1 - a) * 24}px)`}}>
          <Icon name={icon} size={54} color={col} />
          <div><div style={{fontSize: 24, color: C.muted}}>{label}</div><div style={{fontSize: 38, fontWeight: 800}}>{value}</div></div>
        </div>;
      })}
    </div>
  </div>;
};

/* ───────────── growth: honest 2–3 point chart + rate panel ───────────── */
export const GrowthChart: React.FC<{data: any; note: string; p: number}> = ({data, note, p}) => {
  const col = accent(data.color); const pts = data.pts as [string, number][];
  const X0 = 90, X1 = 1000, Y0 = 395, H = 290; const max = data.total * 1.06;
  const days = pts.length === 3 ? [30, 7, 0] : [30, 0];
  const xs = days.map((d) => X0 + ((30 - d) / 30) * (X1 - X0));
  const ys = pts.map(([, v]) => Y0 - (v / max) * H);
  const line = xs.map((x, i) => `${i ? 'L' : 'M'}${x} ${ys[i]}`).join(' ');
  const area = `${line} L${xs[xs.length - 1]} ${Y0} L${xs[0]} ${Y0} Z`;
  const draw = seg(p, 0.12, 0.62);
  const total = data.total * ease(p * 1.6);
  const star = 1 + Math.sin(p * 60) * 0.06;
  return <div style={{display: 'flex', gap: 28}}>
    <div style={{...box, padding: 0, flex: '0 0 1130px'}}>
      <svg width={1130} height={455} viewBox="0 0 1130 455" style={{fontFamily: sans}}>
        <defs><linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={col} stopOpacity="0.45" /><stop offset="100%" stopColor={col} stopOpacity="0.02" /></linearGradient>
          <clipPath id="reveal"><rect x="0" y="0" width={X0 + (X1 - X0) * draw + 40} height="455" /></clipPath></defs>
        <T x={X0} y={52} size={26} color={C.muted}>Số sao tích lũy</T>
        <T x={X1 + 30} y={60} size={54} color={C.white} weight={900} anchor="end">{fmt(total)}</T>
        <g transform={`translate(${X1 + 40},24) scale(${star})`}><IconG name="star" size={44} color={col} sw={2} /></g>
        {[0.25, 0.5, 0.75, 1].map((f) => <line key={f} x1={X0} x2={X1} y1={Y0 - f * H * (1 / 1.06)} y2={Y0 - f * H * (1 / 1.06)} stroke={C.border} strokeDasharray="4 8" opacity={0.5} />)}
        <line x1={X0} x2={X1} y1={Y0} y2={Y0} stroke={C.border} strokeWidth={2} />
        <T x={X0 - 12} y={Y0 + 8} size={20} color={C.muted} anchor="end">0</T>
        <g clipPath="url(#reveal)"><path d={area} fill="url(#ar)" /><path d={line} fill="none" stroke={col} strokeWidth={6} strokeLinejoin="round" strokeLinecap="round" /></g>
        {xs.map((x, i) => {
          const at = i / (xs.length - 1);
          return <g key={i} opacity={i === 0 ? 1 : clamp((draw - at + 0.08) / 0.08)}>
            <circle cx={x} cy={ys[i]} r={11} fill={C.bg} stroke={col} strokeWidth={5} />
            <T x={x} y={ys[i] - 24} size={30} color={C.white} anchor="middle" weight={800}>{fmt(pts[i][1])}</T>
            <T x={x} y={Y0 + 38} size={22} color={C.muted} anchor="middle">{pts[i][0]}</T>
          </g>;
        })}
        {data.segs && data.segs.map((r: number, i: number) => {
          const a = seg(p, 0.55 + i * 0.12, 0.7 + i * 0.12);
          const mx = (xs[i] + xs[i + 1]) / 2, my = Y0 - 36 - i * 0;
          return <g key={i} opacity={a} transform={`translate(0,${(1 - a) * 12})`}>
            <rect x={mx - 112} y={my - 34} width={224} height={42} rx={21} fill={i ? col : C.border} />
            <T x={mx} y={my - 5} size={23} color={i ? C.bg : C.white} anchor="middle" weight={800}>≈ {fmt(r)} sao / ngày</T>
          </g>;
        })}
      </svg>
    </div>
    <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 16}}>
      <div style={{...box, padding: '20px 26px', borderTop: `8px solid ${col}`, opacity: seg(p, 0.5, 0.65)}}>
        <div style={{fontSize: 22, color: C.muted}}>Cứ khoảng</div>
        <div style={{fontSize: 62, fontWeight: 900, color: col, lineHeight: 1.05}}>{data.tick.replace('≈ ', '')}</div>
        <div style={{fontSize: 22, color: C.muted, marginTop: 6}}>có thêm một sao · {data.tick_basis}</div>
      </div>
      <div style={{display: 'flex', gap: 14}}>
        {[['30 ngày', '+' + fmt(data.month)], data.week != null ? ['7 ngày', '+' + fmt(data.week)] : ['Hôm nay', '+' + fmt(data.today)]].map(([l, v], i) => (
          <div key={l} style={{...box, flex: 1, padding: '14px 18px', textAlign: 'center', opacity: seg(p, 0.62 + i * 0.08, 0.78 + i * 0.08)}}>
            <div style={{fontSize: 22, color: C.muted}}>{l}</div><div style={{fontSize: 40, fontWeight: 900, color: col}}>{v}</div></div>))}
      </div>
      <div style={{fontSize: 21, color: C.muted, lineHeight: 1.35, opacity: seg(p, 0.7, 0.85)}}>{note}</div>
    </div>
  </div>;
};

/* ───────────── flow: animated pipeline with a travelling packet ───────────── */
export const FlowDiagram: React.FC<{data: any; note?: string; p: number}> = ({data, note, p}) => {
  const col = accent(data.color); const steps = data.steps as string[][]; const n = steps.length;
  const x0 = 150, x1 = 1618; const xs = steps.map((_, i) => x0 + (i * (x1 - x0)) / (n - 1)); const y = 135;
  const travel = seg(p, 0.08, 0.86); const px = x0 + (x1 - x0) * travel;
  return <Svg>
    <line x1={x0} y1={y} x2={x1} y2={y} stroke={C.border} strokeWidth={6} strokeLinecap="round" />
    <line x1={x0} y1={y} x2={px} y2={y} stroke={col} strokeWidth={6} strokeLinecap="round" />
    {xs.map((x, i) => {
      const lit = px >= x - 4; const a = stagger(p, i, 0.07, 0.16);
      const [icon, title, sub] = steps[i]; const lines = wrap(sub, 17);
      return <g key={i} opacity={a} transform={`translate(0,${(1 - a) * 20})`}>
        <circle cx={x} cy={y} r={70} fill={lit ? C.panel : C.deep} stroke={lit ? col : C.border} strokeWidth={lit ? 5 : 3} />
        {lit && <circle cx={x} cy={y} r={82} fill="none" stroke={col} strokeWidth={2} opacity={0.4} />}
        <IconG name={icon} x={x - 32} y={y - 32} size={64} color={lit ? col : C.muted} sw={1.6} />
        <circle cx={x - 58} cy={y - 58} r={19} fill={col} /><T x={x - 58} y={y - 51} size={22} color={C.bg} anchor="middle" weight={900}>{i + 1}</T>
        <T x={x} y={y + 118} size={32} anchor="middle" weight={800} color={lit ? C.white : C.muted}>{title}</T>
        {lines.map((l, k) => <T key={k} x={x} y={y + 156 + k * 28} size={22} color={C.muted} anchor="middle" weight={500}>{l}</T>)}
      </g>;
    })}
    <g opacity={1 - seg(p, 0.86, 0.95)}><circle cx={px} cy={y} r={13} fill={C.white} /><circle cx={px} cy={y} r={26} fill={col} opacity={0.35} /></g>
    {note && <T x={884} y={448} size={27} color={col} anchor="middle" weight={700} opacity={seg(p, 0.75, 0.92)}>{note}</T>}
  </Svg>;
};

/* ───────────── story illustrations (why / problem) ───────────── */
const Robot: React.FC<{x: number; y: number; size?: number; color?: string}> = ({x, y, size = 110, color = C.white}) => <IconG name="robot" x={x} y={y} size={size} color={color} sw={1.5} />;

const ArtCtx: React.FC<P> = ({p, col}) => {
  const fill = seg(p, 0.1, 0.62); const cols = 14, rows = 6, total = cols * rows; const scanned = Math.floor(seg(p, 0.1, 0.62) * 26);
  const full = fill > 0.97;
  return <Svg>
    <rect x={50} y={30} width={560} height={420} rx={32} fill={C.panel} stroke={full ? C.red : C.border} strokeWidth={4} />
    <T x={90} y={82} size={28} color={C.muted}>Ngữ cảnh của agent</T>
    <rect x={90} y={104} width={480} height={40} rx={20} fill={C.deep} stroke={C.border} />
    <rect x={90} y={104} width={Math.max(0, 480 * fill)} height={40} rx={20} fill={full ? C.red : col} />
    <T x={330} y={133} size={24} color={C.white} anchor="middle" weight={800}>{Math.round(fill * 100)}%</T>
    <Robot x={230} y={190} size={160} color={col} />
    <g opacity={seg(p, 0.25, 0.4)}><rect x={90} y={360} width={250} height={62} rx={31} fill={C.deep} stroke={col} /><T x={215} y={402} size={26} anchor="middle" color={C.white}>1 giả thuyết / lúc</T></g>
    {full && <g transform={`translate(0,${Math.sin(p * 50) * 3})`}><rect x={360} y={362} width={220} height={58} rx={29} fill={C.red} /><T x={470} y={400} size={26} anchor="middle" color={C.bg} weight={900}>Ngữ cảnh đầy</T></g>}
    <T x={1130} y={28} size={26} color={C.muted} anchor="middle">Một repo thật</T>
    {Array.from({length: total}).map((_, i) => {
      const cx = 690 + (i % cols) * 76, cy = 55 + Math.floor(i / cols) * 62; const on = i < scanned;
      return <rect key={i} x={cx} y={cy} width={60} height={48} rx={10} fill={on ? col : C.dim} opacity={on ? 1 : 0.9} />;
    })}
    {(() => { const i = Math.min(scanned, total - 1); return <IconG name="search" x={690 + (i % cols) * 76 + 14} y={55 + Math.floor(i / cols) * 62 + 4} size={44} color={C.white} sw={2.4} />; })()}
    <T x={1130} y={455} size={28} color={C.white} anchor="middle" weight={700} opacity={seg(p, 0.68, 0.82)}>Mới đọc được một phần nhỏ</T>
  </Svg>;
};

const Verdict: React.FC<{x: number; y: number; icon: string; label: string; color: string; a: number; w?: number}> = ({x, y, icon, label, color, a, w = 310}) => (
  <g opacity={a} transform={`translate(0,${(1 - a) * 14})`}>
    <rect x={x} y={y} width={w} height={64} rx={32} fill={C.deep} stroke={color} strokeWidth={3} />
    <IconG name={icon} x={x + 18} y={y + 14} size={36} color={color} sw={2.4} /><T x={x + 66} y={y + 42} size={27} color={color} mono weight={800}>{label}</T>
  </g>);
const ArtSplit: React.FC<P> = ({p, col}) => <Svg>
  <T x={50} y={34} size={26} color={C.red} weight={800}>MỘT AGENT LÀM TẤT CẢ</T>
  <g opacity={seg(p, 0.02, 0.15)}>
    <Robot x={60} y={50} size={120} color={C.red} /><IconG name="arrow" x={200} y={92} size={44} color={C.muted} />
    <rect x={260} y={74} width={170} height={64} rx={14} fill={C.deep} stroke={C.border} /><T x={345} y={116} size={25} anchor="middle" color={C.white}>phát hiện</T>
    <path d="M430 106 C520 106 520 190 345 190 C200 190 120 170 120 170" fill="none" stroke={C.red} strokeWidth={4} strokeDasharray="10 8" opacity={seg(p, 0.12, 0.28)} />
    <g opacity={seg(p, 0.2, 0.34)}><rect x={540} y={74} width={330} height={64} rx={32} fill={C.deep} stroke={C.red} strokeWidth={3} /><IconG name="check" x={556} y={88} size={36} color={C.red} sw={2.6} /><T x={604} y={116} size={25} color={C.red} weight={800}>tự chấm: ổn!</T></g>
    <T x={1000} y={118} size={27} color={C.muted} opacity={seg(p, 0.3, 0.42)}>= tự chấm bài thi của chính mình</T>
  </g>
  <line x1={50} y1={222} x2={1718} y2={222} stroke={C.border} strokeDasharray="6 10" />
  <T x={50} y={272} size={26} color={col} weight={800} opacity={seg(p, 0.4, 0.5)}>HAI AGENT TÁCH BIỆT</T>
  <g opacity={seg(p, 0.42, 0.55)}><Robot x={60} y={290} size={120} color={col} /><T x={120} y={448} size={22} color={C.muted} anchor="middle">hunter</T></g>
  <g opacity={seg(p, 0.5, 0.62)}><IconG name="arrow" x={200} y={330} size={44} color={C.muted} /><rect x={260} y={312} width={170} height={64} rx={14} fill={C.deep} stroke={C.border} /><T x={345} y={354} size={25} anchor="middle">ứng viên</T></g>
  <g opacity={seg(p, 0.58, 0.7)}><IconG name="arrow" x={440} y={330} size={44} color={C.muted} /><Robot x={500} y={290} size={120} color={C.amber} /><IconG name="eye" x={572} y={284} size={40} color={C.amber} sw={2.4} /><T x={560} y={448} size={22} color={C.muted} anchor="middle">người kiểm: chỉ để bác bỏ</T></g>
  <Verdict x={760} y={282} icon="check" label="confirmed" color={C.green} a={seg(p, 0.68, 0.78)} w={380} />
  <Verdict x={760} y={356} icon="clock" label="needs_validation" color={C.amber} a={seg(p, 0.74, 0.84)} w={380} />
  <Verdict x={1170} y={282} icon="cross" label="rejected" color={C.red} a={seg(p, 0.8, 0.9)} />
  <T x={1170} y={400} size={24} color={C.muted} opacity={seg(p, 0.85, 0.95)}>Thiếu bằng chứng ≠ lỗ hổng</T>
</Svg>;

const MiniUi: React.FC<{x: number; y: number; a: number}> = ({x, y, a}) => (
  <g opacity={a} transform={`translate(${x},${y + (1 - a) * 20})`}>
    <rect width={380} height={190} rx={14} fill="#f1eefb" /><defs><linearGradient id="slop" x1="0" x2="1"><stop offset="0" stopColor="#8b5cf6" /><stop offset="1" stopColor="#3b82f6" /></linearGradient></defs>
    <rect width={380} height={62} rx={14} fill="url(#slop)" /><rect y={30} width={380} height={32} fill="url(#slop)" />
    <rect x={22} y={86} width={44} height={44} rx={12} fill="#c4b5fd" /><rect x={80} y={90} width={150} height={14} rx={7} fill="#1f2937" /><rect x={80} y={112} width={110} height={10} rx={5} fill="#9ca3af" />
    <rect x={22} y={140} width={336} height={38} rx={12} fill="#ffffff" /><rect x={34} y={150} width={140} height={10} rx={5} fill="#9ca3af" /><rect x={200} y={148} width={140} height={22} rx={11} fill="#e0e7ff" /><rect x={212} y={154} width={90} height={10} rx={5} fill="#a5b4fc" />
  </g>);
const ArtSlop: React.FC<P> = ({p, col}) => {
  const tells = ['Inter cho mọi thứ', 'Gradient tím → xanh', 'Thẻ lồng trong thẻ', 'Chữ xám trên nền màu', 'Ô icon trên mỗi tiêu đề'];
  return <Svg>
    {[0, 1, 2, 3, 4, 5].map((i) => <MiniUi key={i} x={30 + (i % 3) * 405} y={20 + Math.floor(i / 3) * 215} a={stagger(p, i, 0.06, 0.14)} />)}
    <T x={640} y={478} size={28} color={C.white} weight={700} anchor="middle" opacity={seg(p, 0.45, 0.6)}>Sáu trang, sáu dự án… giống hệt nhau?</T>
    {tells.map((t, i) => { const a = seg(p, 0.5 + i * 0.08, 0.62 + i * 0.08);
      return <g key={t} opacity={a} transform={`translate(${(1 - a) * 40},0)`}>
        <rect x={1280} y={30 + i * 90} width={450} height={70} rx={35} fill={C.panel} stroke={col} strokeWidth={2} />
        <circle cx={1318} cy={65 + i * 90} r={20} fill={col} /><T x={1318} y={73 + i * 90} size={22} color={C.bg} weight={900} anchor="middle">{i + 1}</T>
        <T x={1356} y={74 + i * 90} size={26} color={C.white} weight={600}>{t}</T></g>; })}
  </Svg>;
};

const ArtNamed: React.FC<P> = ({p, col}) => {
  const cmds = ['bolder', 'quieter', 'distill', 'typeset', 'layout', 'animate'];
  const sev = [['P0', C.red, 210, 'chặn phát hành'], ['P1', C.amber, 160, ''], ['P2', C.blue, 110, ''], ['P3', C.muted, 60, 'đánh bóng']];
  return <Svg>
    <T x={60} y={40} size={26} color={C.red} weight={800}>MƠ HỒ</T>
    <g opacity={seg(p, 0.02, 0.16)}>
      <rect x={60} y={64} width={520} height={92} rx={24} fill={C.panel} stroke={C.border} /><T x={90} y={122} size={34}>“Làm cho nổi bật hơn!”</T>
      <rect x={60} y={210} width={520} height={14} rx={7} fill={C.dim} /><circle cx={60 + 260 + Math.sin(p * 14) * 150} cy={217} r={22} fill={C.red} />
      <Robot x={230} y={260} size={150} color={C.red} /><T x={400} y={330} size={90} color={C.red} weight={900} opacity={seg(p, 0.2, 0.3)}>?</T>
      <T x={320} y={450} size={24} color={C.muted} anchor="middle">agent phải đoán → đường an toàn</T>
    </g>
    <T x={680} y={40} size={26} color={col} weight={800} opacity={seg(p, 0.3, 0.4)}>CÓ TÊN</T>
    {cmds.map((c, i) => { const a = stagger(p, i, 0.06, 0.14) * seg(p, 0.3, 0.42);
      return <g key={c} opacity={a} transform={`translate(0,${(1 - a) * 14})`}>
        <rect x={680 + (i % 2) * 210} y={64 + Math.floor(i / 2) * 84} width={196} height={68} rx={34} fill={C.deep} stroke={col} strokeWidth={3} />
        <IconG name="sliders" x={698 + (i % 2) * 210} y={80 + Math.floor(i / 2) * 84} size={34} color={col} sw={2.2} /><T x={742 + (i % 2) * 210} y={108 + Math.floor(i / 2) * 84} size={26} mono weight={800}>{c}</T></g>; })}
    <T x={680} y={350} size={24} color={C.muted} opacity={seg(p, 0.55, 0.65)}>một lệnh · một playbook · một mục tiêu</T>
    <T x={1180} y={40} size={26} color={col} weight={800} opacity={seg(p, 0.55, 0.65)}>critique · audit</T>
    {sev.map(([l, c, h, d], i) => { const a = stagger(p, i, 0.07, 0.16) * seg(p, 0.58, 0.72);
      return <g key={l as string} opacity={a}>
        <rect x={1180 + i * 130} y={380 - (h as number) * a} width={100} height={(h as number) * a} rx={14} fill={c as string} />
        <T x={1230 + i * 130} y={420} size={30} anchor="middle" weight={900} color={c as string}>{l as string}</T>
        {d && <T x={1230 + i * 130} y={455} size={20} anchor="middle" color={C.muted}>{d as string}</T>}</g>; })}
  </Svg>;
};

const ArtAmnesia: React.FC<P> = ({p, col}) => <Svg>
  {[0, 1, 2].map((i) => { const a = stagger(p, i, 0.2, 0.25); const x = 40 + i * 590;
    return <g key={i} opacity={a} transform={`translate(0,${(1 - a) * 24})`}>
      <rect x={x} y={20} width={540} height={400} rx={32} fill={C.panel} stroke={C.border} strokeWidth={3} />
      <IconG name="calendar" x={x + 28} y={44} size={44} color={C.muted} /><T x={x + 86} y={78} size={30} color={C.muted}>Phiên {i + 1}</T>
      <Robot x={x + 210} y={120} size={130} color={col} />
      <rect x={x + 40} y={290} width={460} height={96} rx={28} fill={C.deep} stroke={C.red} strokeWidth={3} />
      <T x={x + 270} y={350} size={29} anchor="middle" color={C.white}>Dự án này cấu trúc thế nào?</T>
      {i < 2 && <g opacity={seg(p, 0.2 + i * 0.25, 0.32 + i * 0.25)}><circle cx={x + 565} cy={220} r={34} fill={C.bg} stroke={C.red} strokeWidth={3} /><IconG name="repeat" x={x + 545} y={200} size={40} color={C.red} sw={2.2} /></g>}
    </g>; })}
  <T x={884} y={470} size={28} color={C.white} anchor="middle" weight={700} opacity={seg(p, 0.75, 0.9)}>Đóng phiên là quên sạch. Mỗi sáng lại giải thích từ đầu.</T>
</Svg>;

const ArtFunnel: React.FC<P> = ({p, col}) => {
  const blocks = Array.from({length: 22});
  return <Svg>
    <T x={60} y={40} size={26} color={C.red} weight={800}>NHÉT TOÀN BỘ LỊCH SỬ</T>
    <rect x={60} y={60} width={380} height={390} rx={24} fill={C.panel} stroke={C.border} strokeWidth={3} />
    {blocks.map((_, i) => { const a = seg(p, 0.03 + i * 0.012, 0.1 + i * 0.012);
      return <rect key={i} x={84 + (i % 2) * 168} y={78 + Math.floor(i / 2) * 31} width={156} height={24} rx={6} fill={C.red} opacity={0.85 * a} />; })}
    <T x={250} y={478} size={25} anchor="middle" color={C.muted}>tốn token · loãng sự chú ý</T>
    <T x={560} y={40} size={26} color={col} weight={800} opacity={seg(p, 0.35, 0.45)}>TIẾT LỘ DẦN</T>
    {[['search', 'search', 'chỉ mục · ≈50–100 token / kết quả', 1000], ['layers', 'timeline', 'bối cảnh quanh mục quan tâm', 760], ['doc', 'get_observations', 'chi tiết · ≈500–1.000 token / mục', 520]].map(([ic, t, d, w], i) => {
      const a = seg(p, 0.4 + i * 0.12, 0.54 + i * 0.12); const y = 70 + i * 120;
      return <g key={t as string} opacity={a} transform={`translate(${(1 - a) * 30},0)`}>
        <rect x={560} y={y} width={w as number} height={100} rx={24} fill={C.panel} stroke={col} strokeWidth={3} />
        <IconG name={ic as string} x={586} y={y + 26} size={48} color={col} sw={2} /><T x={654} y={y + 46} size={32} mono weight={800}>{t as string}</T><T x={654} y={y + 82} size={24} color={C.muted}>{d as string}</T></g>; })}
    <g opacity={seg(p, 0.8, 0.92)} transform={`translate(0,${(1 - seg(p, 0.8, 0.92)) * 10})`}>
      <rect x={940} y={400} width={760} height={64} rx={32} fill={col} /><T x={1320} y={443} size={28} color={C.bg} weight={900} anchor="middle">≈ 10× tiết kiệm token (ước tính của README)</T></g>
  </Svg>;
};

export const StoryArt: React.FC<{data: any; p: number}> = ({data, p}) => {
  const col = accent(data.color); const k = data.art;
  return k === 'ctx' ? <ArtCtx p={p} col={col} /> : k === 'split' ? <ArtSplit p={p} col={col} /> : k === 'slop' ? <ArtSlop p={p} col={col} />
    : k === 'named' ? <ArtNamed p={p} col={col} /> : k === 'amnesia' ? <ArtAmnesia p={p} col={col} /> : <ArtFunnel p={p} col={col} />;
};

/* ───────────── usage: terminal + schematic result ───────────── */
const ResultArt: React.FC<{kind: string; p: number; col: string}> = ({kind, p, col}) => {
  if (kind === 'ledger') {
    const n = Math.floor(seg(p, 0.35, 0.85) * 40);
    return <svg width={620} height={420} viewBox="0 0 620 420" style={{fontFamily: sans}}>
      <T x={0} y={26} size={24} color={C.muted}>Sổ coverage: phần đã được xem</T>
      {Array.from({length: 80}).map((_, i) => <rect key={i} x={(i % 16) * 38} y={44 + Math.floor(i / 16) * 38} width={30} height={30} rx={7} fill={i < n ? col : C.dim} />)}
      <Verdict x={0} y={255} icon="check" label="confirmed" color={C.green} a={seg(p, 0.55, 0.7)} w={290} /><Verdict x={0} y={335} icon="clock" label="needs_validation" color={C.amber} a={seg(p, 0.65, 0.8)} w={380} />
      <g opacity={seg(p, 0.75, 0.9)}><rect x={320} y={255} width={290} height={64} rx={32} fill={C.deep} stroke={C.red} strokeWidth={3} /><IconG name="cross" x={338} y={269} size={36} color={C.red} sw={2.4} /><T x={386} y={297} size={27} color={C.red} mono weight={800}>rejected</T></g>
    </svg>;
  }
  if (kind === 'critique') {
    const a = (s: number) => seg(p, s, s + 0.12);
    return <svg width={620} height={380} viewBox="0 0 620 380" style={{fontFamily: sans}}>
      <g opacity={seg(p, 0.3, 0.45)}><MiniUi x={30} y={20} a={1} /></g>
      {[['P0', 330, 150, C.red, 0.5], ['P1', 120, 60, C.amber, 0.6], ['P2', 300, 118, C.blue, 0.7]].map(([l, x, y, c, s]) => (
        <g key={l as string} opacity={a(s as number)}><circle cx={(x as number) + 20} cy={(y as number) + 20} r={26} fill={c as string} /><T x={(x as number) + 20} y={(y as number) + 29} size={22} color={C.bg} weight={900} anchor="middle">{l as string}</T></g>))}
      <T x={30} y={262} size={26} color={C.white} weight={700} opacity={a(0.75)}>critique: xếp hạng việc cần sửa trước</T>
      <T x={30} y={300} size={22} color={C.muted} opacity={a(0.8)}>P0 chặn phát hành → P3 đánh bóng</T>
    </svg>;
  }
  const items = [['doc', 'Cấu trúc dự án'], ['check', 'Quyết định đã chốt'], ['bug', 'Lỗi đã sửa']];
  return <svg width={620} height={380} viewBox="0 0 620 380" style={{fontFamily: sans}}>
    <rect x={0} y={10} width={620} height={340} rx={28} fill={C.panel} stroke={col} strokeWidth={3} opacity={seg(p, 0.3, 0.42)} />
    <g opacity={seg(p, 0.35, 0.5)}><Robot x={24} y={30} size={90} color={col} /><T x={128} y={68} size={28} weight={800}>Phiên mới · đã nhớ:</T></g>
    {items.map(([ic, t], i) => { const a = seg(p, 0.5 + i * 0.12, 0.62 + i * 0.12);
      return <g key={t} opacity={a} transform={`translate(${(1 - a) * 30},0)`}><rect x={40} y={140 + i * 66} width={540} height={52} rx={26} fill={C.deep} stroke={C.border} /><IconG name={ic} x={58} y={150 + i * 66} size={32} color={col} sw={2.2} /><T x={106} y={176 + i * 66} size={26}>{t}</T></g>; })}
  </svg>;
};
export const UsageScene: React.FC<{data: any; line: string; p: number}> = ({data, line, p}) => {
  const col = accent(data.color); const cmds = data.cmds as string[]; const total = cmds.join('\n').length;
  let budget = Math.floor(total * clamp(p * 1.9));
  return <div style={{display: 'flex', gap: 28}}>
    <div style={{flex: '0 0 1100px'}}>
      <div style={{...box, padding: 0, overflow: 'hidden', fontFamily: mono, background: '#071321'}}>
        <div style={{display: 'flex', gap: 10, padding: '12px 20px', background: C.deep}}>{['#ff6b6b', '#ffcc73', '#57ecd0'].map((c) => <div key={c} style={{width: 14, height: 14, borderRadius: '50%', background: c}} />)}</div>
        <div style={{padding: '14px 26px', minHeight: 300, fontSize: 25, lineHeight: 1.5}}>
          {cmds.map((l, i) => { const shown = l.slice(0, Math.max(0, budget)); budget -= l.length + 1;
            const comment = l.startsWith('#'), prompt = l.startsWith('>');
            return <div key={i} style={{color: comment ? C.muted : prompt ? col : C.white, whiteSpace: 'pre', minHeight: 37, fontFamily: comment ? sans : mono}}>{shown}</div>; })}
        </div>
      </div>
      <div style={{marginTop: 14, fontSize: 26, color: C.amber, lineHeight: 1.3}}>{data.note}</div>
      <div style={{marginTop: 4, fontSize: 22, color: C.muted, lineHeight: 1.3}}>{line}</div>
    </div>
    <div style={{flex: 1}}><ResultArt kind={data.art} p={p} col={col} /></div>
  </div>;
};

/* ───────────── value: balance of benefits vs. cost ───────────── */
export const ValueScale: React.FC<{data: any; caveat: string; p: number}> = ({data, caveat, p}) => {
  const col = accent(data.color); const pros = data.pros as string[][]; const cons = data.cons as string[][];
  const tilt = -6 * ease(seg(p, 0.15, 0.55)) + Math.sin(seg(p, 0.5, 0.75) * 9) * 0.8 * (1 - seg(p, 0.5, 0.9));
  const L = 490, cx = 884, cy = 104; const rad = (tilt * Math.PI) / 180;
  const lY = cy + L * Math.sin(-rad); // tilt < 0: the benefits side sinks (heavier)
  const rY = cy + L * Math.sin(rad);
  const pan = (x: number, y: number, items: string[][], c: string, warn: boolean, start: number) => (
    <g>
      <line x1={x} y1={y} x2={x - 150} y2={y + 70} stroke={C.muted} strokeWidth={3} /><line x1={x} y1={y} x2={x + 150} y2={y + 70} stroke={C.muted} strokeWidth={3} />
      <rect x={x - 230} y={y + 70} width={460} height={items.length * 62 + 26} rx={26} fill={warn ? '#2a2a22' : C.panel} stroke={c} strokeWidth={3} />
      {items.map(([ic, t], i) => { const a = seg(p, start + i * 0.1, start + 0.12 + i * 0.1);
        return <g key={t} opacity={a} transform={`translate(0,${(1 - a) * 14})`}>
          <IconG name={ic} x={x - 206} y={y + 88 + i * 62} size={42} color={c} sw={2.2} /><T x={x - 148} y={y + 121 + i * 62} size={30} weight={600}>{t}</T></g>; })}
    </g>);
  return <Svg>
    <polygon points={`${cx - 44},${cy + 150} ${cx + 44},${cy + 150} ${cx},${cy}`} fill={C.border} />
    <line x1={cx - L * Math.cos(rad)} y1={lY} x2={cx + L * Math.cos(rad)} y2={rY} stroke={C.white} strokeWidth={10} strokeLinecap="round" />
    <circle cx={cx} cy={cy} r={16} fill={col} />
    <T x={cx - 400} y={30} size={28} color={col} weight={800} anchor="middle">CÁI ĐƯỢC</T><T x={cx + 400} y={30} size={28} color={C.amber} weight={800} anchor="middle">CÁI GIÁ</T>
    {pan(cx - L * Math.cos(rad), lY, pros, col, false, 0.25)}
    {pan(cx + L * Math.cos(rad), rY, cons, C.amber, true, 0.35)}
    <g opacity={seg(p, 0.75, 0.9)}><rect x={60} y={448} width={1648} height={46} rx={23} fill="#2a2a22" stroke={C.amber} strokeWidth={2} /><IconG name="warn" x={80} y={455} size={32} color={C.amber} sw={2.2} /><T x={124} y={481} size={23} color={C.amber} weight={600}>{caveat}</T></g>
  </Svg>;
};

/* ───────────── ideas: four pictogram tiles ───────────── */
export const IdeaTiles: React.FC<{data: any; p: number}> = ({data, p}) => {
  const col = accent(data.color);
  return <div style={{display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 22}}>{(data.ideas as string[][]).map(([ic, h, d], i) => {
    const a = stagger(p, i, 0.12, 0.2);
    return <div key={h} style={{...box, height: 470, padding: '34px 22px', textAlign: 'center', opacity: a, transform: `translateY(${(1 - a) * 40}px)`, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div style={{fontSize: 26, fontWeight: 900, color: col, alignSelf: 'flex-start'}}>0{i + 1}</div>
      <div style={{width: 170, height: 170, borderRadius: '50%', background: `radial-gradient(circle, ${col}33, transparent 70%)`, border: `3px solid ${col}`, display: 'grid', placeItems: 'center', margin: '8px 0 22px',
        transform: `scale(${1 + Math.sin(p * 30 + i) * 0.015})`}}><Icon name={ic} size={96} color={col} sw={1.6} /></div>
      <div style={{fontSize: 34, fontWeight: 800, lineHeight: 1.2}}>{h}</div>
      <div style={{fontSize: 24, color: C.muted, marginTop: 10, lineHeight: 1.3}}>{d}</div></div>;
  })}</div>;
};

/* ───────────── outro ───────────── */
export const OutroScene: React.FC<{data: any; q: string; p: number}> = ({data, q, p}) => {
  const col = accent(data.color);
  return <div style={{display: 'flex', gap: 28}}>
    <div style={{flex: 1.5, display: 'flex', flexDirection: 'column', gap: 16}}>
      {(data.chips as string[][]).map(([ic, t], i) => { const a = stagger(p, i, 0.12, 0.2);
        return <div key={t} style={{...box, display: 'flex', alignItems: 'center', gap: 22, padding: '16px 28px', opacity: a, transform: `translateX(${(1 - a) * 30}px)`, borderLeft: `10px solid ${col}`}}>
          <Icon name={ic} size={52} color={col} /><div style={{fontSize: 33, fontWeight: 700}}>{t}</div></div>; })}
    </div>
    <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 16}}>
      <div style={{...box, flex: 1, display: 'grid', placeItems: 'center', borderTop: `8px solid ${C.cyan}`}}>
        <div style={{textAlign: 'center'}}><div style={{fontSize: 28, color: C.muted}}>Kieu Studio</div><div style={{fontSize: 68, fontWeight: 900, color: C.cyan}}>{data.url}</div></div></div>
      <div style={{...box, display: 'flex', alignItems: 'center', gap: 16, padding: '16px 24px', opacity: seg(p, 0.55, 0.7)}}>
        <Icon name="arrow" size={44} color={col} /><div style={{fontSize: 26, color: C.white, lineHeight: 1.25}}>{data.teaser}</div></div>
    </div>
  </div>;
};
