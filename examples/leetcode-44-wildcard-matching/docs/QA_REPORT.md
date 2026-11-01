# QA report - EP03 LeetCode #44 Wildcard Matching

**Release status: `REVIEW ONLY`.** The video is a candidate render with local VoiceStudio narration (Narrator 03, a synthetic voice). It is **not** approved for publication: no human has listened to the narration or approved the episode. Nothing has been uploaded, pushed or published.

Statuses: PASS / FAIL / NOT RUN / PARTIAL. Every PASS below was produced by a command run on 29 Oct 2026 on the author's Mac (Python 3.9.6, Remotion 4.0.539); nothing is carried over from claims.

## Deliverables (in this folder)

| File | Git | Note |
|---|---|---|
| `output/EP03_VOICESTUDIO_REVIEW.mp4` | ignored | 1920x1080, 30 fps, h264/yuv420p + AAC 48 kHz, 766.720 s (12:47), 68.1 MB. sha256 `3cbb48d9d076...` (first 12 hex) |
| `publish/thumbnail.png` | committed | 1280x720 still, composition `EP03-Thumbnail` |
| `publish/youtube_metadata.md` (= `docs/YOUTUBE_METADATA.md`) | committed | title, description, tags, chapters; DRAFT |
| `publish/chapters.txt` (= `docs/CHAPTERS.md`) | committed | 14 chapters (revised for the slower pacing), timestamps from the real timeline, each >= 10 s |
| `publish/subtitles.vi.srt` / `.vtt` | committed | 121 cues from the measured sentence offsets of the real WAVs |
| `audio_manifest/*.json` | committed | per-scene hashes (text + voice + model), beat offsets |
| `output/release_qa.json` | ignored | machine-readable result of `scripts/release_qa.py` |

## Checks

### Algorithm and facts

| Check | Status | Evidence |
|---|---|---|
| 3/3 official examples through the real `Solution.isMatch` | PASS | `src/data/verification.json` |
| 16 edge cases | PASS | 0 failures |
| Exhaustive differential test (alphabet `ab` for s, `ab?*` for p, |s|<=6, |p|<=5) | PASS | 173,355 cases vs regex `fullmatch` and a 2-D DP table, 0 mismatches. **Bounded**: not a proof |
| Seeded random test (seed 44, |s|<=40, |p|<=30) | PASS | 20,000 cases vs DP (every case), 14,393 also vs regex; 0 mismatches |
| Worst case n = 2000 | MEASURED | 1,002,001 loop iterations (exact); 0.16 s wall-clock on this Mac (machine-dependent) |
| Typical case | MEASURED | 40 seeded random cases at n = 2000: mean 0.592, max 1.434 loop iterations per character |
| Brute-force blow-up | MEASURED | 62 -> 203,078 recursive calls for k = 1..6 (n = 20) |
| DP table at the maximum constraints | THEORY | 2001 x 2001 = 4,004,001 cells; labelled `LY THUYET` in the video |
| Greedy counter-example (no backtracking) | PASS | `s = "adceb"`, `p = "*a*b"`: the no-backtrack version returns false, the answer is true; produced by `build_trace.py` |
| Code-trace scene vs real execution | PASS | highlighted line and variables come from `sys.settrace` on the real function; last-beat bug (variables shown before the line ran) fixed and re-checked on the final render |
| Problem statistics | PASS (snapshot) | read from the LeetCode page on 28 Oct 2026: 967,654 accepted submissions, 33.1 %; labelled as submissions, not people, with the date. The page shows only a rounded total (about 2.9 M), so none is claimed as exact. See `docs/SOURCE_MANIFEST.json` |
| Problem #10 difficulty label | NOT RUN | page could not be fetched in this session; label taken from EP02 docs. Re-check before publishing |

### Tests and static checks

