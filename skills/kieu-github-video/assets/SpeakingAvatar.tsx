import React from 'react';
import {Img, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';

/**
 * Kieu Studio presenter avatar: small circle, bottom-right, ringed like an AI voice assistant that is speaking.
 * Owner-approved geometry at 1920x1080: 220 px diameter, 64 px right/bottom margins, 4 px cyan (#72dce0) ring.
 *
 * Audio-driven tracks (one value per video frame, built from the real narration WAVs by scripts/make_envelope.py):
 *  - `levels`  speech loudness 0..1  -> halo rings, glow, head scale, equalizer pill
 *  - `mouthO` / `mouthS`  mouth opening 0..1 and lip spread 0..1 (0 = rounded o/u, 1 = wide i/e)
 *    -> a drawn mouth (SVG) over the mouthless face (`kieu-avatar-nomouth.png`), so the lips open, close, round and
 *       spread with the sound that is actually heard. Silence closes the lips.
 * This is audio-driven articulation of a drawn mouth, not a neural face model. For photoreal lip-sync pass `faceVideo`
 * (a silent 256x256 SadTalker video of the whole narration from scripts/make_lipsync.py): the face is then played from
 * that video and the drawn mouth is skipped; the halo, glow and equalizer still follow the audio.
 * While narration is silent (e.g. the 10-second thinking pause) the avatar stays idle: no halo, closed lips.
 */
const CYAN = '#72dce0';
const D = 220, RIGHT = 64, BOTTOM = 64, BORDER = 4;
export type MouthAnchor = {cx: number; cy: number; width: number; tilt: number};

const Mouth: React.FC<{o: number; s: number; a: MouthAnchor}> = ({o, s, a}) => {
  const hw = (a.width * (0.76 + 0.34 * s)) / 2;      // rounded (o/u) is narrower, spread (i/e) wider
  const H = o * 34 * (1.08 - 0.22 * s);              // opening in 512-px face space
  const c = -2 + (1 - s) * 1.2;                      // corner height: slight smile, flatter when rounded
  const top = `M ${-hw} ${c} C ${-hw * 0.5} ${-11} ${-hw * 0.18} ${-12.5} 0 ${-8.5} C ${hw * 0.18} ${-12.5} ${hw * 0.5} ${-11} ${hw} ${c}`;
  const outer = `${top} C ${hw * 0.55} ${13 + H} ${-hw * 0.55} ${13 + H} ${-hw} ${c} Z`;
  const inner = `M ${-hw + 6} ${c + 1} C ${-hw * 0.5} -1 ${hw * 0.5} -1 ${hw - 6} ${c + 1} C ${hw * 0.5} ${H + 3} ${-hw * 0.5} ${H + 3} ${-hw + 6} ${c + 1} Z`;
  const open = H > 1.4;
  return (
    <g transform={`translate(${a.cx},${a.cy + H * 0.1}) rotate(${a.tilt})`}>
      <path d={outer} fill="url(#lip)" stroke="#9a5560" strokeWidth={1.3} strokeOpacity={0.55} strokeLinejoin="round" />
      {open && <>
        <clipPath id="mouthClip"><path d={inner} /></clipPath>
        <path d={inner} fill="#3b161b" />
        <g clipPath="url(#mouthClip)">
          <rect x={-hw + 8} y={-0.5} width={2 * hw - 16} height={Math.min(H * 0.55 + 2, 12)} rx={3} fill="#f2ede7" />
          {H > 12 && <ellipse cx={0} cy={H + 1} rx={hw * 0.4} ry={Math.min(9, H * 0.38)} fill="#b4575f" />}
        </g>
        <path d={inner} fill="none" stroke="#7a3a42" strokeWidth={1.2} strokeOpacity={0.6} />
      </>}
      <path d={`M ${-hw + 2} ${c} C ${-hw * 0.5} 2.2 ${hw * 0.5} 2.2 ${hw - 2} ${c}`} fill="none" stroke="#8a4a54" strokeWidth={2.2}
        strokeLinecap="round" opacity={Math.max(0, 1 - H / 3)} />
      <ellipse cx={0} cy={8 + H} rx={hw * 0.3} ry={2.4} fill="#fff" opacity={0.2} />
    </g>
  );
};

export const SpeakingAvatar: React.FC<{
  levels: number[]; mouthO?: number[]; mouthS?: number[]; anchor?: MouthAnchor; faceVideo?: string | null; src?: string; mouthlessSrc?: string; diameter?: number;
}> = ({levels, mouthO, mouthS, anchor, faceVideo, src = 'brand/kieu-avatar.png', mouthlessSrc = 'brand/kieu-avatar-nomouth.png', diameter = D}) => {
  const frame = useCurrentFrame();
  const at = (arr: number[] | undefined, f: number) => (arr ? arr[Math.max(0, Math.min(arr.length - 1, f))] ?? 0 : 0);
  const level = at(levels, frame);
  const slow = (at(levels, frame - 4) + at(levels, frame - 8)) / 2;
  const speaking = level > 0.04 || slow > 0.04;
  const lip = !faceVideo && !!(mouthO && anchor);
  const k = diameter / D;
  const breathe = 1 + Math.sin(frame / 22) * 0.008;
  const bars = [0.55, 0.9, 1, 0.8, 0.5].map((w, i) => {
    const l = at(levels, frame - i * 2);
    return Math.max(0.12, Math.min(1, l * w * 1.15 + (speaking ? 0.08 : 0)));
  });
  return (
    <div style={{position: 'absolute', right: RIGHT * k, bottom: BOTTOM * k, width: D * k, height: D * k, zIndex: 20}}>
      {[{o: 16, a: slow}, {o: 34, a: at(levels, frame - 10) * 0.7}].map((h, i) => (
        <div key={i} style={{
          position: 'absolute', inset: -h.o * k, borderRadius: '50%', border: `${2 * k}px solid ${CYAN}`,
          opacity: speaking ? 0.12 + h.a * 0.55 : 0, transform: `scale(${1 + h.a * 0.06})`,
        }} />
      ))}
      <div style={{
        position: 'absolute', inset: 0, borderRadius: '50%', border: `${BORDER * k}px solid ${CYAN}`, overflow: 'hidden',
        background: '#071321', boxShadow: `0 0 ${(18 + level * 46) * k}px ${CYAN}${speaking ? '99' : '33'}, 0 10px 30px #0008`,
      }}>
        <div style={{position: 'absolute', inset: 0, transform: `scale(${(1.02 + level * 0.03) * breathe}) translateY(${-level * 2 * k}px)`}}>
          {faceVideo
            ? <OffthreadVideo src={staticFile(faceVideo)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
            : <Img src={staticFile(lip ? mouthlessSrc : src)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />}
          {lip && (
            <svg viewBox="0 0 512 512" width="100%" height="100%" style={{position: 'absolute', inset: 0}}>
              <defs><linearGradient id="lip" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#c27a82" /><stop offset="1" stopColor="#df9498" /></linearGradient></defs>
              <Mouth o={at(mouthO, frame)} s={at(mouthS, frame)} a={anchor!} />
            </svg>
          )}
        </div>
      </div>
      <div style={{
        position: 'absolute', left: '50%', bottom: -10 * k, transform: 'translateX(-50%)', height: 28 * k, padding: `0 ${12 * k}px`,
        borderRadius: 14 * k, background: '#071321f2', border: `${2 * k}px solid ${CYAN}`, display: 'flex', alignItems: 'center', gap: 4 * k,
      }}>
        {bars.map((b, i) => (
          <div key={i} style={{width: 4 * k, height: 18 * k * b, borderRadius: 2 * k, background: speaking ? CYAN : '#315675'}} />
        ))}
      </div>
    </div>
  );
};
