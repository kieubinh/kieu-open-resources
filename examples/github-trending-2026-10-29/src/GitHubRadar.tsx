import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import timeline from './timeline.json';
import captions from './captions.json';
import envelope from './envelope.json';
import mouth from './mouth.json';
import anchor from './avatar.mouth.json';
import {SpeakingAvatar} from './SpeakingAvatar';
import {C, accent, sans, clamp} from './theme';
import {RadarIntro, GrowthChart, FlowDiagram, StoryArt, UsageScene, ValueScale, IdeaTiles, OutroScene} from './art';

type Scene = {id: string; phase: string; title: string; lines: string[]; script: string; fromFrame: number; frames: number;
  mode: string; silent: boolean; repo: string; beat: string; data: Record<string, any>; audio: string};

function Visual({s, frame}: {s: Scene; frame: number}) {
  const p = clamp(frame / Math.max(1, s.frames * 0.88)); // animations finish a little before the narration ends
  switch (s.mode) {
    case 'intro': return <RadarIntro data={s.data} p={p} />;
    case 'growth1': return <GrowthChart data={s.data} note={s.lines[0]} p={p} />;
    case 'story': return <StoryArt data={s.data} p={p} />;
    case 'flow': return <FlowDiagram data={s.data} note={s.lines[0]} p={p} />;
    case 'usage': return <UsageScene data={s.data} line={s.lines[0] ?? ''} p={p} />;
    case 'value': return <ValueScale data={s.data} caveat={s.lines[0]} p={p} />;
    case 'ideas': return <IdeaTiles data={s.data} p={p} />;
    case 'outro': return <OutroScene data={s.data} q={s.title} p={p} />;
    default: return null;
  }
}

function Subtitle({s, frame}: {s: Scene; frame: number}) {
  if (s.silent || !s.script) return null;
  const abs = s.fromFrame + frame;
  const cue = (captions as Array<{sceneId: string; fromFrame: number; toFrame: number; text: string}>)
    .find((c) => c.sceneId === s.id && c.fromFrame <= abs && c.toFrame > abs);
  if (!cue) return null;
  return <div style={{position: 'absolute', left: 150, right: 330, bottom: 57, background: '#050e1bdc', borderRadius: 12, textAlign: 'center',
    minHeight: 54, padding: '14px 22px', fontSize: 29, fontWeight: 650, lineHeight: 1.34}}>{cue.text}</div>;
}

function SceneCard({s}: {s: Scene}) {
  const frame = useCurrentFrame();
  const progress = clamp(frame / Math.max(1, s.frames));
  const rise = interpolate(progress, [0, 0.05], [20, 0], {extrapolateRight: 'clamp'});
  const color = s.repo ? accent(s.data.color) : C.amber;
  const intro = s.mode === 'intro';
  return <AbsoluteFill style={{background: `radial-gradient(1200px 700px at 85% -10%, #12335a55, transparent), ${C.bg}`, color: C.white, fontFamily: sans}}>
    <div style={{position: 'absolute', left: 76, right: 76, top: 38, display: 'flex', justifyContent: 'space-between', fontSize: 27, alignItems: 'center'}}>
      <div><b style={{color: C.teal}}>KIEU STUDIO</b><span style={{color: C.muted}}> / GITHUB RADAR</span></div>
      <div style={{color: C.amber, fontWeight: 850}}>kieu.app</div></div>
    <div style={{position: 'absolute', left: 76, right: 76, top: 92, height: 2, background: C.border}} />
    <div style={{position: 'absolute', left: 76, right: 76, top: 112, fontSize: 25, color, letterSpacing: 0.8, fontWeight: 700}}>{s.phase}</div>
    {!intro && <h1 style={{position: 'absolute', left: 76, right: 76, top: 150, margin: 0, fontSize: 50, lineHeight: 1.16, letterSpacing: -0.8, maxHeight: 118,
      overflow: 'hidden', transform: `translateY(${rise}px)`}}>{s.title}</h1>}
    <div style={{position: 'absolute', left: 76, right: 76, top: intro ? 170 : 296, height: intro ? 620 : 500}}><Visual s={s} frame={frame} /></div>
    <Subtitle s={s} frame={frame} />
    <div style={{position: 'absolute', bottom: 22, left: 76, right: 76, height: 5, background: C.border}}><div style={{width: `${progress * 100}%`, background: C.teal, height: 5}} /></div>
  </AbsoluteFill>;
}

export function GitHubRadar({faceVideo = null}: {faceVideo?: string | null}) {
  const scenes = timeline as Scene[];
  const env = envelope as Record<string, number[]>;
  // One continuous speech-level track across the whole video so the avatar halo can look back a few frames.
  const levels = React.useMemo(() => scenes.flatMap((s) => env[s.id] ?? new Array(s.frames).fill(0)), [scenes, env]);
  const mo = mouth as Record<string, {o: number[]; s: number[]}>;
  const mouthO = React.useMemo(() => scenes.flatMap((s) => mo[s.id]?.o ?? new Array(s.frames).fill(0)), [scenes, mo]);
  const mouthS = React.useMemo(() => scenes.flatMap((s) => mo[s.id]?.s ?? new Array(s.frames).fill(0.5)), [scenes, mo]);
  return <AbsoluteFill>
    {scenes.map((s) => <Sequence key={s.id} from={s.fromFrame} durationInFrames={s.frames}>
      <SceneCard s={s} />{s.audio && !s.silent && <Audio src={staticFile(s.audio)} />}
    </Sequence>)}
    <SpeakingAvatar levels={levels} mouthO={mouthO} mouthS={mouthS} anchor={anchor} faceVideo={faceVideo} />
  </AbsoluteFill>;
}
