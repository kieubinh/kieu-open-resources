# Production pipeline

Paths: `STUDIO` is the installed 2D Studio folder, `P` is `projects/<name>` inside it, `EP` is the episode folder that holds docs, audio and deliverables. `SK` is this skill.

## 1. Studio setup
The kit comes from the Thanh Hai Learn AI 2D Studio plugin and is not in this repository. Install it by following the plugin's `skills/make-2d-video/references/install.md`: copy `kit/` to a git-ignored `STUDIO`, install node and Playwright Chromium, create `.venv` with numpy, scipy and faster-whisper. Then:

```bash
.venv/bin/python SK/scripts/patch_kit.py --studio STUDIO
```

Run it again after every kit update. `build_episode.sh` refuses to run until it passes.

## 2. Voice
1. Check VoiceStudio: `curl -s http://127.0.0.1:3900/health`. Another job holding it answers 429; the script waits. Avoid running TTS during a render.
2. Copy `assets/episode.example.json` to `EP/episode.json` and fill it. Put the script at `EP/docs/script.txt`.
3. `.venv/bin/python SK/scripts/voice.py --episode EP --plan`, then read `audio/voice_ledger.json`. Keep emotional beats in their own chunks. A split must not separate "mười chín tuổi..." from "vẫn còn".
4. `.venv/bin/python SK/scripts/voice.py --episode EP` in the background. It must run with the studio `.venv` Python, because numpy and faster-whisper live there. About 30-50 s per take plus about 10 s of checking, slower while another job holds VoiceStudio. Budget about 4 h of voice and 40 min of render for a 7-minute episode.
5. Read `voice_qc.json` and handle what is left:

| Report | Meaning | Action |
| --- | --- | --- |
| `missing` | a scripted word was not heard | re-read with another `--seed`, or re-split the chunk |
| `tail_cut` | the last words were not heard alone | same; this was the worst fault in EP01 |
| `abrupt` | the take stops mid-sound, word still heard | acceptable, `join_voice.py` fades 12 ms |
| `stray` | a short extra syllable ends the take | use an earlier take, or add a `mute` range |

Lessons from EP01:
- **Blind means blind.** Whole-file alignment with the script as a prompt scored 89% and hid clipped endings the owner heard at once. Never trust a prompted transcript for completeness.
- **Do not append "..." to the input** to protect the ending. It made the engine speak an extra syllable.
- A word the ASR hears the same wrong way on every seed may be ASR rather than voice ("giùm" as "dùng"). After four takes, keep the best and name the timestamp for a human.
- Silence strays with `mute`, which keeps the timeline, so only the mix needs re-running.
- Stray syllables also appear after a dramatic "...". Test by hearing the clip with the suspect sound removed: if the next word is still there, the sound is stray.

Lessons from EP02:
- **ASR writes "bốn phẩy hai" as "4,2".** "Phẩy" is then reported missing on every take, so add it to `asr_skip` in `episode.json`, along with name syllables ASR spells its own way. A word in `asr_skip` no longer counts as missing or as one of the last words.
- **A tail flag on a final number is a false alarm** when the take ends in clean silence. "Sáu phẩy năm" at the end of a chunk raised `tail_cut` on all four takes because ASR heard "6,5". Check the silence after the number, for example with `ffmpeg -i take.wav -af silencedetect=n=-40dB:d=0.1 -f null -`, then record the pass and the reason in `voice_qc.json`.
- **Reword a line that ends in a hard phrase after 4 failed takes.** Four seeds of an EP02 chunk ending in "in sai" all failed, and "sửa lỗi chính tả trong đề" passed once the ending changed. Update `docs/script.txt` and the ledger together.

## 3. Shots
1. Copy `assets/starter-project/` to `P`. Put the script in `input/script.txt`.
2. Rewrite `story/shotlist.py`: entries `(id, first words of the shot, options)` in order, about one shot per 2-3 s, plus `MUSIC`. Anchors must appear in the script, in order.
3. Rewrite `scenes/cast.js`, `scenes/sets/world.js` and `scenes/shots/*.js`. Keep `scenes/lib.js` unless a template is missing. `MINH`, the shot templates and the sets show the working idioms.
4. Before voice exists: `python P/story/estimate_words.py`, `python P/story/build_shots.py`, then `node render.mjs --project P --sheet --scale 0.4`.
5. Inspect every still. Past faults to look for: text under the scope bars, figures floating above a bed or hill, floating props, hidden bike wheels, low contrast labels, overlapping labels, captions clipped at the top.

`config.json`: keep `captions: false`, burned captions clipped in EP01 and the SRT is better for YouTube. Music moods must exist in the kit; `warm` does not, use `calm`. Split shots longer than about 12 s.

## 4. Build

```bash
zsh SK/scripts/build_episode.sh STUDIO P EP
```

Run it in the background. A 7-minute 1080p render takes about 40 minutes on a MacBook Air M5. A voice-only change that keeps every timestamp needs just `join_voice.py`, `audio/mix.py` and a copy of the MP4.

## 5. QA
- Re-run `voice.py --episode EP` and confirm nothing regressed.
- Diff a blind transcript of the final voiceover against the script. Read every line where ASR has extra words. Alignment near 89% is normal here because ASR writes numbers as digits and confuses accents, so read the diff rather than the percentage.
- `ffmpeg -i review.mp4 -vf "fps=1/8,scale=320:-1,tile=8x6" qa/contact.png`, then look at it.
- Loudness: EP01 measured -15.1 LUFS against a -14 target, acceptable for YouTube.
- Report what was not checked, and keep the "chưa ai nghe bằng tai" warning until a human has listened.
- A 480p copy under 30 MB lets the owner review on a phone.

## 6. Shorts
Cut a Short from a finished episode, from inside `STUDIO`. `START` and `END` are seconds on the episode voiceover. Cut on a sentence boundary from `timeline/words.json`.

```bash
.venv/bin/python SK/scripts/make_short.py projects/<episode> <short-name> START END
node render.mjs --project projects/<short-name> --sheet --scale 0.4
node render.mjs --project projects/<short-name>
.venv/bin/python audio/mix.py --project projects/<short-name>
```

The script builds a new 9:16 project with the episode's scenes and the words, shots, music and voice of that range, plus 1.2 s of tail. It replaces any project with the same name. Unlike an episode, a Short has `captions: true`. Inspect the sheet before the full render, because the shots were drawn for 16:9.
