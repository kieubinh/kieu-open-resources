#!/usr/bin/env python3
"""Build the frame-aligned Remotion timeline (src/timeline.json) and subtitle files.

Release mode reads the real scene WAVs + audio_manifest/*.json written by voicestudio.py and fails
if any is missing or stale. ``--preview`` produces a SILENT editing timeline with *estimated*
durations (never publishable). The 10-second thinking pause is always exactly 300 frames and
carries no audio and no subtitle.
"""
import argparse
import json
import math
import wave
from pathlib import Path

from episode import PAUSE_ID, S
from voicestudio import AUDIO, AUDIO_SLUG, FPS, LANGUAGE as LANG, MANIFEST, RATE, SAMPLES_PER_FRAME, digest, scene_layout

ROOT = Path(__file__).resolve().parents[1]
PUBLISH = ROOT / "publish"
PAUSE_FRAMES = 10 * FPS
SUBTITLE_HOLD = 36  # frames (1.2 s) to keep a subtitle after its sentence ends, so it can be read to the end


def estimate_seconds(text):
    return max(1.6, len(text) * 0.07)


def preview_scene(index, scene):
    if scene.silent:
        return PAUSE_FRAMES, "", [], None
    lead, tail = scene_layout(index)
    t, beats = lead, []
    for k, beat in enumerate(scene.beats):
        if k:
            t += 0.25
        end = t + estimate_seconds(beat.spoken)
        beats.append((t, end, beat))
        t = end
    t += tail
    return math.ceil(t * FPS), "", beats, None


def release_scene(index, scene):
    if scene.silent:
        return PAUSE_FRAMES, "", [], None
    wav, meta_path = AUDIO / f"{scene.id}.wav", MANIFEST / f"{scene.id}.json"
    if not wav.is_file() or not meta_path.is_file():
        raise SystemExit(f"Missing VoiceStudio audio for {scene.id}: run voice:generate (no fallback voice is used).")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    identity = {"id": meta["voice"], "seed": meta["seed"]}
    from voicestudio import MODEL, LANGUAGE
    for k, beat in enumerate(scene.beats):
        expected = digest({"voice": identity["id"], "seed": identity["seed"], "model": meta["model"],
                           "lang": LANGUAGE, "text": beat.spoken})
        if meta["beats"][k]["key"] != expected:
            raise SystemExit(f"Stale audio for {scene.id} beat {k + 1}: narration text/profile changed; regenerate.")
    if len(meta["beats"]) != len(scene.beats):
        raise SystemExit(f"Stale audio for {scene.id}: beat count changed.")
    with wave.open(str(wav), "rb") as w:
        if (w.getframerate(), w.getnchannels(), w.getsampwidth()) != (RATE, 1, 2):
            raise SystemExit(f"{wav.name}: expected 48 kHz mono 16-bit PCM")
        samples = w.getnframes()
    if samples % SAMPLES_PER_FRAME:
        raise SystemExit(f"{wav.name}: duration is not a whole number of video frames")
    beats = [(m["start"], m["end"], beat) for m, beat in zip(meta["beats"], scene.beats)]
    return samples // SAMPLES_PER_FRAME, f"audio/{AUDIO_SLUG}/{scene.id}.wav", beats, meta


def fmt(ts, sep):
    ms = round(ts * 1000)
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"


def wrap_two_lines(text, limit=46):
    if len(text) <= limit:
        return text
    words, best = text.split(" "), None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        score = abs(len(a) - len(b))
        if best is None or score < best[0]:
            best = (score, a, b)
    return best[1] + "\n" + best[2]


def main(preview):
    rows, at, cues = [], 0, []
    for index, scene in enumerate(S):
        frames, audio, beats, meta = (preview_scene if preview else release_scene)(index, scene)
        beat_rows = []
        for k, (start, end, beat) in enumerate(beats):
            sf = round(start * FPS)
            ef = round(end * FPS) + SUBTITLE_HOLD
            if k + 1 < len(beats):
                ef = min(ef, round(beats[k + 1][0] * FPS))
            ef = min(ef, frames)
            beat_rows.append({"text": beat.text, "startFrame": sf, "endFrame": ef, "audioEndFrame": round(end * FPS), "cue": beat.cue})
            cues.append((at + sf, at + ef, beat.text))
        rows.append({"id": scene.id, "phase": scene.phase, "title": scene.title, "lines": list(scene.lines),
                     "mode": scene.mode, "silent": scene.silent, "fromFrame": at, "frames": frames,
                     "audio": audio, "beats": beat_rows})
        at += frames
    dest = ROOT / "src/timeline.json"
    dest.write_text(json.dumps({"fps": FPS, "lang": LANG, "preview": preview, "totalFrames": at, "scenes": rows},
                               ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Timeline: {len(rows)} scenes, {at} frames = {at / FPS:.1f} s ({'PREVIEW / SILENT / ESTIMATED' if preview else 'VoiceStudio audio'})")
    if not preview:
        PUBLISH.mkdir(exist_ok=True)
        srt, vtt = [], ["WEBVTT", ""]
        for n, (a, b, text) in enumerate(cues, 1):
            body = wrap_two_lines(text)
            srt += [str(n), f"{fmt(a / FPS, ',')} --> {fmt(b / FPS, ',')}", body, ""]
            vtt += [f"{fmt(a / FPS, '.')} --> {fmt(b / FPS, '.')}", body, ""]
        (PUBLISH / f"subtitles.{LANG}.srt").write_text("\n".join(srt), encoding="utf-8")
        (PUBLISH / f"subtitles.{LANG}.vtt").write_text("\n".join(vtt), encoding="utf-8")
        print(f"Subtitles: {len(cues)} cues -> publish/subtitles.{LANG}.srt / .vtt")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="silent editing timeline with estimated durations (NOT publishable)")
    main(ap.parse_args().preview)
