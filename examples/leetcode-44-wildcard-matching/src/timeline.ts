import timelineJson from './timeline.json';
import traceJson from './data/trace.json';
import verificationJson from './data/verification.json';

export type Beat = {text: string; startFrame: number; endFrame: number; audioEndFrame: number; cue: unknown};
export type SceneRow = {
  id: string; phase: string; title: string; lines: string[]; mode: string; silent: boolean;
  fromFrame: number; frames: number; audio: string; beats: Beat[];
};
export type Timeline = {fps: number; preview: boolean; totalFrames: number; scenes: SceneRow[]};
export type Vars = {i: number | null; j: number | null; star: number | null; mark: number | null};
export type Step = Vars & {line: number; ret?: boolean};
export type EventRow = {kind: string; step: number; line: number; before: Vars; after: Vars};
export type Run = {s: string; p: string; result: boolean; steps: Step[]; events: EventRow[]; dp: boolean[][]; expected?: boolean; id?: number};
export type TreeNode = {id: number; i: number; j: number; how: string; children: number[]; result: boolean; why?: string; repeat: boolean; dup: boolean};
export type Trace = {
  source: {lines: string[]; firstLine: number; lineOf: Record<string, number>};
  official: Run[];
  main: Run;
  noBacktrack: {s: string; p: string; result: boolean; correct: boolean; events: {kind: string; before: {i: number; j: number}; after: {i: number; j: number}}[]};
  tree: {s: string; p: string; nodes: TreeNode[]; calls: number; distinctStates: number};
  blowup: {n: number; pattern: string; rows: {k: number; calls: number}[]};
};
export type Verification = {
  official: {s: string; p: string; expected: boolean; actual: boolean; pass: boolean}[];
  edge: {cases: number; failures: unknown[]};
  exhaustive: {cases: number; mismatches: number; max_s: number; max_p: number};
  random: {cases: number; mismatches: number; regex_checked: number};
  worst: {n: number; loop_iterations: number; seconds: number; answer: boolean};
  typical: {mean_iterations_per_char: number; max_iterations_per_char: number; cases: number; n: number};
  dp_cells: number;
  python: string;
};

export const timeline = timelineJson as unknown as Timeline;
export const trace = traceJson as unknown as Trace;
export const verification = verificationJson as unknown as Verification;

/** Scene-local view of "which narration beat is active" used by every visual. */
export type Ctx = {
  scene: SceneRow;
  f: number;            // frame inside the scene
  beat: number;         // index of the active beat (-1 before the first)
  bf: number;           // frames since the active beat started
  bp: number;           // 0..1 progress through the active beat's narration
  start: (i: number) => number;   // start frame of beat i
  since: (i: number) => number;   // frames since beat i started (negative before it)
  at: (i: number) => boolean;     // beat i has started
};

export function makeCtx(scene: SceneRow, f: number): Ctx {
  const beats = scene.beats;
  let beat = -1;
  for (let i = 0; i < beats.length; i++) if (f >= beats[i].startFrame) beat = i;
  const b = beat >= 0 ? beats[beat] : null;
  const span = b ? Math.max(1, b.audioEndFrame - b.startFrame) : 1;
  const bp = b ? Math.min(1, Math.max(0, (f - b.startFrame) / span)) : 0;
  const start = (i: number) => (beats[i] ? beats[i].startFrame : Number.MAX_SAFE_INTEGER / 4);
  return {scene, f, beat, bf: b ? f - b.startFrame : 0, bp, start, since: (i) => f - start(i), at: (i) => beat >= i};
}
