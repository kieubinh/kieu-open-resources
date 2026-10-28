# Kieu Studio · EP04 — LeetCode #4: Median of Two Sorted Arrays

**Status: REVIEW ONLY — not publish-ready.**

Standalone, isolated episode scaffold based on `skills/kieu-leetcode-video/SKILL.md` in [Kieu Open Resources](https://github.com/kieubinh/kieu-open-resources). Does not modify LeetCode #10 or any existing episode.

## Learning objective

Use LeetCode #4 to practise **understand → hypothesize → test → reflect**, not memorize the Python solution. Includes both official examples, all constraints, dated difficulty/acceptance facts, three hints, precisely ten seconds without narration, partition proof, counterexamples and rejected alternatives, code/trace, complexity and three further exercises.

**Sources:** `docs/SOURCE_MANIFEST.json`.

## Produced here

- `output/EP04_MEDIAN_VISUAL_REVIEW_ONLY.mp4` — silent offline storyboard, 1280×720 at 2 fps, 24:09. **It is not the final Remotion animation.**
- `src/Episode04.tsx` — editable animated Remotion scenes for 1920×1080, 30 fps.
- `src/timeline.json`, `src/captions.json` — 31 scene timings and text cues.
- `scripts/episode.py` — Vietnamese 31-scene voiceover and visual script (3,113 words).
- `code/solution.py`, `code/trace.py`, `src/traces.json` — working algorithm plus execution frames.
- `tests/` — 10 tests including 20,000 deterministic differential cases.
- `output/EP04_REVIEW_ESTIMATED.srt` — **estimated** subtitles based on review timing; not speech-aligned.
- `output/EP04_THUMBNAIL.png`, `output/QA_CONTACT_SHEET.png` — preview-only assets.
- `docs/QA_REPORT.md` — release gates and test results.

## Complete the episode on a machine with VoiceStudio and npm networking

From this directory:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 code/trace.py
npm install
npm run voice:check
npm run voice:voices
export VOICESTUDIO_VOICE_PROFILE='<exact voice ID shown by voice:voices>'
npm run voice:generate
npm run render:release
```

The voice adapter requires `http://127.0.0.1:3900` (or a different *localhost* port via `VOICESTUDIO_BASE`), validates the chosen voice ID, writes **separate WAVs per scene**, and checks SHA-256 hashes based on text, voice and model. The ten-second pause creates **no WAV and no audio in the Remotion Sequence**. `render:release` generates a candidate `output/EP04_VOICESTUDIO_CANDIDATE.mp4`, not editorially approved content. After synthesis, `build_timeline.py` uses the actual WAV durations and rejects a total outside 18–25 minutes.

**Important:** Audio-aligned subtitles need word-level alignment or human timing checks after audio generation. The included SRT and Remotion cues are based on nominal scene timings. For the final upload, validate each cue against the new scene WAV, render 100%-scale Remotion frames and listen to opening, both official examples, hints, code trace and closing.

**Fonts:** DejaVu Sans is used by the visual design. The local source and preview glyph audit passed for Vietnamese and mathematical symbols. Install a glyph-complete font on the final render machine; no font binaries are bundled.

## Review / test

```bash
python3 scripts/build_timeline.py --preview
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/qa.py
npm run render:review      # requires installed Remotion; outputs separate review MP4
```

`output/EP04_MEDIAN_VISUAL_REVIEW_ONLY.mp4` was produced with a lower-fidelity offline PIL/FFmpeg fallback **solely for visual review** because the execution environment lacks Remotion and VoiceStudio. No cloud TTS, eSpeak or guide voice was substituted.

**Not affiliated with LeetCode.** The public source uses original explanations and animations; official screenshots and graphics are not copied.
