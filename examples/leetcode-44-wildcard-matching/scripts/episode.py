"""Kieu Studio EP03 — LeetCode #44 Wildcard Matching.

Single source of truth for scenes, narration beats and subtitles.

* ``Beat.text`` is the subtitle exactly as the viewer reads it.
* ``Beat.say``  is what VoiceStudio speaks (numbers/symbols spelled out in Vietnamese).
* ``Beat.cue``  is optional, mode-specific data that lets a visual stay in step with a beat
  (code line range, trace step, trace event...). Real timings come from the generated audio.

Compatible with skills/kieu-leetcode-video/scripts/audit_episode.py and check_glyphs.py
(Scene fields: id, phase, title, lines, script, min_seconds, mode, silent).
"""
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so the skill's audit script can load this file by path

from build_trace import derive_events, source_block, summarise
from vi_text import vi_decimal, vi_int, vn_group

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = json.loads((ROOT / "src/data/verification.json").read_text(encoding="utf-8"))

EPISODE = {"number": 3, "problem": 44, "title": "Wildcard Matching", "difficulty": "Hard",
           "url": "https://leetcode.com/problems/wildcard-matching/"}
# Verified on the live LeetCode problem page, 28 Oct 2026 (see docs/SOURCES.md).
STATS = {"date": "2026-10-28", "accepted": 967654, "total_display": "2.9M", "acceptance": "33.1%"}


@dataclass(frozen=True)
class Beat:
    text: str
    say: str = ""
    cue: object = None

    @property
    def spoken(self):
        return self.say or self.text


@dataclass(frozen=True)
class Scene:
    id: str
    phase: str
    title: str
    lines: tuple
    script: str
    min_seconds: float
    mode: str
    silent: bool
    beats: tuple


def b(text, say="", cue=None):
    return Beat(text, say, cue)


def sc(id, phase, title, lines, beats, mode, silent=False, secs=0.0):
    beats = tuple(beats)
    return Scene(id, phase, title, tuple(lines), " ".join(x.text for x in beats), float(secs), mode, silent, beats)


# ---- real execution data used for cues -------------------------------------------------
_LINES, _FIRST = source_block()
_MAIN = summarise("adceb", "*a*b", _LINES, _FIRST)
_EVENTS = _MAIN["events"]
_STEPS = _MAIN["steps"]
assert [e["kind"] for e in _EVENTS] == ["star", "match", "star", "backtrack", "backtrack", "backtrack", "match"]
_RET_STEP = len(_STEPS) - 1  # the 'return' event
_TOTAL_STEPS = len(_STEPS)

V = VERIFICATION
EX_CASES = V["exhaustive"]["cases"]
RAND_CASES = V["random"]["cases"]
WORST_ITERS = V["worst"]["loop_iterations"]
TYPICAL_RATIO = V["typical"]["mean_iterations_per_char"]
BLOW = json.loads((ROOT / "src/data/trace.json").read_text(encoding="utf-8"))["blowup"]["rows"]
BLOW_FIRST, BLOW_LAST = BLOW[0]["calls"], BLOW[-1]["calls"]
DP_CELLS = V["max_cells_for_constraints"]


def _ratio_text(x):
    return str(x).replace(".", ",")


