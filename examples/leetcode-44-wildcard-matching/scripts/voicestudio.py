#!/usr/bin/env python3
"""Generate EP03 narration from the LOCAL VoiceStudio endpoint only — never a silent fallback.

Layout of the audio produced for each scene (all frame-aligned at 30 fps / 48 kHz):

    [lead] beat1 [gap] beat2 [gap] ... beatN [tail]

* one VoiceStudio request per *beat* (sentence) so subtitles and animation cues use the
  real start/end of each sentence — no estimated timing;
* the raw synthesis is cached by sha256(voice, model, seed, language, spoken text);
* the speed factor (atempo, pitch preserved, applied exactly once; 1.0 = natural voice speed since the EP03 review, was 1.25) is applied after raw
  synthesis (``--speed`` records it in every manifest); raw cache is never sped up;
* the scene WAV and its manifest are rebuilt only when any input hash changes.

Usage (the profile must be chosen explicitly):
    export VOICESTUDIO_VOICE_PROFILE=27ad8d83      # an ID returned by --voices
    python3 scripts/voicestudio.py --check | --voices | --synthesize [--only 01-mission] | --asr-check
"""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

from episode import LANG, PAUSE_ID, S

ROOT = Path(__file__).resolve().parents[1]
BASE = os.getenv("VOICESTUDIO_BASE", "http://127.0.0.1:3900").rstrip("/")
AUDIO_SLUG = "ep03-voicestudio" + ("-en" if LANG == "en" else "")
AUDIO = ROOT / "public/audio" / AUDIO_SLUG
RAW = AUDIO / "raw"
MANIFEST = ROOT / "audio_manifest" / ("en" if LANG == "en" else "")
FPS, RATE = 30, 48000
SAMPLES_PER_FRAME = RATE // FPS  # 1600
LEAD, GAP, TAIL = 0.60, 0.70, 1.60  # seconds: unhurried pacing (revised after viewer feedback: too fast)
LANGUAGE = LANG
MODEL = os.getenv("VOICESTUDIO_MODEL", "voxcpm2")


def request(path, payload=None, timeout=1800, form=None):
    if not (BASE.startswith("http://localhost:") or BASE.startswith("http://127.0.0.1:")):
        raise RuntimeError("A local (loopback) VoiceStudio endpoint is required; refusing to send the script elsewhere.")
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(BASE + path, data=data, method="POST",
                                     headers={"Content-Type": "application/json", "Accept": "audio/wav"})
    else:
        req = urllib.request.Request(BASE + path, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def get_json(path):
    return json.loads(request(path, timeout=20))


def voices():
    data = get_json("/v1/audio/voices")
    items = data.get("voices", data.get("data", [])) if isinstance(data, dict) else data
    return [v for v in items if isinstance(v, dict)]


def profile_identity(voice_id):
    """Return the saved profile dict (id, name, seed, ...) — refuse unknown or alias IDs."""
    ids = {str(v.get("voice_id", v.get("id"))): v for v in voices()}
    if voice_id not in ids:
        raise SystemExit("Select a returned VoiceStudio voice with VOICESTUDIO_VOICE_PROFILE (see --voices).")
    if ids[voice_id].get("type") != "profile":
        raise SystemExit("Refusing an engine alias: choose a saved synthetic narrator profile.")
    saved = {p["id"]: p for p in get_json("/profiles")}
    return {"id": voice_id, "name": ids[voice_id].get("name"), "seed": saved[voice_id].get("seed"),
            "language": ids[voice_id].get("language")}


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def raw_key(identity, text):
    return digest({"voice": identity["id"], "seed": identity["seed"], "model": MODEL, "lang": LANGUAGE, "text": text})


def wav_info(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate(), w.getframerate(), w.getnchannels(), w.getsampwidth()


def peak_of(path):
    with wave.open(str(path), "rb") as w:
        samples = array.array("h")
        samples.frombytes(w.readframes(w.getnframes()))
    return max((abs(x) for x in samples), default=0) / 32768.0


def synth_raw(identity, text, out):
    payload = {"model": MODEL, "voice": identity["id"], "input": text, "language": LANGUAGE,
               "response_format": "wav", "speed": 1.0, "seed": identity["seed"]}
    raw = request("/v1/audio/speech", payload)
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise RuntimeError("VoiceStudio returned something that is not a WAV file")
    out.write_bytes(raw)
    if wav_info(out)[0] < 0.3:
        out.unlink()
        raise RuntimeError("VoiceStudio returned audio shorter than 0.3 s")


TRIM = ("silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB:start_silence=0.04,"
        "areverse,silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB:start_silence=0.06,areverse")


def process(raw_path, out_path, speed):
    """atempo (pitch preserved) exactly once -> 48 kHz mono -> trim edge silence."""
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw_path),
                    "-af", f"atempo={speed},{TRIM}", "-ar", str(RATE), "-ac", "1", "-c:a", "pcm_s16le", str(out_path)],
                   check=True)


