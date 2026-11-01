import React from 'react';
import {Img, staticFile} from 'remotion';
import {C, Card, Glass, MONO, Pill, vn, t, EN} from '../theme';
import {Ctx, trace, verification} from '../timeline';
import {fade} from './common';

const dec = (x: number) => (EN ? String(x) : String(x).replace('.', ','));

const Tick: React.FC<{ok?: boolean; size?: number}> = ({ok = true, size = 44}) => (
  <svg width={size} height={size} viewBox="0 0 44 44">
    <circle cx={22} cy={22} r={20} fill={ok ? 'rgba(88,225,164,0.22)' : 'rgba(255,123,142,0.22)'} stroke={ok ? C.good : C.bad} strokeWidth={3} />
    {ok ? <path d="M12 23 L19 30 L32 14" fill="none" stroke={C.good} strokeWidth={4.5} strokeLinecap="round" strokeLinejoin="round" />
      : <path d="M14 14 L30 30 M30 14 L14 30" stroke={C.bad} strokeWidth={4.5} strokeLinecap="round" />}
  </svg>
);

/** Scene 22: evidence, taken from src/data/verification.json (produced by scripts/run_verification.py). */
export const Verify: React.FC<{c: Ctx}> = ({c}) => {
  const V = verification;
  const rows: [string, string, string][] = [
    [t('VÍ DỤ CHÍNH THỨC', 'OFFICIAL EXAMPLES'), `${V.official.filter((o) => o.pass).length}/${V.official.length}` + t(' ví dụ cho kết quả đúng như đề', ' examples give the expected result'), C.good],
    [t('VÉT CẠN', 'EXHAUSTIVE'), t(`${vn(V.exhaustive.cases)} ca · so với regex và bảng DP · ${V.exhaustive.mismatches} sai lệch`, `${vn(V.exhaustive.cases)} cases · vs regex and DP table · ${V.exhaustive.mismatches} mismatches`), C.cyanLight],
    [t('NGẪU NHIÊN', 'RANDOM'), t(`${vn(V.random.cases)} ca · ${V.random.mismatches} sai lệch`, `${vn(V.random.cases)} cases · ${V.random.mismatches} mismatches`), C.blue],
    [t('TRƯỜNG HỢP XẤU NHẤT', 'WORST CASE'), `n = ${vn(V.worst.n)} → ${vn(V.worst.loop_iterations)}` + t(' vòng lặp chính', ' main-loop iterations'), C.warn],
  ];
  return (
    <div style={{display: 'flex', gap: 36, height: '100%'}}>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 16}}>
        {rows.map(([t, body, col], k) => (
          <Glass key={t} style={{...fade(c, k), flex: 1, padding: '12px 30px', borderColor: c.beat >= k ? col : C.line, display: 'flex', alignItems: 'center', gap: 24}}>
            <Tick ok={k === 3 ? true : true} />
            <div>
              <div style={{color: col, fontSize: 24, fontWeight: 800, letterSpacing: 1.5}}>{t}</div>
              <div style={{fontSize: 33, fontWeight: 700, marginTop: 2}}>{body}</div>
            </div>
          </Glass>
        ))}
        {c.beat >= 4 && (
          <Glass style={{...fade(c, 4), padding: '14px 30px', borderColor: C.warn, background: 'rgba(245,186,104,0.12)'}}>
            <div style={{fontSize: 33, fontWeight: 800}}>{t(<>Thử nghiệm là bằng chứng mạnh, <span style={{color: C.warn}}>chưa phải chứng minh toán học</span>.</>, <>Experiments are strong evidence, <span style={{color: C.warn}}>not a mathematical proof</span>.</>)}</div>
          </Glass>
        )}
      </div>
      <div style={{width: 560}}>
        <Card title={t('BA VÍ DỤ CỦA ĐỀ', 'THE THREE OFFICIAL EXAMPLES')} accent={C.cyanLight} style={{height: '100%'}}>
          {V.official.map((o, k) => (
            <div key={k} style={{display: 'flex', alignItems: 'center', gap: 16, padding: '16px 0', borderBottom: k < 2 ? `1px solid ${C.line}` : undefined}}>
              <Tick ok={o.pass} size={38} />
              <div style={{fontFamily: MONO, fontSize: 28, lineHeight: 1.35}}>s = "{o.s}" · p = "{o.p}"<br /><span style={{color: o.actual ? C.good : C.bad}}>{String(o.actual)}</span> <span style={{color: C.muted}}>({t('đề', 'expected')}: {String(o.expected)})</span></div>
            </div>
          ))}
        </Card>
      </div>
    </div>
  );
};

