---
name: kieu-leetcode-video
description: Produce and QA Kieu Studio educational LeetCode videos that teach problem-solving skills, with every official example (however many), rejected approaches and a correctness argument before code, approachable algorithm animations, a ten-second thinking pause, Python 3, local VoiceStudio narration, Remotion, and a publishing checklist. Use for new episodes or revisions of the Kieu Studio / The Art of Coding series.
---

# Kieu Studio — LeetCode Problem-Solving Video Factory

## Purpose (non-negotiable)
LeetCode is **practice material**; the outcome is **a stronger problem-solving process**, not copying code. Start every episode with a meaningful Kieu Studio introduction, then model the habits: **understand → hypothesize → test → reflect**. Show code only once the viewer understands the underlying decisions.

## Required episode workflow
1. **Ground the source.** Open the exact LeetCode problem. Record problem number, title, difficulty, **all** official examples (inputs/outputs), constraints, documented operators, required complexity and source URL in `docs/SOURCE_MANIFEST.json`. Never invent or paraphrase away a required constraint. Use only short quotations from the original, attribution and paraphrases otherwise. Never publish full screenshots/official illustrations in this open-source repo without rights review (`licensing.official_images_included` stays `false`).
2. **Verify time-sensitive metrics.** Record acceptance rate, accepted *submissions* and total submissions from a dated reliable snapshot, with source, snapshot date and check date. Mark a third-party snapshot as **not** the live LeetCode rate. If an absolute accepted/total pair cannot be verified, set both to `null` and omit them from the video rather than inventing them. Never call submission attempts “people who solved it”. Put snapshot date/source in the video and the manifest.
3. **Write scenes in a pedagogical order.** Mission and episode hook → problem statement → what key terms mean (e.g. median vs mean) → difficulty/metrics and **every** constraint (and the edge cases they imply) → **every** official example with inputs, output and a clear visual explanation → recap of what the examples share → the naive approach and **why it is rejected** → at least two hints (three preferred) → **exactly 10 seconds of silent, onscreen countdown** → explicit reveal (“thinking” → “solution”) → solution discovery with a concrete decision visualization, including the invariant/proof and each branch → worked walkthroughs, edge cases and counterexamples (empty input, duplicates, …) → pseudocode → Python 3 with highlighted execution → narrated trace → complexity → transfer to everyday problem solving → three related challenges → outro. Avoid obscure data-structure jargon until introduced.
4. **Design the visuals.** State variables must match actual code; no knowingly invalid states (e.g., a regex suffix containing standalone `*` shown as an ordinary valid state); every example illustration must match expected output. Prefer visual evidence (choices, branches, state transitions) over text cards. Never show “PREVIEW”, “GUIDE VOICE”, renderer watermarks or production notes in image frames.
5. **Build traces and test.** Validate official examples and edge cases. Differential-test Python 3 against an independent oracle (the EP04 reference runs 20,000 seeded random cases against a sorted-merge oracle). Test any DP table and branch labels against the exact state definition. Generate `src/traces.json` by running `code/trace.py`; surface algorithm traces in captions/code highlights only if grounded by actual execution.
6. **Text quality gate.** Use fonts that cover all needed **Vietnamese accents and mathematical symbols** (`≤`, `≥`, `≠`, `→`, `×`, superscripts, etc.). Run `scripts/check_glyphs.py` (or the episode's own `scripts/qa.py` glyph checks) against **every** font used, on the **final render machine**, inspect contact sheets, test a source frame at 100% width, and detect clipped titles/cards. Avoid replacing symbols with square glyphs. Apply a readable font-size minimum for YouTube mobile. Do not bundle font binaries.
7. **VoiceStudio strict narration.** Generate a **separate WAV per scene** (the silent pause gets none) using the user's **local** VoiceStudio endpoint and an explicitly selected profile; the adapter must refuse any non-`127.0.0.1`/`localhost` base URL and any voice ID not returned by `--voices`. Validate each response is a real WAV (`RIFF`/`WAVE`, ≥ 0.5 s). Keep a SHA-256 of text + voice + model per scene to invalidate outdated audio. Build the final timeline from each actual WAV duration plus a short tail (EP04 uses +0.6 s) — don't truncate — and reject totals outside the 18–25 minute target unless the user overrides it. Do **not** silently substitute eSpeak/cloud TTS when VoiceStudio fails (fail with `VOICE GATE BLOCKED; no fallback`). A temporary guide-voice MP4 must be labeled **REVIEW ONLY**, never release-ready.
8. **Render and QA.** Prefer Remotion at 1920×1080, 30fps. Validate codec streams, run duration, read/speaker sync, countdown at 10.0 seconds (300 frames at 30 fps) of silence with **no `<Audio/>`, music or captions inside it**, no black tail, no text clipping; watch/listen to opening, all examples, hints, pause, proof/DP, code trace, ending. If npm/Remotion is unavailable, the offline PIL/FFmpeg renderer (`scripts/render_visual_review.py`, 1280×720, 2 fps, silent) may produce a storyboard for visual review **only**; it is not production animation and not a Remotion render.
9. **Speaking avatar and speed (all Kieu videos).** Show the small circular presenter avatar at the bottom-right (220 px circle, 64 px margins, 4 px `#72dce0` ring at 1080p) with the audio-reactive halo/equalizer from `skills/kieu-github-video/assets/SpeakingAvatar.tsx`; build `src/envelope.json` from the real WAVs, prepare the portrait with `skills/kieu-github-video/scripts/prepare_avatar.py` (git-ignored; never commit a founder portrait), keep it idle and halo-free during the 10-second silent pause, and keep subtitles clear of it. Narration speed is **1.0x unless the user asks otherwise**; apply `atempo` once and only for an explicit request. The EP04 reference scaffold predates the avatar: when copying it for a new episode, add the component and envelope step. Remotion `<Folder name>` accepts only `a-z A-Z 0-9 -`.
10. **Captions.** Generate `src/captions.json` and the SRT from the same timeline. Preview-timing cues are **estimated**; after real WAVs exist, validate cues against the audio (forced alignment or human check) before upload.
11. **Release gate.** Final publish-ready only after authorized VoiceStudio audio, full visual inspection, source facts reviewed, speech-aligned subtitles, title, thumbnail, 10-second pause, and human editorial approval. Otherwise mark status `REVIEW ONLY` and identify blockers. GitHub source commits and publishing a YouTube video are different actions.

## Project structure and tools
- **Reference episodes** (all under `examples/`):
  - `leetcode-4-median-of-two-sorted-arrays` — **current standard** (EP04): complete layout, 2 official examples, rejected approaches + invariant proof, QA scripts, tests, docs. Start new episodes from this one.
  - `leetcode-44-wildcard-matching` — extended publishing tooling (`publish/`, audio manifests, frame QA, contact sheets).
  - `leetcode-10-regular-expression-matching` — original, smaller scaffold.
- **EP04 layout** (copy this shape):
  - `code/solution.py`, `code/trace.py` — algorithm and grounded execution trace.
  - `tests/test_solution.py`, `tests/test_episode.py` — official/edge/differential tests; story-order, stats attribution, 300-frame pause, 18–25 min and three-challenge gates.
  - `scripts/config.py` — **the only place with episode-specific names** (`AUDIO_SLUG`, `OUT_PREFIX`, `REVIEW_MP4`) and the portable font lookup `find_font()` used by `qa.py` and `render_visual_review.py`. Override fonts with `KIEU_FONT_REGULAR`, `KIEU_FONT_BOLD`, `KIEU_FONT_MONO` (absolute TTF/TTC paths). Default search: DejaVu (Linux/macOS/Windows locations), then macOS Arial Unicode / Menlo. Arial Unicode has no bold weight; macOS Arial Bold lacks `⁶` and `⇒`, so it is not used. Install DejaVu Sans on the render machine for the intended look.
  - `requirements.txt` — Python deps for QA/preview (`fonttools`, `pillow`); `qa.py` exits with an install hint if `fontTools` is missing.
  - `scripts/episode.py` — scene list `S` (`Scene(id, phase, title, lines, script, min_seconds, mode, silent, trace)`); one narration script and visual definition per scene.
  - `scripts/build_timeline.py [--preview]` — writes `src/timeline.json`, `src/captions.json`, `output/*.srt`, `output/timeline_report.json`; without `--preview` it requires per-scene WAVs.
  - `scripts/voicestudio.py --check | --voices | --synthesize` — strict local adapter.
  - `scripts/qa.py` — machine-readable `output/QA_results.json` (needs `fontTools`); `scripts/render_visual_review.py` — offline storyboard.
  - `src/Episode04.tsx`, `src/root.tsx`, `src/index.ts` — Remotion scenes (composition `EP04-Median`, 1920×1080, 30 fps).
  - `docs/SOURCE_MANIFEST.json`, `docs/QA_REPORT.md`, `docs/CHAPTERS.md`, `docs/YOUTUBE_METADATA.md`.
- **Skill scripts** (this folder):
  - `scripts/audit_episode.py --episode <ep>/scripts/episode.py [--examples N]` — structure audit. The official example count is read from `docs/SOURCE_MANIFEST.json` (or `--examples`); scenes must use modes `ex1…exN`. Fails if the count is unknown.
  - `scripts/check_glyphs.py --font <ttf> --episode <ep>/scripts/episode.py` — glyph coverage.
- **Pipeline** (inside the episode folder):
  ```bash
  python3 -m pip install -r requirements.txt
  python3 -m unittest discover -s tests -p 'test_*.py' -v
  python3 code/trace.py
  python3 scripts/build_timeline.py --preview        # estimated timing, silent
  python3 scripts/qa.py
  npm install
  npm run voice:check && npm run voice:voices
  export VOICESTUDIO_VOICE_PROFILE='<exact voice ID>'
  npm run voice:generate
  npm run render:release                              # candidate MP4, not approved
  ```
  VoiceStudio defaults to `http://127.0.0.1:3900` (override `VOICESTUDIO_BASE` with another *local* port; `VOICESTUDIO_MODEL` defaults to `tts-1`). Generated MP4/WAV/`output/*` are git-ignored; keep only `.gitkeep` placeholders.
- For a new episode, copy the EP04 folder to `examples/leetcode-<N>-<slug>/` and replace algorithm, examples, constraints, visual states, metadata, sources, narration, subtitles, chapters, thumbnail and tests; edit `scripts/config.py`, then rename the Remotion composition id (`src/root.tsx`), the component/file `Episode04`, and the `package.json` name and render targets to match. `scripts/` itself no longer hardcodes the episode. Do **not** simply rename the episode. The example is a scaffold, not a generic LeetCode parser; scene modes (`ex1…exN`, `hints`, `think`, `code1`, `practice`, …) are what the audit and Remotion switch rely on.
- The user may specify a different pause duration. Unless overridden, the standard is **10 seconds**.

## How to invoke
Ask Codex or Claude Code: “Use the kieu-leetcode-video skill to build a problem-solving video for LeetCode #N, showing all official examples, verified statistics, a 10-second thinking pause, VoiceStudio voice, and QA results.”

## Outputs
1. A `REVIEW` MP4 (or approved final video) and scene/source manifest.
2. `code/solution.py`, execution traces and tests.
3. Remotion scene project, VoiceStudio WAVs/timestamps where available, subtitles, thumbnail, and upload metadata (title, description, chapters).
4. `docs/QA_REPORT.md` and `output/QA_results.json` with every check marked PASS / FAIL / NOT RUN / BLOCKED and the release status.

## Fail-closed checks
- An unverified acceptance statistic is not a valid fact; unverifiable absolute counts are omitted, not guessed.
- A source screenshot being available does not grant redistribution rights.
- A silent pause shorter/longer than ten seconds fails unless expressly overridden.
- Missing VoiceStudio audio means **not publish-ready**; an unreachable VoiceStudio endpoint in a sandbox says nothing about the user's machine — report it as BLOCKED, not as a pass or a fallback.
- A generated MP4 with guide audio, or the silent offline storyboard, remains a **review**.
- Estimated subtitles are not audio-aligned subtitles.
- Anything not actually run is reported as NOT RUN, never as passed.
