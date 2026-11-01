# EP03 — Wildcard Matching (#44)

**Mission:** practise problem-solving, not memorise a LeetCode answer.

Official source and the facts used: [SOURCES.md](SOURCES.md). QA results: [QA_REPORT.md](QA_REPORT.md).

## What the episode contains (26 scenes, 1920×1080, 30 fps)

| # | Scenes | Content |
|---|---|---|
| 1 | 01 | Kieu Studio introduction and the four-step problem-solving loop |
| 2 | 02–04 | Statement, input/output, constraints (`0 ≤ length ≤ 2000`), difficulty, accepted submissions and acceptance rate with source date |
| 3 | 05–08 | All three official examples animated from the real execution trace, then a recap of the three habits |
| 4 | 09–10 | Three hints, then **exactly 10.0 s (300 frames) of silence** with a countdown, no audio and no subtitle |
| 5 | 11–14 | The simplest recursion, its decision tree (20 calls, 14 distinct states), measured blow-up, and a *failing* greedy idea with its counter-example |
| 6 | 15 | Memoisation as a 2-D DP table filled cell by cell |
| 7 | 16–19 | Why only the nearest `*` matters, the two-pointer algorithm (`i, j, star, mark`), a step-by-step trace, pseudocode |
| 8 | 20–21 | Python 3 solution (22 lines), then line-by-line execution with the variables read from a real `sys.settrace` run |
| 9 | 22–23 | Verification evidence and a comparison of the three approaches (measured vs. theory tags) |
| 10 | 24–26 | Six problem-solving lessons, three practice problems (#392, #72, #10), outro |

The visualisations were designed for this algorithm (call tree, DP table, pointer/marker trace, code execution). They are **not** renamed EP02 scenes.

## Folder layout

```
scripts/   episode.py (single source of truth for scenes, subtitles and spoken text), solution.py, oracles.py,
           build_trace.py, run_verification.py, voicestudio.py, build_timeline.py, build_publish.py, QA helpers, tests
src/       Remotion project (Episode, Frame, theme, visuals/*), data/ (trace.json, verification.json), timeline.json
public/    fonts (OFL), brand logo crops, audio/ (git-ignored)
audio_manifest/  per-scene hashes and measured sentence offsets (commit these)
publish/   thumbnail.png, subtitles.vi.srt/.vtt, youtube_metadata.md, chapters.txt
output/    renders (git-ignored)
docs/      this file, SOURCES.md, QA_REPORT.md
```

## Review without audio (no VoiceStudio needed)

```bash
npm install
python3 -m unittest discover -s scripts -p '*test.py' -v     # 38 Python tests
npm run typecheck
python3 ../../skills/kieu-leetcode-video/scripts/audit_episode.py --episode scripts/episode.py
npm run studio                  # preview timeline, silent, ESTIMATED durations
npm run render:preview          # output/EP03_SILENT_REVIEW.mp4  (NOT publishable)
```

## Release build with local VoiceStudio

```bash
npm run voice:check
npm run voice:voices
export VOICESTUDIO_VOICE_PROFILE="<profile id shown by voice:voices>"   # required, no default, no fallback
npm run voice:generate          # resumable; about 40 s per sentence on the reference Mac
npm run voice:verify            # ASR proxy check (not a listening test)
npm run render:review           # output/EP03_VOICESTUDIO_REVIEW.mp4
npm run thumbnail
python3 scripts/build_publish.py
```

`voicestudio.py` refuses to start without an explicit profile, refuses aliases and non-loopback endpoints, and never falls back to another voice. If VoiceStudio is unavailable, only the silent preview can be produced and it is labelled REVIEW.

## Timing model

`build_timeline.py` reads every scene WAV and its manifest, validates that the audio is not stale (hash of voice + seed + model + language + spoken text), requires the WAV to be a whole number of video frames, and writes `src/timeline.json`. Subtitle and animation cues use the **measured** start and end of each sentence, not estimates. The scenes next to the thinking pause carry no padding so the silence is exactly 10.0 s.

## Status labels

- Algorithm, trace, tests, render pipeline: verified in this repository (see QA_REPORT.md).
- Narrator 03 voice: **not yet approved** by a human listener. The release video is a **REVIEW** build until someone has listened to it.
- Nothing has been uploaded or published.
