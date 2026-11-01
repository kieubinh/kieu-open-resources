# EP03 sources and evidence

## Official problem (LeetCode #44, Hard)

Page read on **28 October 2026**: https://leetcode.com/problems/wildcard-matching/

| Item | Value used in the episode |
|---|---|
| Statement | `s` and a pattern `p`; `?` matches any single character; `*` matches any sequence of characters, including the empty sequence; the match must cover the **entire** string |
| Example 1 | `s = "aa"`, `p = "a"` → `false` |
| Example 2 | `s = "aa"`, `p = "*"` → `true` |
| Example 3 | `s = "cb"`, `p = "?a"` → `false` |
| Constraints | `0 <= s.length, p.length <= 2000`; `s` lowercase English letters; `p` lowercase English letters, `?` or `*` |
| Difficulty | Hard |
| Statistics shown on the page | 967,654 accepted submissions of about 2.9M; acceptance 33.1% (the page shows rounded totals) |

The statistics are a **snapshot** and change continuously. They count **submissions**, not people. The video says so and shows the date.

All three official examples are executed by the real solution (`scripts/solution_test.py`, `src/data/verification.json`).

## Hints

The three hints in the episode are written by Kieu Studio. They are not LeetCode's official hints.

## Practice problems

| Problem | Difficulty label | Status |
|---|---|---|
| #392 Is Subsequence | Easy | page read on 28 Oct 2026 |
| #72 Edit Distance | Medium | page read on 28 Oct 2026 |
| #10 Regular Expression Matching | Hard | taken from the EP02 docs in this repository; the page could not be fetched during the EP03 session, so re-check before publishing |

## Algorithm evidence (all produced by code in this folder)

- `scripts/build_trace.py` runs the real `Solution.isMatch` under `sys.settrace` and writes `src/data/trace.json` (execution steps, events, DP table, call tree, blow-up measurements). The Remotion scenes only draw this data.
- `scripts/oracles.py` provides three independent reference implementations: a regular-expression translation, a 2-D DP table and naive recursion.
- `scripts/run_verification.py` writes `src/data/verification.json` (exhaustive, random, worst-case and typical-case runs).
- `scripts/solution_test.py`, `scripts/episode_test.py`, `scripts/timeline_test.py`: 38 unit tests, run by `npm test`.

Numbers shown in the video as **measured** (`ĐO`) come from those runs. The DP memory/time figures are labelled **theory** (`LÝ THUYẾT`).

## Narration

Voice: local VoiceStudio, profile "Narrator 03 · Trầm chững chạc (synthetic)", model `voxcpm2`, language `vi`, fixed seed, natural voice speed (1.0×; the first review render used a 1.25× ffmpeg speed-up, removed after viewer feedback that it was too fast). No other TTS provider was used or substituted. The raw per-sentence audio is cached under `public/audio/ep03-voicestudio/raw/` (git-ignored) and keyed by a hash of voice + seed + model + language + spoken text; `audio_manifest/` records the hashes and measured beat offsets.

## Assets

- Fonts: Noto Sans and JetBrains Mono variable fonts (SIL Open Font License; license texts are in `public/fonts/`).
- Kieu Studio logo: raster crops from the existing brand assets (`public/brand/`). A vector master was not available.
- No official LeetCode screenshots or audio are included.
