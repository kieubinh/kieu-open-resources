"""Episode 02 — all three official examples and problem-solving narrative."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Scene:
    id: str
    phase: str
    title: str
    lines: tuple[str, ...]
    script: str
    min_seconds: float = 8.0
    mode: str = "cards"
    silent: bool = False

def sc(id, phase, title, lines, narration, secs=11, mode="cards", silent=False):
    return Scene(id, phase, title, tuple(lines), narration, float(secs), mode, silent)

S = [
sc("01-hook","KIEU STUDIO / OUR MISSION","LeetCode là bài tập. Tư duy là mục tiêu.",[
    "KIEU STUDIO · THE ART OF CODING",
    "Không chỉ tìm đáp án cho một bài LeetCode.",
    "Mỗi bài toán giúp luyện kỹ năng giải quyết vấn đề.",
    "HIỂU → GIẢ THUYẾT → KIỂM CHỨNG → RÚT KINH NGHIỆM"],
    "Chào mừng đến với Kieu Studio, The Art of Coding. LeetCode không phải đích đến. Đây là nơi chúng ta luyện kỹ năng giải quyết vấn đề bằng cách hiểu yêu cầu, thử giả thuyết, kiểm chứng và rút kinh nghiệm.",19,"mission"),
sc("02-question","01 / ĐỌC ĐỀ","Regular Expression Matching",[
    "Input: văn bản s và mẫu p",
    "Dấu chấm . khớp đúng một ký tự bất kỳ",
    "Dấu sao * lặp phần tử ngay trước: không hoặc nhiều lần",
    "Phải khớp TOÀN BỘ chuỗi"],
    "Trong bài số mười, ta phải kiểm tra một mẫu có khớp toàn bộ chuỗi hay không. Dấu chấm là bất kỳ một ký tự; dấu sao có nghĩa là lặp phần tử đứng trước không hoặc nhiều lần.",16,"problem"),
sc("03-read-input","01 / ĐỌC ĐỀ","Input, Output và Constraints",[
    "INPUT: s = chuỗi văn bản, p = mẫu",
    "OUTPUT: true nếu khớp toàn bộ; ngược lại false",
    "Độ dài s và p từ 1 đến 20",
    "s chỉ chứa a–z; p chứa a–z, . và *",
    "Mỗi dấu * có phần tử hợp lệ ngay trước"],
    "Đầu vào gồm s và p. Đầu ra là đúng hoặc sai. Mỗi chuỗi dài từ một đến hai mươi ký tự. Mẫu chỉ được dùng chữ thường, dấu chấm và dấu sao, với dấu sao đi sau một phần tử hợp lệ.",17,"constraints"),
sc("04-stats","01 / ĐỌC ĐỀ","Bài Hard có gì đặc biệt?",[
    "Hard · 32,0% acceptance rate",
    "Khoảng 1,52 triệu lượt nộp được chấp nhận",
    "Khoảng 4,8 triệu lượt nộp tổng cộng",
    "Số liệu lượt nộp, không phải số người"],
    "Tại thời điểm tra cứu hai mươi tám tháng mười năm hai nghìn không trăm hai mươi sáu, LeetCode xếp bài này ở mức Hard. Tỷ lệ chấp nhận khoảng ba mươi hai phần trăm. Nhớ rằng lượt nộp không có nghĩa là số người.",14,"stats"),
sc("05-ex1","02 / ĐỌC VÍ DỤ","Ví dụ 1: aa và a",[
    's = "aa"', 'p = "a"', "Output: false"],
    "Mẫu chỉ có một chữ a, nhưng chuỗi có hai chữ a. Dù khớp được chữ đầu tiên, còn một chữ chưa được xử lý nên kết quả là sai.",13,"ex1"),
sc("06-ex1-lesson","02 / ĐỌC VÍ DỤ","Bài học 1: Đừng bỏ sót yêu cầu",[
    "Khớp một phần không phải khớp toàn bộ",
    "Luôn kiểm tra điều kiện kết thúc"],
    "Đây là thói quen đầu tiên: đừng kết luận chỉ vì một phần có vẻ đúng. Hãy kiểm tra điều kiện hoàn thành của toàn bộ vấn đề.",12,"lesson1"),
sc("07-ex2","02 / ĐỌC VÍ DỤ","Ví dụ 2: aa và a*",[
    's = "aa"', 'p = "a*"', "Output: true"],
    "Dấu sao cho phép dùng chữ a không lần nào, một lần hoặc nhiều lần. Dùng hai chữ a chính là cách làm cho mẫu khớp toàn bộ chuỗi.",13,"ex2"),
sc("08-ex2-lesson","02 / ĐỌC VÍ DỤ","Bài học 2: Một quy tắc, nhiều lựa chọn",[
    'a* có thể là "", "a", "aa" hoặc "aaa"...',
    "Hãy liệt kê các khả năng trước khi chọn"],
    "Dấu sao không chỉ là một ký tự khác. Nó tạo ra nhiều lựa chọn. Việc nhận diện tất cả lựa chọn có thể là chìa khóa của bài toán.",13,"lesson2"),
sc("09-ex3","02 / ĐỌC VÍ DỤ","Ví dụ 3: ab và .*",[
    's = "ab"', 'p = ".*"', "Output: true"],
    "Dấu chấm có thể đại diện cho a hoặc b. Dấu sao cho phép lặp quy tắc này. Ta dùng hai lần để khớp cả a và b, vậy kết quả đúng.",13,"ex3"),
sc("10-ex3-lesson","02 / ĐỌC VÍ DỤ","Bài học 3: Kết hợp quy tắc đơn giản",[
    ". là một ký tự bất kỳ",
    "* là số lần lặp",
    ".* có thể khớp cả chuỗi bất kỳ, kể cả rỗng"],
    "Khi bài toán có nhiều quy tắc, hãy hiểu từng quy tắc trước và sau đó quan sát điều gì xảy ra khi chúng kết hợp.",14,"lesson3"),
sc("11-recap","02 / ĐỌC VÍ DỤ","Ba ví dụ, ba bài học",[
    "Kiểm tra TOÀN BỘ yêu cầu",
    "Tìm các điểm tạo nhiều lựa chọn",
    "Hiểu tác động khi kết hợp quy tắc"],
    "Chúng ta chưa viết code nhưng đã học được ba thói quen quan trọng: kiểm tra đầy đủ, nhận diện lựa chọn và phân tích quy tắc kết hợp.",12,"recap"),
sc("12-hints","03 / TỰ GIẢI","Ba gợi ý trước khi xem lời giải",[
    "HINT 1: Có thể giải phần nhỏ hơn không?",
    "HINT 2: Khi gặp x*, có bao nhiêu lựa chọn?",
    "HINT 3: Có gặp lại cùng câu hỏi không?"],
    "Hãy thử tự nghĩ. Ta có thể giải phần còn lại của chuỗi không? Khi gặp x sao, ta có thể bỏ qua hay dùng thêm? Và liệu có những câu hỏi nhỏ mà ta gặp đi gặp lại?",15,"hints"),
sc("13-pause","03 / TỰ GIẢI","10 GIÂY — ĐẾN LƯỢT BẠN",[
    "Nếu mẫu có a*, bạn thử lựa chọn nào trước?",
    "Tự đưa ra một giả thuyết."],
    "",10,"think",True),
sc("14-reveal","04 / XÂY TƯ DUY","Chia thành câu hỏi nhỏ",[
    "i = vị trí trong s",
    "j = vị trí trong p",
    "Từ (i, j), phần còn lại khớp được không?"],
    "Ta thay một câu hỏi lớn bằng câu hỏi nhỏ: tại vị trí i trong s và j trong p, liệu hai phần còn lại có khớp không? Đây là cách chia nhỏ vấn đề.",15,"state"),
sc("15-normal","04 / XÂY TƯ DUY","Trường hợp thông thường",[
    "Chữ giống nhau: cả hai tiến một bước",
    "Dấu .: chấp nhận đúng một ký tự rồi tiến",
    "Không khớp: nhánh này thất bại"],
    "Với chữ bình thường hoặc dấu chấm, nếu ký tự hiện tại khớp thì di chuyển cả hai vị trí. Nếu không, đường đi này thất bại.",14,"normal"),
sc("16-star","04 / XÂY TƯ DUY","Khi gặp a*: hai con đường",[
    "A: Bỏ qua a* hoàn toàn",
    "B: Nếu khớp, dùng một ký tự rồi giữ a*"],
    "Ta có hai lựa chọn. Bỏ qua a sao, bởi nó có thể xuất hiện không lần nào; hoặc nếu chữ hiện tại khớp a thì dùng một chữ, và giữ nguyên a sao để tiếp tục.",18,"branch"),
sc("17-tree","04 / XÂY TƯ DUY","Thử đường đi và quay lại",[
    's = "aab"; p = "c*a*b"',
    "Bỏ c*; dùng a* hai lần; cuối cùng khớp b"],
    "Trong ví dụ bổ sung a a b và c sao a sao b, ta bỏ c sao, dùng a sao hai lần, rồi khớp b. Đây là một đường đi thành công.",16,"tree"),
sc("18-pitfall","04 / XÂY TƯ DUY","Đừng luôn chọn lặp nhiều nhất",[
    "Chọn tham lam có thể làm mất lời giải",
    "Giữ cả lựa chọn bỏ qua và dùng thêm"],
    "Nếu cứ dùng dấu sao nhiều nhất có thể, đôi khi phần còn lại không khớp. Vì vậy cần xét cả hai lựa chọn thay vì đoán.",13,"pitfall"),
sc("19-cache","05 / GHI NHỚ","Có những câu hỏi cũ xuất hiện lại",[
    "(i, j) xác định một câu hỏi",
    "Hai nhánh có thể đi đến cùng câu hỏi",
    "Lưu kết quả và dùng lại"],
    "Hai nhánh khác nhau đôi khi dẫn tới cùng cặp vị trí i và j. Đừng giải lại. Lưu kết quả của câu hỏi nhỏ để dùng sau. Đây là ghi nhớ kết quả, còn gọi là memoization.",16,"cache"),
sc("20-dp","05 / GHI NHỚ","Bảng ghi nhớ là bản đồ câu hỏi",[
    "Mỗi ô là câu hỏi về phần còn lại",
    "TRUE hoặc FALSE",
    "Tối đa khoảng (m+1) × (n+1) trạng thái"],
    "Hãy xem bảng gồm các vị trí của hai chuỗi. Mỗi ô là một câu hỏi: hai phần còn lại khớp không? Khi đã có đáp án, không cần tính lại. Đây là tư duy quy hoạch động.",17,"grid"),
sc("21-dp-demo","05 / GHI NHỚ","Xem bảng nhỏ với aa và a*",[
    "Chỉ xét đầu mẫu j=0 và khi hết mẫu j=2",
    "Không xem riêng dấu * là một mẫu hợp lệ",
    "Dùng a hai lần, rồi kết thúc cả hai chuỗi"],
    "Với a a và a sao, ta dùng a sao hai lần rồi bỏ qua nó. Khi cả hai phần còn lại đều kết thúc, kết quả đúng. Đừng coi dấu sao đơn lẻ là một trạng thái mẫu hợp lệ.",16,"dp_demo"),
sc("22-solution","06 / THIẾT KẾ GIẢI PHÁP","Từ suy nghĩ sang pseudocode",[
    "match(i,j): phần còn lại có khớp không?",
    "Hết mẫu thì cũng phải hết chuỗi",
    "Có *: bỏ qua hoặc dùng tiếp",
    "Không có *: so ký tự rồi tiến",
    "Ghi nhớ kết quả"],
    "Trước khi viết Python, hãy viết logic bằng lời: kiểm tra kết thúc, chọn hai nhánh khi có sao, so ký tự khi không có sao, và ghi nhớ kết quả.",17,"pseudocode"),
sc("23-python1","06 / PYTHON 3","Python: tạo hàm và điều kiện dừng",[
    "from functools import cache", "@cache", "def dfs(i, j):", "    if j == len(p):", "        return i == len(s)"],
    "Hàm dfs nhận cặp vị trí i và j. Cache giúp không xử lý lại cùng trạng thái. Nếu mẫu đã hết thì chỉ thành công khi chuỗi cũng hết.",14,"code1"),
sc("24-python2","06 / PYTHON 3","Python: hai nhánh của dấu sao",[
    "first = i < len(s) and (s[i] == p[j] or p[j] == '.')",
    "if j+1 < len(p) and p[j+1] == '*':",
    "    return dfs(i,j+2) or (first and dfs(i+1,j))",
    "return first and dfs(i+1,j+1)"],
    "Nếu ký tự sau là dấu sao, ta bỏ qua cặp ký tự và dấu sao hoặc dùng một ký tự hiện tại rồi thử tiếp. Nếu không, chỉ tiến khi ký tự đang xét khớp.",18,"code2"),
sc("25-complexity","07 / ĐÁNH GIÁ","Vì sao giải pháp đủ nhanh?",[
    "m là độ dài s; n là độ dài p",
    "Mỗi trạng thái (i,j) chỉ xử lý một lần",
    "Thời gian O(m × n)",
    "Bộ nhớ O(m × n)"],
    "Với tối đa khoảng m nhân n trạng thái và mỗi trạng thái chỉ giải một lần, độ phức tạp cả thời gian và bộ nhớ là O của m nhân n.",14,"complexity"),
sc("26-lesson","08 / PROBLEM SOLVING","Bốn thói quen mang sang công việc",[
    "Hiểu chính xác yêu cầu",
    "Kiểm tra ví dụ đúng và phản ví dụ",
    "Chia thành lựa chọn nhỏ",
    "Ghi nhớ kết quả đã tìm"],
    "Điều quan trọng không phải ghi nhớ code. Hãy nhớ cách hiểu yêu cầu, thử giả thuyết, chia nhỏ lựa chọn và không giải lại vấn đề cũ.",15,"lessons"),
sc("27-practice","09 / BÀI TẬP LUYỆN","Ba bài tương tự",[
    "LeetCode #44 · Wildcard Matching",
    "LeetCode #72 · Edit Distance",
    "LeetCode #97 · Interleaving String"],
    "Hãy thử Wildcard Matching, Edit Distance và Interleaving String. Đừng tìm code ngay. Trước tiên hãy tự hỏi trạng thái nhỏ là gì và có những lựa chọn nào.",15,"practice"),
sc("28-outro","THE ART OF CODING","Đừng ghi nhớ code. Hãy ghi nhớ cách nghĩ.",[
    "Understand → Explore → Decide → Remember",
    "KIEU STUDIO"],
    "Một bài khó sẽ dễ tiếp cận hơn khi ta đặt đúng câu hỏi. Hẹn gặp trong tập tiếp theo của Kieu Studio, The Art of Coding.",10,"outro"),
]
