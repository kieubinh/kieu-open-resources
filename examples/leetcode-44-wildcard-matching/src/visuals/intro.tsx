import React from 'react';
import {Img, interpolate, staticFile} from 'remotion';
import {C, Card, Glass, MONO, Pill, Tok, TokState, ramp, vn, t} from '../theme';
import {Ctx} from '../timeline';

import {fade} from './common';

/** Scene 01 — Kieu Studio mission: the four-step problem-solving loop. */
export const Mission: React.FC<{c: Ctx}> = ({c}) => {
  const steps = [
    ['01', t('HIỂU ĐỀ', 'UNDERSTAND'), t('Đọc kỹ yêu cầu, ví dụ và ràng buộc', 'Read the requirement, examples and constraints')],
    ['02', t('ĐẶT GIẢ THUYẾT', 'HYPOTHESIZE'), t('Chọn một hướng và dự đoán kết quả', 'Pick a direction and predict the result')],
    ['03', t('KIỂM CHỨNG', 'TEST'), t('Chạy ví dụ, tìm phản ví dụ', 'Run examples, look for counterexamples')],
    ['04', t('RÚT KINH NGHIỆM', 'REFLECT'), t('Ghi lại điều dùng lại được', 'Write down what you can reuse')],
  ];
  const lit = c.beat < 2 ? -1 : c.beat === 2 ? Math.min(3, Math.floor(c.bp * 4.4)) : 3;
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 24, height: '100%'}}>
      <div style={{display: 'flex', gap: 28, height: 190}}>
        <div style={{...fade(c, 0), width: 560, borderRadius: 26, background: '#F3F8FF', display: 'grid', placeItems: 'center', boxShadow: '0 18px 50px rgba(0,0,0,0.35)'}}>
          <Img src={staticFile('brand/kieu-studio-lockup.png')} style={{height: 150, width: 'auto'}} />
        </div>
        <Glass style={{...fade(c, 1), flex: 1, padding: '26px 34px', display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
          <div style={{color: C.warn, fontSize: 26, fontWeight: 800, letterSpacing: 2}}>{t('MỤC TIÊU', 'OUR GOAL')}</div>
          <div style={{fontSize: 40, fontWeight: 700, lineHeight: 1.25, marginTop: 6}}>{t('Rèn kỹ năng giải quyết vấn đề, không chỉ tìm đáp án.', 'Train problem-solving skills, not just find answers.')}</div>
        </Glass>
      </div>
      <div style={{display: 'flex', gap: 22, flex: 1, alignItems: 'stretch'}}>
        {steps.map(([n, t, d], k) => (
          <React.Fragment key={n}>
            <Glass style={{flex: 1, padding: '22px 24px', borderColor: k <= lit ? C.cyanLight : C.line, opacity: lit < 0 ? 0.55 : k <= lit ? 1 : 0.4,
              background: k <= lit ? 'rgba(49,196,207,0.18)' : undefined, transform: `scale(${k === lit ? 1.03 : 1})`}}>
              <div style={{fontFamily: MONO, color: C.cyanLight, fontSize: 34, fontWeight: 800}}>{n}</div>
              <div style={{fontSize: 31, fontWeight: 800, margin: '8px 0 6px'}}>{t}</div>
              <div style={{fontSize: 25, color: C.muted, lineHeight: 1.3}}>{d}</div>
            </Glass>
            {k < 3 && <div style={{alignSelf: 'center', color: C.cyan, fontSize: 40, fontWeight: 800}}>→</div>}
          </React.Fragment>
        ))}
      </div>
      <div style={{...fade(c, 3), display: 'flex', alignItems: 'center', gap: 28, height: 110}}>
        <Glass style={{flex: 1, height: '100%', display: 'flex', alignItems: 'center', gap: 26, padding: '0 34px', borderColor: C.warn}}>
          <Pill color={C.warn} size={30}>EP03</Pill>
          <div style={{fontSize: 40, fontWeight: 800}}>LeetCode #44 · Wildcard Matching</div>
          <div style={{flex: 1}} />
          <Pill color={C.bad} size={30}>HARD</Pill>
        </Glass>
      </div>
    </div>
  );
};

