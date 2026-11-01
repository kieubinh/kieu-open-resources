#!/usr/bin/env python3
"""Release QA for the rendered EP03 review video. Measures, does not assume.

Checks: container/codec/size/fps/duration, audio stream, the 10 s silent
thinking pause (silencedetect), black-frame tail, and subtitle/audio agreement
(every SRT cue lies inside the scene window that owns its beat).
Writes output/release_qa.json and exits non-zero on any failed check.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEO = ROOT / "output" / "EP03_VOICESTUDIO_REVIEW.mp4"
TL = json.loads((ROOT / "src" / "timeline.json").read_text())
FPS = TL["fps"]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe():
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(VIDEO)])
    return json.loads(r.stdout)


def main():
    checks = []

    def check(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name + ": " + str(detail))

    if not VIDEO.exists():
        print("missing", VIDEO)
        return 2
    p = probe()
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    a = next((s for s in p["streams"] if s["codec_type"] == "audio"), None)
    dur = float(p["format"]["duration"])
    expect = TL["totalFrames"] / FPS
    num, den = v["r_frame_rate"].split("/")
    fps = int(num) / int(den)
    check("video codec/pix_fmt", v["codec_name"] == "h264" and v["pix_fmt"] == "yuv420p", f'{v["codec_name"]} {v["pix_fmt"]}')
    check("resolution 1920x1080", (v["width"], v["height"]) == (1920, 1080), f'{v["width"]}x{v["height"]}')
    check("fps 30", abs(fps - 30) < 1e-6, fps)
    check("duration matches timeline", abs(dur - expect) < 0.1, f"{dur:.3f}s vs {expect:.3f}s")
    check("audio stream present", a is not None, a and f'{a["codec_name"]} {a["sample_rate"]}Hz ch={a["channels"]}')

    # silent thinking pause: must be detected as ~10 s silence starting at the scene start
    start = 0
    pause = None
    for s in TL["scenes"]:
        if s["id"] == "10-think":
            pause = (start / FPS, (start + s["frames"]) / FPS)
        start += s["frames"]
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(VIDEO), "-af", "silencedetect=noise=-50dB:d=0.5", "-f", "null", "-"])
    sil = [(float(x), float(y)) for x, y in zip(
        re.findall(r"silence_start: ([\d.]+)", r.stderr), re.findall(r"silence_end: ([\d.]+)", r.stderr))]
    pauses = [(s0, s1) for s0, s1 in sil if s1 - s0 >= 9.0]
    gaps = [(s0, s1) for s0, s1 in sil if 2.0 <= s1 - s0 < 9.0]
    check("exactly one silence >= 9 s (the thinking pause)", len(pauses) == 1, pauses)
    # Every other long silence must be a deliberate scene boundary (lead 0.6 s + tail 1.6 s = about 2.2 s)
    check("other long silences are scene gaps <= 2.6 s", all(s1 - s0 <= 2.6 for s0, s1 in gaps), f"{len(gaps)} gaps, longest {max([s1 - s0 for s0, s1 in gaps] or [0]):.2f}s")
    if pauses and pause:
        s0, s1 = pauses[0]
        check("pause scene is exactly 10.0 s", abs((pause[1] - pause[0]) - 10.0) < 1e-9, pause)
        check("silence covers the pause window", s0 <= pause[0] + 0.25 and s1 >= pause[1] - 0.25 and (s1 - s0) < 11.5,
              f"silence {s0:.2f}-{s1:.2f}, pause {pause[0]:.2f}-{pause[1]:.2f} (len {s1 - s0:.2f}s)")

    # black tail
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(VIDEO), "-vf", "blackdetect=d=0.5:pix_th=0.05", "-an", "-f", "null", "-"])
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)
    check("no black segment >= 0.5 s", not blacks, blacks)

    # subtitles lie inside the narrated scene windows and are ordered
    srt = (ROOT / "publish" / "subtitles.vi.srt").read_text()
    cues = re.findall(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", srt)
    t = lambda h, m, s, ms: int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    spans = [(t(*c[:4]), t(*c[4:])) for c in cues]
    ordered = all(spans[i][1] <= spans[i + 1][0] + 1e-6 for i in range(len(spans) - 1))
    inside = all(0 <= s0 < s1 <= dur + 1e-6 for s0, s1 in spans)
    in_pause = [sp for sp in spans if pause and sp[0] < pause[1] - 0.01 and sp[1] > pause[0] + 0.01]
    check("subtitle cues ordered, non-overlapping, inside video", ordered and inside, f"{len(spans)} cues")
    check("no subtitle during the thinking pause", not in_pause, in_pause)

    out = {"video": str(VIDEO.relative_to(ROOT)), "duration_s": dur, "checks": checks, "all_ok": all(c["ok"] for c in checks)}
    (ROOT / "output" / "release_qa.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print("ALL OK" if out["all_ok"] else "SOME CHECKS FAILED")
    return 0 if out["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
