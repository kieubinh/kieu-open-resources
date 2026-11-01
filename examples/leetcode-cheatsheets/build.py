#!/usr/bin/env python3
"""One-page A4 cheat sheet (PDF) for each Kieu Studio LeetCode video: #44, #10, #4.

Run:  python3 examples/leetcode-cheatsheets/build.py
Writes the HTML to examples/<video>/cheatsheet/<name>.html and the PDF to docs/cheatsheets/leetcode/<name>.pdf (headless Google Chrome), then checks every PDF has ONE page.

Everything printed on the sheets is checked here before rendering: the code shown is executed on the official
examples, and the numbers drawn in the illustrations come from running the algorithm, not typed by hand.
"""
import base64, html, re, statistics, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parent
DOCS = EXAMPLES.parent / 'docs' / 'cheatsheets' / 'leetcode'   # PDFs live here (public); HTML sources stay in each example
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
MARK = base64.b64encode((HERE / 'kieu-studio-mark.png').read_bytes()).decode()

GREEN, GREEN_BG = '#0e9f6e', '#e3f7ee'
ORANGE, ORANGE_BG = '#d9822b', '#fdf0de'
BLUE, BLUE_BG = '#0070f3', '#e6f1ff'
RED, RED_BG = '#d6455d', '#fde8ec'
NAVY, MUTED, SOFT, LINE = '#0b2554', '#5a6478', '#f3f7fd', '#dbe4f3'


# ---------------------------------------------------------------- SVG helpers
def tile(x, y, w, h, text, fg, bg, size=24):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{bg}" stroke="{fg}" stroke-width="2.5"/>'
            f'<text x="{x + w / 2}" y="{y + h / 2 + size * 0.35}" text-anchor="middle" font-family="Menlo,monospace" '
            f'font-weight="700" font-size="{size}" fill="{fg}">{html.escape(text)}</text>')


def label(x, y, text, fg=NAVY, size=13, anchor='middle', weight=600, mono=False):
    fam = 'Menlo,monospace' if mono else '-apple-system,Helvetica,Arial,sans-serif'
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{fam}" font-weight="{weight}" '
            f'font-size="{size}" fill="{fg}">{html.escape(text)}</text>')


def line(x1, y1, x2, y2, fg, dash=None, width=2):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{fg}" stroke-width="{width}"{d}/>'


def svg(inner, w, h):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg">{inner}</svg>'


# ---------------------------------------------------------------- code shown on the sheets (verified below)
CODE44 = '''class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        i = j = 0
        star = -1
        mark = 0
        while i < len(s):
            if j < len(p) and (p[j] == s[i] or p[j] == "?"):
                i += 1
                j += 1
            elif j < len(p) and p[j] == "*":
                star = j
                mark = i
                j += 1
            elif star != -1:
                mark += 1
                i = mark
                j = star + 1
            else:
                return False
        while j < len(p) and p[j] == "*":
            j += 1
        return j == len(p)'''

CODE10 = '''from functools import cache

class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        @cache
        def dfs(i: int, j: int) -> bool:
            if j == len(p):
                return i == len(s)
            first = i < len(s) and (s[i] == p[j] or p[j] == ".")
            if j + 1 < len(p) and p[j + 1] == "*":
                return dfs(i, j + 2) or (first and dfs(i + 1, j))
            return first and dfs(i + 1, j + 1)
        return dfs(0, 0)'''

CODE4 = '''class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        a, b = nums1, nums2
        if len(a) > len(b):
            a, b = b, a
        m, n = len(a), len(b)
        left_size = (m + n + 1) // 2
        lo, hi = 0, m
        while lo <= hi:
            i = (lo + hi) // 2
            j = left_size - i
            a_left = a[i - 1] if i else float('-inf')
            a_right = a[i] if i < m else float('inf')
            b_left = b[j - 1] if j else float('-inf')
            b_right = b[j] if j < n else float('inf')
            if a_left <= b_right and b_left <= a_right:
                if (m + n) % 2:
                    return float(max(a_left, b_left))
                return (max(a_left, b_left) + min(a_right, b_right)) / 2.0
            if a_left > b_right:
                hi = i - 1
            else:
                lo = i + 1'''


