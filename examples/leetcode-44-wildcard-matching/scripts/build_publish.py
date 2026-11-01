#!/usr/bin/env python3
"""Generate publish/youtube_metadata.md (title, description, chapters, tags) from src/timeline.json.

Chapter timestamps are the REAL scene start times of the timeline that was rendered. A preview (silent, estimated)
timeline is refused unless --allow-preview is given, and then everything is labelled as estimated.
Nothing here uploads or publishes anything.
"""
import argparse
import json
from pathlib import Path

from episode import EPISODE, PRACTICE, STATS

ROOT = Path(__file__).resolve().parents[1]
PUBLISH = ROOT / "publish"

# (first scene id of the chapter, chapter title). Every chapter lasts >= 10 s and the first starts at 00:00 (YouTube rules).
CHAPTERS = [
    ("01-mission", "Kieu Studio và mục tiêu rèn tư duy"),
    ("02-problem", "Đọc đề, input/output, ràng buộc và thống kê"),
    ("05-example1", "Ba ví dụ chính thức"),
    ("09-hints", "Ba gợi ý và 10 giây tự suy nghĩ"),
    ("11-rules", "Ý tưởng đệ quy và cây quyết định"),
    ("13-blowup", "Vì sao thử hết mọi nhánh không đủ nhanh"),
    ("14-greedy-fail", "Ý tưởng tham lam sai: phản ví dụ"),
    ("15-dp", "Quy hoạch động: bảng dp"),
    ("16-insight", "Tối ưu: chỉ nhớ dấu * gần nhất"),
    ("17-greedy", "Thuật toán hai con trỏ và chạy thử"),
    ("20-code1", "Lời giải Python 3"),
    ("21-code2", "Chạy code từng dòng"),
    ("22-verify", "Kiểm chứng và so sánh độ phức tạp"),
    ("24-lessons", "Bài học, ba bài luyện tập và lời kết"),
]


def stamp(seconds):
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m:02}:{s:02}"


def chapters(timeline):
    fps = timeline["fps"]
    start = {s["id"]: s["fromFrame"] / fps for s in timeline["scenes"]}
    total = timeline["totalFrames"] / fps
    rows = [(start[sid], title) for sid, title in CHAPTERS]
    assert rows[0][0] == 0, "first chapter must start at 00:00"
    ends = [r[0] for r in rows[1:]] + [total]
    for (a, title), b in zip(rows, ends):
        assert b - a >= 10, f"chapter '{title}' is shorter than 10 s ({b - a:.1f} s)"
    assert all(rows[k][0] < rows[k + 1][0] for k in range(len(rows) - 1)), "chapters must be in order"
    return [(stamp(a), title) for a, title in rows]


def build(timeline, estimated):
    ch = chapters(timeline)
    title = f"LeetCode #{EPISODE['problem']} Wildcard Matching (Hard): giải từng bước với Python 3 | Kieu Studio EP{EPISODE['number']:02}"
    assert len(title) <= 100, len(title)
    practice = "\n".join(f"- #{p['n']} {p['title']} ({p['difficulty']}): {p['url']}" for p in PRACTICE)
    desc = f"""Tập {EPISODE['number']} của Kieu Studio, The Art of Coding: luyện kỹ năng giải quyết vấn đề qua bài LeetCode #{EPISODE['problem']} Wildcard Matching (Hard).

Trong video: đọc đề và ràng buộc, ba ví dụ chính thức, ba gợi ý, 10 giây tự suy nghĩ, rồi đi từ đệ quy thử mọi nhánh, ý tưởng tham lam sai, bảng quy hoạch động, đến thuật toán hai con trỏ O(1) bộ nhớ, kèm code Python 3 chạy từng dòng.

Đề bài: {EPISODE['url']}
Theo trang LeetCode ngày 28/10/2026: mức Hard, {STATS['accepted']:,} lượt nộp được chấp nhận, tỷ lệ chấp nhận 33,1% (đây là số lượt nộp bài, không phải số người).

Chương:
""".replace(f"{STATS['accepted']:,}", f"{STATS['accepted']:,}".replace(",", "."))
    desc += "\n".join(f"{t} {name}" for t, name in ch)
    desc += f"""

Ba bài luyện tập liên quan:
{practice}

Kiểm chứng: lời giải được so sánh với biểu thức chính quy và bảng quy hoạch động trên các ca vét cạn và ngẫu nhiên (xem docs/QA_REPORT.md trong mã nguồn). Thử nghiệm là bằng chứng mạnh nhưng không phải chứng minh toán học.

Giọng đọc được tạo bằng VoiceStudio chạy cục bộ (giọng tổng hợp, không phải người thật). Hình ảnh dựng bằng Remotion.

Mã nguồn tập này: examples/leetcode-44-wildcard-matching trong kho kieu-open-resources.
kieu.app
"""
    tags = ["LeetCode", "LeetCode 44", "Wildcard Matching", "thuật toán", "quy hoạch động", "greedy", "Python", "giải thuật", "lập trình", "phỏng vấn lập trình", "Kieu Studio", "The Art of Coding"]
    head = "# YouTube metadata - EP03 LeetCode #44 Wildcard Matching\n\n"
    head += ("STATUS: **REVIEW - estimated timeline, silent preview. Do not publish.**\n\n" if estimated else
             "STATUS: **DRAFT for human review - not uploaded.** Publish only after the narration (Narrator 03, synthetic) is approved by a person.\n\n")
    return head + f"## Title ({len(title)} characters)\n\n{title}\n\n## Description\n\n```\n{desc}```\n\n## Tags\n\n{', '.join(tags)}\n\n## Chapters (also in publish/chapters.txt)\n\n" + "\n".join(f"{t} {n}" for t, n in ch) + "\n", ch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-preview", action="store_true")
    args = ap.parse_args()
    timeline = json.loads((ROOT / "src/timeline.json").read_text(encoding="utf-8"))
    if timeline["preview"] and not args.allow_preview:
        raise SystemExit("src/timeline.json is a PREVIEW (estimated) timeline; run scripts/build_timeline.py with real audio first.")
    md, ch = build(timeline, timeline["preview"])
    PUBLISH.mkdir(exist_ok=True)
    (PUBLISH / "youtube_metadata.md").write_text(md, encoding="utf-8")
    (PUBLISH / "chapters.txt").write_text("\n".join(f"{t} {n}" for t, n in ch) + "\n", encoding="utf-8")
    print(f"wrote publish/youtube_metadata.md and chapters.txt ({len(ch)} chapters, {'ESTIMATED' if timeline['preview'] else 'real'} timestamps)")


if __name__ == "__main__":
    main()
