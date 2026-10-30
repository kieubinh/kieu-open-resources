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