def solution(code):
    ns = {}
    exec(code, ns)
    return ns['Solution']()


def check_code():
    """The code printed on the sheets must solve the official examples."""
    s44, s10, s4 = solution(CODE44), solution(CODE10), solution(CODE4)
    assert [s44.isMatch('aa', 'a'), s44.isMatch('aa', '*'), s44.isMatch('cb', '?a'), s44.isMatch('adceb', '*a*b')] == [False, True, False, True]
    assert [s10.isMatch('aa', 'a'), s10.isMatch('aa', 'a*'), s10.isMatch('ab', '.*'), s10.isMatch('aab', 'c*a*b')] == [False, True, True, True]
    assert s4.findMedianSortedArrays([1, 3], [2]) == 2.0 and s4.findMedianSortedArrays([1, 2], [3, 4]) == 2.5
    assert s4.findMedianSortedArrays([1, 3, 8, 9], [2, 4, 5, 7]) == 4.5 == statistics.median([1, 2, 3, 4, 5, 7, 8, 9])


# ---------------------------------------------------------------- illustrations (numbers come from running the algorithms)
def illustration_44():
    s, p = 'adceb', '*a*b'
    # Instrumented copy of CODE44: record what the second * ends up swallowing.
    i = j = 0; star = -1; mark = 0; start = 0; tries = []
    while i < len(s):
        if j < len(p) and (p[j] == s[i] or p[j] == '?'):
            i += 1; j += 1
        elif j < len(p) and p[j] == '*':
            star, mark, start = j, i, i; j += 1; tries = ['']      # a new * swallows "" first
        elif star != -1:
            mark += 1; i = mark; j = star + 1; tries.append(s[start:mark])  # swallow one more char
        else:
            raise AssertionError
    swallowed = tries[-1]                                          # the last try is the one that matched
    assert tries == ['', 'd', 'dc', 'dce'] and swallowed == s[start:mark] == 'dce', tries

    x0, step, w = 110, 68, 60
    out = []
    out.append(label(4, 70, 'Mẫu p', MUTED, 12, 'start'))
    out.append(label(4, 172, 'Chuỗi s', MUTED, 12, 'start'))
    # p row
    out.append(tile(80, 36, 24, 56, '*', ORANGE, ORANGE_BG, 22))
    out.append(tile(x0, 36, w, 56, 'a', GREEN, GREEN_BG))
    out.append(tile(x0 + step, 36, 3 * step - 8, 56, '*', ORANGE, ORANGE_BG, 26))
    out.append(tile(x0 + 4 * step, 36, w, 56, 'b', GREEN, GREEN_BG))
    # s row
    for k, ch in enumerate(s):
        swallowed_k = 1 <= k <= 3
        out.append(tile(x0 + k * step, 138, w, 56, ch, ORANGE if swallowed_k else GREEN, ORANGE_BG if swallowed_k else GREEN_BG))
    # links
    out.append(line(92, 92, 92, 120, ORANGE, '4 3'))
    out.append(label(92, 114, '', ORANGE))
    out.append(label(92, 134, 'rỗng', ORANGE, 11))
    out.append(line(x0 + w / 2, 92, x0 + w / 2, 138, GREEN, '4 3'))
    out.append(line(x0 + 2.5 * step - 4, 92, x0 + 2.5 * step - 4, 138, ORANGE, '4 3'))
    out.append(line(x0 + 4 * step + w / 2, 92, x0 + 4 * step + w / 2, 138, GREEN, '4 3'))
    out.append(label(x0 + w / 2, 218, 'khớp', GREEN, 12))
    out.append(label(x0 + 4 * step + w / 2, 218, 'khớp', GREEN, 12))
    out.append(f'<rect x="{x0 + step}" y="204" width="{3 * step - 8}" height="6" rx="3" fill="{ORANGE}"/>')
    out.append(label(x0 + 2.5 * step - 4, 230, f'* nuốt "{swallowed}"', ORANGE, 13))
    # right panel: the retries of the second *
    px = 480
    out.append(f'<rect x="{px}" y="14" width="228" height="214" rx="12" fill="{SOFT}" stroke="{LINE}"/>')
    out.append(label(px + 114, 38, 'Dấu * thứ hai thử dần', NAVY, 13, weight=700))
    for r, t in enumerate(tries):
        y = 52 + r * 42
        ok = r == len(tries) - 1
        out.append(tile(px + 16, y, 100, 32, f'"{t}"', GREEN if ok else RED, GREEN_BG if ok else RED_BG, 15))
        out.append(label(px + 130, y + 22, '✓ khớp b' if ok else '✗ sai', GREEN if ok else RED, 13, 'start', 700))
    out.append(label(px + 114, 222, 'sai → nuốt thêm 1 ký tự', MUTED, 11))
    return svg(''.join(out), 720, 244)


