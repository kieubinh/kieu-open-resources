"""One-minute short cuts of the three GitHub Radar videos (KIEU_FORMAT=short).

A short keeps the spine of the full episode and drops the rest: hook -> numbers -> why -> how -> use -> cost -> verdict.
It drops the separate "problem" and "ideas" beats; the "why" scene carries the problem, and the verdict closes the
hook question. Visuals (art, chips, chart points, steps, commands, pros/cons) are taken from the full episode scenes by
id, so a number can never differ between the long video and its short. Narration is rewritten shorter and spells numbers
out in words; the caveat from the value beat stays on screen and in the narration.

Budget: measured with Narrator 03 at 1.0x, speech runs about 2.9 words per second (English product names are slow), so
about 150 words fit in 60 s together with the 0.4 s scene tails. Dates are on screen, not in the narration.
"""
from __future__ import annotations

SHORT_MAX_SECONDS = 60
SHORT_WORDS = (100, 160)   # sanity band for total narration words per short

# scene key -> (full-episode scene id suffix, short narration, seconds budget)
_TEXT = {
    'gr01': {
        'intro': 'AI agent báo hai mươi lỗ hổng. Bao nhiêu cái là thật? Hôm nay trên GitHub Radar: security-audit-skill của Cloudflare.',
        'growth': 'Ba mươi ngày trước, khoảng hai mươi bốn nghìn sao. Hôm nay hơn năm mươi hai nghìn: gấp đôi trong một tháng, '
                  'và còn đang tăng tốc.',
        'why': 'Agent vừa tìm vừa tự chấm điểm, như học sinh tự chấm bài. Skill này tách hai vai: '
               'một agent tìm lỗi, một agent chỉ để bác bỏ.',
        'how': 'Sáu giai đoạn: trinh sát, săn lỗi, kiểm chứng, ghi dữ liệu, xác minh lại, rồi báo cáo từ bản ghi đã duyệt.',
        'usage': 'Cài bằng Skills CLI, rồi nói với agent: security audit this codebase. Chạy mã cần sandbox.',
        'value': 'Kết quả là dữ liệu có schema, chạy lại thì cộng dồn. Cái giá: tốn token, cần sandbox, '
                 'và chỉ quét mã bạn được phép.',
        'outro': 'Vậy hai mươi phát hiện, cái nào là thật? Cái nào tự chứng minh được. Hãy thử trong sandbox.',
    },
    'gr02': {
        'intro': 'Trang web do AI làm, mà bạn thấy quen quen? Hôm nay: Impeccable của Paul Bakaus, từ vựng thiết kế cho coding agent.',
        'growth': 'Gần chín mươi lăm nghìn sao, thêm hơn hai mươi sáu phần trăm trong một tháng, '
                  'và tuần qua tăng gần gấp đôi tốc độ.',
        'why': 'Agent hay cho ra cùng một kiểu: font Inter, gradient tím xanh, thẻ lồng trong thẻ. '
               'Impeccable lấp khoảng trống bằng từ vựng chung.',
        'how': 'Ba lớp: ngữ cảnh trong PRODUCT.md và DESIGN.md, hai mươi bốn lệnh có tên, '
               'và sáu mươi hai quy tắc phát hiện không cần LLM.',
        'usage': 'Chạy npx impeccable install, rồi gọi lệnh với mục tiêu hẹp, như critique the pricing cards.',
        'value': 'Từ vựng chung, kết quả lặp lại được. Nhưng hook đã cài vẫn chạy ngoài phê duyệt của model, '
                 'và có telemetry ẩn danh.',
        'outro': 'Lần tới thấy trang quen quen, bạn đã có từ để gọi tên nó. Thử với một thành phần nhỏ, xem hook trước.',
    },
    'gr03': {
        'intro': 'Sáng nay bạn bảo agent: tiếp tục việc hôm qua. Nó hỏi lại: dự án này là gì? Hôm nay: claude-mem, trí nhớ cho Claude Code.',
        'growth': 'Hơn một trăm linh bốn nghìn sao, thêm khoảng mười phần trăm trong một tháng. Lớn mà vẫn tăng đều.',
        'why': 'Phiên kết thúc, ngữ cảnh biến mất. Hôm sau agent bắt đầu từ trang giấy trắng, '
               'và bạn lại giải thích dự án từ đầu.',
        'how': 'Sáu hook ghi lại phiên làm việc vào SQLite. Khi cần nhớ, agent tìm ba bước: chỉ mục gọn, bối cảnh, '
               'rồi mới tải chi tiết.',
        'usage': 'Chạy npx claude-mem install, khởi động lại Claude Code, ngữ cảnh phiên trước tự xuất hiện. '
                 'Bước đăng nhập có thể bỏ qua.',
        'value': 'Bạn không phải giải thích lại mỗi sáng. Nhưng nó ghi lại hoạt động của agent: hãy xem dữ liệu lưu ở đâu.',
        'outro': 'Nếu agent nhớ hôm qua, bạn bắt đầu từ đâu? Thử trên một dự án nhỏ trước.',
    },
}
# short beat -> full-episode beat whose visuals it reuses
_FROM = {'intro': 'intro', 'growth': 'growth', 'why': 'why', 'how': 'how', 'usage': 'usage', 'value': 'value', 'outro': 'outro'}


