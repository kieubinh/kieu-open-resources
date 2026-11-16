---
name: kieu-ifelse-video
description: Make or revise a "Nếu Như" (What If) video for the @NeuNhuPhim channel - a faceless Vietnamese stick-figure short film that pushes one human ability to the extreme ("Nếu Trí Nhớ Của Bạn Mạnh Gấp 100 Lần?"), told in second person with real science and a human ending. Covers title and script rules, fact sourcing, local VoiceStudio narration at 1.1x with a blind check of every take, 2D Studio shots, render, mix, channel branding and Private upload. Use for new episodes, sequels, voice fixes, or "tạo video Nếu Như", "làm tập What If mới".
---

# Kieu If-Else Video — "Nếu Như" films

## Purpose (non-negotiable)
Each episode changes exactly one thing about the viewer's body or mind, follows the real consequences, and ends with a person, not a trophy. The power is fiction; everything around it is true and sourced. No invented studies, numbers or quotes. Disclose AI-assisted production on every upload.

## Setup gate (ask once, only what is missing)
- **Language:** ask first if the session has not settled it. Vietnamese is the channel default.
- **Topic:** a title the owner picked, or propose from `media/videos/neu-nhu/channel/titles-35.md`.
- **Series position:** standalone, or a sequel (read the previous script; EP01 ends by promising Phần Hai).
- **Studio:** the Thanh Hai Learn AI 2D Studio plugin must be installed (`references/production-pipeline.md`). This repository does not contain the kit. If it is missing, ask for the `.plugin` file.

## Workflow (each gate must pass before the next)
1. **Title.** Follow `references/script-playbook.md`. One change, starts with "Nếu", ends with "?", 6-10 syllables.
2. **Facts first.** List at least five checkable facts with sources in `docs/SOURCES.md` before the script. Mark anything not cross-checked. A number you cannot source gets written around.
3. **Script.** Write one spoken paragraph to `docs/script.txt` using the playbook's beats. Run `python3 scripts/audit_script.py docs/script.txt --title "..." --strict`.
4. **Approval.** Show title, rule, chosen beat, facts and script. Wait unless the owner already told you to go straight through. Changing the rule, the ending or a fact re-opens approval.
5. **Voice.** `voice.py --plan`, edit the ledger so no chunk breaks a thought, then `voice.py`. Fix every take the check reports (pipeline section 2). Speed is **1.1x**, applied once in `join_voice.py`.
6. **Shots.** Copy `assets/starter-project/` into the studio, replace story and scenes, draft with estimated timing, check the contact sheet (pipeline section 3).
7. **Build.** Run `scripts/build_episode.sh` in the background. It joins, aligns on the real voice, snaps word edges to the real pauses, renders, mixes and writes metadata.
8. **QA.** Re-run the blind check, look at a frame every 8-10 s, read the ASR diff for extra words (pipeline section 5). State what was not checked. Nobody has listened until a human says so.
9. **Release.** Only on request: `references/publish.md`. Upload means **Private**. Public and playlists are separate go-aheads. Committing is separate too.

## House rules
- Narration: local VoiceStudio only, Narrator 03 (`27ad8d83`), 1.1x, no fallback engine, no cloud TTS.
- Faceless: no Kieu speaking avatar on this channel, unlike other Kieu videos.
- 16:9, 1080p, 24 fps, style `dusk`, about 6 minutes at 1.1x, captions as an SRT rather than burned in.
- A review MP4 is never called publish-ready. The audio is not verified until a human has listened.

## Files
- `references/script-playbook.md`: title rules, beats, voice, facts, final checklist.
- `references/production-pipeline.md`: studio setup, voice checks, shots, build, QA, known failures.
- `references/publish.md`: channel branding safe areas and upload differences for this channel.
- `assets/starter-project/`: EP01 as a working template (cast, shot library, sets, shots, story tools, script, sources).
- `assets/episode.example.json`: per-episode voice, pause, mute and YouTube settings.
- `assets/brand/brand.js`: banner, logo and thumbnail shots.
- `scripts/audit_script.py`, `voice.py`, `join_voice.py`, `make_meta.py`, `patch_kit.py`, `build_episode.sh`.
- `NOTICE.md`: what is original here and what stays out of this repository.
- `scripts/snap_words.py`: moves ASR word edges onto the real pauses. `build_episode.sh` runs it.

## How to invoke
"Use the kieu-ifelse-video skill to make a Nếu Như episode: Nếu Bạn Không Bao Giờ Cần Ngủ?"
Vietnamese: "Dùng kieu-ifelse-video làm tập Nếu Như mới về giấc ngủ, cho mình duyệt kịch bản trước khi đọc giọng."

## Outputs
Episode folder: `docs/script.txt`, `docs/SOURCES.md`, `episode.json`, `audio/` with the ledger and `voice_qc.json`, `review.mp4`, `subtitles.srt`, `thumbnail_1280x720.png`, `YOUTUBE_METADATA.md`, `qa/` frames.