def illustration_10():
    s, p = 'aab', 'c*a*b'
    seen = {}

    def dfs(i, j):
        if (i, j) in seen:
            return seen[i, j]
        if j == len(p):
            r = i == len(s)
        else:
            first = i < len(s) and (s[i] == p[j] or p[j] == '.')
            if j + 1 < len(p) and p[j + 1] == '*':
                r = dfs(i, j + 2) or (first and dfs(i + 1, j))
            else:
                r = first and dfs(i + 1, j + 1)
        seen[i, j] = bool(r)
        return seen[i, j]

    assert dfs(0, 0) is True and solution(CODE10).isMatch(s, p) is True
    total = (len(s) + 1) * (len(p) + 1)
    out = []
    # left: the two choices at x*
    out.append(f'<rect x="70" y="8" width="210" height="50" rx="10" fill="{BLUE_BG}" stroke="{BLUE}" stroke-width="2.5"/>')
    out.append(label(175, 30, 'dfs(i, j)', BLUE, 16, weight=700, mono=True))
    out.append(label(175, 48, "gặp x* ở p[j], p[j+1]", BLUE, 12))
    out.append(line(120, 58, 85, 112, MUTED, None, 2.5)); out.append(line(230, 58, 265, 112, MUTED, None, 2.5))
    out.append(f'<rect x="4" y="112" width="152" height="86" rx="10" fill="{GREEN_BG}" stroke="{GREEN}" stroke-width="2.5"/>')
    out.append(label(80, 136, '0 lần', GREEN, 16, weight=700))
    out.append(label(80, 156, 'bỏ cả cặp x*', GREEN, 12))
    out.append(label(80, 180, 'dfs(i, j+2)', GREEN, 13, weight=700, mono=True))
    out.append(f'<rect x="198" y="112" width="152" height="86" rx="10" fill="{ORANGE_BG}" stroke="{ORANGE}" stroke-width="2.5"/>')
    out.append(label(274, 136, 'thêm 1 lần', ORANGE, 16, weight=700))
    out.append(label(274, 156, 'nếu s[i] khớp x', ORANGE, 12))
    out.append(label(274, 180, 'dfs(i+1, j)', ORANGE, 13, weight=700, mono=True))
    out.append(label(177, 160, 'HOẶC', NAVY, 11, weight=700))
    out.append(label(177, 222, 'đúng nếu một trong hai nhánh đúng', MUTED, 12))
    # right: memo table
    gx, gy, cw, ch = 440, 60, 42, 34
    out.append(label(gx + 3 * cw, 24, 'Bảng nhớ: s = "aab", p = "c*a*b"', NAVY, 13, weight=700))
    out.append(label(gx - 12, gy - 8, 'j →', MUTED, 11, 'end'))
    for j in range(len(p) + 1):
        out.append(label(gx + j * cw + cw / 2, gy - 8, p[j] if j < len(p) else '∅', MUTED, 14, weight=700, mono=True))
    for i in range(len(s) + 1):
        out.append(label(gx - 12, gy + i * ch + ch / 2 + 5, s[i] if i < len(s) else '∅', MUTED, 14, 'end', 700, True))
        for j in range(len(p) + 1):
            r = seen.get((i, j))
            fg, bg, t = (MUTED, '#ffffff', '') if r is None else ((GREEN, GREEN_BG, 'T') if r else (RED, RED_BG, 'F'))
            out.append(f'<rect x="{gx + j * cw}" y="{gy + i * ch}" width="{cw - 3}" height="{ch - 3}" rx="5" fill="{bg}" stroke="{LINE if r is None else fg}" stroke-width="1.6"/>')
            if t:
                out.append(label(gx + j * cw + (cw - 3) / 2, gy + i * ch + (ch - 3) / 2 + 5, t, fg, 14, weight=700, mono=True))
    out.append(label(gx - 36, gy - 8, 'i ↓', MUTED, 11, 'end'))
    out.append(label(gx + 3 * cw, gy + 4 * ch + 22, f'Chỉ {len(seen)}/{total} ô được tính, mỗi ô một lần', NAVY, 13, weight=700))
    return svg(''.join(out), 720, 252)


