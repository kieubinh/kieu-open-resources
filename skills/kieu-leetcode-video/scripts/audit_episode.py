#!/usr/bin/env python3
"""Source and story structure QA; content verification still needs human review."""
from pathlib import Path
import argparse, sys, importlib.util, json

def official_example_count(path,override):
 # Count comes from --examples, else docs/SOURCE_MANIFEST.json next to scripts/; never guessed.
 if override:return override
 manifest=path.parent.parent/'docs/SOURCE_MANIFEST.json'
 if manifest.exists():return len(json.loads(manifest.read_text())['problem']['official_examples'])
 return None

def audit(path,examples=None):
 spec=importlib.util.spec_from_file_location('episode',path)
 mod=importlib.util.module_from_spec(spec);sys.modules['episode']=mod;spec.loader.exec_module(mod)
 scenes=mod.S;idset={s.id for s in scenes}
 count=official_example_count(path,examples)
 if count is None:print('FAIL official-example-count unknown: pass --examples N or add docs/SOURCE_MANIFEST.json');return 1
 modes=[s.mode for s in scenes]
 checks={
  'unique-scene-ids':len(idset)==len(scenes),
  'mission-first': scenes[0].mode=='mission' and 'studio' in (scenes[0].phase+' '+scenes[0].script).lower(),
  'one-10s-silent-pause':len([s for s in scenes if s.silent])==1 and abs(next(s.min_seconds for s in scenes if s.silent)-10)<1e-6,
  'hints-before-pause':any('hint' in s.id or 'hints' in s.mode for s in scenes[:next(i for i,s in enumerate(scenes) if s.silent)]),
  f'all-{count}-official-examples': all('ex'+str(k) in modes for k in range(1,count+1)),
  'examples-before-hints': 'hints' in modes and all(modes.index('ex'+str(k))<modes.index('hints') for k in range(1,count+1) if 'ex'+str(k) in modes),
  'has-python':any(s.mode in ('code1','code2') for s in scenes),
  'has-practice':any(s.mode=='practice' for s in scenes),
 }
 for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
 return 0 if all(checks.values()) else 1
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--episode',required=True)
 p.add_argument('--examples',type=int,help='official example count; default reads docs/SOURCE_MANIFEST.json');a=p.parse_args()
 raise SystemExit(audit(Path(a.episode).resolve(),a.examples))
