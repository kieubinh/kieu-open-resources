#!/usr/bin/env python3
"""Print YouTube chapter lines (m:ss Title) for the FULL video of an episode, from the real VoiceStudio WAV lengths.

Usage: KIEU_EPISODE=gr01 youtube_chapters.py --project <episode dir> [--first "Mở đầu: <hook question>"]

Timing is identical to build_timeline.py (scene start = sum of ceil((WAV seconds + tail) * 30) frames), so the chapters
match the rendered video. Refuses to guess: a missing WAV is an error. YouTube needs the first chapter at 0:00, at least
three chapters, each at least 10 s.
"""
from __future__ import annotations
import argparse, math, sys, wave
from pathlib import Path

LABELS = {'intro': 'Mở đầu', 'growth': 'Con số tăng trưởng', 'why': 'Vì sao tác giả làm ra nó', 'problem': 'Bài toán cụ thể',
          'how': 'Cách hoạt động', 'usage': 'Cách sử dụng', 'value': 'Cái được và cái giá', 'ideas': 'Bốn ý tưởng ứng dụng', 'outro': 'Tóm lại'}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--project', required=True); ap.add_argument('--first', help='label for the 0:00 chapter')
    a = ap.parse_args(); project = Path(a.project).resolve()
    sys.path.insert(0, str(project / 'scripts'))
    import config                                   # noqa: E402
    from episode import S                           # noqa: E402
    if config.SHORT:
        raise SystemExit('chapters are for the full video: unset KIEU_FORMAT')
    at, rows = 0.0, []
    for s in S:
        wav = config.AUDIO_DIR / f'{s.id}.wav'
        if not wav.is_file():
            raise SystemExit(f'WAV missing: {wav} (run voice:generate first)')
        with wave.open(str(wav), 'rb') as w:
            frames = math.ceil((w.getnframes() / w.getframerate() + config.TAIL_SECONDS) * 30)
        label = (a.first if (s.beat == 'intro' and a.first) else LABELS.get(s.beat, s.title))
        rows.append((int(at), label)); at += frames / 30
    for sec, label in rows:
        print(f'{sec // 60}:{sec % 60:02d} {label}')
    print(f'# total {at:.1f}s', file=sys.stderr)


if __name__ == '__main__':
    main()
