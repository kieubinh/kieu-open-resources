#!/usr/bin/env python3
"""Produce a Remotion timeline and estimated SRT; never release without per-scene VoiceStudio WAVs."""
from __future__ import annotations
import argparse, json, re, wave, math
from pathlib import Path
from episode import S
from config import ROOT, AUDIO_DIR as AUD, AUDIO_URL, OUT_PREFIX
FPS=30

def subunits(text):
    # Sentence boundaries are safer than splitting arbitrary grapheme clusters.
    pieces=re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ỹ0-9])',text.strip())
    units=[]
    for piece in pieces:
        if len(piece)<128:units.append(piece);continue
        words=piece.split(); chunk=[]
        for word in words:
            if sum(map(len,chunk))+len(chunk)+len(word)>103 and chunk:
                units.append(' '.join(chunk));chunk=[]
            chunk.append(word)
        if chunk:units.append(' '.join(chunk))
    return [v for v in units if v]

def timecode(seconds):
    millis=round(seconds*1000)
    h,rem=divmod(millis,3600000);m,rem=divmod(rem,60000);s,ms=divmod(rem,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def make(preview=True):
    at=0;rows=[];subs=[];cues=[];i=0
    for scene in S:
        audio=''
        if scene.silent:
            frames=10*FPS
        elif preview:
            frames=round(scene.min_seconds*0.95*FPS)
        else:
            wav=AUD/(scene.id+'.wav')
            if not wav.exists():raise RuntimeError('VoiceStudio WAV missing: '+str(wav))
            with wave.open(str(wav),'rb') as w:
                frames=math.ceil((w.getnframes()/w.getframerate()+0.6)*FPS)
            audio=f'{AUDIO_URL}/{scene.id}.wav'
        rows.append(dict(id=scene.id,phase=scene.phase,title=scene.title,lines=list(scene.lines),
            script=scene.script,fromFrame=at,frames=frames,mode=scene.mode,
            silent=scene.silent,trace=scene.trace,audio=audio))
        if scene.script:
            units=subunits(scene.script)
            if units:
                allchars=sum(len(u) for u in units)
                frac=at
                usable=frames-9
                for n,u in enumerate(units):
                    start=frac
                    delta=max(1,round(usable*len(u)/allchars))
                    end=min(at+frames-2,start+delta)
                    if n==len(units)-1:end=at+frames-2
                    i+=1
                    subs.append(f'{i}\n{timecode(start/FPS)} --> {timecode(end/FPS)}\n{u}\n')
                    cues.append(dict(sceneId=scene.id,fromFrame=start,toFrame=end,text=u))
                    frac=end
        at+=frames
    duration=at/FPS
    if not 18*60 <= duration <=25*60:raise RuntimeError(f'Target runtime 18–25min violated: {duration:.2f}s')
    out=ROOT/'src/timeline.json'
    out.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'src/captions.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2)+'\n')
    (ROOT/f'output/{OUT_PREFIX}_REVIEW_ESTIMATED.srt' if preview else ROOT/f'output/{OUT_PREFIX}_VOICESTUDIO_ESTIMATED.srt').write_text('\n'.join(subs),encoding='utf-8')
    (ROOT/'output/timeline_report.json').write_text(json.dumps(dict(preview=preview,scenes=len(rows),frames=at,
        fps=FPS,seconds=duration,minutes=duration/60,silent=[dict(id=x['id'],start=x['fromFrame']/FPS,seconds=x['frames']/FPS) for x in rows if x['silent']],audio_segments=sum(bool(x['audio']) for x in rows)),indent=2))
    print(f'{len(rows)} scenes, {duration:.2f}s, {at} frames, {"REVIEW / SILENT" if preview else "VoiceStudio"}')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');args=p.parse_args()
    make(args.preview)
