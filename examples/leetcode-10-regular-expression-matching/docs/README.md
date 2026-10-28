# EP02 — Regular Expression Matching (#10)

**Mission:** practise problem-solving, not memorize LeetCode solutions.

Official source: https://leetcode.com/problems/regular-expression-matching/description/

- Difficulty: Hard
- Examples: `s="aa", p="a" → false`; `s="aa", p="a*" → true`; `s="ab", p=".*" → true`
- Constraints: `1 <= s.length, p.length <= 20`; `s` lowercase letters; `p` lowercase letters and `.`, `*`; every star has a valid element immediately before it
- Snapshot (28 October 2026): ~1.52M accepted submissions / ~4.8M submissions; 32.0% acceptance. This is **not** a count of people.
- The episode explains the question, all three examples, hints, ten seconds of silence, branching/memoization, Python 3, and reflection.
- More practice: #44 Wildcard Matching, #72 Edit Distance, #97 Interleaving String.

## Review the content

```bash
python3 -m unittest discover -s scripts -p '*test.py' -v
python3 ../../skills/kieu-leetcode-video/scripts/audit_episode.py --episode scripts/episode.py
npm install
npm run studio
npm run render:preview
```

The preview is **silent and NOT publish-ready**. Do not substitute other TTS providers without approval.

## Create a VoiceStudio release on your Mac

```bash
npm run voice:check
npm run voice:voices
export VOICESTUDIO_VOICE_PROFILE="<valid ID shown by voice:voices>"
npm run voice:generate
npm run render:release
```

The local VoiceStudio endpoint defaults to `http://127.0.0.1:3900`. Each scene gets one WAV file, and timeline durations are computed from the real audio. The 10-second thinking pause has no audio file.

**Release QA remains mandatory:** Check spoken Vietnamese and punctuation, title/constraint typography, moving characters, the exact 10 seconds of silence, audio/caption alignment, source facts, output codec and no clipping. A successful render command alone is not editorial approval.

The public source does **not** contain official LeetCode screenshots or audio; assess redistribution rights separately.

The prior 7-minute V6 offline guide-voice review is available as a separate conversation artifact and is **not** a publishable VoiceStudio master.
