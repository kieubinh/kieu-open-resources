"""Kieu Studio GitHub Radar — ONE repo per video (GR01..GR03), snapshot 2026-10-29.

Each video is a short story: a relatable scene → the numbers → the pain → the idea → how it works → how to use
it → what it costs → what to build → a verdict that closes the opening question. On screen there is almost no
prose: scenes carry illustration keys (`art`), icons and short chips; the narration carries the story.

Every number comes from docs/SOURCE_MANIFEST.json (GitHub REST API totals + github.com/trending windows).
Narration spells numbers out in words so local TTS reads them correctly; digits appear only on screen.
"""
import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Scene:
    id: str
    phase: str
    title: str
    lines: tuple
    script: str
    min_seconds: float
    mode: str = 'cards'
    silent: bool = False
    repo: str = ''
    beat: str = ''
    data: dict = field(default_factory=dict)


def sc(id, phase, title, lines, script, secs=40, mode='cards', repo='', beat='', data=None, silent=False):
    return Scene(id, phase, title, tuple(lines), script.strip(), float(secs), mode, silent, repo, beat, data or {})


R1, R2, R3 = 'cloudflare/security-audit-skill', 'pbakaus/impeccable', 'thedotmack/claude-mem'
NOTE = 'Tổng sao: GitHub API · mức tăng: GitHub Trending (hai cửa sổ 7 và 30 ngày) · chụp 29/10/2026'

