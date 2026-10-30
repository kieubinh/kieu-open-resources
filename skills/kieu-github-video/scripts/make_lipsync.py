#!/usr/bin/env python3
"""Render a photoreal lip-synced face for a whole video with the local SadTalker install (kieu-studio).

Usage: make_lipsync.py --project <episode dir> --episode gr01 [--studio <kieu-studio repo>]

1. Reads <project>/src/timeline.json (the voiced release timeline) and joins the per-scene narration WAVs into ONE
   narration track whose length equals the video (each scene padded with silence to its timeline length).
2. Calls kieu-studio's resumable chunked SadTalker worker (tools/avatar_render.py, 30 s chunks, MPS) on it.
3. Writes <project>/public/lipsync/<episode>.mp4 (256x256, 25 fps, silent, git-ignored). The Remotion avatar plays it
   instead of the drawn mouth; the original WAVs stay the only soundtrack.

Needs the approved SadTalker checkpoints (kieu-studio/tools/sadtalker-local/README.md). It is slow: several minutes
of compute per minute of speech. Interrupt with Ctrl-C/SIGTERM and re-run: finished chunks are reused.
Never run this against a portrait other than the approved one without the owner's consent.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path

FPS = 30


def find_studio(arg: str | None) -> Path:
    env = arg or os.environ.get('KIEU_STUDIO_REPO')
    here = Path(__file__).resolve()
    for r in ([Path(env)] if env else []) + [p / 'kieu-studio' for p in here.parents] + [p.parent / 'kieu-studio' for p in here.parents]:
        if (r / 'tools' / 'avatar_render.py').is_file():
            return r
    raise SystemExit('kieu-studio checkout not found: pass --studio or set KIEU_STUDIO_REPO')


def build_narration(project: Path, audio_dir: Path, out: Path) -> float:
    timeline = json.loads((project / 'src' / 'timeline.json').read_text())
    parts, total = [], 0.0
    with tempfile.TemporaryDirectory() as tmp:
        for row in timeline:
            seconds = row['frames'] / FPS; total += seconds
            part = Path(tmp) / f"{row['id']}.wav"
            src = audio_dir / f"{row['id']}.wav"
            if row['silent'] or not src.exists():
                cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=16000:cl=mono', '-t', f'{seconds:.4f}', str(part)]
            else:
                cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-af', f'apad=whole_dur={seconds:.4f}', '-t', f'{seconds:.4f}',
                       '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(part)]
            subprocess.run(cmd, check=True); parts.append(part)
        lst = Path(tmp) / 'list.txt'; lst.write_text(''.join(f"file '{p}'\n" for p in parts))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c:a', 'pcm_s16le', str(out)], check=True)
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True); ap.add_argument('--episode', required=True)
    ap.add_argument('--audio-dir', help='default: <project>/public/audio/<slug>, found from scripts/config.py')
    ap.add_argument('--studio')
    a = ap.parse_args()
    project, studio = Path(a.project).resolve(), find_studio(a.studio)
    audio_dir = Path(a.audio_dir) if a.audio_dir else None
    if audio_dir is None:
        sys.path.insert(0, str(project / 'scripts')); import config  # noqa: E402
        audio_dir = config.AUDIO_DIR
    py = studio / 'tools' / 'sadtalker-local' / '.venv' / 'bin' / 'python'
    if not py.is_file():
        raise SystemExit('SadTalker venv missing: ' + str(py))
    out_dir = project / 'public' / 'lipsync'; out_dir.mkdir(parents=True, exist_ok=True)
    narration = out_dir / f'{a.episode}_narration.wav'; face = out_dir / f'{a.episode}.mp4'
    seconds = build_narration(project, audio_dir, narration)
    print(f'narration {seconds:.1f}s -> {narration}', flush=True)
    r = subprocess.run([str(py), str(studio / 'tools' / 'avatar_render.py'), str(narration), str(face)], cwd=studio)
    if r.returncode:
        raise SystemExit(f'SadTalker worker exited {r.returncode} (130 = paused; re-run to resume)')
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(face)], capture_output=True, text=True, check=True)
    dur = float(probe.stdout)
    if abs(dur - seconds) > 0.5:
        raise SystemExit(f'face video {dur:.2f}s does not match narration {seconds:.2f}s')
    print(f'lip-sync face ready: {face} ({dur:.1f}s)')


if __name__ == '__main__':
    main()
