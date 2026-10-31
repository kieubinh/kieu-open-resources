---
name: kieu-github-video
description: Produce and QA Kieu Studio "GitHub Radar" videos, ONE GitHub repository per video, about fast-growing useful repos - verified star-growth numbers, why the author built it, the concrete problem, how it works, how to use it, why it matters, caveats and application ideas - with local VoiceStudio narration at 1.0x, the circular speaking avatar (drawn or SadTalker lip-sync), Remotion, a one-minute vertical 9:16 YouTube Short per episode, thumbnails, and (only when the owner asks) YouTube upload, publish and playlist steps. Use for new episodes, Shorts, thumbnails or publishing of the Kieu Studio GitHub Radar series.
---

# Kieu Studio - GitHub Radar Video Factory

## Purpose (non-negotiable)
**One video introduces exactly one GitHub repository** (owner rule, 2026-10-30). Several candidates become several videos in a series (`GR01`, `GR02`, ...), never a roundup; a recap may mention the other episodes only by name.

Help viewers **decide whether a tool deserves their time**, not hype it. Star counts measure attention, not quality, so every repo gets the same structured treatment, including *what to be careful about*. Keep the Kieu Studio look and rules of `kieu-leetcode-video` (same palette, header `KIEU STUDIO / <SERIES>`, `kieu.app` upper right, progress bar, Vietnamese-capable fonts, strict local VoiceStudio, REVIEW-only until approved).

## Required episode workflow
1. **Find candidates by growth.** Read `https://github.com/trending?since=weekly`, `...monthly` and `...daily`, and the GitHub REST API (`gh api repos/<owner>/<repo>`). Record, per repo and with the snapshot date: total stars (API), gain per window (Trending), forks, licence, created/pushed dates, owner type. Mark Trending numbers as **Trending-reported, not independently reconstructed**. If the stargazers endpoint is unavailable, do not fake a history. Compute only derived values that follow arithmetically (previous = total - gain; average per day = gain / days) and label them derived. Never invent a number missing from a source; omit it (set `null`).
2. **Vet before choosing.** Keep a repo only if it has an identifiable owner, an explicit licence, a README that explains how it works, recent commits and no signs of being a star-farm, impersonation, malware bait or an unverifiable "free and unlimited" offer. Pick the strongest candidate for each video; for a series prefer **different problems** and growth profiles (very fast new repo, large established repo). Record skipped repos without defaming them (state that criteria were not met or could not be checked). Do not feature tools that only help defeat others' safeguards or privacy.
3. **Ground each repo.** Read the README (`gh api repos/<r>/readme -H "Accept: application/vnd.github.raw"`), the author's own write-ups (blog, docs) and the install commands. Put facts, sources and **author claims vs verified facts** in `docs/SOURCE_MANIFEST.json`. Short paraphrases only; no copied README text, screenshots or logos (`licensing.official_images_included` stays `false`).
4. **Storytelling arc (nine beats, one repo, ~4-5 min at 1.0x)** - write it as a story, not a README read-out.
   - `intro`: **cold open** - a relatable scene or question the viewer has lived ("Hãy tưởng tượng...", "Bạn đã bao giờ..."), then the series greeting, then what the repo is, owner, licence, created date; promise that the numbers are surprising. Visual: radar sweep + the question + four info chips. **Close this question in the `outro`.**
   - `growth`: total stars, value 30 days ago, gain, and the **shape** of growth. Only use points you have: 30 days ago = total - month gain, 7 days ago = total - week gain, today = total. Chart these as a 2-3 point line from a **zero baseline**; label per-day rates between points as derived; never draw a daily curve you do not have; say when Trending lists no weekly figure. Add a relatable rate ("cứ ~38 giây có 1 sao"). End with an open question into `why`.
   - `why`: the author's pain as a picture (context filling up, identical AI-slop pages, a goldfish agent), from their own words; end by asking how it can be solved.
   - `problem`: before/after illustration of the concrete problem; each idea is shown, not listed.
   - `how`: six-node animated pipeline with icons and a travelling packet.
   - `usage`: typed terminal commands beside a schematic result (no fake numbers or real screenshots); state the one condition people skip.
   - `value`: a balance - benefits vs cost - with the caveat strip.
   - `ideas`: four pictogram tiles with a call to start small.
   - `outro`: **answer the opening question**, who should try it and how, the snapshot-date warning, and a one-line teaser for the next episode.
   Rules: every scene ends by handing the viewer to the next one; at most one short chip line of text per visual; narration spells numbers out in words; digits only on screen; illustrations are original drawings (no third-party logos/screenshots).