# ═══════════════════════ GR01 · cloudflare/security-audit-skill ═══════════════════════
GR01 = [
sc('r1-intro', 'GITHUB RADAR · TẬP 1', 'Một AI agent báo 20 lỗ hổng. Bao nhiêu cái là thật?', [],
   '''Hãy tưởng tượng bạn nhờ một AI agent: tìm giúp tôi lỗ hổng bảo mật trong dự án này. Vài phút sau, nó trả về hai mươi phát hiện, cái nào cũng trông rất thuyết phục. Câu hỏi là: bao nhiêu cái trong số đó là thật? Chào mừng bạn đến với Kieu Studio, GitHub Radar, nơi mỗi video chúng tôi chỉ soi một repository. Hôm nay radar bắt được security-audit-skill của Cloudflare, tạo ngày mười tám tháng sáu năm hai nghìn không trăm hai mươi sáu, giấy phép MIT. Và nó có một con số tăng trưởng khiến chúng tôi phải dừng lại. Hãy xem.''',
   30, 'intro', repo=R1, beat='intro',
   data={'repo': R1, 'q': 'Bao nhiêu phát hiện của AI là thật?', 'color': 'teal', 'art': 'shield',
         'chips': [['users', 'Chủ sở hữu', 'Cloudflare'], ['doc', 'Giấy phép', 'MIT'], ['calendar', 'Tạo từ', '18/06/2026'], ['branch', 'Fork', '3.365']]}),
sc('r1-growth', 'CON SỐ TĂNG TRƯỞNG', 'Đang tăng tốc, không phải nguội dần', [NOTE],
   '''Đây là con số. Ba mươi ngày trước, repo có khoảng hai mươi ba nghìn chín trăm mười ba sao. Hôm nay là năm mươi hai nghìn năm trăm ba mươi: hơn gấp đôi trong một tháng. Nhưng điều thú vị nằm ở hình dạng của đường tăng. Ghép hai cửa sổ của trang Trending lại, hai mươi ba ngày đầu tăng khoảng năm trăm bốn mươi tám sao mỗi ngày. Còn bảy ngày gần nhất? Khoảng hai nghìn hai trăm tám mươi sáu sao mỗi ngày, nghĩa là chưa đến bốn mươi giây lại có thêm một người bấm sao. Một repo đang tăng tốc chứ không nguội dần. Nhưng sao chỉ đo sự chú ý. Câu hỏi thật là: vì sao Cloudflare làm ra nó?''',
   40, 'growth1', repo=R1, beat='growth',
   data={'total': 52530, 'month': 28617, 'week': 16002, 'today': None, 'color': 'teal', 'factor': 'gấp 2,2 lần',
         'pts': [['30 ngày trước', 23913], ['7 ngày trước', 36528], ['Hôm nay', 52530]],
         'segs': [548, 2286], 'avg': 954, 'tick': '≈ 38 giây / sao', 'tick_basis': 'theo tốc độ 7 ngày gần nhất'}),
sc('r1-why', 'VÌ SAO TÁC GIẢ LÀM RA NÓ', 'Agent đọc đến đâu thì ngữ cảnh đầy đến đó', [],
   '''Câu chuyện bắt đầu từ một giới hạn rất đời thường. Một phiên agent chỉ theo dõi được một giả thuyết tại một thời điểm. Nó đọc, đọc, rồi ngữ cảnh đầy, trong khi mới xem được một phần nhỏ của một repo thật. Chạy lâu thì có thể lỗi, hoặc chạm giới hạn tốc độ, và hàng giờ công sức biến mất. Cloudflare còn muốn quét liên tục nhiều repo mà không bị buộc vào một model duy nhất. Họ bắt đầu từ một skill chỉ khoảng bốn trăm năm mươi dòng, chạy trên một repo. Vậy làm sao biến một agent hay quên thành một đội kiểm tra có kỷ luật?''',
   36, 'story', repo=R1, beat='why', data={'art': 'ctx', 'color': 'teal'}),
sc('r1-problem', 'BÀI TOÁN CỤ THỂ', 'Tự chấm bài thi của chính mình', [],
   '''Vấn đề không chỉ là tìm lỗi, mà là tin được kết quả. Một agent vừa tìm vừa tự chấm điểm giống như học sinh tự chấm bài thi của mình. Skill này đảo ngược cách làm: người tìm và người kiểm là hai agent khác nhau, và agent kiểm tra chỉ có một việc là bác bỏ phát hiện. Kết quả chỉ có ba loại: confirmed, needs_validation và rejected. Thiếu bằng chứng thì không được gọi là lỗ hổng. Thiếu một lớp phòng thủ thứ hai chỉ là gợi ý gia cố. Nghe hợp lý rồi, nhưng cụ thể nó chạy thế nào?''',
   38, 'story', repo=R1, beat='problem', data={'art': 'split', 'color': 'teal'}),
sc('r1-how', 'CÁCH HOẠT ĐỘNG', 'Sáu giai đoạn, mỗi giai đoạn một nhiệm vụ', ['Báo cáo cuối được sinh từ các bản ghi đã xác minh, không viết tay.'],
   '''Bên trong là sáu giai đoạn. Trinh sát: vẽ kiến trúc và ranh giới tin cậy, ghi vào một sổ coverage. Săn lỗi: các hunter tách biệt nhận từng phần của sổ. Kiểm chứng: mỗi ứng viên đến tay một agent mới, nhiệm vụ là bác bỏ nó. Rồi findings được ghi thành dữ liệu và kiểm bằng schema. Giai đoạn năm, agent độc lập đối chiếu lại mã nguồn. Cuối cùng, báo cáo được sinh từ chính các bản ghi đã xác minh, không viết tay. Và hai validator viết bằng JavaScript, không cần cài thêm thư viện.''',
   38, 'flow', repo=R1, beat='how',
   data={'color': 'teal', 'steps': [
       ['map', 'Trinh sát', 'kiến trúc · ranh giới'], ['search', 'Săn lỗi', 'hunter tách biệt'], ['shield', 'Kiểm chứng', 'cố bác bỏ'],
       ['doc', 'Dữ liệu', 'findings + schema'], ['eye', 'Xác minh lại', 'agent độc lập'], ['check', 'Báo cáo', 'từ bản ghi đã duyệt']]}),
sc('r1-usage', 'CÁCH SỬ DỤNG', 'Hai bước, và một điều kiện không được bỏ qua', ['Cần: agent có tool use và sub-agent song song · Node.js · sandbox do hệ điều hành thực thi.'],
   '''Dùng thế nào? Chỉ cần hai bước. Cài skill bằng Skills CLI. Rồi mở agent trong thư mục mã nguồn và nói: security audit this codebase. Mặc định kết quả nằm trong thư mục home, mục security-audit-skill, theo tên repo và số lần chạy. Nhưng có một điều kiện bạn không được bỏ qua: bước nào phải build hoặc chạy mã thì cần sandbox do hệ điều hành thực thi, không có mạng ngoài. Không có sandbox, skill giữ phát hiện ở trạng thái cần xác thực, thay vì chạy mã lạ trên máy bạn.''',
   40, 'usage', repo=R1, beat='usage',
   data={'art': 'ledger', 'color': 'teal',
         'cmds': ['npx skills add https://github.com/cloudflare/security-audit-skill \\', '  --skill security-audit', '', '# trong agent, tại thư mục mã nguồn', '> security audit this codebase'],
         'note': 'Không có sandbox → giữ ở needs_validation, không chạy mã mục tiêu.'}),
sc('r1-value', 'VÌ SAO HỮU ÍCH', 'Cái được và cái giá', ['Cần cân nhắc: tốn token, cần sandbox, chỉ quét mã bạn được phép kiểm tra.'],
   '''Vì sao nhiều người quan tâm? Thứ nhất, kết quả là dữ liệu có schema, không phải một đoạn văn dài, nên đưa được vào quy trình theo dõi lỗi. Thứ hai, chạy nhiều lần thì cộng dồn: tác giả cho biết một lần chạy chỉ tìm được khoảng một nửa số lỗ hổng mà các lần lặp tìm thấy. Thứ ba, bạn nhìn thấy phần nào đã được xem, phần nào chưa. Nhưng hãy cân nhắc cái giá: nhiều agent nghĩa là tốn token, cần sandbox, và chỉ quét mã bạn được phép kiểm tra.''',
   38, 'value', repo=R1, beat='value',
   data={'color': 'teal', 'pros': [['doc', 'Dữ liệu có schema'], ['repeat', 'Chạy lại cộng dồn'], ['eye', 'Thấy phần đã xem']],
         'cons': [['clock', 'Tốn token'], ['lock', 'Cần sandbox']], 'caveat_from': 0}),
sc('r1-ideas', 'Ý TƯỞNG ỨNG DỤNG', 'Bốn việc bạn có thể làm ngay', [],
   '''Bạn có thể dùng nó vào bốn việc. Một, chạy trước mỗi lần phát hành, rồi đọc mục needs_validation để biết còn thiếu bằng chứng ở đâu. Hai, kiểm tra một thư viện lạ, trong sandbox, trước khi đưa vào dự án. Ba, biến nó thành bài tập: một nhóm đóng vai săn lỗi, nhóm kia đóng vai phản biện, đúng như hai agent tách biệt. Bốn, đọc các tệp attack class như danh sách câu hỏi khi tự review mã. Chọn một việc, bắt đầu nhỏ thôi.''',
   34, 'ideas', repo=R1, beat='ideas',
   data={'color': 'teal', 'ideas': [['rocket', 'Trước khi phát hành', 'đọc needs_validation'], ['box', 'Thư viện lạ', 'thử trong sandbox'],
                                    ['users', 'Bài tập hai đội', 'săn lỗi đấu phản biện'], ['book', 'Checklist review', 'dùng attack class']]}),
sc('r1-outro', 'TÓM LẠI', 'Câu trả lời cho 20 phát hiện?', [],
   '''Vậy câu trả lời cho câu hỏi ở đầu video là gì? Trong hai mươi phát hiện của agent, cái nào là thật? Security-audit-skill không hứa cho bạn câu trả lời hoàn hảo. Nó cho bạn một quy trình để mỗi phát hiện phải tự chứng minh mình. Hãy thử trên repo của chính bạn, trong sandbox, và nhớ rằng số liệu hôm nay là ảnh chụp ngày hai mươi chín tháng mười năm hai nghìn không trăm hai mươi sáu. Tập sau, chúng ta xem một công cụ giúp AI làm giao diện bớt giống nhau. Cảm ơn bạn đã xem Kieu Studio.''',
   34, 'outro', repo=R1, beat='outro',
   data={'color': 'teal', 'url': 'kieu.app', 'chips': [['check', 'Thử trên repo của bạn'], ['lock', 'Trong sandbox'], ['clock', 'Kiểm tra lại số liệu']], 'teaser': 'Tập sau: giao diện AI làm ra bớt giống nhau'}),
]

