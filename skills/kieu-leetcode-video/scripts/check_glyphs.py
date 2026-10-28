#!/usr/bin/env python3
"""Fail if Vietnamese text/math in the episode lacks a font glyph."""
from pathlib import Path
import argparse, sys
from fontTools.ttLib import TTFont

def run(font, episode):
 sys.path.insert(0,str(episode.parent))
 from episode import S
 cmap=TTFont(font).getBestCmap()
 corpus='\n'.join((s.title+'\n'+s.phase+'\n'+'\n'.join(s.lines) if isinstance(s.lines,tuple) else s.title+'\n'+s.phase+'\n'+str(s.lines))+'\n'+s.script for s in S)
 corpus+=' ≤ ≥ ≠ → × • Đ ă ê ô ơ ư ạ ắ ễ ệ'
 missing=sorted({ch for ch in corpus if not ch.isspace() and ord(ch) not in cmap})
 if missing:
  print('FAIL font',font,'missing glyphs:', ' '.join(f'{c}(U+{ord(c):04X})' for c in missing))
  return 1
 print('PASS glyph coverage:',len(corpus),'characters;',len(set(corpus)),'distinct')
 return 0

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--font',required=True);p.add_argument('--episode',required=True,help='path to scripts/episode.py');a=p.parse_args()
 raise SystemExit(run(Path(a.font),Path(a.episode).resolve()))