def read_pcm(path):
    with wave.open(str(path), "rb") as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (RATE, 1, 2), path
        return w.readframes(w.getnframes())


def scene_layout(index):
    """(lead, tail) seconds; the 10-second pause must not be lengthened by padding."""
    prev_is_pause = index > 0 and S[index - 1].id == PAUSE_ID
    next_is_pause = index + 1 < len(S) and S[index + 1].id == PAUSE_ID
    return (0.0 if prev_is_pause else LEAD), (0.0 if next_is_pause else TAIL)


def beat_spoken(scene):
    return [beat.spoken for beat in scene.beats]


def synthesize(only, speed, voice_id, limit):
    identity = profile_identity(voice_id)
    print(f"Voice: {identity['name']} [{identity['id']}] seed={identity['seed']} model={MODEL} speed={speed}x", flush=True)
    RAW.mkdir(parents=True, exist_ok=True)
    MANIFEST.mkdir(exist_ok=True)
    started, made = time.time(), 0
    for index, scene in enumerate(S):
        if scene.silent or (only and scene.id not in only):
            continue
        spoken = beat_spoken(scene)
        keys = [raw_key(identity, text) for text in spoken]
        lead, tail = scene_layout(index)
        scene_hash = digest({"keys": keys, "speed": speed, "lead": lead, "gap": GAP, "tail": tail, "trim": TRIM})
        wav_path, meta_path = AUDIO / f"{scene.id}.wav", MANIFEST / f"{scene.id}.json"
        if wav_path.is_file() and meta_path.is_file() and json.loads(meta_path.read_text()).get("sha256") == scene_hash:
            print("Cached scene", scene.id, flush=True)
            continue
        pcm, cursor, beats = [b"\x00\x00" * int(lead * RATE)], int(lead * RATE), []
        for k, (text, key) in enumerate(zip(spoken, keys)):
            raw_path = RAW / f"{key}.wav"
            if not raw_path.is_file():
                if limit is not None and made >= limit:
                    print("Reached --limit; stopping.", flush=True)
                    return 0
                t0 = time.time()
                synth_raw(identity, text, raw_path)
                made += 1
                print(f"  synthesized {scene.id}#{k + 1} raw={wav_info(raw_path)[0]:.2f}s in {time.time() - t0:.0f}s "
                      f"(total {made}, elapsed {(time.time() - started) / 60:.1f} min)", flush=True)
            processed = RAW / f"{key}.x{speed}.wav"
            if not processed.is_file():
                process(raw_path, processed, speed)
            data = read_pcm(processed)
            if k:
                pcm.append(b"\x00\x00" * int(GAP * RATE))
                cursor += int(GAP * RATE)
            beats.append({"index": k, "key": key, "start": cursor / RATE, "end": (cursor + len(data) // 2) / RATE,
                          "peak": round(peak_of(processed), 4)})
            pcm.append(data)
            cursor += len(data) // 2
        pcm.append(b"\x00\x00" * int(tail * RATE))
        cursor += int(tail * RATE)
        pad = (-cursor) % SAMPLES_PER_FRAME
        pcm.append(b"\x00\x00" * pad)
        cursor += pad
        with wave.open(str(wav_path), "wb") as w:
            w.setnchannels(1), w.setsampwidth(2), w.setframerate(RATE)
            w.writeframes(b"".join(pcm))
        meta_path.write_text(json.dumps({
            "scene": scene.id, "sha256": scene_hash, "engine": "VoiceStudio local", "base": BASE,
            "model": MODEL, "voice": identity["id"], "voice_name": identity["name"], "seed": identity["seed"],
            "language": LANGUAGE, "speed": speed, "speed_applied": "ffmpeg atempo once, pitch preserved",
            "lead": lead, "gap": GAP, "tail": tail, "duration": cursor / RATE, "frames": cursor // SAMPLES_PER_FRAME,
            "beats": beats}, ensure_ascii=False, indent=2) + "\n")
        print(f"Built {wav_path.name}: {cursor / RATE:.2f}s, {len(beats)} beats", flush=True)
    print(f"Done. {made} new VoiceStudio requests in {(time.time() - started) / 60:.1f} min.", flush=True)
    return 0


def normalise(text):
    text = text.lower()
    text = re.sub(r"[^\wÀ-ỹ ]+", " ", text, flags=re.UNICODE)
    return text.split()


def edit_distance(a, b):
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        new = [i]
        for j, y in enumerate(b, 1):
            new.append(min(row[j] + 1, new[-1] + 1, row[j - 1] + (x != y)))
        row = new
    return row[-1]


def transcribe(path):
    boundary = "----ep03" + hashlib.md5(str(path).encode()).hexdigest()
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\nwhisper-1\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\n{LANGUAGE}\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode(),
        Path(path).read_bytes(), f"\r\n--{boundary}--\r\n".encode()])
    req = urllib.request.Request(BASE + "/v1/audio/transcriptions", data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.loads(urllib.request.urlopen(req, timeout=300).read())["text"]


def asr_check(speed, voice_id):
    """Proxy for text fidelity: VoiceStudio's own ASR vs the spoken text. Not a listening test."""
    identity = profile_identity(voice_id)
    rows = []
    for scene in S:
        for k, beat in enumerate(scene.beats):
            processed = RAW / f"{raw_key(identity, beat.spoken)}.x{speed}.wav"
            if not processed.is_file():
                raise SystemExit(f"Missing audio for {scene.id}#{k + 1}; run --synthesize first.")
            heard = transcribe(processed)
            ref, hyp = normalise(beat.spoken), normalise(heard)
            wer = edit_distance(ref, hyp) / max(1, len(ref))
            rows.append({"scene": scene.id, "beat": k + 1, "wer": round(wer, 3), "expected": beat.spoken, "heard": heard})
            print(f"{scene.id}#{k + 1} WER={wer:.2f}", flush=True)
    mean = sum(r["wer"] for r in rows) / len(rows)
    report = {"engine": "VoiceStudio /v1/audio/transcriptions (faster-whisper)", "language": LANGUAGE,
              "note": "Automatic proxy for text fidelity. English terms and single letters are often mis-transcribed; "
                      "this is NOT a substitute for listening.", "mean_wer": round(mean, 3), "beats": rows}
    MANIFEST.mkdir(exist_ok=True)
    (MANIFEST / "asr_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Mean WER {mean:.3f} over {len(rows)} beats -> audio_manifest/asr_report.json")
    return 0


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--voices", action="store_true")
    mode.add_argument("--synthesize", action="store_true")
    mode.add_argument("--asr-check", action="store_true")
    ap.add_argument("--only", nargs="*", help="scene ids to (re)build")
    ap.add_argument("--speed", type=float, default=float(os.getenv("VOICESTUDIO_SPEED", "1.0")))
    ap.add_argument("--limit", type=int, default=None, help="stop after N new VoiceStudio requests")
    args = ap.parse_args()
    if not 0.5 <= args.speed <= 2.0:
        raise SystemExit("speed must be between 0.5 and 2.0")
    if args.check:
        print(json.dumps(get_json("/health"), ensure_ascii=False, indent=2))
        return 0
    if args.voices:
        print(json.dumps(voices(), ensure_ascii=False, indent=2))
        return 0
    voice = os.environ.get("VOICESTUDIO_VOICE_PROFILE", "").strip()
    if not voice:
        raise SystemExit("Select a returned VoiceStudio voice with VOICESTUDIO_VOICE_PROFILE (see --voices).")
    if args.synthesize:
        return synthesize(set(args.only or []), args.speed, voice, args.limit)
    return asr_check(args.speed, voice)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (urllib.error.URLError, RuntimeError, subprocess.CalledProcessError) as exc:
        sys.exit(f"VoiceStudio failed (no fallback to another voice or provider): {exc}")