# ═══════════════════════ GR02 · pbakaus/impeccable ═══════════════════════
GR02 = [
sc('r2-intro', 'GITHUB RADAR · TẬP 2', 'Trang này… mình thấy ở đâu rồi?', [],
   '''Bạn đã bao giờ nhìn một trang web do AI làm và nghĩ: mình thấy cái này ở đâu rồi? Font giống nhau, gradient tím xanh giống nhau, thẻ nằm trong thẻ. Chào mừng bạn đến với Kieu Studio, GitHub Radar, nơi mỗi video chúng tôi chỉ soi một repository. Hôm nay là Impeccable của Paul Bakaus, bộ từ vựng thiết kế cho coding agent. Repo tạo từ tháng mười một năm hai nghìn không trăm hai mươi lăm, giấy phép Apache hai chấm không, và tác giả cho biết nó bắt đầu từ skill frontend-design của Anthropic. Chưa đầy một năm tuổi, nhưng con số của nó thì không nhỏ.''',
   30, 'intro', repo=R2, beat='intro',
   data={'repo': R2, 'q': 'Trang này… mình thấy ở đâu rồi?', 'color': 'amber', 'art': 'palette',
         'chips': [['users', 'Tác giả', 'Paul Bakaus'], ['doc', 'Giấy phép', 'Apache-2.0'], ['calendar', 'Tạo từ', '16/11/2025'], ['branch', 'Fork', '5.593']]}),
sc('r2-growth', 'CON SỐ TĂNG TRƯỞNG', 'Gần gấp đôi tốc độ chỉ trong tuần qua', [NOTE],
   '''Impeccable đã có chín mươi bốn nghìn bảy trăm tám mươi bốn sao. Ba mươi ngày trước là khoảng bảy mươi bốn nghìn chín trăm sáu mươi ba, nghĩa là thêm hơn hai mươi sáu phần trăm trong một tháng. Ghép hai cửa sổ Trending lại, hai mươi ba ngày đầu tăng khoảng năm trăm bốn mươi lăm sao mỗi ngày, còn bảy ngày gần nhất khoảng một nghìn bốn mươi: gần gấp đôi tốc độ. Chưa đến một phút rưỡi lại có thêm một sao. Một repo lớn như vậy mà còn tăng tốc, điều gì đang chạm vào nỗi đau của người dùng?''',
   36, 'growth1', repo=R2, beat='growth',
   data={'total': 94784, 'month': 19821, 'week': 7283, 'today': None, 'color': 'amber', 'factor': '+26,4%',
         'pts': [['30 ngày trước', 74963], ['7 ngày trước', 87501], ['Hôm nay', 94784]],
         'segs': [545, 1040], 'avg': 661, 'tick': '≈ 83 giây / sao', 'tick_basis': 'theo tốc độ 7 ngày gần nhất'}),
sc('r2-why', 'VÌ SAO TÁC GIẢ LÀM RA NÓ', 'Năm dấu hiệu của giao diện "AI slop"', [],
   '''Tác giả mô tả hiện tượng này rất cụ thể. Hãy nhờ agent làm một trang mà không đưa thêm chỉ dẫn, và bạn gần như chắc chắn nhận được font Inter cho mọi thứ, gradient từ tím sang xanh, thẻ lồng trong thẻ, chữ xám trên nền màu, và một ô icon bo góc phía trên mỗi tiêu đề. Chúng xuất hiện qua nhiều model và nhiều dự án. Impeccable cố lấp khoảng trống đó bằng từ vựng chung: những từ để chỉ đạo, một người đánh giá và một bộ phát hiện.''',
   34, 'story', repo=R2, beat='why', data={'art': 'slop', 'color': 'amber'}),
sc('r2-problem', 'BÀI TOÁN CỤ THỂ', '"Làm cho nổi bật hơn" là một yêu cầu mơ hồ', [],
   '''Khi bạn nói hãy làm cho nó nổi bật hơn, agent phải đoán, và đoán thì thường chọn đường an toàn. Impeccable thay đoán bằng lệnh có tên. Bolder tải một playbook riêng cho động tác làm mạnh hơn, và chỉ vào đúng một mục tiêu, ví dụ thẻ giá. Critique chấm điểm thiết kế theo các tiêu chí về khả năng sử dụng và xếp thứ tự cần sửa. Audit kiểm tra khả năng truy cập, hiệu năng, theme và responsive, với mức từ P0 chặn phát hành tới P3 là đánh bóng. Vậy các lệnh đó nằm ở đâu trong hệ thống?''',
   38, 'story', repo=R2, beat='problem', data={'art': 'named', 'color': 'amber'}),
sc('r2-how', 'CÁCH HOẠT ĐỘNG', 'Ba lớp: ngữ cảnh, lệnh, bộ phát hiện', ['Bộ phát hiện: 62 quy tắc xác định, không cần LLM hay API key.'],
   '''Hệ thống có ba lớp. Lớp ngữ cảnh: init đọc mã của bạn, chỉ hỏi những gì không suy ra được, rồi ghi PRODUCT.md; document ghi hệ thống hình ảnh hiện có vào DESIGN.md. Lớp lệnh: hai mươi bốn lệnh chia thành điều chỉnh, đánh giá, hoàn thiện, lặp trực tiếp và lập kế hoạch. Lớp cuối là bộ phát hiện: sáu mươi hai quy tắc xác định, không dùng LLM và không cần API key, chạy trong agent qua hook hoặc trong CI. Điều đó nghĩa là một phần việc review thiết kế của bạn có thể chạy giống hệt nhau mỗi lần.''',
   38, 'flow', repo=R2, beat='how',
   data={'color': 'amber', 'steps': [
       ['doc', 'init', 'ghi PRODUCT.md'], ['palette', 'document', 'ghi DESIGN.md'], ['sliders', 'Steer', 'bolder · quieter · distill'],
       ['eye', 'Review', 'critique · audit P0–P3'], ['check', 'Finish', 'polish · harden · adapt'], ['bug', 'Detect', '62 quy tắc · hook / CI']]}),
sc('r2-usage', 'CÁCH SỬ DỤNG', 'Cài một lần, gọi lệnh theo mục tiêu hẹp', ['Quy tắc cần trang đã render (tương phản, chữ nhỏ) chạy khi quét một URL.'],
   '''Bắt đầu thế nào? Từ thư mục gốc dự án, chạy npx impeccable install rồi tải lại công cụ của bạn. Trong agent, chạy impeccable init một lần để tạo ngữ cảnh. Sau đó gọi lệnh kèm một mục tiêu hẹp, như critique the pricing cards. Không dùng agent cũng được: npx impeccable detect quét thư mục mã, hoặc một địa chỉ trang đang chạy để bắt cả lỗi tương phản và chữ quá nhỏ. Tác giả khuyên: một phần được xem thật kỹ tốt hơn cả trang xem lướt.''',
   38, 'usage', repo=R2, beat='usage',
   data={'art': 'critique', 'color': 'amber',
         'cmds': ['npx impeccable install', '', '# trong agent', '> /impeccable init', '> /impeccable critique the pricing cards', '', '# CI hoặc terminal, không cần agent', 'npx impeccable detect src/'],
         'note': 'Hẹp thì rõ: một thành phần mỗi lần.'}),
sc('r2-value', 'VÌ SAO HỮU ÍCH', 'Cái được và cái giá', ['Cần cân nhắc: hook chạy ngoài phê duyệt của model; telemetry ẩn danh có thể tắt.'],
   '''Vì sao nó hữu ích? Nó biến cảm giác mơ hồ rằng có gì đó sai thành những từ gọi được tên. Người không học thiết kế vẫn có thể nói quieter, distill hoặc typeset và biết agent sẽ làm gì. Bộ phát hiện không dùng LLM nên kết quả lặp lại được. Nhưng README nói thẳng hai điều cần cân nhắc: trong Claude Code, hook đã cài vẫn chạy ngay cả khi bạn từ chối lệnh của model, nên hãy xem hook trước khi chạy không giám sát; và có telemetry ẩn danh, bạn tắt được bằng lệnh hoặc biến môi trường.''',
   38, 'value', repo=R2, beat='value',
   data={'color': 'amber', 'pros': [['sliders', 'Từ vựng chung'], ['eye', 'Có người đánh giá'], ['repeat', 'Kết quả lặp lại được']],
         'cons': [['hook', 'Hook chạy ngoài phê duyệt'], ['eye', 'Telemetry ẩn danh']], 'caveat_from': 0}),
sc('r2-ideas', 'Ý TƯỞNG ỨNG DỤNG', 'Bốn việc bạn có thể làm ngay', [],
   '''Bốn cách dùng. Một, thêm detect vào CI như một bước lint thiết kế, báo ngay trên pull request. Hai, dùng critique trong buổi review giao diện để cả nhóm nhìn cùng một danh sách ưu tiên. Ba, chạy document trên sản phẩm đang có để có DESIGN.md và giữ đúng phong cách khi giao việc cho agent. Bốn, làm bài tập quan sát: cho học viên xem trang trước và sau, rồi cùng gọi tên những mẫu AI hay lặp lại.''',
   32, 'ideas', repo=R2, beat='ideas',
   data={'color': 'amber', 'ideas': [['bug', 'Lint thiết kế trong CI', 'detect trên pull request'], ['users', 'Buổi review giao diện', 'critique cho cả nhóm'],
                                    ['palette', 'Giữ đúng phong cách', 'DESIGN.md cho agent'], ['book', 'Bài tập quan sát', 'gọi tên mẫu AI lặp lại']]}),
sc('r2-outro', 'TÓM LẠI', 'Lần tới thấy trang quen quen, bạn đã có từ để gọi tên', [],
   '''Vậy lần tới khi bạn thấy một trang quen quen, bạn đã có từ để gọi tên nó. Impeccable đáng thử nếu giao diện AI làm ra cứ giống nhau. Hãy bắt đầu với một thành phần nhỏ, xem hook trước khi chạy không giám sát, và tắt telemetry nếu bạn muốn. Số liệu trong video là ảnh chụp ngày hai mươi chín tháng mười năm hai nghìn không trăm hai mươi sáu. Tập sau, chúng ta xem một repo giúp agent không còn quên mọi thứ sau mỗi phiên. Cảm ơn bạn đã xem Kieu Studio.''',
   32, 'outro', repo=R2, beat='outro',
   data={'color': 'amber', 'url': 'kieu.app', 'chips': [['sliders', 'Bắt đầu từ một thành phần'], ['hook', 'Xem hook đã cài'], ['clock', 'Kiểm tra lại số liệu']], 'teaser': 'Tập sau: trí nhớ cho AI agent'}),
]