const CELL = 112, STEP = 128;

/** Scene 02 — the problem: ? and * symbols and an aligned demo. */
export const Problem: React.FC<{c: Ctx}> = ({c}) => {
  const s = 'abcde';
  const starGrow = ramp(c.since(2), 6, 26);
  const eX = interpolate(starGrow, [0, 1], [3 * STEP, 4 * STEP]);
  const starW = interpolate(starGrow, [0, 1], [CELL, CELL * 2 + 16]);
  const final = c.beat >= 3;
  const sState = (i: number): TokState => {
    if (final) return i === 2 || i === 3 ? 'eaten' : 'match';
    if (c.beat === 1 && i === 1) return 'cursor';
    if (c.beat === 2 && (i === 2 || i === 3)) return 'eaten';
    return 'idle';
  };
  const pStates: TokState[] = [final ? 'match' : 'idle', c.beat === 1 ? 'cursor' : final ? 'match' : 'idle', c.beat >= 2 ? 'eaten' : 'idle', final ? 'match' : 'idle'];
  const lineOpacity = c.beat === 1 ? ramp(c.since(1), 6, 12) : 0;
  return (
    <div style={{display: 'flex', gap: 40, height: '100%'}}>
      <div style={{width: 600, display: 'flex', flexDirection: 'column', gap: 24}}>
        <Card accent={C.cyanLight} active={c.beat >= 1} title={t('DẤU HỎI CHẤM', 'QUESTION MARK')} style={{...fade(c, 1), flex: 1}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 26}}>
            <Tok ch="?" state="cursor" w={116} h={116} size={76} />
            <div style={{fontSize: 34, fontWeight: 700, lineHeight: 1.25}}>{t(<>đúng <span style={{color: C.cyanLight}}>một</span> ký tự bất kỳ</>, <>exactly <span style={{color: C.cyanLight}}>one</span> character</>)}</div>
          </div>
        </Card>
        <Card accent={C.warn} active={c.beat >= 2} title={t('DẤU SAO', 'STAR')} style={{...fade(c, 2), flex: 1}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 26}}>
            <Tok ch="*" state="eaten" w={116} h={116} size={76} />
            <div style={{fontSize: 34, fontWeight: 700, lineHeight: 1.25}}>{t(<>một <span style={{color: C.warn}}>dãy</span> ký tự bất kỳ, kể cả dãy rỗng</>, <>any <span style={{color: C.warn}}>sequence</span> of characters, even an empty one</>)}</div>
          </div>
        </Card>
      </div>
      <div style={{flex: 1, position: 'relative'}}>
        <div style={{position: 'absolute', left: 0, top: 30, color: C.muted, fontSize: 28, fontWeight: 700}}>s = "abcde"</div>
        <div style={{position: 'absolute', left: 0, top: 80, display: 'flex', gap: 16}}>
          {s.split('').map((ch, i) => <Tok key={i} ch={ch} w={CELL} h={CELL} state={sState(i)} />)}
        </div>
        <div style={{position: 'absolute', left: 0, top: 292, color: C.muted, fontSize: 28, fontWeight: 700}}>p = "a?*e"</div>
        <div style={{position: 'absolute', left: 0, top: 342, width: 660, height: CELL}}>
          <div style={{position: 'absolute', left: 0}}><Tok ch="a" w={CELL} h={CELL} state={pStates[0]} /></div>
          <div style={{position: 'absolute', left: STEP}}><Tok ch="?" w={CELL} h={CELL} state={pStates[1]} /></div>
          <div style={{position: 'absolute', left: 2 * STEP}}><Tok ch="*" w={starW} h={CELL} state={pStates[2]} /></div>
          <div style={{position: 'absolute', left: eX}}><Tok ch="e" w={CELL} h={CELL} state={pStates[3]} /></div>
        </div>
        <svg width={700} height={330} style={{position: 'absolute', left: 0, top: 80, pointerEvents: 'none', opacity: lineOpacity}}>
          <line x1={STEP + CELL / 2} y1={CELL} x2={STEP + CELL / 2} y2={262} stroke={C.cyanLight} strokeWidth={4} strokeDasharray="10 8" />
        </svg>
        {final && (
          <div style={{position: 'absolute', left: 0, top: 480, width: 660, ...fade(c, 3)}}>
            <div style={{height: 10, borderRadius: 6, background: C.good}} />
            <div style={{color: C.good, fontSize: 30, fontWeight: 800, marginTop: 10}}>{t('Khớp phủ kín TOÀN BỘ s  →  true', 'The match covers ALL of s  →  true')}</div>
          </div>
        )}
        <div style={{position: 'absolute', right: 0, top: 120, width: 330, fontSize: 28, color: C.muted, lineHeight: 1.4}}>
          <span style={{color: C.cyanLight}}>?</span> = b<br /><span style={{color: C.warn}}>*</span> = "cd"
        </div>
      </div>
    </div>
  );
};

