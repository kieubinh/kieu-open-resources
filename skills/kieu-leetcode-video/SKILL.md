---
name: kieu-leetcode-video
description: Produce and QA Kieu Studio educational LeetCode videos that teach problem-solving skills, with all official examples, approachable algorithm animations, a ten-second thinking pause, Python 3, local VoiceStudio narration, Remotion, and a publishing checklist. Use for new episodes or revisions of the Kieu Studio / The Art of Coding series.
---

# Kieu Studio — LeetCode Problem-Solving Video Factory

## Purpose (non-negotiable)
LeetCode is **practice material**; the outcome is **a stronger problem-solving process**, not copying code. Start every episode with a meaningful Kieu Studio introduction, then model the habits: **understand → hypothesize → test → reflect**. Show code only once the viewer understands the underlying decisions.

## Required episode workflow
1. **Ground the source.** Open the exact LeetCode problem. Record problem number, title, difficulty, all examples, input/output, constraints, documented operators, and source URL. Never invent or paraphrase away a required constraint. Use only short quotations from the original, attribution and paraphrases otherwise. Never publish full screenshots/official illustrations in this open-source repo without rights review.
2. **Verify time-sensitive metrics.** Record acceptance rate, accepted *submissions* and total submissions from a dated reliable snapshot. Never call submission attempts “people who solved it”; omit unsupported statistics. Put snapshot date/source in the video or documentation.
3. **Write scenes in a pedagogical order.** First Kieu Studio mission and episode hook; problem statement; difficulty/metrics and constraints; **every** official example with inputs, output and clear visual explanation; at least two hints; **exactly 10 seconds of silent, onscreen countdown**; solution discovery with a concrete decision visualization; avoid obscure data-structure jargon until introduced; pseudocode; Python 3 with highlighted execution; code verification; complexity; transfer to everyday problem solving; three related challenges. Make the transition from “thinking” to “solution” explicit.
4. **Design the visuals.** State variables must match actual code; no knowingly invalid states (e.g., a regex suffix containing standalone `*` shown as an ordinary valid state); every example illustration must match expected output. Prefer visual evidence (choices, branches, state transitions) over text cards. Never show “PREVIEW”, “GUIDE VOICE”, renderer watermarks or production notes in image frames.
5. **Build traces and test.** Validate official examples and edge cases. Differential-test Python 3 against an independent oracle when feasible. Test any DP table and branch labels against the exact state definition. Surface algorithm traces in captions/code highlights only if grounded by actual execution.
6. **Text quality gate.** Use fonts that cover all needed **Vietnamese accents and mathematical symbols** (`≤`, `≥`, `≠`, `→`, `×`, etc.). Run the bundled glyph test, inspect contact sheets, test a source frame at 100% width, and detect clipped titles/cards. Avoid replacing symbols with square glyphs. Apply a readable font-size minimum for YouTube mobile.
7. **VoiceStudio strict narration.** Generate a **separate WAV per scene** using the user's local VoiceStudio endpoint and an explicitly selected profile. Keep a hash of text/profile/model to invalidate outdated audio. Use each actual WAV duration to align scenes/subtitles; don't truncate. Do **not** silently substitute eSpeak/cloud TTS when VoiceStudio fails. A temporary guide-voice MP4 must be labeled **REVIEW ONLY**, never release-ready.
8. **Render and QA.** Prefer Remotion at 1920×1080, 30fps. Validate codec streams, run duration, read/speaker sync, countdown at 10.0 seconds of silence, no black tail, no text clipping; watch/listen to opening, all examples, hints, DP, ending. Optionally use the offline Python renderer for a low-fps storyboard/review if npm is unavailable, **not** as a guarantee of production animation quality.
9. **Release gate.** Final publish-ready only after authorized VoiceStudio audio, full visual inspection, source facts reviewed, subtitles, title, thumbnail, 10-second pause, and human editorial approval. Otherwise mark status `review` and identify blockers. GitHub source commits and publishing a YouTube video are different actions.

## Project structure and tools
- Example episode: `examples/leetcode-10-regular-expression-matching`.
- Reusable scripts: `scripts/audit_episode.py`, `scripts/check_glyphs.py` in this skill folder.
- Pipeline: `npm install`, `npm run studio` or `npm run voice:generate`, `npm run render:release` within example project. Set `VOICESTUDIO_VOICE_PROFILE` from a voice ID returned by `python3 scripts/voicestudio.py --voices`. VoiceStudio local defaults to `http://127.0.0.1:3900`.
- For a new episode, copy `examples/leetcode-10-regular-expression-matching` to a new folder and replace algorithm, examples, constraints, visual states, metadata, sources, narration, subtitles and tests; do **not** simply rename the episode. The example is a scaffold, not a generic LeetCode parser.
- The user may specify a different pause duration. Unless overridden, the standard is **10 seconds**.

## How to invoke
Ask Codex or Claude Code: “Use the kieu-leetcode-video skill to build a problem-solving video for LeetCode #N, showing all official examples, verified statistics, a 10-second thinking pause, VoiceStudio voice, and QA results.”

## Outputs
1. A `REVIEW` MP4 (or approved final video) and scene/source manifest.
2. `code/solution.py`, execution traces and tests.
3. Remotion scene project, VoiceStudio WAVs/timestamps where available, subtitles, thumbnail, and upload metadata.
4. A QA report with every check marked passed/failed/not run, and release status.

## Fail-closed checks
- An unverified acceptance statistic is not a valid fact.
- A source screenshot being available does not grant redistribution rights.
- A silent pause shorter/longer than ten seconds fails unless expressly overridden.
- Missing VoiceStudio audio means **not publish-ready**.
- A generated MP4 with guide audio remains a **review**.
