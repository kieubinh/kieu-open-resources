import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import timeline from './timeline.json';
import captions from './captions.json';
import envelope from './envelope.json';
import mouth from './mouth.json';
import anchor from './avatar.mouth.json';
import {SpeakingAvatar} from './SpeakingAvatar';
import {C, accent, sans, mono, clamp} from './theme';
import {IntroV, GrowthV, FlowV, StoryV, UsageV, ValueV, OutroV, VW, VH} from './artV';

/**
 * 1080 x 1920 YouTube Short. Safe zone (YouTube Shorts UI): keep content inside x 40..960 (buttons on the right) and
 * above y 1575 (title/channel overlay at the bottom). The speaking avatar sits bottom-right of that safe zone.
 */
type Scene = {id: string; phase: string; title: string; lines: string[]; script: string; fromFrame: number; frames: number;
  mode: string; silent: boolean; repo: string; beat: string; data: Record<string, any>; audio: string};

const X = 40, AVATAR = 190, AV_RIGHT = 120, AV_BOTTOM = 345;
const Y_TITLE = 236, Y_VISUAL = 450, Y_VISUAL_INTRO = 340, Y_CAPTION = 1205;

function Visual({s, frame}: {s: Scene; frame: number}) {
  const p = clamp(frame / Math.max(1, s.frames * 0.88)); // animations finish a little before the narration ends
  switch (s.mode) {
    case 'intro': return <IntroV data={s.data} p={p} />;
    case 'growth1': return <GrowthV data={s.data} note={s.lines[0]} p={p} />;
    case 'story': return <StoryV data={s.data} p={p} />;
    case 'flow': return <FlowV data={s.data} note={s.lines[0]} p={p} />;
    case 'usage': return <UsageV data={s.data} line={s.lines[0] ?? ''} p={p} />;
    case 'value': return <ValueV data={s.data} caveat={s.lines[0]} p={p} />;
    case 'outro': return <OutroV data={s.data} p={p} />;
    default: return null;
  }
}

function Subtitle({s, frame}: {s: Scene; frame: number}) {
  if (s.silent || !s.script) return null;
  const abs = s.fromFrame + frame;
  const cue = (captions as Array<{sceneId: string; fromFrame: number; toFrame: number; text: string}>)
    .find((c) => c.sceneId === s.id && c.fromFrame <= abs && c.toFrame > abs);
  if (!cue) return null;
  return <div style={{position: 'absolute', left: X, width: VW, top: Y_CAPTION, minHeight: 100, background: '#050e1be6', borderRadius: 22,
    textAlign: 'center', padding: '14px 24px', fontSize: 38, fontWeight: 700, lineHeight: 1.3, display: 'grid', placeItems: 'center'}}>{cue.text}</div>;
}

function SceneCard({s}: {s: Scene}) {
  const frame = useCurrentFrame();
  const progress = clamp(frame / Math.max(1, s.frames));
  const rise = interpolate(progress, [0, 0.05], [20, 0], {extrapolateRight: 'clamp'});
  const color = accent(s.data.color);
  const intro = s.mode === 'intro';
  return <AbsoluteFill style={{background: `radial-gradient(900px 700px at 90% -5%, #12335a66, transparent), ${C.bg}`, color: C.white, fontFamily: sans}}>
    <div style={{position: 'absolute', left: X, width: VW, top: 128, display: 'flex', justifyContent: 'space-between', fontSize: 31, alignItems: 'center'}}>
      <div><b style={{color: C.teal}}>KIEU STUDIO</b><span style={{color: C.muted}}> / GITHUB RADAR</span></div>
    </div>
    <div style={{position: 'absolute', left: X, width: VW, top: 178, height: 2, background: C.border}} />
    <div style={{position: 'absolute', left: X, width: VW, top: 192, fontSize: 27, color, letterSpacing: 0.8, fontWeight: 700}}>{s.phase}</div>
    {!intro && <h1 style={{position: 'absolute', left: X, width: VW, top: Y_TITLE, margin: 0, fontSize: 56, lineHeight: 1.16, letterSpacing: -0.6, maxHeight: 200,
      overflow: 'hidden', transform: `translateY(${rise}px)`}}>{s.title}</h1>}
    <div style={{position: 'absolute', left: X, width: VW, top: intro ? Y_VISUAL_INTRO : Y_VISUAL, height: VH}}><Visual s={s} frame={frame} /></div>
    <Subtitle s={s} frame={frame} />
    {!intro && <div style={{position: 'absolute', left: X, top: 1420, display: 'flex', alignItems: 'center', gap: 12, background: C.panel, border: `2px solid ${color}`, borderRadius: 18, padding: '10px 20px'}}>
      <span style={{fontFamily: mono, fontSize: 28, fontWeight: 800, color}}>{s.repo}</span></div>}
    <div style={{position: 'absolute', left: X, top: 1500, fontSize: 27, color: C.amber, fontWeight: 800}}>kieu.app</div>
    <div style={{position: 'absolute', left: X, width: VW, top: 1630, height: 6, background: C.border}}><div style={{width: `${progress * 100}%`, background: C.teal, height: 6}} /></div>
  </AbsoluteFill>;
}

export function GitHubRadarShort({faceVideo = null}: {faceVideo?: string | null}) {
  const scenes = timeline as Scene[];
  const env = envelope as Record<string, number[]>;
  const levels = React.useMemo(() => scenes.flatMap((s) => env[s.id] ?? new Array(s.frames).fill(0)), [scenes, env]);
  const mo = mouth as Record<string, {o: number[]; s: number[]}>;
  const mouthO = React.useMemo(() => scenes.flatMap((s) => mo[s.id]?.o ?? new Array(s.frames).fill(0)), [scenes, mo]);
  const mouthS = React.useMemo(() => scenes.flatMap((s) => mo[s.id]?.s ?? new Array(s.frames).fill(0.5)), [scenes, mo]);
  return <AbsoluteFill>
    {scenes.map((s) => <Sequence key={s.id} from={s.fromFrame} durationInFrames={s.frames}>
      <SceneCard s={s} />{s.audio && !s.silent && <Audio src={staticFile(s.audio)} />}
    </Sequence>)}
    <SpeakingAvatar levels={levels} mouthO={mouthO} mouthS={mouthS} anchor={anchor} faceVideo={faceVideo} diameter={AVATAR} right={AV_RIGHT} bottom={AV_BOTTOM} />
  </AbsoluteFill>;
}
