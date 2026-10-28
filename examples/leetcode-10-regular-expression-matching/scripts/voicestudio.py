#!/usr/bin/env python3
"""Generate scene WAVs from LOCAL VoiceStudio only; no silent provider fallback."""
from __future__ import annotations
import argparse, hashlib, json, os, urllib.request, urllib.error
from pathlib import Path
import wave
from episode import S

ROOT = Path(__file__).resolve().parents[1]
BASE = os.getenv("VOICESTUDIO_BASE", "http://127.0.0.1:3900").rstrip("/")

def request(path: str, payload=None):
    if not (BASE.startswith("http://localhost:") or BASE.startswith("http://127.0.0.1:")):
        raise RuntimeError("A local VoiceStudio endpoint is required.")
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload else None
    req = urllib.request.Request(BASE + path, data=data,
        headers={"Accept": "application/json" if payload is None else "audio/wav",
                 "Content-Type": "application/json"},
        method="POST" if payload else "GET")
    with urllib.request.urlopen(req, timeout=180 if payload else 15) as r:
        raw = r.read()
    return raw if payload else json.loads(raw)

def main():
    ap=argparse.ArgumentParser()
    opts=ap.add_mutually_exclusive_group(required=True)
    opts.add_argument("--check", action="store_true")
    opts.add_argument("--voices", action="store_true")
    opts.add_argument("--synthesize", action="store_true")
    args=ap.parse_args()
    if args.check:
        print(json.dumps(request("/health"), ensure_ascii=False, indent=2)); return
    voices=request("/v1/audio/voices")
    items=voices.get("data", voices.get("voices", [])) if isinstance(voices, dict) else voices
    if args.voices:
        print(json.dumps(items, ensure_ascii=False, indent=2)); return
    voice=os.environ.get("VOICESTUDIO_VOICE_PROFILE", "").strip()
    model=os.environ.get("VOICESTUDIO_MODEL", "tts-1")
    ids={str(v.get("id", v.get("voice_id"))) for v in items if isinstance(v, dict)}
    if not voice or voice not in ids:
        raise SystemExit("Select a returned VoiceStudio voice with VOICESTUDIO_VOICE_PROFILE")
    dest=ROOT/"public/audio/ep02-voicestudio"
    dest.mkdir(parents=True, exist_ok=True)
    for scene in S:
        if scene.silent: continue
        output=dest/(scene.id+".wav")
        meta=dest/(scene.id+".json")
        digest=hashlib.sha256(json.dumps({"voice":voice,"model":model,"text":scene.script},
            ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        if output.is_file() and meta.is_file() and json.loads(meta.read_text()).get("sha256")==digest:
            print("Cached",scene.id); continue
        raw=request("/v1/audio/speech",{"model":model,"voice":voice,
            "input":scene.script,"response_format":"wav"})
        if raw[:4]!=b"RIFF" or raw[8:12]!=b"WAVE":
            raise RuntimeError(f"{scene.id}: invalid WAV")
        output.write_bytes(raw)
        with wave.open(str(output),"rb") as wav:
            duration=wav.getnframes()/wav.getframerate()
        if duration<0.3: raise RuntimeError(f"{scene.id}: short audio")
        meta.write_text(json.dumps({"sha256":digest,"duration":duration,
            "voice":voice,"engine":"VoiceStudio local"},indent=2))
        print("Created",output.name,round(duration,2))
    print("Build timeline and render with npm run render:release")
if __name__=="__main__":
    try: main()
    except (urllib.error.URLError,RuntimeError) as exc:
        raise SystemExit(f"VoiceStudio failed (no fallback): {exc}")