/** Scene 23: three approaches. Every number is tagged as measured (ĐO) or analysis (LÝ THUYẾT). */
export const Complexity: React.FC<{c: Ctx}> = ({c}) => {
  const V = verification;
  const B = trace.blowup.rows;
  const last = B[B.length - 1];
  const rows: [string, string, string, React.ReactNode, string][] = [
    [t('Thử hết mọi nhánh', 'Try every branch'), t('hàm mũ', 'exponential'), t('O(độ sâu)', 'O(depth)'), <><b style={{color: C.bad}}>{vn(last.calls)}</b>{t(' lần gọi', ' calls')} (n = {trace.blowup.n}, k = {last.k})</>, 'ĐO'],
    [t('Bảng quy hoạch động', 'DP table'), 'O(m × n)', 'O(m × n)', <>{t('hơn ', 'over ')}<b>{vn(2001 * 2001)}</b>{t(' ô khi m = n = 2000', ' cells when m = n = 2000')}</>, 'LÝ THUYẾT'],
    [t('Hai con trỏ', 'Two pointers'), t('O(m × n) tệ nhất', 'O(m × n) worst'), 'O(1)', <><b style={{color: C.good}}>{vn(V.worst.loop_iterations)}</b>{t(' vòng lặp ở n = ', ' iterations at n = ')}{vn(V.worst.n)}</>, 'ĐO'],
  ];
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 18, height: '100%'}}>
      <div style={{display: 'grid', gridTemplateColumns: '400px 280px 200px 1fr 190px', gap: 14, padding: '0 28px', color: C.muted, fontSize: 24, fontWeight: 800, letterSpacing: 1}}>
        <div>{t('CÁCH LÀM', 'APPROACH')}</div><div>{t('THỜI GIAN', 'TIME')}</div><div>{t('BỘ NHỚ', 'MEMORY')}</div><div>{t('BẰNG CHỨNG', 'EVIDENCE')}</div><div>{t('LOẠI', 'TYPE')}</div>
      </div>
      {rows.map(([name, time, mem, ev, tag], k) => (
        <Glass key={name} style={{...fade(c, k + 1), flex: 1, display: 'grid', gridTemplateColumns: '400px 280px 200px 1fr 190px', gap: 14, alignItems: 'center', padding: '0 28px',
          borderColor: c.beat === k + 1 ? C.cyanLight : C.line}}>
          <div style={{fontSize: 38, fontWeight: 800}}>{name}</div>
          <div style={{fontFamily: MONO, fontSize: 28, fontWeight: 700}}>{time}</div>
          <div style={{fontFamily: MONO, fontSize: 28, fontWeight: 700, color: mem === 'O(1)' ? C.good : C.text}}>{mem}</div>
          <div style={{fontSize: 27, lineHeight: 1.3}}>{ev}</div>
          <div><Pill color={tag === 'ĐO' ? C.good : C.warn} size={22}>{tag === 'ĐO' ? t('ĐO', 'MEASURED') : t('LÝ THUYẾT', 'ANALYSIS')}</Pill></div>
        </Glass>
      ))}
      <div style={{display: 'flex', gap: 18, height: 130}}>
        <Glass style={{...fade(c, 4), flex: 1, padding: '10px 28px', borderColor: c.beat >= 4 ? C.good : C.line, display: 'flex', alignItems: 'center', gap: 20}}>
          <Pill color={C.good} size={22}>{t('ĐO', 'MEASURED')}</Pill>
          <div style={{fontSize: 29, lineHeight: 1.3}}>{t('Dữ liệu ngẫu nhiên: trung bình ', 'Random data: on average ')}<b style={{color: C.good}}>{dec(V.typical.mean_iterations_per_char)}</b>{t(' vòng lặp cho mỗi ký tự (', ' iterations per character (')}{vn(V.typical.cases)}{t(' ca, n = ', ' cases, n = ')}{V.typical.n}).</div>
        </Glass>
        <Glass style={{...fade(c, 5), flex: 1, padding: '10px 28px', borderColor: c.beat >= 5 ? C.warn : C.line, display: 'flex', alignItems: 'center'}}>
          <div style={{fontSize: 31, fontWeight: 800, lineHeight: 1.3}}>{t('Không có cách luôn tốt nhất: chọn theo giới hạn, bộ nhớ và độ dễ chứng minh.', 'No approach is always best: choose by limits, memory and ease of proof.')}</div>
        </Glass>
      </div>
    </div>
  );
};