5. **Honesty gates.** Say where each figure comes from and its date. Distinguish what the authors claim ("README estimates ~10x") from what you verified. Mention data-collection, hooks that run commands, hosted/sign-in defaults and sandbox requirements whenever the README says so. Do not give investment advice; do not present a tool as endorsed by Kieu Studio unless actually tested - label tested/untested.
6. **Voice.** Local VoiceStudio only, endpoint must be `127.0.0.1`/`localhost`, voice ID must be returned by `--voices`. Vietnamese default: Narrator 03 (`27ad8d83`). **Speed is 1.0x (normal) unless the user asks otherwise**; apply `atempo` once, only for a non-1.0 request. One WAV per scene; SHA-256 of text+voice+model+speed invalidates stale audio; timeline = actual WAV duration + 0.6 s. No eSpeak/cloud fallback: `VOICE GATE BLOCKED; no fallback`. Voice and avatar are synthetic: disclose in the description.
7. **Speaking avatar (every Kieu video).** Small circular avatar at the bottom-right, ring like an AI voice that is speaking. Approved geometry at 1920×1080: 220 px circle, 64 px right/bottom margins, 4 px cyan `#72dce0` ring; extra halo rings, glow, subtle head scale and a 5-bar equalizer follow the **measured loudness of the real narration WAV** (`scripts/make_envelope.py`). Keep the avatar idle (no halo/bars) in silent moments. Keep subtitles clear of it (`right ≥ 330 px`). Use `assets/SpeakingAvatar.tsx`.
   - **Lip-sync (mouth follows the spoken sound):** `prepare_avatar.py` also writes `public/brand/kieu-avatar-nomouth.png` (lips inpainted with OpenCV) and `src/avatar.mouth.json` (mouth anchor); `scripts/make_envelope.py` measures, per video frame from the real WAVs, mouth **opening** (loudness + open-vowel band; silence = closed lips) and lip **spread** (high-frequency share: i/e wide, o/u rounded) into `src/mouth.json`; the component draws the lips/teeth/tongue as SVG on the mouthless face. It is audio-driven articulation of a drawn mouth, not a neural model and not phoneme-exact; for photoreal lip-sync install the approved SadTalker checkpoints in `kieu-studio` and use its overlay instead (never both). Needs numpy + opencv-python-headless (`npm run setup` creates `.venv`). Generated `src/timeline.json`, `captions.json`, `envelope.json`, `mouth.json` are git-ignored: run `npm run timeline:preview` first. A custom portrait needs `--mouth cx,cy,width[,tilt]` (landmark detection was not installed).
   - **Photoreal lip-sync (SadTalker, optional but preferred when time allows):** with the approved checkpoints installed in `kieu-studio/tools/sadtalker-local` (README there lists URLs and SHA-256; download into a fresh folder, verify hashes, then move in), run `npm run lipsync` (`scripts/make_lipsync.py`): it joins the scene WAVs into one narration track padded to the timeline, runs kieu-studio's resumable chunked worker (256 px, 25 fps, MPS; expect hours of compute per video) and writes `public/lipsync/<ep>.mp4` (git-ignored). `npm run render:release` (`scripts/render.py`) then plays that video in the avatar circle instead of the drawn mouth (set `KIEU_LIPSYNC=drawn` to force the drawn one). Never combine both; the WAVs stay the only soundtrack. Use only the approved portrait.
   - Source image: `scripts/prepare_avatar.py --project <ep>` crops the approved Kieu Studio avatar (`kieu-studio/studio/assets/avatar_source.png`) into `public/brand/kieu-avatar.png`. To base it on founder **Anthony Kieu**'s likeness use `--image <photo or approved portrait>` (consent: only an image the founder supplied/approved).
   - **Never commit the portrait** (`public/brand/*` is git-ignored); `src/avatar.mouth.json` holds coordinates only.
   - Audio-reactive halo, glow and equalizer stay as before. For true mouth motion beyond this, see the SadTalker note above.