S = [
    sc("01-mission", "KIEU STUDIO · SỨ MỆNH", "LeetCode là bài tập. Tư duy là mục tiêu.",
       ["KIEU STUDIO · THE ART OF CODING", "EP03 · LeetCode #44 · Wildcard Matching",
        "Hiểu → Giả thuyết → Kiểm chứng → Rút kinh nghiệm"],
       [b("Chào mừng bạn đến với Kieu Studio, The Art of Coding.",
          "Chào mừng bạn đến với Kiều Studio, The Art of Coding."),
        b("Ở đây, LeetCode chỉ là bài tập luyện. Điều chúng ta thật sự rèn là kỹ năng giải quyết vấn đề."),
        b("Với mỗi bài toán, ta lặp lại bốn bước: hiểu đề, đặt giả thuyết, kiểm chứng, và rút kinh nghiệm."),
        b("Tập 3 hôm nay là bài #44, Wildcard Matching. Đây là bài Hard, nhưng ta sẽ đi từng bước.",
          "Tập ba hôm nay là bài bốn mươi bốn, Wildcard Matching. Đây là bài Hard, nhưng ta sẽ đi từng bước.")],
       "mission"),

    sc("02-problem", "01 · ĐỌC ĐỀ", "Wildcard Matching",
       ["? khớp đúng một ký tự bất kỳ", "* khớp một dãy ký tự bất kỳ, kể cả dãy rỗng", "Khớp phải phủ kín TOÀN BỘ chuỗi"],
       [b("Đề bài cho một chuỗi s và một mẫu p. Ta cần cho biết mẫu có khớp toàn bộ chuỗi hay không."),
        b("Trong mẫu, dấu hỏi chấm (?) khớp đúng một ký tự bất kỳ.", "Trong mẫu, dấu hỏi chấm khớp đúng một ký tự bất kỳ."),
        b("Dấu sao (*) khớp một dãy ký tự bất kỳ, kể cả dãy rỗng.", "Dấu sao khớp một dãy ký tự bất kỳ, kể cả dãy rỗng."),
        b("Chữ cái thường chỉ khớp chính nó. Và khớp phải phủ kín toàn bộ chuỗi, không phải chỉ một phần.")],
       "problem"),

    sc("03-constraints", "01 · ĐỌC ĐỀ", "Input, Output và Constraints",
       ["INPUT: s (chuỗi), p (mẫu)", "OUTPUT: true / false", "0 ≤ s.length, p.length ≤ 2000",
        "s: chữ cái thường a–z", "p: chữ cái thường, ? và *"],
       [b("Đầu vào là chuỗi s và mẫu p. Đầu ra là một giá trị đúng hoặc sai."),
        b("Độ dài của s và p đều từ 0 đến 2000, nên cả hai đều có thể rỗng.",
          "Độ dài của s và p đều từ không đến hai nghìn, nên cả hai đều có thể rỗng."),
        b("Chuỗi s chỉ có chữ cái thường tiếng Anh. Mẫu p có chữ cái thường, dấu ? và dấu *.",
          "Chuỗi s chỉ có chữ cái thường tiếng Anh. Mẫu p có chữ cái thường, dấu hỏi chấm và dấu sao."),
        b("2000 × 2000 = 4 triệu. Hãy nhớ con số này: nó cho biết cách làm nào còn dùng được.",
          "Hai nghìn nhân hai nghìn bằng bốn triệu. Hãy nhớ con số này: nó cho biết cách làm nào còn dùng được.")],
       "constraints"),

    sc("04-stats", "01 · ĐỌC ĐỀ", "Bài này khó đến mức nào?",
       ["Hard", f"{vn_group(STATS['accepted'])} lượt nộp được chấp nhận", "≈ 2,9 triệu lượt nộp", "33,1% acceptance rate"],
       [b("Theo trang LeetCode ngày 28/10/2026, bài này được xếp mức Hard.",
          "Theo trang LeetCode ngày hai mươi tám tháng mười năm hai nghìn không trăm hai mươi sáu, bài này được xếp mức Hard."),
        b(f"Có {vn_group(STATS['accepted'])} lượt nộp được chấp nhận, trên tổng khoảng 2,9 triệu lượt nộp.",
          f"Có {vi_int(STATS['accepted'])} lượt nộp được chấp nhận, trên tổng khoảng hai phẩy chín triệu lượt nộp."),
        b("Tỷ lệ chấp nhận là 33,1%. Đây là số lượt nộp bài, không phải số người đã giải được.",
          f"Tỷ lệ chấp nhận là {vi_decimal('33,1')} phần trăm. Đây là số lượt nộp bài, không phải số người đã giải được."),
        b("Bài Hard không phải bài không thể. Nó chỉ cần một quy trình suy nghĩ tốt.")],
       "stats"),

    sc("05-example1", "02 · VÍ DỤ CHÍNH THỨC", "Ví dụ 1",
       ['s = "aa"', 'p = "a"', "Output: false"],
       [b('Ví dụ 1: chuỗi s là "aa", mẫu p là "a".', "Ví dụ một: chuỗi s là hai chữ a, mẫu p là một chữ a."),
        b("Chữ a của mẫu khớp với chữ a đầu tiên của chuỗi."),
        b("Nhưng chuỗi còn dư một chữ a, trong khi mẫu đã hết. Khớp một phần là chưa đủ, nên kết quả là sai (false).",
          "Nhưng chuỗi còn dư một chữ a, trong khi mẫu đã hết. Khớp một phần là chưa đủ, nên kết quả là sai."),
        b("Bài học 1: luôn kiểm tra điều kiện kết thúc của cả hai phía.", "Bài học một: luôn kiểm tra điều kiện kết thúc của cả hai phía.")],
       "ex1"),

    sc("06-example2", "02 · VÍ DỤ CHÍNH THỨC", "Ví dụ 2",
       ['s = "aa"', 'p = "*"', "Output: true"],
       [b('Ví dụ 2: chuỗi s vẫn là "aa", nhưng mẫu p chỉ có một dấu sao.',
          "Ví dụ hai: chuỗi s vẫn là hai chữ a, nhưng mẫu p chỉ có một dấu sao."),
        b("Dấu sao thay cho bất kỳ dãy ký tự nào. Nó nuốt chữ a đầu tiên, rồi nuốt thêm chữ a thứ hai."),
        b("Cả chuỗi và mẫu cùng kết thúc, nên kết quả là đúng (true).", "Cả chuỗi và mẫu cùng kết thúc, nên kết quả là đúng."),
        b("Bài học 2: một ký hiệu có thể tạo ra nhiều lựa chọn. Dấu sao có thể nuốt không, một, hai ký tự, hoặc nhiều hơn.",
          "Bài học hai: một ký hiệu có thể tạo ra nhiều lựa chọn. Dấu sao có thể nuốt không, một, hai ký tự, hoặc nhiều hơn.")],
       "ex2"),

    sc("07-example3", "02 · VÍ DỤ CHÍNH THỨC", "Ví dụ 3",
       ['s = "cb"', 'p = "?a"', "Output: false"],
       [b('Ví dụ 3: chuỗi s là "cb", mẫu p là "?a".', "Ví dụ ba: chuỗi s là c b, mẫu p là dấu hỏi chấm rồi chữ a."),
        b("Dấu ? khớp đúng một ký tự, ở đây là chữ c.", "Dấu hỏi chấm khớp đúng một ký tự, ở đây là chữ c."),
        b("Tiếp theo mẫu cần chữ a, nhưng chuỗi lại là chữ b. Hai chữ khác nhau, nên kết quả là sai (false).",
          "Tiếp theo mẫu cần chữ a, nhưng chuỗi lại là chữ b. Hai chữ khác nhau, nên kết quả là sai."),
        b("Bài học 3: nếu không có dấu sao, mọi thứ bị xếp thẳng hàng, và lệch một vị trí là hỏng cả bài.",
          "Bài học ba: nếu không có dấu sao, mọi thứ bị xếp thẳng hàng, và lệch một vị trí là hỏng cả bài.")],
       "ex3"),

    sc("08-recap", "02 · VÍ DỤ CHÍNH THỨC", "Ba ví dụ, ba thói quen",
       ["Kiểm tra điều kiện kết thúc", "Tìm nơi phát sinh lựa chọn", "Biết khi nào mọi thứ bị ép thẳng hàng"],
       [b("Ba ví dụ cho ta ba thói quen: kiểm tra điều kiện kết thúc, tìm nơi phát sinh lựa chọn, và nhận ra khi mọi thứ bị ép thẳng hàng."),
        b("Ta chưa viết dòng code nào, nhưng đã biết chỗ khó của bài nằm ở dấu sao.")],
       "recap"),

    sc("09-hints", "03 · TỰ GIẢI", "Ba gợi ý trước khi xem lời giải",
       ["GỢI Ý 1 · Nhiều lựa chọn chỉ xuất hiện ở một ký hiệu. Là ký hiệu nào?",
        "GỢI Ý 2 · Thu nhỏ bài toán: i ký tự đầu của s có khớp j ký tự đầu của p không?",
        "GỢI Ý 3 · Khi gặp lệch, cần quay lại mọi dấu sao đã qua, hay chỉ một vài?"],
       [b("Trước khi xem lời giải, hãy thử tự nghĩ. Đây là ba gợi ý."),
        b("Gợi ý 1: chỗ duy nhất có nhiều lựa chọn là dấu sao. Hãy tự hỏi dấu sao nên nuốt bao nhiêu ký tự.",
          "Gợi ý một: chỗ duy nhất có nhiều lựa chọn là dấu sao. Hãy tự hỏi dấu sao nên nuốt bao nhiêu ký tự."),
        b("Gợi ý 2: hãy thu nhỏ bài toán. Với i ký tự đầu của chuỗi và j ký tự đầu của mẫu, hai phần đó có khớp nhau không?",
          "Gợi ý hai: hãy thu nhỏ bài toán. Với i ký tự đầu của chuỗi và j ký tự đầu của mẫu, hai phần đó có khớp nhau không?"),
        b("Gợi ý 3: khi đã có một cách chạy được, hãy hỏi: gặp lệch thì ta cần quay lại mọi dấu sao đã qua, hay chỉ một vài dấu?",
          "Gợi ý ba: khi đã có một cách chạy được, hãy hỏi: gặp lệch thì ta cần quay lại mọi dấu sao đã qua, hay chỉ một vài dấu?"),
        b("Hãy tự nghĩ trong mười giây tới: nếu gặp dấu sao, bạn sẽ thử lựa chọn nào trước?")],
       "hints"),

    sc("10-think", "03 · TỰ GIẢI", "10 giây · Đến lượt bạn",
       ["Nếu gặp dấu *, bạn sẽ thử lựa chọn nào trước?", 's = "adceb"   p = "*a*b"'],
       [], "think", silent=True, secs=10.0),

    sc("11-rules", "04 · XÂY DỰNG TƯ DUY", "Bắt đầu từ ý tưởng đơn giản nhất",
       ["Chữ cái hoặc ? → so một ký tự, cả hai tiến", "* → nhảy qua, hoặc nuốt thêm một ký tự", "Hết mẫu → chuỗi cũng phải hết"],
       [b("Hết mười giây. Dù bạn đã có đáp án hay chưa, ta hãy bắt đầu từ ý tưởng đơn giản nhất."),
        b("Đặt con trỏ i trên chuỗi s và con trỏ j trên mẫu p. Câu hỏi nhỏ là: từ vị trí i và j, phần còn lại có khớp không?", cue=0),
        b("Nếu p[j] là chữ cái hoặc dấu ?, ta so một ký tự rồi cho cả hai con trỏ tiến lên một bước.",
          "Nếu p j là chữ cái hoặc dấu hỏi chấm, ta so một ký tự rồi cho cả hai con trỏ tiến lên một bước.", cue=1),
        b("Nếu p[j] là dấu *, ta có hai lựa chọn. Một là nhảy qua dấu sao, tức là cho nó nuốt rỗng.",
          "Nếu p j là dấu sao, ta có hai lựa chọn. Một là nhảy qua dấu sao, tức là cho nó nuốt rỗng.", cue=2),
        b("Hai là cho dấu sao nuốt thêm một ký tự, và giữ nguyên dấu sao để còn nuốt tiếp.", cue=2),
        b("Hết mẫu thì chuỗi cũng phải hết. Đó chính là điều kiện kết thúc của bài học đầu tiên.", cue=3)],
       "rules"),

    sc("12-tree", "04 · XÂY DỰNG TƯ DUY", "Thử mọi lựa chọn: cây quyết định",
       ['s = "aaa"   p = "*a*b"   → false', "Nhánh trái: nhảy qua *   ·   Nhánh phải: nuốt thêm một ký tự"],
       [b('Hãy chạy ý tưởng đó trên ví dụ nhỏ: s là "aaa", p là "*a*b". Đáp án là sai, nên ta phải thử hết mọi nhánh.',
          "Hãy chạy ý tưởng đó trên ví dụ nhỏ: chuỗi là ba chữ a, mẫu là dấu sao, a, dấu sao, b. Đáp án là sai, nên ta phải thử hết mọi nhánh."),
        b("Mỗi nút là một cặp vị trí (i, j). Nhánh bên trái là nhảy qua dấu sao. Nhánh bên phải là nuốt thêm một ký tự.",
          "Mỗi nút là một cặp vị trí i, j. Nhánh bên trái là nhảy qua dấu sao. Nhánh bên phải là nuốt thêm một ký tự."),
        b("Nhánh nào thất bại thì ta quay lại và thử nhánh khác. Đó là quay lui."),
        b("Nhìn kỹ: có những cặp (i, j) xuất hiện nhiều lần, được tô vàng. Ta đang giải đi giải lại cùng một câu hỏi.",
          "Nhìn kỹ: có những cặp i, j xuất hiện nhiều lần, được tô vàng. Ta đang giải đi giải lại cùng một câu hỏi."),
        b("Cây có 20 lần gọi hàm, nhưng chỉ 14 câu hỏi khác nhau.", f"Cây có {vi_int(20)} lần gọi hàm, nhưng chỉ {vi_int(14)} câu hỏi khác nhau.")],
       "tree"),

    sc("13-blowup", "04 · XÂY DỰNG TƯ DUY", "Vì sao cách này không đủ nhanh?",
       ["s = 'a' × 20   p = '*a' × k + 'b'", f"k = 1 → {vn_group(BLOW_FIRST)} lần gọi", f"k = 6 → {vn_group(BLOW_LAST)} lần gọi (đã đo)"],
       [b("Số lần gọi hàm tăng rất nhanh khi mẫu có thêm dấu sao."),
        b(f"Chúng tôi đã chạy thật. Với chuỗi 20 chữ a, mẫu có một dấu sao cần {vn_group(BLOW_FIRST)} lần gọi; sáu dấu sao cần {vn_group(BLOW_LAST)} lần.",
          f"Chúng tôi đã chạy thật. Với chuỗi hai mươi chữ a, mẫu có một dấu sao cần {vi_int(BLOW_FIRST)} lần gọi; sáu dấu sao cần {vi_int(BLOW_LAST)} lần."),
        b("Với độ dài tới 2000, thử hết mọi nhánh là không thể. Ta cần cách tốt hơn.",
          "Với độ dài tới hai nghìn, thử hết mọi nhánh là không thể. Ta cần cách tốt hơn.")],
       "blowup"),

    sc("14-greedy-fail", "04 · XÂY DỰNG TƯ DUY", "Ý tưởng tham lam: có đúng không?",
       ['s = "adceb"   p = "*a*b"', "Dấu * chỉ nuốt rỗng, không bao giờ quay lại", "Kết quả: false   ·   Đáp án đúng: true"],
       [b("Thử một ý tưởng nhanh hơn: gặp dấu sao thì cho nó nuốt rỗng, và không bao giờ quay lại."),
        b('Chạy trên s là "adceb", p là "*a*b". Dấu sao đầu nuốt rỗng, chữ a khớp chữ a, dấu sao thứ hai cũng nuốt rỗng.',
          "Chạy trên chuỗi a d c e b, mẫu là dấu sao, a, dấu sao, b. Dấu sao đầu nuốt rỗng, chữ a khớp chữ a, dấu sao thứ hai cũng nuốt rỗng."),
        b("Bây giờ chữ b của mẫu gặp chữ d của chuỗi: lệch. Ý tưởng này kết luận sai."),
        b("Nhưng đáp án đúng là đúng, vì dấu sao thứ hai có thể nuốt d, c, e rồi chữ b mới khớp.",
          "Nhưng đáp án đúng là đúng, vì dấu sao thứ hai có thể nuốt d, c, e rồi chữ b mới khớp."),
        b("Bài học: một giả thuyết hay vẫn có thể sai. Ta cần phản ví dụ để biết, và dấu sao phải được cho cơ hội nuốt thêm.")],
       "greedy_fail"),

    sc("15-dp", "05 · GHI NHỚ", "Ghi nhớ kết quả: bảng quy hoạch động",
       ["dp[i][j] = s[:i] khớp p[:j]", "Chữ cái / ?  →  dp[i-1][j-1] và ký tự khớp", "*  →  dp[i-1][j] hoặc dp[i][j-1]"],
       [b("Cách an toàn: đừng giải lại câu hỏi cũ. Hãy lưu kết quả vào một bảng."),
        b("Ô dp[i][j] trả lời: i ký tự đầu của chuỗi có khớp j ký tự đầu của mẫu hay không?",
          "Ô dp i j trả lời: i ký tự đầu của chuỗi có khớp j ký tự đầu của mẫu hay không?"),
        b("Chuỗi rỗng khớp mẫu rỗng. Và chuỗi rỗng chỉ khớp một mẫu toàn dấu sao."),
        b("Nếu ký tự mẫu là chữ cái hoặc dấu ?, ô này đúng khi hai ký tự khớp và ô chéo phía trên bên trái đúng.",
          "Nếu ký tự mẫu là chữ cái hoặc dấu hỏi chấm, ô này đúng khi hai ký tự khớp và ô chéo phía trên bên trái đúng."),
        b("Nếu ký tự mẫu là dấu *, ô này đúng khi ô phía trên đúng, tức là dấu sao nuốt thêm một ký tự, hoặc ô bên trái đúng, tức là nuốt rỗng.",
          "Nếu ký tự mẫu là dấu sao, ô này đúng khi ô phía trên đúng, tức là dấu sao nuốt thêm một ký tự, hoặc ô bên trái đúng, tức là nuốt rỗng."),
        b('Điền bảng cho s là "adceb" và p là "*a*b", từng hàng một.',
          "Điền bảng cho chuỗi a d c e b và mẫu dấu sao, a, dấu sao, b, từng hàng một."),
        b("Ô cuối cùng là đúng, vậy đáp án là đúng."),
        b(f"Với giới hạn của đề, bảng có hơn 4 triệu ô, mỗi ô tính một lần: thời gian O(m × n), bộ nhớ cũng O(m × n).",
          "Với giới hạn của đề, bảng có hơn bốn triệu ô, mỗi ô tính một lần: thời gian O của m nhân n, bộ nhớ cũng O của m nhân n.")],
       "dp"),

    sc("16-insight", "06 · TỐI ƯU HÓA", "Có thể nhớ ít hơn không?",
       ["Dấu * gần nhất là lựa chọn linh hoạt nhất", "Đoạn giữa hai dấu *: khớp sớm nhất có thể", "Khi lệch: chỉ quay về dấu * gần nhất"],
       [b("Nhìn lại bảng: mỗi ô chỉ cần hàng phía trên và ô bên cạnh. Ta đang nhớ nhiều hơn mức cần thiết."),
        b("Hãy nghĩ về dấu sao. Nó nuốt được bất cứ thứ gì. Vì vậy, khi một đoạn phía sau dấu sao đã khớp, mọi thứ phía trước coi như ổn."),
        b("Đoạn nằm giữa hai dấu sao nên khớp ở vị trí sớm nhất có thể, để chừa lại nhiều ký tự nhất cho phần phía sau."),
        b("Vì thế, khi gặp lệch, ta chỉ cần quay về dấu sao gần nhất. Các dấu sao cũ hơn không cần thử lại.")],
       "insight"),

    sc("17-greedy", "06 · TỐI ƯU HÓA", "Thuật toán hai con trỏ",
       ["i · j · star · mark", "Khớp hoặc ? → i, j cùng tiến", "* → ghi nhớ rồi nuốt rỗng", "Lệch + có * → nuốt thêm một ký tự", "Lệch + chưa có * → false"],
       [b("Ta giữ bốn biến: i trên chuỗi, j trên mẫu, star là vị trí dấu sao gần nhất, và mark là vị trí chuỗi mà dấu sao đã nuốt tới.", cue=0),
        b("Nếu hai ký tự khớp hoặc mẫu là dấu ?, cho i và j cùng tiến.", "Nếu hai ký tự khớp hoặc mẫu là dấu hỏi chấm, cho i và j cùng tiến.", cue=1),
        b("Nếu mẫu là dấu *: ghi nhớ star và mark, rồi chỉ tiến j, tức là cho dấu sao nuốt rỗng trước.",
          "Nếu mẫu là dấu sao: ghi nhớ star và mark, rồi chỉ tiến j, tức là cho dấu sao nuốt rỗng trước.", cue=2),
        b("Nếu lệch mà đã có dấu sao: cho nó nuốt thêm một ký tự. Tăng mark, đặt i bằng mark, và đặt j về ngay sau dấu sao.", cue=3),
        b("Nếu lệch mà chưa có dấu sao nào: không còn cách cứu, kết quả là sai.", cue=4),
        b("Hết chuỗi thì bỏ qua các dấu sao còn lại ở cuối mẫu. Mẫu phải đi hết thì kết quả mới đúng.", cue=5)],
       "greedy"),

    sc("18-trace", "06 · TỐI ƯU HÓA", "Chạy thử: adceb với *a*b",
       ['s = "adceb"   p = "*a*b"', "Mỗi bước là một sự kiện thật từ lần chạy của solution.py"],
       [b("Bắt đầu: j gặp dấu sao đầu tiên. Ghi nhớ star bằng 0, cho nó nuốt rỗng, j tiến lên.",
          "Bắt đầu: j gặp dấu sao đầu tiên. Ghi nhớ star bằng không, cho nó nuốt rỗng, j tiến lên.", cue=0),
        b("Chữ a của mẫu khớp chữ a của chuỗi. Cả i và j cùng tiến.", cue=1),
        b("Dấu sao thứ hai: ghi nhớ star bằng 2, mark bằng 1, và lại cho nó nuốt rỗng.",
          "Dấu sao thứ hai: ghi nhớ star bằng hai, mark bằng một, và lại cho nó nuốt rỗng.", cue=2),
        b("Chữ b của mẫu gặp chữ d: lệch. Dấu sao thứ hai nuốt thêm chữ d, và j quay về chữ b.", cue=3),
        b("Lại lệch với chữ c, dấu sao nuốt thêm chữ c. Rồi lệch với chữ e, dấu sao nuốt thêm chữ e.", cue=4),
        b("Lần này chữ b khớp chữ b. Chuỗi đã hết, mẫu cũng đã đi hết: kết quả là đúng.", cue=6)],
       "trace"),

    sc("19-pseudocode", "06 · TỐI ƯU HÓA", "Từ ý tưởng sang giả mã",
       ["Lặp khi chuỗi còn ký tự:", "    khớp / ? → tiến i, j", "    * → nhớ vị trí, tiến j", "    lệch + có * → nuốt thêm, quay j", "    lệch + chưa có * → trả về false",
        "Bỏ các * dư ở cuối mẫu", "Trả về: j đã tới cuối mẫu"],
       [b("Trước khi viết Python, hãy viết logic bằng lời."),
        b("Lặp trong khi chuỗi còn ký tự: khớp thì tiến, gặp dấu sao thì ghi nhớ, lệch thì quay về dấu sao, không có dấu sao thì trả về sai."),
        b("Sau vòng lặp, bỏ qua các dấu sao thừa ở cuối mẫu, rồi kiểm tra j đã tới cuối mẫu chưa.")],
       "pseudocode"),

    sc("20-code1", "07 · PYTHON 3", "Python 3: cấu trúc lời giải",
       ["scripts/solution.py"],
       [b("Đây là lời giải Python 3 hoàn chỉnh, chỉ khoảng 20 dòng.", "Đây là lời giải Python ba hoàn chỉnh, chỉ khoảng hai mươi dòng.", cue=[0, 21]),
        b("Khởi tạo: i và j bằng 0, star bằng -1 nghĩa là chưa có dấu sao, mark bằng 0.",
          "Khởi tạo: i và j bằng không, star bằng trừ một nghĩa là chưa có dấu sao, mark bằng không.", cue=[2, 4]),
        b("Vòng lặp chính chạy khi i còn nhỏ hơn độ dài của chuỗi.", cue=[5, 5]),
        b("Nhánh một: nếu còn mẫu và ký tự khớp, hoặc là dấu ?, thì tăng i và j.",
          "Nhánh một: nếu còn mẫu và ký tự khớp, hoặc là dấu hỏi chấm, thì tăng i và j.", cue=[6, 8]),
        b("Nhánh hai: gặp dấu sao thì lưu star và mark, rồi tăng j.", cue=[9, 12]),
        b("Nhánh ba: đã có dấu sao thì tăng mark, đặt lại i và j. Nhánh cuối: chưa có dấu sao thì trả về sai.", cue=[13, 18]),
        b("Sau vòng lặp, bỏ các dấu sao ở cuối mẫu. Kết quả đúng khi j đã đến cuối mẫu.", cue=[19, 21])],
       "code1"),

    sc("21-code2", "07 · PYTHON 3", "Chạy code từng dòng",
       ["s = \"adceb\"  p = \"*a*b\"", "Highlight và giá trị biến lấy từ lần chạy thật (sys.settrace)"],
       [b("Hãy xem code chạy với s là \"adceb\" và p là \"*a*b\". Bên phải là giá trị các biến ở mỗi dòng.",
          "Hãy xem code chạy với chuỗi a d c e b và mẫu dấu sao, a, dấu sao, b. Bên phải là giá trị các biến ở mỗi dòng.", cue=0),
        b("Dòng star gán bằng j: dấu sao đầu tiên được ghi nhớ.", cue=_EVENTS[0]["step"]),
        b("Chữ a khớp: i và j cùng tăng.", cue=_EVENTS[1]["step"]),
        b("Dấu sao thứ hai được ghi nhớ: star bằng 2.", "Dấu sao thứ hai được ghi nhớ: star bằng hai.", cue=_EVENTS[2]["step"]),
        b("Chữ b lệch với chữ d, nên chương trình vào nhánh thứ ba: mark tăng, i bằng mark, j bằng star cộng một.", cue=_EVENTS[3]["step"]),
        b("Hai lần lệch nữa, với chữ c và chữ e: dấu sao nuốt thêm hai chữ.", cue=_EVENTS[4]["step"]),
        b("Cuối cùng chữ b khớp chữ b. i bằng 5, vòng lặp kết thúc.", "Cuối cùng chữ b khớp chữ b. i bằng năm, vòng lặp kết thúc.", cue=_EVENTS[6]["step"]),
        b("Dòng cuối: j bằng 4, đúng bằng độ dài mẫu. Hàm trả về true.", "Dòng cuối: j bằng bốn, đúng bằng độ dài mẫu. Hàm trả về true.", cue=_RET_STEP - 1)],
       "code2"),

    sc("22-verify", "08 · KIỂM CHỨNG", "Kiểm chứng bằng thử nghiệm",
       ["3/3 ví dụ chính thức đúng", f"{vn_group(EX_CASES)} ca vét cạn · 0 sai lệch", f"{vn_group(RAND_CASES)} ca ngẫu nhiên · 0 sai lệch",
        f"Trường hợp xấu nhất: {vn_group(WORST_ITERS)} vòng lặp"],
       [b("Ta không chỉ tin vào lập luận. Ba ví dụ chính thức cho kết quả đúng như đề."),
        b(f"Chúng tôi so sánh lời giải với hai cách độc lập là biểu thức chính quy và bảng quy hoạch động, trên {vn_group(EX_CASES)} ca vét cạn.",
          f"Chúng tôi so sánh lời giải với hai cách độc lập là biểu thức chính quy và bảng quy hoạch động, trên {vi_int(EX_CASES)} ca vét cạn."),
        b(f"Cộng thêm {vn_group(RAND_CASES)} ca ngẫu nhiên. Không có một sai lệch nào.",
          f"Cộng thêm {vi_int(RAND_CASES)} ca ngẫu nhiên. Không có một sai lệch nào."),
        b(f"Trường hợp xấu nhất, chuỗi 2000 chữ a, vòng lặp chính chạy {vn_group(WORST_ITERS)} lần.",
          f"Trường hợp xấu nhất, chuỗi hai nghìn chữ a, vòng lặp chính chạy {vi_int(WORST_ITERS)} lần."),
        b("Thử nghiệm là bằng chứng mạnh, nhưng chưa phải chứng minh toán học.")],
       "verify"),

    sc("23-complexity", "08 · KIỂM CHỨNG", "So sánh các cách làm",
       ["Thử hết mọi nhánh · hàm mũ · không dùng được", "Bảng quy hoạch động · O(m × n) · bộ nhớ O(m × n)",
        "Hai con trỏ · O(m × n) tệ nhất · bộ nhớ O(1)"],
       [b("Hãy so sánh ba cách làm."),
        b(f"Thử hết mọi nhánh: số lần gọi tăng rất nhanh theo số dấu sao. Đã đo: hơn {vn_group(BLOW_LAST // 1000 * 1000)} lần gọi chỉ với chuỗi 20 ký tự.",
          f"Thử hết mọi nhánh: số lần gọi tăng rất nhanh theo số dấu sao. Đã đo: hơn {vi_int(BLOW_LAST // 1000 * 1000)} lần gọi chỉ với chuỗi hai mươi ký tự."),
        b("Bảng quy hoạch động: thời gian O(m × n), bộ nhớ O(m × n). Với giới hạn của đề, đó là hơn 4 triệu ô, vẫn chạy được.",
          "Bảng quy hoạch động: thời gian O của m nhân n, bộ nhớ O của m nhân n. Với giới hạn của đề, đó là hơn bốn triệu ô, vẫn chạy được."),
        b("Hai con trỏ: bộ nhớ O(1). Trường hợp xấu nhất vẫn là O(m × n).",
          "Hai con trỏ: bộ nhớ O của một. Trường hợp xấu nhất vẫn là O của m nhân n."),
        b(f"Trên dữ liệu ngẫu nhiên, chúng tôi đo trung bình {_ratio_text(TYPICAL_RATIO)} vòng lặp cho mỗi ký tự của chuỗi và mẫu.",
          f"Trên dữ liệu ngẫu nhiên, chúng tôi đo trung bình {vi_decimal(_ratio_text(TYPICAL_RATIO))} vòng lặp cho mỗi ký tự của chuỗi và mẫu."),
        b("Không có cách nào luôn tốt nhất. Hãy chọn theo giới hạn, bộ nhớ, và độ dễ chứng minh.")],
       "complexity"),

    sc("24-lessons", "09 · TỔNG KẾT", "Bài học giải quyết vấn đề",
       ["1 · Đọc kỹ yêu cầu và điều kiện kết thúc", "2 · Tìm nơi sinh ra lựa chọn", "3 · Bắt đầu đơn giản, rồi đo vì sao nó chậm",
        "4 · Câu hỏi lặp lại → ghi nhớ", "5 · Tìm cấu trúc để nhớ ít hơn", "6 · Kiểm chứng bằng ví dụ và phản ví dụ"],
       [b("Một: đọc kỹ yêu cầu, đặc biệt là điều kiện kết thúc."),
        b("Hai: tìm nơi sinh ra lựa chọn. Ở bài này, đó là dấu sao."),
        b("Ba: bắt đầu bằng cách đơn giản và đúng, rồi đo xem vì sao nó chậm."),
        b("Bốn: nếu cùng một câu hỏi lặp lại, hãy ghi nhớ kết quả."),
        b("Năm: tìm cấu trúc để nhớ ít hơn, như chỉ giữ dấu sao gần nhất."),
        b("Sáu: luôn kiểm chứng bằng ví dụ, phản ví dụ, và một cách làm độc lập."),
        b("Những thói quen này dùng được ngoài LeetCode: khi lập kế hoạch, sửa lỗi, hay thiết kế một hệ thống.")],
       "lessons"),

    sc("25-practice", "09 · TỔNG KẾT", "Ba bài luyện tập liên quan",
       ["#392 · Is Subsequence · Easy", "#72 · Edit Distance · Medium", "#10 · Regular Expression Matching · Hard"],
       [b("Ba bài để luyện tiếp, từ dễ đến khó."),
        b("Bài #392, Is Subsequence, mức Easy: dùng hai con trỏ trên hai chuỗi, một bước khởi động cho tư duy tham lam.",
          "Bài ba trăm chín mươi hai, Is Subsequence, mức Easy: dùng hai con trỏ trên hai chuỗi, một bước khởi động cho tư duy tham lam."),
        b("Bài #72, Edit Distance, mức Medium: hãy tự định nghĩa ô của bảng và ba lựa chọn ở mỗi ô.",
          "Bài bảy mươi hai, Edit Distance, mức Medium: hãy tự định nghĩa ô của bảng và ba lựa chọn ở mỗi ô."),
        b("Bài #10, Regular Expression Matching, mức Hard: dấu sao ở đó có nghĩa khác. Hãy so sánh với bài hôm nay.",
          "Bài mười, Regular Expression Matching, mức Hard: dấu sao ở đó có nghĩa khác. Hãy so sánh với bài hôm nay."),
        b("Đừng xem code ngay. Hãy tự hỏi: câu hỏi nhỏ là gì, lựa chọn nằm ở đâu, và có cần ghi nhớ không?")],
       "practice"),

    sc("26-outro", "THE ART OF CODING", "Hãy nhớ cách nghĩ, đừng chỉ nhớ code.",
       ["Hiểu → Giả thuyết → Kiểm chứng → Rút kinh nghiệm", "KIEU STUDIO · kieu.app"],
       [b("Hãy nhớ cách nghĩ, đừng chỉ nhớ code."),
        b("Cảm ơn bạn đã xem. Hẹn gặp lại ở tập tiếp theo của Kieu Studio, The Art of Coding. Thêm tài liệu tại kieu.app.",
          "Cảm ơn bạn đã xem. Hẹn gặp lại ở tập tiếp theo của Kiều Studio, The Art of Coding. Thêm tài liệu tại kiều chấm app.")],
       "outro"),
]

PAUSE_ID = "10-think"
PRACTICE = [{"n": 392, "title": "Is Subsequence", "difficulty": "Easy", "url": "https://leetcode.com/problems/is-subsequence/"},
            {"n": 72, "title": "Edit Distance", "difficulty": "Medium", "url": "https://leetcode.com/problems/edit-distance/"},
            {"n": 10, "title": "Regular Expression Matching", "difficulty": "Hard",
             "url": "https://leetcode.com/problems/regular-expression-matching/"}]


# KIEU_LANG=en swaps in the English edition (same ids, modes, cues and verified numbers).
import os as _os
LANG = _os.environ.get("KIEU_LANG", "vi")
if LANG not in ("vi", "en"):
    raise RuntimeError(f"KIEU_LANG must be vi or en, not {LANG!r}")
if LANG == "en":
    from episode_en import S  # noqa: E402,F811


def all_beats():
    for scene in S:
        for k, beat in enumerate(scene.beats):
            yield scene, k, beat
