#!/usr/bin/env python3
"""Build the avatar tracks and speech-aligned subtitles of a LeetCode episode from its real narration WAVs.

Usage (after build_timeline.py wrote a VoiceStudio timeline, with KIEU_LANG set like that build):
  python3 make_av_tracks.py --project <episode dir> [--srt <output.srt>] [--captions]

Writes src/envelope.json: {levels, mouthO, mouthS}, one value per video frame of the whole video, measured from the
audio (the same articulation as examples/github-trending-*/scripts/make_envelope.py). Silent scenes stay at zero.
With --srt, every scene is transcribed by local VoiceStudio (cached in output/asr-<lang>/), script sentences are mapped
to the word timestamps, and an SRT plus output/asr_report-<lang>.json (word error rate per scene) are written.
--captions also rewrites src/captions.json, which the episode burns in. The script text stays the subtitle text.
"""
from __future__ import annotations
import argparse, difflib, importlib, json, os, re, subprocess, sys, urllib.request, uuid
from pathlib import Path
import numpy as np

FPS, SR, WIN = 30, 16000, 1024
BASE = os.environ.get('VOICESTUDIO_BASE', 'http://127.0.0.1:3900').rstrip('/')
HOLD = 0.6  # seconds a subtitle stays after its last word when no sentence follows