def illustration_4():
    a, b, i, j = [1, 3, 8, 9], [2, 4, 5, 7], 2, 2
    al, ar, bl, br = a[i - 1], a[i], b[j - 1], b[j]
    assert al <= br and bl <= ar
    med = (max(al, bl) + min(ar, br)) / 2
    assert med == solution(CODE4).findMedianSortedArrays(a, b) == 4.5
    x0, step, w, h = 150, 64, 56, 50
    ya, yb = 52, 146
    cx = x0 + i * step - 4
    out = []
    out.append(f'<rect x="{x0 - 10}" y="14" width="{i * step + 6}" height="214" rx="12" fill="{BLUE_BG}"/>')
    out.append(f'<rect x="{cx + 6}" y="14" width="{(len(a) - i) * step + 4}" height="214" rx="12" fill="{ORANGE_BG}"/>')
    out.append(label(x0 + i * step / 2 - 6, 30, 'nửa trái', BLUE, 12, weight=700))
    out.append(label(cx + 6 + ((len(a) - i) * step + 4) / 2, 30, 'nửa phải', ORANGE, 12, weight=700))
    for row, arr, y, name in ((0, a, ya, 'A'), (1, b, yb, 'B')):
        out.append(label(x0 - 28, y + h / 2 + 7, name, NAVY, 22, 'middle', 800))
        for k, v in enumerate(arr):
            key = (name == 'A' and k in (i - 1, i)) or (name == 'B' and k in (j - 1, j))
            left = k < (i if name == 'A' else j)
            fg = (BLUE if left else ORANGE)
            out.append(tile(x0 + k * step, y, w, h, str(v), fg, '#ffffff' if not key else (BLUE_BG if left else ORANGE_BG), 22))
    out.append(line(cx, 38, cx, 216, RED, '6 4', 3))
    out.append(label(cx, 238, '✂ đường cắt', RED, 12, weight=700))
    out.append(label(x0 + (i - 1) * step + w / 2, ya - 6, f'AL={al}', BLUE, 13, weight=700))
    out.append(label(x0 + i * step + w / 2, ya - 6, f'AR={ar}', ORANGE, 13, weight=700))
    out.append(label(x0 + (j - 1) * step + w / 2, yb + h + 18, f'BL={bl}', BLUE, 13, weight=700))
    out.append(label(x0 + j * step + w / 2, yb + h + 18, f'BR={br}', ORANGE, 13, weight=700))
    px = 450
    out.append(f'<rect x="{px}" y="14" width="258" height="214" rx="12" fill="{SOFT}" stroke="{LINE}"/>')
    out.append(label(px + 129, 38, 'Cắt hợp lệ khi', NAVY, 13, weight=700))
    out.append(label(px + 18, 66, f'AL ≤ BR :  {al} ≤ {br}  ✓', GREEN, 15, 'start', 700, True))
    out.append(label(px + 18, 92, f'BL ≤ AR :  {bl} ≤ {ar}  ✓', GREEN, 15, 'start', 700, True))
    out.append(line(px + 14, 108, px + 244, 108, LINE, None, 1.5))
    out.append(label(px + 129, 130, 'Trung vị (tổng chẵn)', NAVY, 13, weight=700))
    out.append(label(px + 129, 154, f'(max({al},{bl}) + min({ar},{br})) / 2', NAVY, 14, weight=700, mono=True))
    out.append(label(px + 129, 180, f'= {med}', GREEN, 22, weight=800, mono=True))
    out.append(label(px + 129, 206, 'AL > BR → cắt sang trái ◀   BL > AR → ▶', MUTED, 10.5))
    return svg(''.join(out), 720, 246)


