#!/usr/bin/env python3
"""Put word edges on the real pauses. Whisper starts a word when the last one ended, so a sentence's first word swallows the pause and cuts land early.

Usage: snap_words.py PROJECT
Rebuilds timeline/words.json from timeline/words.raw.json with ffmpeg silencedetect. It always starts from the raw file, so it is safe to re-run.
"""
import json, re, subprocess, sys
from pathlib import Path

SENTENCE_END = re.compile(r'[.?!…]$')


def parse_pauses(log):
    starts = [float(x) for x in re.findall(r'silence_start: (-?[\d.]+)', log)]
    ends = [float(x) for x in re.findall(r'silence_end: (-?[\d.]+)', log)]
    return list(zip(starts, ends))


def find_pauses(wav):
    return parse_pauses(subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(wav), '-af', 'silencedetect=noise=-35dB:d=0.1', '-f', 'null', '-'],
                                       capture_output=True, text=True, check=True).stderr)


def snap(W, P):
    """Move the edges of the words W in place onto the pauses P, a list of (start, end). Returns how many moved."""
    n = 0
    for k, w in enumerate(W):
        for a, b in P:
            if w['start'] < b < w['end']:  # a pause inside a word means the word really starts after it
                if k: W[k - 1]['end'] = max(W[k - 1]['end'], round(a, 3))
                w['start'] = round(b, 3); n += 1
    for k, w in enumerate(W[:-1]):  # a sentence's first word can also sit in front of the pause, holding the last sound of the sentence before
        if not k or not SENTENCE_END.search(W[k - 1]['word']): continue
        if any(SENTENCE_END.search(x['word']) for x in W[k:k + 2]): continue  # a sentence this short can fit whole in front of the pause: "Hà Nội." in EP03
        if any(abs(b - w['start']) < 0.1 for a, b in P): continue
        for a, b in P:
            if b - a >= 0.2 and w['start'] <= a + 0.05 and a - w['start'] < 0.12:
                W[k - 1]['end'] = round(a, 3); w['start'] = round(b, 3); w['end'] = round(b + 0.15, 3); n += 1
                j = k + 1
                while j < len(W) and W[j]['start'] < w['end']:
                    W[j]['start'] = w['end']; W[j]['end'] = max(W[j]['end'], round(W[j]['start'] + 0.05, 3)); j += 1
                break
    return n


def main(project):
    p = Path(project)
    d = json.loads((p / 'timeline/words.raw.json').read_text(encoding='utf-8')); W = d.get('words', d) if isinstance(d, dict) else d
    P = find_pauses(p / 'input/voiceover.wav'); n = snap(W, P)
    (p / 'timeline/words.json').write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    print('snapped', n, 'of', len(W), 'words,', len(P), 'pauses')


if __name__ == '__main__':
    main(sys.argv[1])
