#!/usr/bin/env python3
"""Strict local VoiceStudio API adapter; validates voice ID and WAV bytes, caches by input hash."""
from __future__ import annotations
import argparse, hashlib, json, os, urllib.request, urllib.error, wave
from pathlib import Path
from episode import S
from config import AUDIO_DIR
BASE=os.environ.get('VOICESTUDIO_BASE','http://127.0.0.1:3900').rstrip('/')


def request(path,payload=None):
    if not (BASE.startswith('http://127.0.0.1:') or BASE.startswith('http://localhost:')):
        raise RuntimeError('Only a local VoiceStudio endpoint is permitted')
    req=urllib.request.Request(BASE+path,
        data=json.dumps(payload,ensure_ascii=False).encode('utf-8') if payload is not None else None,
        headers={'Content-Type':'application/json','Accept':'audio/wav' if payload else 'application/json'},
        method='POST' if payload else 'GET')
    with urllib.request.urlopen(req,timeout=180 if payload else 7) as result:
        raw=result.read()
    return raw if payload is not None else json.loads(raw)


def main():
    p=argparse.ArgumentParser(); group=p.add_mutually_exclusive_group(required=True)
    for flag in ['--check','--voices','--synthesize']:group.add_argument(flag,action='store_true')
    args=p.parse_args()
    if args.check:
        print(json.dumps(request('/health'),ensure_ascii=False));return
    response=request('/v1/audio/voices')
    voices=response.get('data',response.get('voices',[])) if isinstance(response,dict) else response
    if args.voices:
        print(json.dumps(voices,ensure_ascii=False,indent=2));return
    selected=os.environ.get('VOICESTUDIO_VOICE_PROFILE','').strip()
    ids={str(x.get('id',x.get('voice_id'))) for x in voices if isinstance(x,dict)}
    if not selected or selected not in ids:raise RuntimeError('Set VOICESTUDIO_VOICE_PROFILE to an ID listed by --voices')
    model=os.environ.get('VOICESTUDIO_MODEL','tts-1')
    dest=AUDIO_DIR;dest.mkdir(parents=True,exist_ok=True)
    for scene in S:
        if scene.silent:continue
        path=dest/(scene.id+'.wav');meta=dest/(scene.id+'.json')
        digest=hashlib.sha256(json.dumps(dict(text=scene.script,voice=selected,model=model),ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        if path.exists() and meta.exists() and json.loads(meta.read_text()).get('sha256')==digest:
            print('cached',scene.id);continue
        blob=request('/v1/audio/speech',dict(model=model,voice=selected,input=scene.script,response_format='wav'))
        if blob[:4]!=b'RIFF' or blob[8:12]!=b'WAVE':raise RuntimeError(scene.id+': invalid WAV signature')
        path.write_bytes(blob)
        with wave.open(str(path),'rb') as w:
            seconds=w.getnframes()/w.getframerate()
            if seconds<0.5:raise RuntimeError(scene.id+': short WAV')
        meta.write_text(json.dumps(dict(sha256=digest,seconds=seconds,voice=selected,model=model,engine='VoiceStudio local'),ensure_ascii=False,indent=2))
        print('generated',scene.id,round(seconds,2))
    print('VoiceStudio WAV generated. Review every scene, then npm run render:release')

if __name__=='__main__':
    try:main()
    except (RuntimeError,urllib.error.URLError) as e:raise SystemExit('VOICE GATE BLOCKED; no fallback: '+str(e))
