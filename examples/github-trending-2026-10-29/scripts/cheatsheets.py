"""One-page A4 cheat sheets (PDF) for the six GitHub Radar Shorts: GR01..GR03 x Vietnamese / English.

Numbers come from docs/SOURCE_MANIFEST.json, steps / commands / pros / cons from the same scene data the videos use,
so a sheet can never disagree with its Short. HTML -> PDF with headless Chrome (no extra Python packages).

    python3 scripts/cheatsheets.py   # writes <repo>/docs/cheatsheets/github-radar/GR0N_<repo>_cheatsheet_{vi,en}.pdf
"""
import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import episode as ep_mod  # noqa: E402  (env defaults: Vietnamese long format)

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
OUT = ROOT.parents[1] / 'docs' / 'cheatsheets' / 'github-radar'
MANIFEST = json.loads((ROOT / 'docs' / 'SOURCE_MANIFEST.json').read_text())
REPO_DATA = {r['full_name']: r for r in MANIFEST['repos']}
COLORS = {'gr01': '#0f9d86', 'gr02': '#d98a00', 'gr03': '#3c6fe0'}
ICONS = {'map': '🗺', 'search': '🔎', 'shield': '🛡', 'doc': '📄', 'eye': '👁', 'check': '✅', 'palette': '🎨', 'sliders': '🎚', 'bug': '🐞',
         'hook': '🪝', 'gear': '⚙️', 'db': '🗄', 'layers': '🧱', 'rocket': '🚀', 'box': '📦', 'users': '👥', 'book': '📖', 'calendar': '📅',
         'clock': '⏱', 'lock': '🔒', 'repeat': '🔁'}

# One-line "what it is" and "why it exists" per episode and language (hand-written, consistent with the narration).
TEXT = {
    'vi': {
        'gr01': ('Skill của Cloudflare cho AI agent săn lỗ hổng bảo mật: một agent săn, một agent khác chỉ cố bác bỏ.',
                 'Một agent vừa tìm lỗi vừa tự chấm điểm giống học sinh tự chấm bài thi của mình. Tách vai để kết quả đáng tin hơn.'),
        'gr02': ('Bộ từ vựng thiết kế cho AI agent: 24 lệnh có tên và 62 quy tắc phát hiện, không cần LLM hay API key.',
                 'AI hay tạo giao diện giống nhau (gradient tím, thẻ lồng thẻ). Có lệnh có tên thì agent không phải đoán.'),
        'gr03': ('Plugin trí nhớ cho Claude Code: tự ghi lại phiên làm việc vào SQLite cục bộ và gợi lại ở phiên sau.',
                 'Hết phiên là ngữ cảnh biến mất, hôm sau agent bắt đầu từ trang giấy trắng. Tiết lộ dần để nhớ nhiều mà không đốt token.')},
    'en': {
        'gr01': ("Cloudflare's skill for AI agents hunting security vulnerabilities: one agent hunts, another only tries to disprove.",
                 'A model that grades its own findings is marking its own exam. Splitting the roles makes the result easier to trust.'),
        'gr02': ('A design vocabulary for AI agents: 24 named commands and 62 detector rules, no LLM or API key.',
                 'AI keeps producing the same look (purple gradients, cards inside cards). Named commands mean the agent stops guessing.'),
        'gr03': ('A memory plugin for Claude Code: records sessions into local SQLite and recalls them in the next session.',
                 'Session ends, context vanishes, and the agent starts blank. Progressive disclosure recalls a lot without burning tokens.')},
}
IDEAS_EN = {
    'gr01': [['rocket', 'Before a release', 'read the needs_validation list'], ['box', 'An unfamiliar library', 'try it in a sandbox'],
             ['users', 'Two-team exercise', 'hunters vs reviewers'], ['book', 'Review checklist', 'reuse the attack classes']],
    'gr02': [['bug', 'Design lint in CI', 'detect on pull requests'], ['users', 'UI review sessions', 'critique for the whole team'],
             ['palette', 'Keep the style', 'DESIGN.md for agents'], ['book', 'Observation exercise', 'name the repeating AI patterns']],
    'gr03': [['book', 'Decision log', 'why we chose this way'], ['calendar', 'Memory for a content series', 'naming · style'],
             ['bug', 'Review debug history', 'where do I go wrong'], ['shield', 'Pair with a security skill', 'remember handled findings']],
}
LABELS = {
    'vi': {'ep': 'TẬP', 'tag': 'CHEATSHEET MỘT TRANG · GITHUB RADAR', 'stars': 'Tổng sao', 'month': 'Tăng 30 ngày', 'week': 'Tăng 7 ngày', 'today': 'Hôm nay',
           'forks': 'Fork', 'license': 'Giấy phép', 'created': 'Tạo từ', 'what': 'Là gì', 'why': 'Vì sao có', 'how': 'Cách hoạt động', 'start': 'Bắt đầu nhanh',
           'pros': 'Được', 'cons': 'Giá phải trả', 'think': 'Cần cân nhắc', 'ideas': 'Làm ngay', 'links': 'Liên kết',
           'data': 'Số liệu: tổng sao từ GitHub API, mức tăng từ GitHub Trending (hai cửa sổ 7 và 30 ngày), chụp ngày 29/10/2026. Sao đo sự chú ý, không đo chất lượng. Hãy kiểm tra lại số trước khi trích dẫn.',
           'tested': 'Kieu Studio chưa chạy thử công cụ này: nội dung dựa trên README và tài liệu của tác giả.', 'ai': 'Giọng đọc và nhân vật trong video là AI (VoiceStudio cục bộ); minh họa do Kieu Studio vẽ.', 'video': 'Xem video'},
    'en': {'ep': 'EPISODE', 'tag': 'ONE-PAGE CHEAT SHEET · GITHUB RADAR', 'stars': 'Total stars', 'month': '30-day gain', 'week': '7-day gain', 'today': 'Today',
           'forks': 'Forks', 'license': 'License', 'created': 'Created', 'what': 'What it is', 'why': 'Why it exists', 'how': 'How it works', 'start': 'Quick start',
           'pros': 'Gains', 'cons': 'Cost', 'think': 'Think twice', 'ideas': 'Try it', 'links': 'Links',
           'data': 'Data: total stars from the GitHub API, gains from GitHub Trending (7 and 30-day windows), snapshot Oct 29, 2026. Stars measure attention, not quality. Re-check the numbers before quoting them.',
           'tested': 'Kieu Studio has not run this tool: the content is based on the README and the authors\' docs.', 'ai': 'The voice and avatar in the video are AI generated (local VoiceStudio); illustrations drawn by Kieu Studio.', 'video': 'Watch the video'},
}