| Check | Status | Evidence |
|---|---|---|
| EP03 unit tests (`npm test`'s Python part) | PASS | 38 tests, `python3 -m unittest discover -s scripts -p "*test.py"` and `pytest examples/leetcode-44-wildcard-matching` |
| `tsc --noEmit` | PASS | clean after the last edit |
| Skill structure audit (`skills/kieu-leetcode-video/scripts/audit_episode.py`) | PASS | after adding `docs/SOURCE_MANIFEST.json`, which the updated skill on `main` now requires (it failed before: example count unknown) |
| Glyph coverage (`check_glyphs.py`, `check_visual_glyphs.py`) | PASS | 118 distinct non-ASCII characters covered by Noto Sans, then JetBrains Mono for `-> ~= != <= >= up/down triangles`; no system-font fallback |
| Repository baseline tests | PASS | `PYTHONPATH=src pytest tests`: 105 passed (run in a temporary venv with pytest) |
| Bare `pytest` from the repository root | NOT A GATE | fails at baseline (3 failures in EP04 tests due to module-name clashes of `episode.py` across examples) and still does with EP03 added; use `pytest tests` or run an example folder on its own |

### Narration and timeline

| Check | Status | Evidence |
|---|---|---|
| Voice | PASS | local VoiceStudio only (`127.0.0.1:3900`), profile "Narrator 03 - Tram chung chac (synthetic)" id `27ad8d83`, model `voxcpm2`, language `vi`, seed 20261017. No other TTS used |
| 25 scene WAVs (the pause has none), 120 sentence requests | PASS | `audio_manifest/` |
| Timeline built from the real WAV durations | PASS | 26 scenes, 23,001 frames = 766.7 s |
| Pacing (revised after viewer feedback: speech too fast, scene changes too abrupt) | PASS (measured) | narration at the voice's natural speed (the earlier 1.25x speed-up was removed; the raw sentences were reused, no re-synthesis); 0.7 s between sentences, 0.6 s lead and 1.6 s tail per scene; subtitles stay 1.2 s after a sentence ends; content fades out over 0.6 s and in over 0.6 s at each scene change. Length 9:24 -> 12:47. Whether it now *sounds* unhurried enough is a listening judgement: NOT RUN |
| Thinking pause | PASS | scene `10-think` is exactly 300 frames (10.000 s), no `<Audio>`, no beats, no captions; `silencedetect` finds one silence >= 9 s, 211.70-221.80 s (10.10 s including the tails of the neighbouring audio); the other 23 silences >= 2 s are scene gaps, longest 2.31 s |
| ASR text-fidelity proxy | PARTIAL | `voicestudio.py --asr-check` was stopped after 37 of 121 beats (about 1 beat per minute): mean WER 0.244, median 0.14 over those beats. Single letters, symbols and English terms are mis-transcribed, so this is only a rough proxy. No `asr_report.json` was written. **Not a listening test** |
| Human listening (pronunciation of `s`, `p`, `*`, `?`, numbers) | NOT RUN | required before release |
| Subtitle alignment | PARTIAL | cues are built from measured per-sentence offsets inside the real WAVs and verified ordered, non-overlapping and absent during the pause. Forced alignment or a human check against the audio: NOT RUN |

### Video

| Check | Status | Evidence |
|---|---|---|
| Container/codec/size/fps/duration | PASS | `scripts/release_qa.py`: h264 yuv420p, 1920x1080, 30 fps, 766.720 s vs timeline 766.700 s |
| Audio stream | PASS | AAC 48 kHz, 2 channels |
| Black frames | PASS | none >= 0.5 s (`blackdetect`) |
| Layout / clipping inspection of frames | PARTIAL | the pacing change did not alter any layout. Contact sheets of the previous (9:24) render were reviewed for scenes 02, 03, 04, 07, 08, 09, 10, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25. Two clipping defects were found and fixed (cards under the subtitle band in scenes 07, 14 and 20); scenes 07, 14, 20, 21 re-checked on the final MP4. Scenes 01, 05, 06, 11, 18, 26 were inspected as stills earlier in the work, not re-inspected in the final MP4; one frame per scene is a sample, not a full watch-through. In the 12:47 render only the Example 2 -> 3 transition (subtitle hold, fade out, fade in) was inspected |
| Full watch-through at normal speed | NOT RUN | |
| Thumbnail legibility | PASS (visual) | viewed at 1280x720; no clipped text |

## Known limitations

- Review build: narration is a synthetic voice that no human has approved. Text typography has been checked by glyph tests and frames; pronunciation has not been listened to.
- Length is 12:47, shorter than the 18-25 minute gate that the EP04 tests use. The task did not set a length; the episode covers every item requested.
- Exhaustive testing is bounded (small alphabets and lengths); the algorithm's correctness rests on differential tests, not a formal proof.
- Statistics are a dated snapshot and will change; total submissions are not shown because only a rounded figure was available.
- The three hints are written by Kieu Studio, not LeetCode's.
- Logo is a raster crop of existing brand assets; no vector master.
- Fonts are vendored (Noto Sans, JetBrains Mono, SIL OFL); the `FONT` stack depends on the vendored files being present at render time.
- Run on Python 3.9.6 (macOS Command Line Tools); other versions were not tried.
- The repository name in the description is not a confirmed public URL.
- Estimated-timing "preview" mode of `build_timeline.py` exists for development; the committed `src/timeline.json` is the release (real-WAV) timeline.

## Reproduce

```bash
cd examples/leetcode-44-wildcard-matching
npm install
npm test                                   # 38 Python tests + tsc
python3 scripts/check_visual_glyphs.py
VOICESTUDIO_VOICE_PROFILE=27ad8d83 python3 scripts/voicestudio.py --synthesize   # needs local VoiceStudio; cached by hash
python3 scripts/build_timeline.py          # release mode
npm run render:review
python3 scripts/release_qa.py
npm run thumbnail && python3 scripts/build_publish.py
```