8. **Text and visuals.** Fonts must cover Vietnamese accents and symbols (`→ ✓ ✗ ⚠ ≈ ·`); run the glyph check on the final render machine; minimum ~27 px body text on 1080p; nothing under the avatar (visual area ends at y = 796); no production notes, "PREVIEW" or watermarks in frames; no third-party screenshots.
9. **Illustration QA.** Render one still per scene (`remotion still`) and inspect a contact sheet: no text overflowing a chip, nothing under the avatar (y ≥ 796 in the visual area), charts start at zero, every icon visible, labels readable at phone size.
9b. **Render and QA.** Remotion 1920×1080 30 fps. The Remotion `Folder` name may contain only `a-z A-Z 0-9 -` (a name with spaces/dashes like "Kieu Studio — X" throws at bundle time). Check: duration 2–8 min at 1.0x (target 3–5), `lipsync_mouth_track` PASS, stills of closed / mid / wide-open / spread mouth, audio present in every non-silent scene, captions generated from the same timeline (estimated until aligned to real audio), no black tail, avatar visible and circular in the corner for the whole video, contact sheets of every scene type, listen to opening, each repo's `how` and `value` scene, and the ending.
10. **Release gate.** Publish-ready only after VoiceStudio audio, full visual inspection, source facts re-checked on the publish date (numbers go stale quickly), human editorial approval, title/thumbnail/description. Otherwise `REVIEW ONLY` with blockers listed. Source commits and YouTube publishing are separate actions.

## Thumbnails and publishing to YouTube (only on the owner's request)
Read `references/youtube-publish.md` before touching YouTube. Summary:
- Each full video needs a 1280x720 thumbnail (`assets/thumb.tsx` + `assets/thumb-index.ts`, a separate Remotion entry), a title <= 100 chars (hook question + fix + `| GitHub Radar #N`), a description with real chapters (`scripts/youtube_chapters.py`), caveat, data sources with the snapshot date, AI disclosure and hashtags, and 9-11 tags. Keep them in `docs/YOUTUBE_METADATA.md`.
- **Upload means Private.** Making it public, and creating or filling a playlist, are separate explicit requests. Always declare **altered or synthetic content: Yes** (AI voice and avatar) and "not made for kids". Studio pre-selects Public at the visibility step: click Private before Save.
- The Chrome bridge moves at most 10 MB per `file_upload` call: `scripts/split_for_upload.sh` splits the MP4, the parts are collected in the Studio page and re-assembled there (recipe in the reference). Verify the summed bytes equal the file.
- Playlist: `GitHub Radar · Tiếng Việt`, public, oldest first, language Tiếng Việt; add every episode and Short.
- After any publish, tell the owner what was not verified (audio not listened to, numbers not re-checked on the publish date).

