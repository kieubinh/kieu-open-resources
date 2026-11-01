#!/usr/bin/env python3
"""Write subtitles.srt and YOUTUBE_METADATA.md from the final timeline and episode.json ("youtube").

Usage: make_meta.py --episode DIR --project STUDIO_PROJECT_DIR
"""
import argparse, json
from pathlib import Path

ts = lambda s: f'{int(s // 3600):02}:{int(s % 3600 // 60):02}:{int(s % 60):02},{int(s % 1 * 1000):03}'
mm = lambda s: f'{int(s // 60)}:{int(s % 60):02}'


def rows(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if w['word'][-1] in '.?!' or len(cur) >= 12: out.append(cur); cur = []
    if cur: out.append(cur)
    return out


def srt(words):
    return ''.join(f"{i}\n{ts(r[0]['start'])} --> {ts(r[-1]['end'] + 0.15)}\n{' '.join(x['word'] for x in r)}\n\n" for i, r in enumerate(rows(words), 1))


def chapters(shots, spec):
    return '\n'.join(f"{mm(0 if n == 0 else shots[i]['start'])} {name}" for n, (i, name) in enumerate(spec))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--episode', required=True); ap.add_argument('--project', required=True); a = ap.parse_args()
    ep, p = Path(a.episode), Path(a.project); y = json.loads((ep / 'episode.json').read_text(encoding='utf-8'))['youtube']
    W = json.loads((p / 'timeline/words.json').read_text(encoding='utf-8')); W = W.get('words', W) if isinstance(W, dict) else W
    (ep / 'subtitles.srt').write_text(srt(W), encoding='utf-8')
    shots = {s['id']: s for s in json.loads((p / 'story/shots.json').read_text(encoding='utf-8'))['shots']}
    desc = '\n\n'.join(x for x in (y['hook'], chapters(shots, y['chapters']), y['sources'], y.get('warning', ''),
                                   'Phim do AI hỗ trợ sản xuất: giọng đọc tổng hợp, hình ảnh vẽ bằng code.', y['hashtags']) if x)
    link = f"**Video:** {y['video_url']}\n\n" if y.get('video_url') else ''
    (ep / 'YOUTUBE_METADATA.md').write_text(f"""# YouTube metadata

{link}**Tiêu đề:** {y['title']}

**Mô tả:**

{desc}

**Thẻ:** {', '.join(y['tags'])}

**Cài đặt:** Riêng tư · Không dành cho trẻ em · Nội dung bị thay đổi hoặc tổng hợp: Có · Phụ đề: subtitles.srt · Thumbnail: thumbnail_1280x720.png
""", encoding='utf-8')
    print('meta ok')


if __name__ == '__main__':
    main()