# ---------------------------------------------------------------- page template
CSS = f'''
@page {{ size: A4; margin: 0; }}
:root {{ --navy:{NAVY}; --blue:{BLUE}; --cyan:#00c8ff; --ink:#1d2433; --muted:{MUTED}; --line:{LINE}; --soft:{SOFT}; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: -apple-system, "SF Pro Text", "Helvetica Neue", Arial, sans-serif; color: var(--ink); font-size: 9.1pt; line-height: 1.38; }}
.page {{ width: 210mm; height: 297mm; padding: 8.5mm 13mm 0; position: relative; overflow: hidden;
  background: linear-gradient(180deg, #ffffff 0%, #ffffff 70%, #eaf3ff 100%); }}
.top {{ display: flex; align-items: center; justify-content: space-between; }}
.brand {{ display: flex; align-items: center; gap: 2.5mm; font-weight: 700; color: var(--navy); letter-spacing: 1px; font-size: 9pt; }}
.brand img {{ width: 9mm; height: 9mm; }}
.pill {{ border: 1.5px solid {RED}; color: {RED}; border-radius: 99px; padding: 0.6mm 3.5mm; font-weight: 800; font-size: 9pt; }}
h1 {{ font-size: 22pt; line-height: 1.1; color: var(--navy); margin: 3mm 0 1mm; letter-spacing: -0.4px; }}
h1 .n {{ color: var(--blue); }}
.hook {{ font-size: 10.4pt; color: var(--muted); margin: 0 0 3mm; }}
.hook b {{ color: var(--navy); }}
h3 {{ font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.7px; color: var(--muted); margin: 0 0 1.6mm; }}
.card {{ border: 1px solid var(--line); background: #fff; border-radius: 3mm; padding: 2.4mm 3.6mm; }}
.row {{ display: grid; gap: 3mm; margin-bottom: 3mm; }}
.r2 {{ grid-template-columns: 1.15fr 1fr; }}
.r2b {{ grid-template-columns: 1fr 1.12fr; }}
.r3 {{ grid-template-columns: 1fr 1fr 1fr; }}
.big {{ background: var(--navy); color: #fff; border: 0; }}
.big h3 {{ color: var(--cyan); }}
.big p {{ margin: 0; font-size: 10.6pt; line-height: 1.36; font-weight: 600; }}
.big code {{ background: rgba(255,255,255,0.16); color: #bfe3ff; }}
.card svg {{ display: block; margin: 0 auto; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 1.5mm; margin-top: 2mm; }}
.chip {{ font: 7.8pt Menlo, monospace; background: var(--soft); border: 1px solid var(--line); border-radius: 2mm; padding: 0.6mm 2mm; color: var(--navy); }}
.chip b {{ color: {GREEN}; }} .chip b.f {{ color: {RED}; }}
p {{ margin: 0 0 1.5mm; }}
ol.steps {{ counter-reset: s; list-style: none; margin: 0; padding: 0; }}
ol.steps li {{ counter-increment: s; position: relative; padding-left: 7.5mm; margin-bottom: 1.5mm; }}
ol.steps li::before {{ content: counter(s); position: absolute; left: 0; top: 0.2mm; width: 5.2mm; height: 5.2mm; border-radius: 50%;
  background: var(--blue); color: #fff; font-weight: 700; font-size: 8pt; text-align: center; line-height: 5.2mm; }}
code, .m {{ font-family: Menlo, "SF Mono", Consolas, monospace; font-size: 8.4pt; color: #0a3d91; background: var(--soft); border-radius: 1mm; padding: 0 1mm; }}
pre {{ margin: 0; background: #0f1b33; color: #e8f0ff; border-radius: 2.5mm; padding: 3mm 3.5mm; font: 6.3pt/1.3 Menlo, "SF Mono", Consolas, monospace; white-space: pre; }}
ul {{ margin: 0; padding-left: 4.2mm; }} li {{ margin-bottom: 1.2mm; }}
.cx {{ display: flex; gap: 2mm; flex-wrap: wrap; }}
.cx span {{ background: {GREEN_BG}; color: #0a6b49; font-weight: 700; border-radius: 2mm; padding: 1mm 2.6mm; font-size: 9pt; }}
.bad li::marker {{ color: {RED}; content: '✗  '; }}
.foot {{ position: absolute; left: 13mm; right: 13mm; bottom: 7mm; display: flex; justify-content: space-between; align-items: flex-end;
  font-size: 7.6pt; color: var(--muted); border-top: 1px solid var(--line); padding-top: 1.6mm; }}
.foot b {{ color: var(--navy); }}
'''