## One-minute vertical Short (9:16) for YouTube Shorts
Every episode also gets a Short: `KIEU_FORMAT=short` (owner request 2026-10-30: vertical 9:16, at most 60 s).
- **Cut, do not squeeze.** Seven beats: intro (hook question + repo), growth, why (carries the problem), how, usage, value (caveat stays), outro (closes the hook). `problem` and `ideas` are dropped. Visuals, chart points, steps, commands and the caveat are taken from the full episode's scenes by id (`scripts/shorts.py`), so a number cannot differ between the video and its Short. Only the narration is rewritten, shorter.
- **Budget.** Narrator 03 at 1.0x speaks about 2.9 words/s (English product names are slow): about 150-160 words, 0.4 s tails. Dates stay on screen (the growth note), not in the narration. Always measure the real WAVs; `build_timeline.py` refuses more than 60 s.
- **Canvas.** `GitHubRadarShort` composition, 1080x1920, `src/GitHubRadarShort.tsx` + `src/artV.tsx`. Shorts UI safe zone: content inside x 40..960 (right buttons) and above y 1575 (title/channel overlay). Body text >= 27 px, captions 38 px, phone-sized. The 190 px avatar (same ring) sits bottom-right of the safe zone (`right: 120, bottom: 345`); captions end above it.
- **Commands.** `KIEU_FORMAT=short KIEU_EPISODE=gr01 npm run voice:generate`, then `npm run render:release` and `npm run qa` (outputs `GR01_SHORT_*`, composition `GitHubRadarShort`). SadTalker: `npm run lipsync` after `build_timeline.py` (face file `public/lipsync/gr01_short.mp4`; narration is built from `output/<PREFIX>_timeline.json`, so it does not depend on the shared `src/` files). Audit: `audit_episode.py --episode <ep>/scripts/episode.py --short`.
- **Never** present a Short as publish-ready: same release gate as the full video. Upload a Short like a full video (reference), then add it to the playlist.
- Example length check from GR01-GR03: 158-160 words gave 54-59 s with 0.4 s tails; 183+ words overran 60 s.

### English cut of a Short and one-page cheat sheets (owner request 2026-10-31)
The owner found Shorts work far better than long videos and asked for English Shorts in their own playlist, plus a one-page PDF cheat sheet per Short in both languages.
- **English cut.** `KIEU_FORMAT=short KIEU_LANG=en KIEU_EPISODE=gr01` (`config.py` refuses `KIEU_LANG=en` without `KIEU_FORMAT=short`). Narration lives in `shorts.py` `_EN_TEXT`, on-screen text in `_EN_VISUAL`; outputs use `OUT_PREFIX` `GR0N_SHORT_EN`, face file `grNN_short_en.mp4`, voice **Kieu Studio English B** (`823d23e3`). English B speaks only about **2.0 words/s** (Vietnamese 2.9), so a 60 s Short needs **90-103 words**: a first draft of 143 words ran 72 s. `audit_episode.py --short --lang en` uses that rate. Measure the real WAVs, trim, and re-synthesize (the WAV cache is keyed by text, so only changed scenes are redone).
- **Portrait art is bilingual.** `src/artV.tsx` wraps every static string in `pick(lang, vi, en)` and formats numbers per language (`1.040` vs `1,040`); a new illustration string needs both.
- **Cheat sheets.** `python3 scripts/cheatsheets.py` (in the example) builds six A4 PDFs (`GR0N_<repo>_cheatsheet_{vi,en}.pdf`) from `docs/SOURCE_MANIFEST.json` and the same scene data as the video, via headless Chrome. They must be exactly one page, say whether Kieu Studio tried the tool (GR01-GR03: not tried), and are hosted in the public repo under `docs/cheatsheets/github-radar/` (PR, owner merges). Put the link in the description (`📄 Cheat sheet PDF (1 page, English): <url>`, after the repo line) and in a first comment from the channel; check the URL returns 200 before posting it.

## Operating lessons (learned building GR01-GR03)
- **Compute is the bottleneck.** VoiceStudio takes ~1-2 min per scene; SadTalker on MPS needs about 30-40 s of compute per second of video (a 4.5 min episode is 2-3 h, a 1 min Short ~40 min). Run the long jobs in the background, sequentially (voice and SadTalker together slow each other down), and let them resume: finished WAVs and SadTalker chunks are cached by hash.
- **SadTalker crashes on a sub-second last chunk** (`IndexError` in `generate_blink_seq_randomly`) when the narration length is 30 s x N + under ~1 s. `kieu-studio/studio/avatar.py` pads any chunk shorter than `MIN_CHUNK_SECONDS = 4` with silence and trims the video back (a local patch to kieu-studio; keep it, and re-apply it if the file is replaced). Pad with `-t max(chunk, 4)`, not `-t chunk`, or the pad is cut off again.
- **Shared generated files.** `src/timeline.json`, `captions.json`, `envelope.json`, `mouth.json` belong to one episode and one format at a time. Never rebuild them for another episode while a render or QA that reads them is running; `make_lipsync.py` reads `output/<PREFIX>_timeline.json` instead, so SadTalker may run while you work on `src/`.
- **Background waits.** `until ! pgrep -f "<name>"` matches its own shell command line and never ends; wait on a log line, a file, or `pgrep -x`.
- **Chrome bridge limits** and Studio defaults: see the YouTube reference.
- **Re-check after every format change**: render one still per scene type for every episode (contact sheet), not only the first.