def load_wav(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def band(power, freqs, lo, hi):
    return power[:, (freqs >= lo) & (freqs < hi)].sum(axis=1)


def measure(path, frames):
    x = load_wav(path)
    hop = SR // FPS
    n = max(1, len(x) // hop)
    idx = np.arange(n)[:, None] * hop + np.arange(WIN)[None, :]
    power = np.abs(np.fft.rfft(np.pad(x, (WIN // 2, WIN))[idx] * np.hanning(WIN)[None, :], axis=1)) ** 2
    freqs = np.fft.rfftfreq(WIN, 1 / SR)
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    loud = np.clip(rms / (np.percentile(rms, 95) or 1e-6), 0, 1)
    total = band(power, freqs, 100, 4000) + 1e-9
    o = np.clip(loud ** 0.75 * (0.55 + 0.9 * band(power, freqs, 500, 1200) / total), 0, 1)
    o[loud < 0.07] = 0.0
    s = np.clip(band(power, freqs, 1800, 4000) / total * 5.5, 0, 1)
    fit = lambda a: np.pad(a, (0, max(0, frames - len(a))))[:frames]
    return fit(loud), fit(o), fit(s)


def smooth(values, attack, release):
    out, prev = np.zeros_like(values), 0.0
    for i, v in enumerate(values):
        prev += (v - prev) * (attack if v > prev else release)
        out[i] = prev
    return out


def transcribe(wav, cache, lang):
    if cache.is_file():
        return json.loads(cache.read_text())
    boundary = uuid.uuid4().hex
    field = lambda k, v: f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    body = b''.join([field('model', 'whisper-1'), field('language', lang), field('response_format', 'verbose_json'),
                     field('timestamp_granularities[]', 'word'),
                     f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode(),
                     wav.read_bytes(), f'\r\n--{boundary}--\r\n'.encode()])
    req = urllib.request.Request(BASE + '/v1/audio/transcriptions', data=body, method='POST',
                                 headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    data = json.loads(urllib.request.urlopen(req, timeout=600).read())
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(data, ensure_ascii=False))
    return data


def norm(word):
    return re.sub(r'[^0-9a-zà-ỹ]', '', word.lower())


def sentences(text):
    units = []
    for piece in re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ỹ0-9])', text.strip()):
        chunk = []
        for word in piece.split():
            if len(piece) >= 128 and chunk and sum(map(len, chunk)) + len(chunk) + len(word) > 103:
                units.append(' '.join(chunk)); chunk = []
            chunk.append(word)
        if chunk:
            units.append(' '.join(chunk))
    return units


def align(units, words, duration):
    """Script sentences -> (start, end) seconds. Words the ASR spelled differently are interpolated from their neighbours."""
    script = [norm(w) for u in units for w in u.split()]
    heard = [norm(w['word']) for w in words]
    matcher = difflib.SequenceMatcher(None, script, heard, autojunk=False)
    times = [None] * len(script)
    for a, b, size in matcher.get_matching_blocks():
        for k in range(size):
            times[a + k] = (words[b + k]['start'], words[b + k]['end'])
    known = [i for i, t in enumerate(times) if t]
    if not known:
        raise SystemExit('No script word was recognised; check this scene by ear.')
    starts = np.interp(range(len(script)), known, [times[i][0] for i in known])
    ends = np.interp(range(len(script)), known, [times[i][1] for i in known])
    out, at = [], 0
    for unit in units:
        n = len(unit.split())
        out.append((float(starts[at]), float(ends[at + n - 1]))); at += n
    return [(s, (out[i + 1][0] if i + 1 < len(out) else min(duration, e + HOLD))) for i, (s, e) in enumerate(out)]


def wer(script, heard):
    a, b = [norm(w) for w in script.split()], [norm(w) for w in heard.split()]
    matched = sum(m.size for m in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks())
    return round(1 - matched / max(1, len(a)), 3)


def timecode(seconds):
    ms = round(seconds * 1000)
    h, rem = divmod(ms, 3600000); m, rem = divmod(rem, 60000); s, ms = divmod(rem, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True, type=Path)
    ap.add_argument('--srt', type=Path)
    ap.add_argument('--captions', action='store_true')
    args = ap.parse_args()
    root = args.project.resolve()
    data = json.loads((root / 'src/timeline.json').read_text())
    rows = data['scenes'] if isinstance(data, dict) else data
    lang = os.environ.get('KIEU_LANG', 'vi')
    total = rows[-1]['fromFrame'] + rows[-1]['frames']
    levels, mouth_o, mouth_s = np.zeros(total), np.zeros(total), np.full(total, 0.5)
    for row in rows:
        if not row['audio']:
            continue
        loud, o, s = measure(root / 'public' / row['audio'], row['frames'])
        at, n = row['fromFrame'], row['frames']
        levels[at:at + n] = smooth(loud, 0.55, 0.55)
        mouth_o[at:at + n] = smooth(o, 0.75, 0.45)
        mouth_s[at:at + n] = smooth(s, 0.5, 0.5)
    (root / 'src/envelope.json').write_text(json.dumps(dict(
        levels=[round(float(v), 3) for v in levels], mouthO=[round(float(v), 2) for v in mouth_o],
        mouthS=[round(float(v), 2) for v in mouth_s])))
    print('envelope:', total, 'frames measured from', sum(bool(r['audio']) for r in rows), 'WAVs')
    if not args.srt:
        return
    sys.path.insert(0, str(root / 'scripts'))
    scenes = {s.id: s for s in importlib.import_module('episode').S}
    srt, cues, report = [], [], []
    for row in rows:
        if not row['audio']:
            continue
        scene = scenes[row['id']]
        script = scene.script if hasattr(scene, 'script') else ' '.join(b.spoken for b in scene.beats)
        asr = transcribe(root / 'public' / row['audio'], root / f'output/asr-{lang}/{row["id"]}.json', lang)
        report.append(dict(id=row['id'], wer=wer(script, asr['text']), heard=asr['text']))
        units = sentences(script)
        for unit, (start, end) in zip(units, align(units, asr['words'], row['frames'] / FPS)):
            a = row['fromFrame'] + round(start * FPS); b = row['fromFrame'] + round(end * FPS)
            cues.append(dict(sceneId=row['id'], fromFrame=a, toFrame=b, text=unit))
            srt.append(f'{len(cues)}\n{timecode(a / FPS)} --> {timecode(b / FPS)}\n{unit}\n')
    args.srt.parent.mkdir(parents=True, exist_ok=True)
    args.srt.write_text('\n'.join(srt), encoding='utf-8')
    if args.captions:
        (root / 'src/captions.json').write_text(json.dumps(cues, ensure_ascii=False, indent=2) + '\n')
    mean = sum(r['wer'] for r in report) / len(report)
    (root / f'output/asr_report-{lang}.json').write_text(json.dumps(dict(mean_wer=round(mean, 3), scenes=report), ensure_ascii=False, indent=2))
    print(f'subtitles: {len(cues)} cues, mean word error {mean:.3f}; worst:',
          sorted(((r['wer'], r['id']) for r in report), reverse=True)[:4])


if __name__ == '__main__':
    main()