/** Scene 24: six lessons, one per narration beat. */
export const Lessons: React.FC<{c: Ctx}> = ({c}) => {
  const L: [string, string, string, string][] = [
    ['1', t('Đọc kỹ yêu cầu', 'Read the requirement'), t('đặc biệt là điều kiện kết thúc', 'especially the ending condition'), C.bad],
    ['2', t('Tìm nơi sinh ra lựa chọn', 'Find where choices come from'), t('ở bài này là dấu *', 'here, it is the *'), C.warn],
    ['3', t('Đơn giản và đúng trước', 'Simple and correct first'), t('rồi đo xem vì sao nó chậm', 'then measure why it is slow'), C.cyanLight],
    ['4', t('Câu hỏi lặp lại → ghi nhớ', 'Repeated questions → remember'), t('bảng quy hoạch động', 'a dynamic programming table'), C.blue],
    ['5', t('Tìm cấu trúc để nhớ ít hơn', 'Find structure to remember less'), t('chỉ giữ dấu * gần nhất', 'keep only the most recent *'), C.good],
    ['6', t('Kiểm chứng độc lập', 'Verify independently'), t('ví dụ, phản ví dụ, cách làm thứ hai', 'examples, counterexamples, a second method'), C.cyanLight],
  ];
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 18, height: '100%'}}>
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gridTemplateRows: '1fr 1fr', gap: 20, flex: 1}}>
        {L.map(([n, t, d, col], k) => (
          <Glass key={n} style={{...fade(c, k), padding: '18px 28px', borderColor: c.beat === k ? col : C.line, opacity: c.beat >= k ? (c.beat === k || c.beat === 6 ? 1 : 0.65) : 0.1,
            display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
            <div style={{fontFamily: MONO, fontSize: 56, fontWeight: 800, color: col, lineHeight: 1}}>{n}</div>
            <div style={{fontSize: 36, fontWeight: 800, lineHeight: 1.2, margin: '8px 0 6px'}}>{t}</div>
            <div style={{fontSize: 26, color: C.muted}}>{d}</div>
          </Glass>
        ))}
      </div>
      <div style={{...fade(c, 6), height: 100, display: 'flex', alignItems: 'center', padding: '0 36px', borderRadius: 24, border: `3px solid ${C.cyanLight}`, background: 'rgba(49,196,207,0.14)'}}>
        <div style={{fontSize: 36, fontWeight: 800}}>{t('Dùng được ngoài LeetCode: lập kế hoạch, sửa lỗi, thiết kế hệ thống.', 'Useful beyond LeetCode: planning, debugging, system design.')}</div>
      </div>
    </div>
  );
};