## Project structure (copy `examples/github-trending-2026-10-29/`)
- `scripts/episode.py` - `EPISODES = {gr01: [...9 scenes], gr02, gr03}`, selected with `KIEU_EPISODE` (`Scene(id, phase, title, lines, script, mode, repo, beat, data)`); `scripts/config.py` - voice, speed (`KIEU_VIDEO_SPEED`, default 1.0), runtime bounds, output prefix.
- `scripts/shorts.py` (one-minute cuts built from the full scenes), `src/GitHubRadarShort.tsx` + `src/artV.tsx` (9:16 layout).
- `scripts/build_timeline.py [--preview]`, `scripts/make_envelope.py [--preview]`, `scripts/voicestudio.py --check|--voices|--synthesize [--only ids]`, `scripts/qa.py`.
- `src/GitHubRadar.tsx` (modes: intro=RadarIntro, growth1=GrowthChart, story=StoryArt, flow=FlowDiagram, usage=UsageScene, value=ValueScale, ideas=IdeaTiles, outro=OutroScene), `src/art.tsx` (hand-drawn SVG icon set + per-repo illustrations), `src/theme.ts`, `src/SpeakingAvatar.tsx`, `src/root.tsx`, `src/index.ts`.
- `docs/SOURCE_MANIFEST.json`, `docs/QA_REPORT.md`, `docs/YOUTUBE_METADATA.md`, `tests/test_episode.py`.
- `src/thumb.tsx`, `src/thumb-index.ts` (thumbnails).
- Skill scripts: `scripts/audit_episode.py --episode <ep>/scripts/episode.py [--short]` (structure audit), `scripts/prepare_avatar.py`, `scripts/make_lipsync.py`, `scripts/youtube_chapters.py`, `scripts/split_for_upload.sh`; `assets/SpeakingAvatar.tsx` (props `diameter`, `right`, `bottom` for the Shorts safe zone), `assets/thumb.tsx`, `assets/thumb-index.ts`; `references/youtube-publish.md`.

```bash
npm install
npm run avatar                    # prepare public/brand/kieu-avatar.png (git-ignored)
npm test                          # structure + facts + gates
npm run timeline:preview && npm run studio
npm run voice:check && npm run voice:voices && npm run voice:generate
npm run render:release            # candidate MP4, not approved
```

## How to invoke
"Use the kieu-github-video skill to pick one fast-growing useful GitHub repo and build a Vietnamese GitHub Radar video about only that repo, with growth numbers, why-built, problem, how it works, usage, value, caveats and ideas." Then, only if asked: "make the 9:16 one-minute Short", "make the thumbnail and upload it Private", "make it public and add it to the GitHub Radar playlist".

## Fail-closed checks
- Any figure without a source and snapshot date is omitted, not guessed. Trending-reported ≠ independently verified.
- A repo missing licence/owner/README evidence is not featured.
- A video that introduces more than one repo fails the audit. A `value` scene without a caveat fails the audit.
- Narration speed other than 1.0x without a user request fails.
- Missing avatar image, or an avatar outside the bottom-right 220 px circle spec, fails QA.
- Missing VoiceStudio audio means not publish-ready; an unreachable endpoint is BLOCKED, not a pass.
- A Short over 60 s, outside the 1080x1920 safe zone (x 40..960, y < 1575), with different numbers from its full episode, or without the caveat fails.
- Uploading, publishing and playlists happen only on the owner's explicit request; uploads are Private until told otherwise; AI-content disclosure is always Yes.
- Anything not actually run is reported as NOT RUN.