def num(n, lang):
    return f'{n:,}'.replace(',', '.' if lang == 'vi' else ',')


def esc(s):
    return html.escape(str(s))


def icon(k):
    return ICONS.get(k, '•')


def build(ep, lang):
    L = LABELS[lang]
    if lang == 'vi':
        scenes = {s.beat: s for s in ep_mod.EPISODES[ep]}
    else:
        scenes = {s.beat: s for s in ep_mod.SHORTS_EN[ep]}
    repo = scenes['intro'].data['repo']
    r = REPO_DATA[repo]
    color = COLORS[ep]
    what, why = TEXT[lang][ep]
    steps, usage, value = scenes['how'].data['steps'], scenes['usage'].data, scenes['value'].data
    ideas = scenes['ideas'].data['ideas'] if lang == 'vi' else IDEAS_EN[ep]
    caveat = scenes['value'].lines[0] if scenes['value'].lines else ''
    note = usage.get('note', '')
    needs = scenes['usage'].lines[0] if scenes['usage'].lines else ''
    facts = [(L['stars'], num(r['stars_total'], lang)), (L['month'], '+' + num(r['stars_month'], lang))]
    facts.append((L['week'], '+' + num(r['stars_week'], lang)) if r.get('stars_week') else (L['today'], '+' + num(r['stars_today'], lang)))
    facts += [(L['forks'], num(r['forks'], lang)), (L['license'], r['license']), (L['created'], r['created'])]
    n = ep[-1]
    links = [(repo, r['url'])] + [(u.split(' ')[0].replace('https://', ''), u.split(' ')[0]) for u in r['sources'] if u.startswith('https://') and 'github.com' not in u]
    links.append(('kieu.app', 'https://kieu.app'))
    cmds = '\n'.join(usage['cmds'])
    return f'''<!doctype html><html lang="{lang}"><meta charset="utf-8"><title>GR0{n} {repo} cheat sheet</title>
<style>
@page {{ size: A4; margin: 0 }}
* {{ box-sizing: border-box }}
body {{ margin: 0; width: 210mm; height: 297mm; font: 9.6pt/1.38 -apple-system, "Helvetica Neue", Arial, sans-serif; color: #14233b; background: #fff; overflow: hidden }}
header {{ background: #0a1a2f; color: #fff; padding: 11mm 13mm 7mm; border-bottom: 3mm solid {color} }}
.tag {{ font-size: 8pt; letter-spacing: .12em; color: #8fb0d8; font-weight: 700 }}
h1 {{ margin: 2mm 0 1.5mm; font: 800 19pt/1.15 ui-monospace, Menlo, monospace; color: {color}; filter: brightness(1.25) }}
.ep {{ font-size: 9pt; color: #c9d8ee }}
main {{ padding: 5mm 13mm 0 }}
.facts {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 2.5mm; margin-bottom: 4mm }}
.fact {{ border: .35mm solid #d5deeb; border-top: 1.2mm solid {color}; border-radius: 1.5mm; padding: 1.8mm 2.2mm; text-align: center }}
.fact b {{ display: block; font-size: 11.5pt }} .fact span {{ font-size: 7.4pt; color: #5b6b82; text-transform: uppercase; letter-spacing: .04em }}
h2 {{ margin: 3.5mm 0 1.6mm; font-size: 9pt; letter-spacing: .1em; text-transform: uppercase; color: {color}; filter: brightness(.85) }}
p {{ margin: 0 0 1.4mm }}
.steps {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.2mm }}
.step {{ background: #f2f6fb; border-radius: 1.8mm; padding: 2mm 2.6mm; display: flex; gap: 2mm; align-items: flex-start }}
.step i {{ font-style: normal; font-size: 13pt; line-height: 1 }} .step b {{ display: block }} .step span {{ font-size: 8.4pt; color: #4b5c75 }}
pre {{ margin: 0; background: #0a1a2f; color: #dff6ff; border-radius: 1.8mm; padding: 3mm 3.4mm; font: 8.3pt/1.45 ui-monospace, Menlo, monospace; white-space: pre-wrap; word-break: break-all }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4mm }}
ul {{ margin: 0; padding: 0; list-style: none }} li {{ margin: 0 0 1mm }}
.pro li::before {{ content: "＋ "; color: #1a8f4a; font-weight: 800 }} .con li::before {{ content: "− "; color: #c0392b; font-weight: 800 }}
.warn {{ background: #fff6e0; border-left: 1.2mm solid #e5a000; border-radius: 1.5mm; padding: 2.2mm 3mm; margin-top: 2.4mm }}
.ideas {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 2.2mm }}
.idea {{ border: .35mm solid #d5deeb; border-radius: 1.8mm; padding: 1.8mm 2.6mm }} .idea b {{ display: block }} .idea span {{ font-size: 8.4pt; color: #4b5c75 }}
footer {{ position: absolute; left: 13mm; right: 13mm; bottom: 7mm; font-size: 7.6pt; color: #5b6b82; border-top: .3mm solid #d5deeb; padding-top: 2mm }}
footer a {{ color: inherit }} .links {{ font-size: 8.4pt; margin-bottom: 1.5mm; color: #14233b }}
</style>
<header><div class="tag">KIEU STUDIO · {esc(L['tag'])}</div><h1>{esc(repo)}</h1><div class="ep">{esc(L['ep'])} {n} · {esc(scenes['intro'].data['q'])}</div></header>
<main>
<div class="facts">{''.join(f'<div class="fact"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for k, v in facts)}</div>
<h2>{esc(L['what'])}</h2><p>{esc(what)}</p>
<h2>{esc(L['why'])}</h2><p>{esc(why)}</p>
<h2>{esc(L['how'])}</h2>
<div class="steps">{''.join(f'<div class="step"><i>{icon(s[0])}</i><div><b>{esc(s[1])}</b><span>{esc(s[2])}</span></div></div>' for s in steps)}</div>
<h2>{esc(L['start'])}</h2><pre>{esc(cmds)}</pre>
<p style="margin-top:1.6mm"><small>{esc(note)} {esc(needs)}</small></p>
<div class="two"><div><h2>{esc(L['pros'])}</h2><ul class="pro">{''.join(f'<li>{esc(p[1])}</li>' for p in value['pros'])}</ul></div>
<div><h2>{esc(L['cons'])}</h2><ul class="con">{''.join(f'<li>{esc(c[1])}</li>' for c in value['cons'])}</ul></div></div>
<div class="warn"><b>{esc(L['think'])}:</b> {esc(caveat.split(':', 1)[-1].strip() if ':' in caveat else caveat)}</div>
<h2>{esc(L['ideas'])}</h2>
<div class="ideas">{''.join(f'<div class="idea"><b>{icon(i[0])} {esc(i[1])}</b><span>{esc(i[2])}</span></div>' for i in ideas)}</div>
</main>
<footer><div class="links"><b>{esc(L['links'])}:</b> {' · '.join(f'<a href="{esc(u)}">{esc(t)}</a>' for t, u in links)}</div>{esc(L['data'])}<br>{esc(L['tested'])} {esc(L['ai'])}</footer></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    for ep in ('gr01', 'gr02', 'gr03'):
        for lang in ('vi', 'en'):
            page = tmp / f'{ep}_{lang}.html'
            page.write_text(build(ep, lang), encoding='utf-8')
            pdf = OUT / f"{ep.upper()}_{ep_mod.EPISODES[ep][0].data['repo'].split('/')[1]}_cheatsheet_{lang}.pdf"
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={pdf}', page.as_uri()],
                           check=True, capture_output=True)
            print('wrote', pdf.relative_to(ROOT.parents[1]))


if __name__ == '__main__':
    main()
