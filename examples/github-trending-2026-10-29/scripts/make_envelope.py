#!/usr/bin/env python3
"""Write the avatar's audio-driven tracks (30 fps, per scene):

  src/envelope.json  speech loudness 0..1          -> halo, glow, equalizer
  src/mouth.json     {o: mouth opening 0..1, s: lip spread 0..1 (0 = rounded o/u, 1 = wide i/e)}  -> lip-sync

With real WAVs both tracks are measured from the audio the viewer hears: opening follows loudness and the
low-vowel band (a/ă/â open, o/u/ô rounded), spread follows the high-frequency share (i/e/s/t wide). Silence closes
the lips. This is audio-driven articulation of a drawn mouth, not a neural face model; with --preview (no audio)
a deterministic syllable-like estimate is used and the report says so.
"""
from __future__ import annotations
import argparse, hashlib, json, math, subprocess
import numpy as np
from config import ROOT, AUDIO_DIR

FPS, SR = 30, 16000


def load_wav(path) -> np.ndarray:
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def band(power, freqs, lo, hi):
    sel = (freqs >= lo) & (freqs < hi)
    return power[:, sel].sum(axis=1)


def measure(path, frames):
    x = load_wav(path)
    hop, win = SR // FPS, 1024
    n = max(1, len(x) // hop)
    pad = np.pad(x, (win // 2, win))
    idx = np.arange(n)[:, None] * hop + np.arange(win)[None, :]
    seg = pad[idx] * np.hanning(win)[None, :]
    power = np.abs(np.fft.rfft(seg, axis=1)) ** 2
    freqs = np.fft.rfftfreq(win, 1 / SR)
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    peak = np.percentile(rms, 95) or 1e-6
    loud = np.clip(rms / peak, 0, 1)
    tot = band(power, freqs, 100, 4000) + 1e-9
    a_band = band(power, freqs, 500, 1200) / tot          # open vowels (a)
    hi_band = band(power, freqs, 1800, 4000) / tot        # spread vowels / sibilants (i, e, s)
    o = np.clip(loud ** 0.75 * (0.55 + 0.9 * a_band), 0, 1)
    o[loud < 0.07] = 0.0
    s = np.clip(hi_band * 5.5, 0, 1)
    fit = lambda a: np.pad(a, (0, max(0, frames - len(a))))[:frames]
    return fit(loud), fit(o), fit(s)


def estimated(script, frames):
    """Syllable-like rhythm (~4.5 Hz) with phrase pauses at punctuation; deterministic per script."""
    seed = int(hashlib.sha256(script.encode()).hexdigest()[:8], 16)
    n_speech = max(1, frames - 18)
    pauses = [round(i / max(1, len(script)) * n_speech) for i, ch in enumerate(script) if ch in ',.:;']
    loud, o, s = [], [], []
    for f in range(frames):
        if f >= n_speech or any(abs(f - p) < 4 for p in pauses):
            loud.append(0.0 if f >= n_speech else 0.05); o.append(0.0); s.append(0.5); continue
        t = f / FPS
        v = (0.5 + 0.5 * math.sin(2 * math.pi * 4.5 * t + (seed % 7))) * (0.65 + 0.35 * math.sin(2 * math.pi * 0.9 * t + (seed % 11)))
        loud.append(max(0.08, v)); o.append(max(0.1, v)); s.append(0.5 + 0.45 * math.sin(2 * math.pi * 1.7 * t + (seed % 5)))
    return np.array(loud), np.array(o), np.array(s)


def smooth(v, attack, release):
    out, prev = np.zeros_like(v), 0.0
    for i, x in enumerate(v):
        prev = prev + (x - prev) * (attack if x > prev else release)
        out[i] = prev
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preview', action='store_true'); args = ap.parse_args()
    timeline = json.loads((ROOT / 'src/timeline.json').read_text())
    env, mouth, kind = {}, {}, 'estimated' if args.preview else 'measured'
    for row in timeline:
        frames = row['frames']
        if row['silent'] or not row['script']:
            z = [0.0] * frames; env[row['id']] = z; mouth[row['id']] = {'o': z, 's': [0.5] * frames}; continue
        loud, o, s = estimated(row['script'], frames) if args.preview else measure(AUDIO_DIR / (row['id'] + '.wav'), frames)
        env[row['id']] = [round(float(v), 3) for v in smooth(loud, 0.55, 0.55)]
        mouth[row['id']] = {'o': [round(float(v), 2) for v in smooth(o, 0.75, 0.45)], 's': [round(float(v), 2) for v in smooth(s, 0.5, 0.5)]}
    (ROOT / 'src/envelope.json').write_text(json.dumps(env))
    (ROOT / 'src/mouth.json').write_text(json.dumps(mouth))
    (ROOT / 'output/envelope_report.json').write_text(json.dumps(dict(kind=kind, scenes=len(env), lipsync='audio-driven drawn mouth'), indent=2))
    print(f'envelope + mouth: {len(env)} scenes ({kind})')


if __name__ == '__main__':
    main()
