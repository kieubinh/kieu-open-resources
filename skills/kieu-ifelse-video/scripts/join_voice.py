#!/usr/bin/env python3
"""Join checked takes into the project voiceover: trim silence, speed the speech, add story pauses.

Usage: join_voice.py --episode DIR --out input/voiceover.wav
episode.json: voice.speed (atempo, applied once per take, so pauses keep their length), breaks (phrases that take a long
pause), gaps ({"042b.wav": 0.6}), mute ({"027.wav": [[6.74, 7.3]]}: stray sounds in take seconds, silenced, not cut, so a
fix never moves the timeline).
"""
import argparse, json, subprocess, wave
from pathlib import Path
import numpy as np


def tempo(x, sr, speed):
    if speed == 1.0: return x.copy()
    raw = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', 'pipe:0',
                          '-filter:a', f'atempo={speed}', '-f', 'f32le', 'pipe:1'], input=x.tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--episode', required=True); ap.add_argument('--out', required=True); a = ap.parse_args()
    ep = Path(a.episode); cfg = json.loads((ep / 'episode.json').read_text(encoding='utf-8')); speed = cfg['voice'].get('speed', 1.1)
    breaks, gaps, mute = cfg.get('breaks', []), cfg.get('gaps', {}), cfg.get('mute', {})
    ledger = json.loads((ep / 'audio/voice_ledger.json').read_text(encoding='utf-8')); parts = []; sr = None
    for name in sorted(ledger):
        with wave.open(str(ep / 'audio/chunks' / name)) as w:
            sr = w.getframerate(); ch = w.getnchannels(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        if ch > 1: x = x.reshape(-1, ch).mean(1)
        hop = int(sr * 0.01); e = np.sqrt(np.convolve(x * x, np.ones(hop) / hop, 'same')); on = np.where(e > 0.006)[0]
        i0, i1 = max(0, on[0] - int(sr * 0.03)), min(len(x), on[-1] + int(sr * 0.08)); x = tempo(x[i0:i1], sr, speed)
        for t0, t1 in mute.get(name, []):
            x[int((t0 * sr - i0) / speed):int((t1 * sr - i0) / speed)] = 0
        fade = int(sr * 0.012); x[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
        gap = gaps.get(name, 0.8 if any(s in ledger[name]['text'] for s in breaks) else 0.26)
        if parts: parts.append(np.zeros(int(sr * gap), np.float32))
        parts.append(x)
    y = np.concatenate([np.zeros(int(sr * 0.5), np.float32), *parts, np.zeros(int(sr * 0.5), np.float32)])
    with wave.open(a.out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    print('voiceover', round(len(y) / sr, 2), 's', len(ledger), 'chunks')


if __name__ == '__main__':
    main()