# ───────────────────────── English cut (KIEU_LANG=en) ─────────────────────────
# Same seven beats, same numbers; narration, titles and on-screen words are English. English B at 1.0x speaks only about 2.0
# words/s (measured: 143 words ran 72 s), so an English short is about 100 words.
_EN_TEXT = {
    'gr01': {
        'intro': "Your AI agent reports twenty vulnerabilities. How many are real? Cloudflare's security-audit-skill.",
        'growth': 'Thirty days ago, about twenty-four thousand stars. Now over fifty-two thousand, and accelerating.',
        'why': 'A model grading its own findings marks its own exam. So one agent hunts, another only disproves.',
        'how': 'Six stages: recon, hunt, verify, record, re-check, report.',
        'usage': 'Install with the Skills CLI, then say: security audit this codebase. Run code only in a sandbox.',
        'value': 'Schema-backed data, and reruns add up. The cost: tokens and a sandbox.',
        'outro': 'So, of twenty findings, which are real? Those that prove themselves.',
    },
    'gr02': {
        'intro': 'A web page made by AI, strangely familiar? Meet Impeccable, a design vocabulary for agents.',
        'growth': 'Almost ninety-five thousand stars, up twenty-six percent in a month, and the last week nearly doubled.',
        'why': 'Same look every time: purple gradients, cards in cards. Impeccable gives agents shared words.',
        'how': 'Three layers: context files, twenty-four named commands, sixty-two rules, no LLM.',
        'usage': 'Run npx impeccable install, then call a command on one target, like critique the pricing cards.',
        'value': "Shared vocabulary, repeatable results. But hooks run outside model approval, and there's anonymous telemetry.",
        'outro': "Next time a page feels familiar, you'll have words for it. Check the hooks first.",
    },
    'gr03': {
        'intro': "This morning: continue yesterday's work. The agent asks: what project? Meet claude-mem.",
        'growth': 'Over a hundred and four thousand stars, up ten percent in a month. Big, and still growing.',
        'why': 'Session ends, context vanishes. Next day the agent starts blank, and you explain everything again.',
        'how': 'Hooks record each session into SQLite. Recall takes three steps: index, context, then only needed details.',
        'usage': 'Run npx claude-mem install and restart Claude Code. The sign-in step is optional.',
        'value': "No more re-explaining. But it records your agent's activity, so check where it's stored.",
        'outro': 'If your agent remembered yesterday, where would you start? Try a small project.',
    },
}
_NOTE_EN = 'Total stars: GitHub API · gains: GitHub Trending (7 and 30-day windows) · snapshot Oct 29, 2026'
# beat -> (title, lines, data overrides); chips/pts labels are translated by helpers below
_EN_VISUAL = {
    'gr01': {
        'intro': ('', [], {'q': "How many of the AI's findings are real?"}),
        'growth': ('Speeding up, not cooling down', [_NOTE_EN], {'tick': '≈ 38 seconds / star', 'tick_basis': 'at the last 7-day rate', 'factor': 'x2.2'}),
        'why': ('The agent reads, and its context fills up', [], {}),
        'how': ('Six stages, one job each', ['The final report is generated from verified records, not written by hand.'],
                {'steps': [['map', 'Recon', 'architecture · boundaries'], ['search', 'Hunt', 'separate hunters'], ['shield', 'Verify', 'tries to disprove'],
                           ['doc', 'Data', 'findings + schema'], ['eye', 'Re-check', 'independent agent'], ['check', 'Report', 'from approved records']]}),
        'usage': ('Two steps, and one condition you must not skip', ['Needs: an agent with tool use and parallel sub-agents · Node.js · an OS-enforced sandbox.'],
                  {'cmds': ['npx skills add https://github.com/cloudflare/security-audit-skill \\', '  --skill security-audit', '', '# in the agent, at the source folder', '> security audit this codebase'],
                   'note': 'No sandbox → stays needs_validation, target code is not run.'}),
        'value': ('The gains and the cost', ['Think twice: token-hungry, needs a sandbox, scan only code you are allowed to test.'],
                  {'pros': [['doc', 'Schema-backed data'], ['repeat', 'Reruns add up'], ['eye', 'See what was covered']], 'cons': [['clock', 'Token cost'], ['lock', 'Needs a sandbox']]}),
        'outro': ('The answer for 20 findings?', [], {'chips': [['check', 'Try it on your repo'], ['lock', 'Inside a sandbox'], ['clock', 'Re-check the numbers']],
                                                    'teaser': 'Next: stopping AI from making identical interfaces'}),
    },
    'gr02': {
        'intro': ('', [], {'q': "Haven't I seen this page before?"}),
        'growth': ('Nearly double the speed in the last week', [_NOTE_EN], {'tick': '≈ 83 seconds / star', 'tick_basis': 'at the last 7-day rate', 'factor': '+26.4%'}),
        'why': ('Five tells of "AI slop" interfaces', [], {}),
        'how': ('Three layers: context, commands, detector', ['Detector: 62 deterministic rules, no LLM or API key.'],
                {'steps': [['doc', 'init', 'writes PRODUCT.md'], ['palette', 'document', 'writes DESIGN.md'], ['sliders', 'Steer', 'bolder · quieter · distill'],
                           ['eye', 'Review', 'critique · audit P0–P3'], ['check', 'Finish', 'polish · harden · adapt'], ['bug', 'Detect', '62 rules · hook / CI']]}),
        'usage': ('Install once, call narrow commands', ['Rules that need a rendered page (contrast, small text) run when scanning a URL.'],
                  {'cmds': ['npx impeccable install', '', '# in the agent', '> /impeccable init', '> /impeccable critique the pricing cards', '', '# CI or terminal, no agent needed', 'npx impeccable detect src/'],
                   'note': 'Narrow is clear: one component at a time.'}),
        'value': ('The gains and the cost', ["Think twice: hooks run outside the model's approval; anonymous telemetry can be turned off."],
                  {'pros': [['sliders', 'Shared vocabulary'], ['eye', 'A reviewer in the loop'], ['repeat', 'Repeatable results']], 'cons': [['hook', 'Hooks bypass approval'], ['eye', 'Anonymous telemetry']]}),
        'outro': ("Next time a page looks familiar, you'll have the words", [], {'chips': [['sliders', 'Start with one component'], ['hook', 'Check installed hooks'], ['clock', 'Re-check the numbers']],
                                                                               'teaser': 'Next: memory for AI agents'}),
    },
    'gr03': {
        'intro': ('', [], {'q': 'What did we do yesterday?'}),
        'growth': ('Already big, still growing steadily', [_NOTE_EN], {'tick': '≈ 4.5 min / star', 'tick_basis': 'at the 30-day average', 'factor': '+10.1%'}),
        'why': ('Every new session is a blank page', [], {}),
        'how': ('Hooks record, a worker stores, MCP tools search', ['Three search layers: search → timeline → get_observations.'],
                {'steps': [['hook', 'Lifecycle hooks', '6 session events'], ['gear', 'Local worker', 'HTTP API · Bun'], ['db', 'SQLite', 'sessions · observations · summaries'],
                           ['layers', 'Chroma', 'keyword + semantic'], ['search', 'search', 'compact index'], ['doc', 'get_observations', 'details, filtered ids only']]}),
        'usage': ('One install, restart, and it remembers', ['Needs Node.js 20+. The installer may offer a sign-in; you can skip it.'],
                  {'cmds': ['npx claude-mem install', '', '# or in Claude Code', '/plugin marketplace add thedotmack/claude-mem', '/plugin install claude-mem', '', '# skip the sign-in',
                            'CLAUDE_MEM_ONLINE_OPTIN=false npx claude-mem install'],
                   'note': 'Restart Claude Code → context from earlier sessions appears.'}),
        'value': ('The gains and the cost', ['Think twice: hooks record tool activity — check what is stored, where, and whether it syncs to the cloud.'],
                  {'pros': [['calendar', 'Continuity between sessions'], ['search', 'Natural-language recall'], ['clock', 'Tokens on demand']], 'cons': [['eye', 'Records activity'], ['lock', 'Check where data lives']]}),
        'outro': ('If your agent remembered yesterday, where would you start?', [], {'chips': [['box', 'Try a small project'], ['lock', 'Check what is stored'], ['clock', 'Re-check the numbers']],
                                                                                    'teaser': 'See you at the next GitHub Radar'}),
    },
}
_CHIP_LABELS = {'Chủ sở hữu': 'Owner', 'Tác giả': 'Author', 'Giấy phép': 'License', 'Tạo từ': 'Created', 'Fork': 'Forks'}
_PT_LABELS = {'30 ngày trước': '30 days ago', '7 ngày trước': '7 days ago', 'Hôm nay': 'Today'}
_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def _en_value(v: str) -> str:
    parts = v.split('/')
    if len(parts) == 3 and all(x.isdigit() for x in parts):              # dd/mm/yyyy -> Mon d, yyyy
        return f'{_MONTHS[int(parts[1]) - 1]} {int(parts[0])}, {parts[2]}'
    if v.replace('.', '').isdigit() and '.' in v:                          # 3.365 -> 3,365
        return v.replace('.', ',')
    return v


