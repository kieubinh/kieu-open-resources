#!/usr/bin/env python3
"""Source, captions, font, binary and video review QA (release requires listening)."""
from __future__ import annotations
import json,subprocess,sys,re,os,hashlib
from pathlib import Path
try:
 from fontTools.ttLib import TTFont
except ImportError:
 raise SystemExit('fontTools missing: python3 -m pip install fonttools')
sys.path.insert(0,str(Path(__file__).resolve().parent))
from config import ROOT,OUT_PREFIX,REVIEW_MP4,AUDIO_DIR,find_font
from episode import S
FPS=30
REPORT={}

def record(key,passed,notes=''):
 REPORT[key]={'status':'PASS' if passed else 'FAIL','notes':notes}; print(REPORT[key]['status'],key,notes)

def run():
 scenes=json.loads((ROOT/'src/timeline.json').read_text())
 cues=json.loads((ROOT/'src/captions.json').read_text())
 report=json.loads((ROOT/'output/timeline_report.json').read_text())
 record('official_examples',any(s.mode=='ex1' for s in S) and any(s.mode=='ex2' for s in S),'2/2 official example modes')
 record('unique_ids',len(set(s.id for s in S))==len(S))
 record('single_10_seconds_silent',len([s for s in scenes if s['silent']])==1 and all(s['frames']==300 and not s['audio'] for s in scenes if s['silent']),'300 frames at source 30fps')
 record('duration_18_to_25_minutes',18*60<=report['seconds']<=25*60,str(report['seconds']))
 record('subtitle_timing', all(c['fromFrame']<c['toFrame'] and 0<=c['fromFrame']<report['frames'] for c in cues))
 pause=next(s for s in scenes if s['silent'])
 record('pause_has_no_captions',not any(c['fromFrame']<pause['fromFrame']+300 and c['toFrame']>pause['fromFrame'] for c in cues),'10 sec silent visual countdown')
 fonts=[]
 for kind in ('REGULAR','BOLD'):
  try:fonts.append(find_font(kind))
  except RuntimeError as e:record('font_found_'+kind.lower(),False,str(e))
 corpus='\n'.join(s.phase+' '+s.title+' '+' '.join(s.lines)+' '+s.script for s in S) + '≤≥≠→×∞−•Đăêôơưạắễệ⁶'
 for font in fonts:
  cmap=TTFont(font,fontNumber=0).getBestCmap();missing=sorted({f'U+{ord(c):04X}({c})' for c in corpus if not c.isspace() and ord(c) not in cmap})
  record('font_glyphs_'+Path(font).stem,len(missing)==0,('missing '+','.join(missing)) if missing else f'{len(set(corpus))} distinct characters')
 video=ROOT/'output'/REVIEW_MP4
 if video.exists():
  info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate','-of','json',str(video)]))
  vs=[s for s in info['streams'] if s['codec_type']=='video']
  aus=[s for s in info['streams'] if s['codec_type']=='audio']
  dur=float(info['format']['duration'])
  record('review_video_decodes',bool(vs) and vs[0]['codec_name']=='h264',f'{len(vs)} video stream(s)')
  record('review_runtime',abs(dur-report['seconds'])<=.26,f'output={dur:.3f}s timeline={report["seconds"]:.3f}s')
  record('review_codec_dimensions',bool(vs) and vs[0]['width']==1280 and vs[0]['height']==720,'1280×720, 2fps offline storyboard')
  REPORT['remotion_final_render']={'status':'NOT RUN','notes':'@remotion/cli unavailable; offline storyboard is not Remotion output'}
  REPORT['audio_validity']={'status':'BLOCKED','notes':f'VoiceStudio unavailable; {len(aus)} audio streams in review'}
 else:
  REPORT['review_video_decodes']={'status':'NOT RUN','notes':'Review MP4 missing'}
 voice_files=list(AUDIO_DIR.glob('*.wav'))
 REPORT['voicestudio_synthesis']={'status':'BLOCKED' if len(voice_files)!=len(S)-1 else 'PENDING REVIEW','notes':f'{len(voice_files)}/{len(S)-1} scene WAVs'}
 REPORT['audio_caption_alignment']={'status':'NOT RUN','notes':'Requires native VoiceStudio WAV and listening / forced alignment'}
 REPORT['visual_editorial_review']={'status':'NOT RUN','notes':'Contact sheet is automated; full human inspection required'}
 REPORT['release_status']={'status':'REVIEW ONLY','notes':'Do not publish as final. No VoiceStudio audio nor Remotion release render.'}
 (ROOT/'output/QA_results.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n')
 return all(v['status']=='PASS' for k,v in REPORT.items() if k not in ['voicestudio_synthesis','audio_caption_alignment','visual_editorial_review','remotion_final_render','audio_validity','release_status'])

if __name__=='__main__':
 raise SystemExit(0 if run() else 1)
