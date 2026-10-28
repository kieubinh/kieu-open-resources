#!/usr/bin/env python3
"""Source and story structure QA; content verification still needs human review."""
from pathlib import Path
import argparse, sys, importlib.util

def audit(path):
 spec=importlib.util.spec_from_file_location('episode',path)
 mod=importlib.util.module_from_spec(spec);sys.modules['episode']=mod;spec.loader.exec_module(mod)
 scenes=mod.S;idset={s.id for s in scenes}
 checks={
  'unique-scene-ids':len(idset)==len(scenes),
  'mission-first': scenes[0].mode=='mission' and 'studio' in (scenes[0].phase+' '+scenes[0].script).lower(),
  'one-10s-silent-pause':len([s for s in scenes if s.silent])==1 and abs(next(s.min_seconds for s in scenes if s.silent)-10)<1e-6,
  'hints-before-pause':any('hint' in s.id or 'hints' in s.mode for s in scenes[:next(i for i,s in enumerate(scenes) if s.silent)]),
  'examples-1-2-3': all(any(s.mode=='ex'+str(k) for s in scenes) for k in [1,2,3]),
  'has-python':any(s.mode in ('code1','code2') for s in scenes),
  'has-practice':any(s.mode=='practice' for s in scenes),
 }
 for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
 return 0 if all(checks.values()) else 1
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--episode',required=True);a=p.parse_args()
 raise SystemExit(audit(Path(a.episode).resolve()))
