#!/usr/bin/env python3
"""Tile the QA stills (output/qa/<scene>_<beat>.png) into 2x2 contact sheets with ffmpeg: output/qa_sheets/<scene>_<n>.png"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC, DST = ROOT / "output/qa", ROOT / "output/qa_sheets"
DST.mkdir(parents=True, exist_ok=True)
prefixes = sys.argv[1:]
scenes = sorted({p.name.rsplit("_", 1)[0] for p in SRC.glob("*.png")})
for scene in scenes:
    if prefixes and not any(scene.startswith(p) for p in prefixes):
        continue
    files = sorted(SRC.glob(f"{scene}_*.png"), key=lambda p: (len(p.stem), p.stem))
    for n in range(0, len(files), 4):
        group = files[n:n + 4]
        cmd = ["ffmpeg", "-y", "-loglevel", "error"]
        for f in group:
            cmd += ["-i", str(f)]
        if len(group) == 1:
            cmd += ["-frames:v", "1", str(DST / f"{scene}_{n // 4}.png")]
        else:
            layout = {2: "0_0|w0_0", 3: "0_0|w0_0|0_h0", 4: "0_0|w0_0|0_h0|w0_h0"}[len(group)]
            cmd += ["-filter_complex", f"xstack=inputs={len(group)}:layout={layout}", "-frames:v", "1", str(DST / f"{scene}_{n // 4}.png")]
        subprocess.run(cmd, check=True)
print("sheets ->", DST)