const PRACTICE: [number, string, string, string, string][] = [
  [392, 'Is Subsequence', 'Easy', t('hai con trỏ trên hai chuỗi · khởi động cho tư duy tham lam', 'two pointers on two strings · a warm-up for greedy thinking'), C.good],
  [72, 'Edit Distance', 'Medium', t('tự định nghĩa ô của bảng · ba lựa chọn ở mỗi ô', 'define the table cell yourself · three choices per cell'), C.warn],
  [10, 'Regular Expression Matching', 'Hard', t('dấu * ở đây có nghĩa khác · so sánh với bài #44', '* means something different here · compare with #44'), C.bad],
];

/** Scene 25: three related problems (difficulty labels as listed on LeetCode, see docs/SOURCES.md). */
export const Practice: React.FC<{c: Ctx}> = ({c}) => (
  <div style={{display: 'flex', flexDirection: 'column', gap: 20, height: '100%'}}>
    <div style={{display: 'flex', gap: 24, flex: 1}}>
      {PRACTICE.map(([n, t, d, hint, col], k) => (
        <Glass key={n} style={{...fade(c, k + 1), flex: 1, padding: '28px 30px', borderColor: c.beat === k + 1 ? col : C.line, opacity: c.beat >= k + 1 ? (c.beat === k + 1 || c.beat >= 4 ? 1 : 0.65) : 0.1,
          display: 'flex', flexDirection: 'column', gap: 14}}>
          <div style={{fontFamily: MONO, fontSize: 76, fontWeight: 800, color: col, lineHeight: 1}}>#{n}</div>
          <div style={{fontSize: 42, fontWeight: 800, lineHeight: 1.2}}>{t}</div>
          <div><Pill color={col} size={28}>{d}</Pill></div>
          <div style={{fontSize: 28, color: C.muted, lineHeight: 1.35, marginTop: 4}}>{hint}</div>
        </Glass>
      ))}
    </div>
    <div style={{...fade(c, 4), height: 130, display: 'flex', alignItems: 'center', gap: 26, padding: '0 36px', borderRadius: 24, border: `3px solid ${C.cyanLight}`, background: 'rgba(49,196,207,0.14)'}}>
      <div style={{fontSize: 33, fontWeight: 800, lineHeight: 1.3}}>{t(<>Đừng xem code ngay. Hãy tự hỏi: <span style={{color: C.cyanLight}}>câu hỏi nhỏ là gì</span> · <span style={{color: C.warn}}>lựa chọn nằm ở đâu</span> · <span style={{color: C.good}}>có cần ghi nhớ không</span>?</>, <>Do not look at code yet. Ask: <span style={{color: C.cyanLight}}>what is the small question</span> · <span style={{color: C.warn}}>where are the choices</span> · <span style={{color: C.good}}>do I need to remember</span>?</>)}</div>
    </div>
  </div>
);

/** Scene 26: closing. */
export const Outro: React.FC<{c: Ctx}> = ({c}) => (
  <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 34, height: '100%'}}>
    <div style={{...fade(c, 0), width: 900, borderRadius: 30, background: '#F3F8FF', display: 'grid', placeItems: 'center', padding: '24px 0', boxShadow: '0 18px 50px rgba(0,0,0,0.35)'}}>
      <Img src={staticFile('brand/kieu-studio-lockup.png')} style={{height: 230, width: 'auto'}} />
    </div>
    <div style={{...fade(c, 1), display: 'flex', gap: 18, alignItems: 'center'}}>
      {t(['Hiểu', 'Giả thuyết', 'Kiểm chứng', 'Rút kinh nghiệm'], ['Understand', 'Hypothesize', 'Test', 'Reflect']).map((t, k) => (
        <React.Fragment key={t}>
          <Pill color={C.cyanLight} size={32}>{t}</Pill>
          {k < 3 && <span style={{color: C.cyan, fontSize: 34, fontWeight: 800}}>→</span>}
        </React.Fragment>
      ))}
    </div>
    <div style={{...fade(c, 1), fontFamily: MONO, fontSize: 40, color: C.warn, fontWeight: 800}}>kieu.app</div>
  </div>
);
