#!/usr/bin/env python3
"""Build frame-aligned Remotion timeline. Release requires real VoiceStudio WAVs."""
import argparse, json, wave
from pathlib import Path
from episode import S
ROOT=Path(__file__).resolve().parents[1]
AUDIO=ROOT/"public/audio/ep02-voicestudio"
FPS=30

def main(preview=False):
    rows=[]; at=0
    for scene in S:
        if scene.silent:
            frames=10*FPS
            audio=""
        elif preview:
            frames=round(scene.min_seconds*FPS)
            audio=""
        else:
            path=AUDIO/(scene.id+".wav")
            if not path.is_file(): raise SystemExit(f"Missing VoiceStudio WAV: {path}")
            with wave.open(str(path),"rb") as w:
                duration=w.getnframes()/w.getframerate()
            frames=max(round(scene.min_seconds*FPS),round((duration+.5)*FPS))
            audio=f"audio/ep02-voicestudio/{scene.id}.wav"
        rows.append({"id":scene.id,"phase":scene.phase,"title":scene.title,
            "lines":list(scene.lines),"mode":scene.mode,"silent":scene.silent,
            "fromFrame":at,"frames":frames,"audio":audio})
        at+=frames
    dest=ROOT/"src/timeline.json"
    dest.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n")
    print("Timeline",len(rows),"scenes",at/FPS,"seconds",("PREVIEW / SILENT" if preview else "VoiceStudio"))
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--preview",action="store_true",help="Generate a silent editing timeline (NOT for publishing)")
    args=ap.parse_args();main(preview=args.preview)
