# QA report - GitHub Radar GR01-GR03

Status: **REVIEW ONLY**. Per-video results are written to `output/QA_results.json` by `KIEU_EPISODE=<id> npm run qa`; anything not run is NOT RUN.

| Check | Status | Note |
| --- | --- | --- |
| Unit tests (11), skill audit | PASS | one repo per video, nine beats, caveat in every `value`, numbers on screen equal `SOURCE_MANIFEST.json`, default speed 1.0 |
| Glyph coverage (regular/bold/mono) | PASS (GR01 run) | Vietnamese comments in terminal blocks render in the sans stack |
| Runtime bounds (2-8 min) | PASS | preview estimates 3.76 / 3.80 / 3.81 min |
| Avatar geometry (220 / 64 / 4 px, bottom-right) | PASS (unit test + rendered frames) | audio-reactive, not lip-synced |
| VoiceStudio WAVs (Narrator 03, 1.0x) | NOT RUN until generation finishes | local engine, resumable `npm run voice:generate` |
| Avatar envelope from real audio | NOT RUN | preview uses a text-based estimate |
| Captions aligned to real audio | NOT RUN | cues are estimated from text |
| Facts re-verified on publish date | NOT RUN | numbers are a 2026-10-29 snapshot |
| Human editorial approval | NOT RUN | owner |

Known limits: Trending gains are Trending-reported (stargazers API returned 404, no independent history); claude-mem has no weekly figure on the weekly Trending page, so only monthly/today values are shown.