def page(d, zoom=1.0):
    chips = ''.join(f'<span class="chip">{html.escape(a)} <b{"" if ok else " class=f"}>→ {out}</b></span>' for a, out, ok in d['examples'])
    steps = ''.join(f'<li>{x}</li>' for x in d['steps'])
    traps = ''.join(f'<li>{x}</li>' for x in d['traps'])
    practice = ''.join(f'<li>{x}</li>' for x in d['practice'])
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>LeetCode {d["num"]} {d["name"]} — Cheatsheet Kieu Studio</title><style>{CSS}</style></head>
<body><section class="page"><div class="inner" style="zoom:{zoom}">
<div class="top"><div class="brand"><img src="data:image/png;base64,{MARK}" alt="">KIEU STUDIO · THE ART OF CODING</div><div class="pill">LEETCODE {d["num"]} · HARD</div></div>
<h1><span class="n">#{d["num"]}</span> {d["name"]}</h1>
<p class="hook">{d["hook"]}</p>
<div class="row r2">
  <div class="card"><h3>Đề bài trong 1 câu</h3><p>{d["problem"]}</p><div class="chips">{chips}</div></div>
  <div class="card big"><h3>Chìa khoá</h3><p>{d["key"]}</p></div>
</div>
<div class="card" style="margin-bottom:3mm"><h3>Hình minh hoạ · {d["fig"]}</h3>{d["svg"]}</div>
<div class="row r2b">
  <div class="card"><h3>Cách làm</h3><ol class="steps">{steps}</ol></div>
  <div><h3 style="margin-left:1mm">Code Python 3 (đã chạy thử trên ví dụ của đề)</h3><pre>{html.escape(d["code"])}</pre></div>
</div>
<div class="row r3">
  <div class="card"><h3>Độ phức tạp</h3><div class="cx">{"".join(f"<span>{x}</span>" for x in d["cx"])}</div><p style="margin-top:2mm;font-size:8.6pt;color:var(--muted)">{d["cx_note"]}</p></div>
  <div class="card"><h3>Bẫy hay gặp</h3><ul class="bad">{traps}</ul></div>
  <div class="card"><h3>Luyện tiếp</h3><ul>{practice}</ul></div>