/** Scene 03 — input / output / constraints + why 2000 × 2000 matters. */
export const Constraints: React.FC<{c: Ctx}> = ({c}) => {
  const filled = c.beat < 3 ? 0 : c.beat === 3 ? c.bp : 1;
  const cols = 50, rows = 14;
  const lit = Math.floor(filled * cols * rows);
  return (
    <div style={{display: 'flex', gap: 36, height: '100%'}}>
      <div style={{width: 640, display: 'flex', flexDirection: 'column', gap: 22, ...fade(c, 0)}}>
        <Card title="INPUT" style={{flex: 1}}>
          <div style={{fontFamily: MONO, fontSize: 36, lineHeight: 1.55}}>
            <span style={{color: C.cyanLight}}>s</span><span style={{color: C.muted}}>{t(' : chuỗi', ' : string')}</span><br />
            <span style={{color: C.warn}}>p</span><span style={{color: C.muted}}>{t(' : mẫu', ' : pattern')}</span>
          </div>
        </Card>
        <Card title="OUTPUT" accent={C.good} style={{flex: 1}}>
          <div style={{fontFamily: MONO, fontSize: 44, fontWeight: 800}}><span style={{color: C.good}}>true</span><span style={{color: C.muted}}> / </span><span style={{color: C.bad}}>false</span></div>
          <div style={{fontSize: 25, color: C.muted, marginTop: 6}}>{t('khớp toàn bộ hay không', 'does it match entirely?')}</div>
        </Card>
      </div>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 22}}>
        <Card title="CONSTRAINTS" accent={C.warn} active={c.beat >= 1} style={{...fade(c, 1), flex: '0 0 auto'}}>
          <div style={{fontFamily: MONO, fontSize: 40, fontWeight: 800, color: C.warn}}>0 ≤ s.length, p.length ≤ 2000</div>
          <div style={{...fade(c, 2), fontSize: 30, marginTop: 14, lineHeight: 1.5}}>
            <div><span style={{fontFamily: MONO, color: C.cyanLight}}>s</span>{t(' : chữ cái thường a–z', ' : lowercase letters a–z')}</div>
            <div><span style={{fontFamily: MONO, color: C.warn}}>p</span>{t(' : chữ cái thường, ', ' : lowercase letters, ')}<span style={{fontFamily: MONO}}>?</span>{t(' và ', ' and ')}<span style={{fontFamily: MONO}}>*</span></div>
          </div>
        </Card>
        <Card title={t('ĐỘ LỚN CỦA BÀI TOÁN', 'PROBLEM SIZE')} accent={C.cyanLight} active={c.beat >= 3} style={{...fade(c, 3), flex: 1}}>
          <div style={{fontFamily: MONO, fontSize: 38, fontWeight: 800, marginBottom: 14}}>2000 × 2000 = <span style={{color: C.cyanLight}}>{vn(4000000)}</span></div>
          <div style={{display: 'grid', gridTemplateColumns: `repeat(${cols}, 14px)`, gap: 3}}>
            {Array.from({length: cols * rows}).map((_, k) => (
              <div key={k} style={{width: 14, height: 14, borderRadius: 3, background: k < lit ? C.cyan : 'rgba(115,237,240,0.12)'}} />
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

const Counter: React.FC<{value: number; frame: number; start: number; dur?: number; fmt?: (n: number) => string}> = ({value, frame, start, dur = 48, fmt = vn}) => (
  <>{fmt(Math.round(value * ramp(frame, start, dur)))}</>
);

/** Scene 04 — difficulty and verified submission statistics (source: LeetCode, 28 Oct 2026). */
export const Stats: React.FC<{c: Ctx}> = ({c}) => {
  const pct = 33.1;
  const ring = ramp(c.since(2), 0, 40);
  const R = 70, L = 2 * Math.PI * R;
  const tile = (beat: number, color: string, label: string, children: React.ReactNode) => (
    <Glass style={{...fade(c, beat), padding: '24px 34px', borderColor: c.beat >= beat ? color : C.line, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
      <div style={{color, fontSize: 26, fontWeight: 800, letterSpacing: 2}}>{label}</div>
      <div style={{fontSize: 84, fontWeight: 800, lineHeight: 1.05, marginTop: 6}}>{children}</div>
    </Glass>
  );
  return (
    <div style={{height: '100%', display: 'flex', flexDirection: 'column', gap: 18}}>
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr', gap: 24, flex: 1}}>
        {tile(0, C.bad, t('ĐỘ KHÓ', 'DIFFICULTY'), <span style={{color: C.bad}}>Hard</span>)}
        {tile(1, C.cyanLight, t('LƯỢT NỘP ĐƯỢC CHẤP NHẬN', 'ACCEPTED SUBMISSIONS'), <span style={{color: C.cyanLight}}><Counter value={967654} frame={c.since(1)} start={0} /></span>)}
        {tile(1, C.muted, t('TỔNG LƯỢT NỘP', 'TOTAL SUBMISSIONS'), <>{t('≈ 2,9 triệu', '≈ 2.9M')}</>)}
        <Glass style={{...fade(c, 2), padding: '24px 34px', borderColor: c.beat >= 2 ? C.good : C.line, display: 'flex', alignItems: 'center', gap: 30}}>
          <svg width={170} height={170} viewBox="0 0 170 170">
            <circle cx={85} cy={85} r={R} fill="none" stroke="rgba(115,237,240,0.16)" strokeWidth={16} />
            <circle cx={85} cy={85} r={R} fill="none" stroke={C.good} strokeWidth={16} strokeLinecap="round" strokeDasharray={`${L * (pct / 100) * ring} ${L}`} transform="rotate(-90 85 85)" />
          </svg>
          <div>
            <div style={{color: C.good, fontSize: 26, fontWeight: 800, letterSpacing: 2}}>ACCEPTANCE RATE</div>
            <div style={{fontSize: 84, fontWeight: 800, color: C.good, lineHeight: 1.05}}>{t('33,1%', '33.1%')}</div>
          </div>
        </Glass>
      </div>
      <div style={{...fade(c, 2), fontSize: 25, color: C.muted, lineHeight: 1.4}}>
        {t(<>Nguồn: trang bài #44 trên LeetCode, đọc ngày 28/10/2026 (hiển thị 967,654 / 2.9M · 33.1%). Đây là số <b style={{color: C.warn}}>lượt nộp bài</b>, không phải số người.</>,
           <>Source: LeetCode problem #44 page, read on 28 Oct 2026 (shown as 967,654 / 2.9M · 33.1%). These are <b style={{color: C.warn}}>submissions</b>, not people.</>)}
      </div>
    </div>
  );
};
