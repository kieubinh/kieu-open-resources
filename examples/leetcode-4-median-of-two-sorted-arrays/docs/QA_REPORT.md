# Kieu Studio EP04 — QA report (28 October 2026)

## Overall status: **REVIEW ONLY**

Full visual review: `output/EP04_MEDIAN_VISUAL_REVIEW_ONLY.mp4`, **1280×720 / H.264 / 2 fps**, 1449.0 s (24:09). This is an **offline storyboard review**, not a Remotion render, and has **no audio stream**. The editable Remotion target is **1920×1080 / 30 fps**.

| Validation | Result | Evidence / limitation |
|---|---|---|
| Official question / examples | PASS | Both official LeetCode examples used verbatim for inputs and outputs. |
| Difficulty | PASS | `Hard` directly from LeetCode. |
| Acceptance snapshot | PASS (dated only) | 46.4% from Leetbot dataset last updated 2026-09-04. Not the live rate. |
| Accepted / total submissions | NOT VERIFIED | No reliable dated absolute pair found; both intentionally omitted rather than fabricated. |
| All official examples | PASS | 2/2 and outputs `2.0` / `2.5`. |
| Algorithm correctness | PASS | 20,000 seeded randomized differential tests against sorted-merge oracle plus official/edge cases. |
| Complexity | REVIEWED | O(log(min(m,n)+1)) time, O(1) additional memory. |
| Hints before reveal | PASS | Three hints before thinking pause. |
| Exactly one 10-second silent pause | PASS (timeline) | 300 source frames at 30 fps. Audio and subtitle cues absent. Offline 2 fps preview displays countdown but has no voice at all. |
| Story structure | PASS | Rejected approaches → proof → pseudocode → Python 3 → narrated trace script → three transfer exercises. |
| Vietnamese & math glyphs | PASS (local available font) | DejaVuSans Regular and Bold cover all 183 distinct characters in narration and graphics. Must check fonts again on final render machine. |
| Captions / timeline | PASS (structure) | `src/captions.json` and SRT generated from same source; timing approximate until local speech is aligned. |
| H.264 review MP4 | PASS | `ffprobe` reports a valid video stream, 1280×720 at 2 fps, 24:09. |
| Contact-sheet spot check | PASS (automated extraction and visual review in this session) | Includes constraints, both examples, hints, countdown, proof, code and ending. Not a full editorial watch. |
| VoiceStudio localhost reachability | BLOCKED | `http://127.0.0.1:3900` is unreachable **from this execution container**. Does not establish the status of VoiceStudio on the user's computer. |
| Per-scene VoiceStudio WAVs | BLOCKED | 0 of 30 narration WAVs; no substitute TTS was used. |
| Remotion runtime / final render | BLOCKED | `npm install --offline` failed because dependencies are not cached; no full Remotion render executed. |
| Spoken Vietnamese / lip or audio sync | NOT RUN | Requires the local VoiceStudio WAVs and listening to the final render. |
| Text clipping in full Remotion export | NOT RUN | Offline PIL preview checks text wrapping; 100% original Remotion frames need inspection. |
| Human editorial approval | NOT RUN | Required before release. |

**Publish gate:** BLOCKED. Do not publish the review MP4 as a finished episode. Generate valid VoiceStudio voice assets, build the timeline using actual WAV durations, render in Remotion, inspect captions/timing, then obtain editorial approval.

See `output/QA_results.json` for machine-readable results and `docs/CHAPTERS.md` for scene timing.