def make_shorts_en(episodes: dict, sc) -> dict:
    """English one-minute cuts. Scene ids use `e` (r1e-intro) so their WAVs never collide with the Vietnamese ones."""
    out = {}
    for ep, scenes in episodes.items():
        by_beat = {s.beat: s for s in scenes}
        rows = []
        for beat, text in _EN_TEXT[ep].items():
            full = by_beat[_FROM[beat]]
            title, lines, over = _EN_VISUAL[ep][beat]
            data = dict(full.data); data.update(over); data['lang'] = 'en'
            if 'chips' in full.data and 'chips' not in over:
                data['chips'] = [[i, _CHIP_LABELS.get(lb, lb), _en_value(val)] for i, lb, val in full.data['chips']]
            if 'pts' in full.data:
                data['pts'] = [[_PT_LABELS[lb], v] for lb, v in full.data['pts']]
            tag = 'GITHUB RADAR · EPISODE ' + full.phase.split('TẬP ')[-1] + ' · SHORT' if beat == 'intro' else {
                'growth': 'THE NUMBERS', 'why': 'WHY THE AUTHOR BUILT IT', 'how': 'HOW IT WORKS', 'usage': 'HOW TO USE IT', 'value': 'WHY IT HELPS', 'outro': 'WRAP-UP'}[beat]
            rows.append(sc(full.id.replace('-', 'e-', 1), tag, title, lines, text, 8, full.mode, repo=full.repo, beat=beat, data=data))
        out[ep] = rows
    return out


def make_shorts(episodes: dict, sc) -> dict:
    """episodes: {'gr01': [Scene...]}, sc: the Scene factory from episode.py. Returns {'gr01': [short Scene...]}."""
    out = {}
    for ep, scenes in episodes.items():
        by_beat = {s.beat: s for s in scenes}
        rows = []
        for beat, text in _TEXT[ep].items():
            full = by_beat[_FROM[beat]]
            sid = full.id.replace('-', 's-', 1)          # r1-intro -> r1s-intro: unique WAV names, shared audio folder
            phase = full.phase + (' · BẢN NGẮN' if beat == 'intro' else '')
            rows.append(sc(sid, phase, full.title, full.lines, text, 8, full.mode, repo=full.repo, beat=beat, data=dict(full.data)))
        out[ep] = rows
    return out
