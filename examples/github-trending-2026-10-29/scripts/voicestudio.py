#!/usr/bin/env python3
"""Strict local VoiceStudio adapter for GitHub Radar.

Raw TTS is cached unsped in public/audio/<slug>/raw/. Speed defaults to 1.0x; any other speed (atempo, pitch preserved)
is applied exactly once with FFmpeg to produce the scene WAV that ASR, captions and the render use.
Refuses non-local endpoints and voice IDs VoiceStudio does not list; never falls back to other TTS.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, urllib.request, urllib.error, wave
from episode import S
from config import AUDIO_DIR, RAW_DIR, DEFAULT_VOICE, VIDEO_SPEED

BASE = os.environ.get('VOICESTUDIO_BASE', 'http://127.0.0.1:3900').rstrip('/')


def request(path, payload=None):
    if not (BASE.startswith('http://127.0.0.1:') or BASE.startswith('http://localhost:')):
        raise RuntimeError('Only a local VoiceStudio endpoint is permitted')
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload is not None else None,
        headers={'Content-Type': 'application/json', 'Accept': 'audio/wav' if payload else 'application/json'},
        method='POST' if payload else 'GET')
    with urllib.request.urlopen(req, timeout=1800 if payload else 7) as result:
        raw = result.read()
    return raw if payload is not None else json.loads(raw)


def _wav_seconds(path):
    with wave.open(str(path), 'rb') as w:
        return w.getnframes() / w.getframerate()


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    for flag in ['--check', '--voices', '--synthesize']:
        g.add_argument(flag, action='store_true')
    p.add_argument('--only', help='comma separated scene ids (e.g. a quick sample)')
    args = p.parse_args()
    if args.check:
        print(json.dumps(request('/health'), ensure_ascii=False)); return
    response = request('/v1/audio/voices')
    voices = response.get('voices', response.get('data', [])) if isinstance(response, dict) else response
    if args.voices:
        print(json.dumps(voices, ensure_ascii=False, indent=2)); return
    selected = os.environ.get('VOICESTUDIO_VOICE_PROFILE', DEFAULT_VOICE).strip()
    ids = {str(x.get('voice_id', x.get('id'))) for x in voices if isinstance(x, dict)}
    if selected not in ids:
        raise RuntimeError('Voice profile is not listed by --voices: ' + selected)
    model = os.environ.get('VOICESTUDIO_MODEL', 'tts-1')
    only = set(args.only.split(',')) if args.only else None
    AUDIO_DIR.mkdir(parents=True, exist_ok=True); RAW_DIR.mkdir(parents=True, exist_ok=True)
    for scene in S:
        if scene.silent or (only and scene.id not in only):
            continue
        raw, final, meta = RAW_DIR / (scene.id + '.wav'), AUDIO_DIR / (scene.id + '.wav'), AUDIO_DIR / (scene.id + '.json')
        digest = hashlib.sha256(json.dumps(dict(text=scene.script, voice=selected, model=model, speed=VIDEO_SPEED),
                                           ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if final.exists() and meta.exists() and json.loads(meta.read_text()).get('sha256') == digest:
            print('cached', scene.id); continue
        raw_digest = hashlib.sha256(json.dumps(dict(text=scene.script, voice=selected, model=model),
                                               ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        raw_meta = RAW_DIR / (scene.id + '.json')
        if not (raw.exists() and raw_meta.exists() and json.loads(raw_meta.read_text()).get('sha256') == raw_digest):
            blob = request('/v1/audio/speech', dict(model=model, voice=selected, input=scene.script, response_format='wav'))
            if blob[:4] != b'RIFF' or blob[8:12] != b'WAVE':
                raise RuntimeError(scene.id + ': invalid WAV signature')
            raw.write_bytes(blob)
            if _wav_seconds(raw) < 0.5:
                raise RuntimeError(scene.id + ': short WAV')
            raw_meta.write_text(json.dumps(dict(sha256=raw_digest), indent=2))
        tempo = [] if VIDEO_SPEED == 1.0 else ['-filter:a', f'atempo={VIDEO_SPEED}']   # applied once, never twice
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(raw), *tempo,
                        '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', str(final)], check=True)
        seconds = _wav_seconds(final)
        meta.write_text(json.dumps(dict(sha256=digest, seconds=seconds, voice=selected, model=model,
                                        speed=VIDEO_SPEED, engine='VoiceStudio local'), ensure_ascii=False, indent=2))
        print('generated', scene.id, round(seconds, 2))
    print('VoiceStudio WAV generated. Listen to every scene before render:release.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError) as e:   # OSError covers URLError and socket.timeout
        raise SystemExit('VOICE GATE BLOCKED; no fallback: ' + str(e))
