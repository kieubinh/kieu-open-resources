# Kieu Studio - GitHub Radar (snapshot 2026-10-29)

Reference series for the `kieu-github-video` skill. **One video = one repository**, same nine beats each time: intro → growth numbers → why the author built it → concrete problem → how it works → how to use it → why it helps (with caveats) → application ideas → verdict. Each video is about 3.5-4 minutes at normal 1.0x speed.

| Video (`KIEU_EPISODE`) | Repo | Problem it targets | Stars (API) | 30-day gain (Trending) |
| --- | --- | --- | --- | --- |
| `gr01` | `cloudflare/security-audit-skill` | trustworthy, verified security audits by a coding agent | 52,530 | +28,617 (week +16,002) |
| `gr02` | `pbakaus/impeccable` | vague design instructions and "AI slop" in generated UIs | 94,784 | +19,821 (week +7,283) |
| `gr03` | `thedotmack/claude-mem` | agents forgetting everything between sessions | 104,433 | +9,592 (today +459) |

Growth windows are **Trending-reported**, not independently reconstructed (see `docs/SOURCE_MANIFEST.json`). Numbers go stale fast: re-check on the publish date.

## Pipeline (per video)
```bash
python3 -m pip install -r requirements.txt && npm install
npm run avatar                  # public/brand/kieu-avatar.png (git-ignored)
npm test
export KIEU_EPISODE=gr01        # gr01 | gr02 | gr03
npm run timeline:preview        # estimated timing + estimated avatar envelope, silent
npm run voice:check && npm run voice:voices
npm run voice:generate          # local VoiceStudio, Narrator 03 at 1.0x (KIEU_VIDEO_SPEED to override)
npm run render:release          # real WAV timeline + measured envelope -> output/GR01_VOICESTUDIO_CANDIDATE.mp4
npm run qa
```

## One-minute vertical Short (9:16)
```bash
export KIEU_FORMAT=short KIEU_EPISODE=gr01     # gr01 | gr02 | gr03; unset KIEU_FORMAT for the full video
npm run voice:generate && npm run render:release && npm run qa   # -> output/GR01_SHORT_VOICESTUDIO_CANDIDATE[_SADTALKER].mp4 (1080x1920, <= 60 s)
npm run lipsync                                                   # optional SadTalker face -> public/lipsync/gr01_short.mp4
```
Same repo, numbers and caveat as the full video (`scripts/shorts.py` reuses the full scenes' visuals); shorter narration, seven beats. Layout stays inside the YouTube Shorts safe zone (x 40..960, y < 1575).

## Speaking avatar
Small circle at the bottom-right (220 px, 64 px margins, 4 px cyan ring) with a halo and a five-bar equalizer that follow the loudness of the narration actually heard. It is audio-reactive, not lip-synced. Image from `skills/kieu-github-video/scripts/prepare_avatar.py` (the approved Kieu Studio avatar, or `--image <portrait>`). `public/brand/*` is git-ignored: never commit a founder portrait to this public repository.

## Status
`REVIEW ONLY` until VoiceStudio audio is listened to, captions are aligned to real audio, facts are re-checked on the publish date and the owner approves. Voice and avatar are synthetic and must be disclosed (see `docs/YOUTUBE_METADATA.md`).
