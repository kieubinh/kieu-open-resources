import React from 'react';
import {Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {SceneFrame} from './Frame';
import envelope from './envelope.json';
import anchor from './avatar.mouth.json';
import {SpeakingAvatar} from './SpeakingAvatar';
import {ensureFonts} from './theme';
import {SceneRow, makeCtx, timeline} from './timeline';
import {Constraints, Mission, Problem, Stats} from './visuals/intro';
import {Example1, Example2, Example3, Recap} from './visuals/examples';
import {Hints, Rules, Think} from './visuals/think';
import {Blowup, GreedyFail, Tree} from './visuals/search';
import {DP, Insight} from './visuals/dp';
import {Greedy, Pseudocode, Trace} from './visuals/greedy';
import {Code1, Code2} from './visuals/code';
import {Complexity, Lessons, Outro, Practice, Verify} from './visuals/wrap';
import {Ctx} from './timeline';

ensureFonts();

const VIEWS: Record<string, React.FC<{c: Ctx}>> = {
  mission: Mission, problem: Problem, constraints: Constraints, stats: Stats,
  ex1: Example1, ex2: Example2, ex3: Example3, recap: Recap,
  hints: Hints, think: Think, rules: Rules,
  tree: Tree, blowup: Blowup, greedy_fail: GreedyFail,
  dp: DP, insight: Insight,
  greedy: Greedy, trace: Trace, pseudocode: Pseudocode,
  code1: Code1, code2: Code2,
  verify: Verify, complexity: Complexity, lessons: Lessons, practice: Practice, outro: Outro,
};

const SceneView: React.FC<{scene: SceneRow}> = ({scene}) => {
  const f = useCurrentFrame();
  const c = makeCtx(scene, f);
  const View = VIEWS[scene.mode];
  if (!View) throw new Error(`No visual for mode ${scene.mode}`);
  return (
    <SceneFrame c={c}>
      <View c={c} />
    </SceneFrame>
  );
};

export const Episode: React.FC = () => (
  <>
    {timeline.scenes.map((scene) => (
      <Sequence key={scene.id} from={scene.fromFrame} durationInFrames={scene.frames} name={scene.id}>
        <SceneView scene={scene} />
        {scene.audio ? <Audio src={staticFile(scene.audio)} /> : null}
      </Sequence>
    ))}
    {envelope.levels.length>0&&<SpeakingAvatar levels={envelope.levels} mouthO={envelope.mouthO} mouthS={envelope.mouthS} anchor={anchor}/>}
  </>
);
