#!/usr/bin/env python3
"""Produce the Remotion timeline and SRT; never release without per-scene VoiceStudio WAVs."""
from __future__ import annotations
import argparse, json, math, re, wave
from episode import S
from config import ROOT, AUDIO_DIR as AUD, AUDIO_URL, OUT_PREFIX, TAIL_SECONDS, RUNTIME_MIN_MAX_SECONDS, VIDEO_SPEED
FPS = 30


def subunits(text):
    pieces = re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ỹ0-9])', text.strip())
    units = []
    for piece in pieces:
        if len(piece) < 120:
            units.append(piece); continue
        chunk = []
        for word in piece.split():
            if sum(map(len, chunk)) + len(chunk) + len(word) > 100 and chunk:
                units.append(' '.join(chunk)); chunk = []
            chunk.append(word)
        if chunk:
            units.append(' '.join(chunk))
    return [u for u in units if u]


def timecode(seconds):
    ms = round(seconds * 1000)
    h, rem = divmod(ms, 3600000); m, rem = divmod(rem, 60000); s, ms = divmod(rem, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def make(preview=True):
    at, rows, subs, cues, i = 0, [], [], [], 0
    for scene in S:
        audio = ''
        if scene.silent:
            frames = 10 * FPS
        elif preview:
            # Vietnamese words are syllables: ~4.3 per second at 1.0x narration (estimate only).
            frames = round((len(scene.script.split()) / (4.3 * VIDEO_SPEED) + TAIL_SECONDS) * FPS)
        else:
            wav = AUD / (scene.id + '.wav')
            if not wav.exists():
                raise RuntimeError('VoiceStudio WAV missing: ' + str(wav))
            with wave.open(str(wav), 'rb') as w:
                frames = math.ceil((w.getnframes() / w.getframerate() + TAIL_SECONDS) * FPS)
            audio = f'{AUDIO_URL}/{scene.id}.wav'
        rows.append(dict(id=scene.id, phase=scene.phase, title=scene.title, lines=list(scene.lines), script=scene.script,
                         fromFrame=at, frames=frames, mode=scene.mode, silent=scene.silent, repo=scene.repo,
                         beat=scene.beat, data=scene.data, audio=audio))
        units = subunits(scene.script) if scene.script else []
        if units:
            total, cursor, usable = sum(len(u) for u in units), at, frames - 9
            for n, u in enumerate(units):
                end = at + frames - 2 if n == len(units) - 1 else min(at + frames - 2, cursor + max(1, round(usable * len(u) / total)))
                i += 1
                subs.append(f'{i}\n{timecode(cursor / FPS)} --> {timecode(end / FPS)}\n{u}\n')
                cues.append(dict(sceneId=scene.id, fromFrame=cursor, toFrame=end, text=u))
                cursor = end
        at += frames
    duration = at / FPS
    lo, hi = RUNTIME_MIN_MAX_SECONDS
    if not lo <= duration <= hi:
        raise RuntimeError(f'Target runtime {lo // 60}–{hi // 60} min violated: {duration:.1f}s')
    (ROOT / 'src/timeline.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'src/captions.json').write_text(json.dumps(cues, ensure_ascii=False, indent=2) + '\n')
    name = 'REVIEW_ESTIMATED' if preview else 'VOICESTUDIO_ESTIMATED'
    (ROOT / f'output/{OUT_PREFIX}_{name}.srt').write_text('\n'.join(subs), encoding='utf-8')
    (ROOT / 'output/timeline_report.json').write_text(json.dumps(dict(
        preview=preview, scenes=len(rows), frames=at, fps=FPS, seconds=duration, minutes=duration / 60,
        audio_segments=sum(bool(r['audio']) for r in rows)), indent=2))
    print(f'{len(rows)} scenes, {duration:.1f}s ({duration / 60:.2f} min), {at} frames, {"REVIEW / SILENT" if preview else "VoiceStudio"}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--preview', action='store_true')
    make(ap.parse_args().preview)