</div></div>
<div class="foot"><div><b>Xem video giải thích từng bước:</b> youtu.be/{d["video"]} · kieu.app<br>Đề bài thuộc LeetCode (leetcode.com/problems/{d["slug"]}). Hình, giải thích và code do Kieu Studio biên soạn.</div><div>Nhớ cách nghĩ, đừng nhớ code.</div></div>
</section><script>addEventListener('load',()=>{{const f=document.querySelector('.foot').getBoundingClientRect().top;const b=Math.max(...[...document.querySelectorAll('.page .row, .page .card')].map(e=>e.getBoundingClientRect().bottom));document.documentElement.dataset.slack=Math.round((f-b)*10)/10;}});</script></body></html>'''


PAGES = [
    dict(dir='leetcode-44-wildcard-matching', file='Kieu-Studio_LeetCode-44_Wildcard-Matching_cheatsheet', num=44, name='Wildcard Matching',
         video='s44HW8mGVzU', slug='wildcard-matching', fig='dấu * nuốt bao nhiêu ký tự?',
         hook='Dấu <b>*</b> nuốt bao nhiêu ký tự? Không cần thử mọi nhánh: <b>nhớ dấu * gần nhất, sai thì quay lại.</b>',
         problem='Ghép chuỗi <code>s</code> với mẫu <code>p</code> (phải khớp <b>toàn bộ</b> s). Trong p: <code>?</code> = đúng 1 ký tự bất kỳ, <code>*</code> = chuỗi bất kỳ, kể cả rỗng.',
         examples=[('s="aa"  p="a"', 'false', False), ('s="aa"  p="*"', 'true', True), ('s="cb"  p="?a"', 'false', False)],
         key='Chỉ cần nhớ <b>một</b> dấu * (cái gần nhất). Đi sai → cho dấu đó <b>nuốt thêm 1 ký tự</b> rồi thử lại. Bộ nhớ O(1), không cần bảng dp.',
         svg=illustration_44(),
         steps=['Khớp ký tự hoặc <code>?</code> → <code>i</code> và <code>j</code> cùng tiến.',
                'Gặp <code>*</code> → ghi lại <code>star = j</code>, <code>mark = i</code>; cho nó nuốt <b>rỗng</b> trước (<code>j += 1</code>).',
                'Sai mà đã có * → <code>mark += 1</code>, <code>i = mark</code>, <code>j = star + 1</code> (nuốt thêm 1 ký tự). Chưa có * → <b>false</b>.',
                'Hết s: bỏ các <code>*</code> còn lại trong p. Đúng khi <code>j</code> chạm hết p.'],
         code=CODE44, cx=['Thời gian O(|s|·|p|) xấu nhất', 'Bộ nhớ O(1)'], cx_note='Trên đa số dữ liệu chạy gần O(|s| + |p|).',
         traps=['Cho * chỉ nuốt rỗng, không quay lại: <code>s="adceb"</code>, <code>p="*a*b"</code> ra false, đáp án đúng là true.',
                'Quên bỏ các * ở cuối p sau khi hết s.',
                'Nhớ mọi dấu * (rối): chỉ cần dấu gần nhất.'],
         practice=['#392 Is Subsequence', '#72 Edit Distance', '#10 Regular Expression Matching']),
    dict(dir='leetcode-10-regular-expression-matching', file='Kieu-Studio_LeetCode-10_Regular-Expression-Matching_cheatsheet', num=10, name='Regular Expression Matching',
         video='jw15lSSuizM', slug='regular-expression-matching', fig='hai lựa chọn khi gặp x* và bảng nhớ',
         hook='Một dấu <b>*</b> có nhiều lựa chọn. Chia nhỏ thành câu hỏi <b>dfs(i, j)</b>, rồi <b>nhớ câu đã trả lời.</b>',
         problem='Ghép <code>s</code> với <code>p</code>, phải khớp <b>toàn bộ</b> s. <code>.</code> = 1 ký tự bất kỳ; <code>x*</code> = <b>0 hoặc nhiều</b> ký tự x liền nhau.',
         examples=[('s="aa"  p="a"', 'false', False), ('s="aa"  p="a*"', 'true', True), ('s="ab"  p=".*"', 'true', True)],
         key='Bài toán lớn = nhiều câu hỏi nhỏ <code>(i, j)</code>: “s[i:] có khớp p[j:] không?”. Cùng một câu hỏi chỉ trả lời <b>một lần</b> (<code>@cache</code>).',
         svg=illustration_10(),
         steps=['Hết p (<code>j == len(p)</code>) → chỉ đúng khi cũng hết s.',
                '<code>first</code> = s[i] khớp p[j] (hoặc p[j] là <code>.</code>).',
                'Nếu <code>p[j+1]</code> là <code>*</code>: thử <b>0 lần</b> (<code>dfs(i, j+2)</code>) <b>hoặc</b> dùng thêm 1 lần (<code>first and dfs(i+1, j)</code>).',
                'Ngược lại: <code>first and dfs(i+1, j+1)</code>.'],
         code=CODE10, cx=['Thời gian O(m·n)', 'Bộ nhớ O(m·n)'], cx_note='m = len(s), n = len(p): tối đa ~m·n trạng thái, mỗi trạng thái giải một lần.',
         traps=['Quên x* có thể khớp <b>0</b> ký tự: <code>"aab"</code> với <code>"c*a*b"</code>.',
                'Đọc <code>p[j+1]</code> mà không kiểm tra <code>j + 1 &lt; len(p)</code>.',
                'Không nhớ kết quả → số nhánh tăng rất nhanh.'],
         practice=['#44 Wildcard Matching', '#72 Edit Distance', '#97 Interleaving String']),
    dict(dir='leetcode-4-median-of-two-sorted-arrays', file='Kieu-Studio_LeetCode-4_Median-of-Two-Sorted-Arrays_cheatsheet', num=4, name='Median of Two Sorted Arrays',
         video='mQ2V4bk37IM', slug='median-of-two-sorted-arrays', fig='đường cắt chia hai mảng thành nửa trái, nửa phải',
         hook='Tìm giữa mà <b>không gộp mảng</b>: tìm <b>đường cắt</b> bằng binary search.',
         problem='Cho hai mảng <b>đã sắp xếp</b> <code>nums1</code>, <code>nums2</code>. Tìm <b>trung vị</b> của tất cả phần tử, trong thời gian <code>O(log(m+n))</code>.',
         examples=[('[1,3]  [2]', '2.0', True), ('[1,2]  [3,4]', '2.5', True)],
         key='Đừng tìm <b>số</b>, hãy tìm <b>đường cắt</b>: cắt cả hai mảng để nửa trái và nửa phải bằng nhau, và <b>mọi số bên trái ≤ mọi số bên phải</b>.',
         svg=illustration_4(),
         steps=['Lấy mảng <b>ngắn</b> làm <code>a</code>. Binary search vị trí cắt <code>i</code> trên a; <code>j = (m+n+1)//2 − i</code> trên b.',
                'Bốn số sát đường cắt: <code>AL, AR</code> (của a), <code>BL, BR</code> (của b). Ngoài biên dùng <code>−∞ / +∞</code>.',
                'Hợp lệ khi <code>AL ≤ BR</code> và <code>BL ≤ AR</code>. Nếu <code>AL &gt; BR</code> → cắt sang trái; ngược lại → sang phải.',
                'Tổng lẻ → <code>max(AL, BL)</code>. Tổng chẵn → <code>(max(AL,BL) + min(AR,BR)) / 2</code>.'],
         code=CODE4, cx=['Thời gian O(log min(m, n))', 'Bộ nhớ O(1)'], cx_note='Không chậm hơn mức O(log(m+n)) mà đề yêu cầu.',
         traps=['Tìm trên mảng <b>dài</b>: j có thể âm. Luôn đổi để a là mảng ngắn.',
                'Quên <code>−∞ / +∞</code> khi một mảng rỗng hoặc cắt ở biên.',
                'Nhầm tổng lẻ/chẵn: tổng lẻ thì nửa trái nhiều hơn 1 phần tử.'],
         practice=['#35 Search Insert Position', '#34 First and Last Position', '#378 Kth Smallest in Sorted Matrix']),
]


def slack_of(h):
    for attempt in range(3):                       # headless Chrome occasionally hangs; retry instead of failing the build
        try:
            dom = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--virtual-time-budget=3000', '--dump-dom', h.as_uri()],
                                 capture_output=True, text=True, timeout=45).stdout
            return float(re.search(r'data-slack="(-?[\d.]+)"', dom).group(1))
        except (subprocess.TimeoutExpired, AttributeError):
            continue
    raise SystemExit(f'{h.name}: could not measure the page after 3 attempts')


def fit(d, h):
    """Largest zoom (<= 1.3) that leaves >= 8 px above the footer."""
    z = 1.3
    while z >= 0.8:
        h.write_text(page(d, round(z, 2)), encoding='utf-8')
        if slack_of(h) >= 8:
            return round(z, 2)
        z -= 0.03
    raise SystemExit(f'{d["file"]}: does not fit on one page even at zoom 0.8')


def main():
    check_code()
    ok = True
    for d in PAGES:
        out = EXAMPLES / d['dir'] / 'cheatsheet'
        out.mkdir(exist_ok=True)
        DOCS.mkdir(parents=True, exist_ok=True)
        h, p = out / f'{d["file"]}.html', DOCS / f'{d["file"]}.pdf'
        zoom = fit(d, h)
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={p}', h.as_uri()],
                       check=True, capture_output=True, timeout=120)
        slack = slack_of(h)
        pages = len(re.findall(rb'/Type\s*/Page[^s]', p.read_bytes()))
        print(p.relative_to(EXAMPLES.parent), p.stat().st_size, 'bytes', pages, 'page(s)', f'zoom {zoom}', f'slack above footer {slack}px' + ('' if slack >= 4 else '  <-- CONTENT RUNS INTO THE FOOTER'))
        ok &= pages == 1 and slack >= 4
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