# ═══════════════════════ GR03 · thedotmack/claude-mem ═══════════════════════
GR03 = [
sc('r3-intro', 'GITHUB RADAR · TẬP 3', 'Hôm qua chúng ta làm gì nhỉ?', [],
   '''Sáng nay bạn mở lại dự án và bảo agent: tiếp tục việc hôm qua. Nó hỏi lại: dự án này cấu trúc thế nào? Bạn thở dài và giải thích lần thứ mười. Chào mừng bạn đến với Kieu Studio, GitHub Radar, nơi mỗi video chúng tôi chỉ soi một repository. Hôm nay là claude-mem của tài khoản thedotmack, hệ thống nén trí nhớ bền vững cho Claude Code. Repo tạo từ tháng tám năm hai nghìn không trăm hai mươi lăm, giấy phép Apache hai chấm không, chín nghìn hai trăm mười bảy fork. Đây là repo lớn nhất trong loạt này, và nó vẫn đang tăng.''',
   30, 'intro', repo=R3, beat='intro',
   data={'repo': R3, 'q': 'Hôm qua chúng ta làm gì nhỉ?', 'color': 'blue', 'art': 'memory',
         'chips': [['users', 'Chủ sở hữu', 'thedotmack'], ['doc', 'Giấy phép', 'Apache-2.0'], ['calendar', 'Tạo từ', '31/08/2025'], ['branch', 'Fork', '9.217']]}),
sc('r3-growth', 'CON SỐ TĂNG TRƯỞNG', 'Đã lớn nhưng vẫn tăng đều', [NOTE],
   '''Claude-mem có một trăm linh bốn nghìn bốn trăm ba mươi ba sao. Ba mươi ngày trước là khoảng chín mươi bốn nghìn tám trăm bốn mươi mốt, nghĩa là thêm chín nghìn năm trăm chín mươi hai, khoảng mười phần trăm, trung bình ba trăm hai mươi sao mỗi ngày, tức cứ khoảng bốn phút rưỡi lại có thêm một sao. Riêng hôm nay, trang Trending ghi bốn trăm năm mươi chín sao. Trang Trending theo tuần không liệt kê repo này, nên chúng tôi không vẽ mốc bảy ngày: chúng tôi không đoán những gì không có số liệu. Một repo đã lớn mà vẫn tăng đều, vậy nó giải quyết nỗi đau nào?''',
   36, 'growth1', repo=R3, beat='growth',
   data={'total': 104433, 'month': 9592, 'week': None, 'today': 459, 'color': 'blue', 'factor': '+10,1%',
         'pts': [['30 ngày trước', 94841], ['Hôm nay', 104433]], 'segs': None, 'avg': 320, 'tick': '≈ 4,5 phút / sao', 'tick_basis': 'theo trung bình 30 ngày'}),
sc('r3-why', 'VÌ SAO TÁC GIẢ LÀM RA NÓ', 'Mỗi phiên mới là một trang giấy trắng', [],
   '''Nỗi đau đó ai dùng coding agent lâu cũng gặp. Phiên kết thúc, ngữ cảnh biến mất. Hôm sau agent bắt đầu từ trang giấy trắng, và bạn lại giải thích cấu trúc dự án, những quyết định đã chốt, lỗi nào đã sửa rồi. README mô tả mục tiêu rõ ràng: tự ghi lại các quan sát khi agent dùng công cụ, tạo bản tóm tắt theo ngữ nghĩa, và cung cấp lại cho phiên sau, để agent giữ được sự liên tục ngay cả khi phiên kết thúc hoặc kết nối lại.''',
   32, 'story', repo=R3, beat='why', data={'art': 'amnesia', 'color': 'blue'}),
sc('r3-problem', 'BÀI TOÁN CỤ THỂ', 'Nhớ nhiều mà không đốt token', [],
   '''Nhưng nhớ không đơn giản. Cách ngây thơ nhất là nhét toàn bộ lịch sử vào ngữ cảnh mỗi lần: tốn token và làm loãng sự chú ý của model. Claude-mem chọn tiết lộ dần. Trước hết chỉ lấy một chỉ mục gọn kèm mã nhận dạng, khoảng năm mươi đến một trăm token mỗi kết quả. Chỉ khi một mục trông liên quan mới tải chi tiết, khoảng năm trăm đến một nghìn token mỗi mục. README ước tính cách này tiết kiệm khoảng mười lần so với tải mọi thứ. Vậy ai ghi, ai lưu, ai tìm?''',
   38, 'story', repo=R3, beat='problem', data={'art': 'funnel', 'color': 'blue'}),
sc('r3-how', 'CÁCH HOẠT ĐỘNG', 'Hook ghi lại, worker lưu, công cụ MCP tìm', ['Ba lớp tìm kiếm: search → timeline → get_observations.'],
   '''Có sáu mắt xích. Sáu hook vòng đời bám theo phiên làm việc: bắt đầu phiên, gửi lời nhắc, trước và sau mỗi lần dùng công cụ, dừng, và kết thúc phiên. Mỗi hook gọi một lệnh claude-mem. Dữ liệu đi vào một dịch vụ worker chạy cục bộ, được lưu trong SQLite, kèm cơ sở dữ liệu vector Chroma để tìm kết hợp từ khóa và ngữ nghĩa. Khi cần nhớ lại, agent dùng ba công cụ MCP theo thứ tự: search lấy chỉ mục, timeline xem bối cảnh, get_observations chỉ tải chi tiết cho những mã đã lọc.''',
   38, 'flow', repo=R3, beat='how',
   data={'color': 'blue', 'steps': [
       ['hook', 'Hook vòng đời', '6 sự kiện của phiên'], ['gear', 'Worker cục bộ', 'API HTTP · Bun'], ['db', 'SQLite', 'phiên · quan sát · tóm tắt'],
       ['layers', 'Chroma', 'từ khóa + ngữ nghĩa'], ['search', 'search', 'chỉ mục gọn'], ['doc', 'get_observations', 'chi tiết, chỉ mã đã lọc']]}),
sc('r3-usage', 'CÁCH SỬ DỤNG', 'Một lệnh cài, khởi động lại, và nó nhớ', ['Cần Node.js 20+. Trình cài có thể mời đăng nhập; có thể bỏ qua.'],
   '''Cách dùng có hai đường. Nhanh nhất là chạy npx claude-mem install. Hoặc trong Claude Code, thêm marketplace thedotmack slash claude-mem rồi cài plugin. Khởi động lại, và ngữ cảnh của các phiên trước tự xuất hiện trong phiên mới. Đọc kỹ bước cài đặt: trình cài có thể mời đăng nhập qua trình duyệt để dùng bộ quan sát được lưu trữ, kèm ba mươi ngày dùng thử. Bạn bỏ qua được bằng cờ provider rõ ràng hoặc đặt CLAUDE_MEM_ONLINE_OPTIN bằng false. Và thẻ private giúp loại nội dung nhạy cảm khỏi bộ nhớ.''',
   40, 'usage', repo=R3, beat='usage',
   data={'art': 'memory', 'color': 'blue',
         'cmds': ['npx claude-mem install', '', '# hoặc trong Claude Code', '/plugin marketplace add thedotmack/claude-mem', '/plugin install claude-mem', '', '# bỏ qua đăng nhập', 'CLAUDE_MEM_ONLINE_OPTIN=false npx claude-mem install'],
         'note': 'Khởi động lại Claude Code → ngữ cảnh phiên trước tự xuất hiện.'}),
sc('r3-value', 'VÌ SAO HỮU ÍCH', 'Cái được và cái giá', ['Cần cân nhắc: hook ghi lại hoạt động công cụ — xem dữ liệu nào được lưu, lưu ở đâu, có đồng bộ đám mây không.'],
   '''Giá trị lớn nhất là bạn không phải giải thích lại dự án mỗi sáng. Bạn hỏi bằng ngôn ngữ tự nhiên về một quyết định cũ hay một lỗi đã sửa, và trả chi phí token theo nhu cầu. Nhưng một công cụ ghi lại hoạt động của agent sẽ biết rất nhiều về mã và công việc của bạn. Hãy xem dữ liệu nào được lưu, lưu ở đâu, có đồng bộ lên đám mây không, và dùng thẻ private cho phần nhạy cảm.''',
   32, 'value', repo=R3, beat='value',
   data={'color': 'blue', 'pros': [['calendar', 'Liên tục giữa các phiên'], ['search', 'Tìm lại bằng ngôn ngữ tự nhiên'], ['clock', 'Token trả theo nhu cầu']],
         'cons': [['eye', 'Ghi lại hoạt động'], ['lock', 'Xem dữ liệu lưu ở đâu']], 'caveat_from': 0}),
sc('r3-ideas', 'Ý TƯỞNG ỨNG DỤNG', 'Bốn việc bạn có thể làm ngay', [],
   '''Bốn ý tưởng. Một, nhật ký quyết định tự động: người mới vào nhóm hỏi vì sao chọn cách này, và agent tìm lại được. Hai, bộ nhớ cho một loạt video hay khóa học: quy ước đặt tên, phong cách, những thứ đã thử. Ba, xem lại lịch sử gỡ lỗi của chính bạn để biết mình hay sai ở đâu. Bốn, ghép với một skill kiểm tra bảo mật để lưu lại những phát hiện đã xử lý cho lần quét sau.''',
   32, 'ideas', repo=R3, beat='ideas',
   data={'color': 'blue', 'ideas': [['book', 'Nhật ký quyết định', 'vì sao chọn cách này'], ['calendar', 'Bộ nhớ cho loạt nội dung', 'quy ước · phong cách'],
                                    ['bug', 'Soi lịch sử gỡ lỗi', 'mình hay sai ở đâu'], ['shield', 'Ghép với skill bảo mật', 'nhớ phát hiện đã xử lý']]}),
sc('r3-outro', 'TÓM LẠI', 'Nếu agent nhớ hôm qua, bạn bắt đầu từ đâu?', [],
   '''Quay lại buổi sáng ở đầu video: nếu agent nhớ hôm qua, bạn sẽ bắt đầu từ đâu? Claude-mem đáng thử nếu bạn dùng Claude Code hằng ngày và mệt vì giải thích lại. Thử trên một dự án nhỏ trước, xem kỹ dữ liệu được lưu ở đâu, và bỏ qua đăng nhập nếu bạn không cần. Số liệu hôm nay là ảnh chụp ngày hai mươi chín tháng mười năm hai nghìn không trăm hai mươi sáu. Cảm ơn bạn đã xem Kieu Studio, hẹn gặp lại ở GitHub Radar tiếp theo.''',
   30, 'outro', repo=R3, beat='outro',
   data={'color': 'blue', 'url': 'kieu.app', 'chips': [['box', 'Thử trên dự án nhỏ'], ['lock', 'Xem dữ liệu được lưu'], ['clock', 'Kiểm tra lại số liệu']], 'teaser': 'Hẹn gặp lại ở GitHub Radar tiếp theo'}),
]

EPISODES = {'gr01': GR01, 'gr02': GR02, 'gr03': GR03}
EPISODE = os.environ.get('KIEU_EPISODE', 'gr01').lower()
if EPISODE not in EPISODES:
    raise SystemExit(f'KIEU_EPISODE must be one of {sorted(EPISODES)}')
S = EPISODES[EPISODE]   # exactly one repo per video

# One-minute cuts (KIEU_FORMAT=short): same repos, same visuals/numbers, shorter narration. See scripts/shorts.py.
from shorts import make_shorts  # noqa: E402
SHORTS = make_shorts(EPISODES, sc)
if os.environ.get('KIEU_FORMAT', 'full').lower() == 'short':
    S = SHORTS[EPISODE]
