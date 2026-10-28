"""Kieu Studio episode LeetCode #4 — all official examples, decisions before Python."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Scene:
    id: str
    phase: str
    title: str
    lines: tuple[str,...]
    script: str
    min_seconds: float
    mode: str = 'cards'
    silent: bool = False
    trace: str = ''


def sc(id,phase,title,lines,script,secs=43,mode='cards',silent=False,trace=''):
    return Scene(id,phase,title,tuple(lines),script.strip(),float(secs),mode,silent,trace)

S=[
sc('01-mission','KIEU STUDIO / THE ART OF CODING','Học cách nghĩ, không học thuộc code',[
 'HIỂU VẤN ĐỀ → THỬ GIẢ THUYẾT → KIỂM CHỨNG → RÚT KINH NGHIỆM',
 'LeetCode là sân tập. Tư duy giải quyết vấn đề mới là mục tiêu.'],
 '''Chào mừng đến với Kieu Studio, The Art of Coding. Trong series này, chúng ta không xem LeetCode như một bộ sưu tập đáp án để học thuộc. Mỗi bài là một tình huống luyện khả năng giải quyết vấn đề. Hôm nay, bạn sẽ tập quan sát yêu cầu, phát hiện điều kiện quan trọng, đưa ra giả thuyết, tự kiểm tra rồi mới viết code. Nếu bạn từng thấy bài Hard quá đáng sợ, hãy thử học cùng chúng tôi theo đúng thứ tự này. Câu hỏi quan trọng không phải viết dòng code nào đầu tiên, mà là vì sao chúng ta cần dòng code đó.''',49,'mission'),
sc('02-hook','01 / CÂU CHUYỆN','Hai hàng đã xếp sẵn — tìm đúng điểm giữa',[
 'Một hàng xanh và một hàng vàng, mỗi hàng đều tăng dần.',
 'Không muốn nhập tất cả thành một hàng dài.',
 'Ta có thể tìm điểm giữa chỉ bằng vài phép so sánh?'],
 '''Hãy tưởng tượng có hai hàng người đã đứng theo chiều cao từ thấp đến cao. Chúng ta muốn tìm người nằm giữa nếu gộp cả hai hàng. Cách tự nhiên là bảo mọi người nhập lại thành một hàng duy nhất. Nhưng nếu một hàng cực dài, việc sắp xếp lại từ đầu sẽ lãng phí. Điều thú vị là thứ tự trong từng hàng đã chứa một phần lớn thông tin. Tại sao phải di chuyển tất cả khi có thể tìm một vị trí phân chia phù hợp? Đây chính là cốt lõi của bài số bốn.''',46,'story'),
sc('03-problem','02 / ĐỌC ĐỀ','Median of Two Sorted Arrays',[
 'Input: nums1, nums2 — hai mảng đã được sắp xếp tăng dần',
 'Output: trung vị của toàn bộ phần tử',
 'Mục tiêu thời gian: O(log(m+n))'],
 '''Bài số bốn trên LeetCode có tên Median of Two Sorted Arrays. Chúng ta nhận hai mảng số nguyên nums một và nums hai. Mỗi mảng đã được sắp xếp tăng dần. Kết quả cần trả về là trung vị của tất cả phần tử hai mảng nếu nhìn chúng như một tập hợp có thứ tự. Một yêu cầu không được bỏ qua là thời gian chạy O của logarit m cộng n. Đây không chỉ là lời khuyên tối ưu hóa; nó khiến giải pháp duyệt từng phần tử chưa đạt mục tiêu của đề.''',46,'problem'),
sc('04-median','02 / ĐỌC ĐỀ','Trung vị nghĩa là gì?',[
 'Tổng lẻ: lấy phần tử nằm chính giữa.',
 'Tổng chẵn: trung bình của hai phần tử ở giữa.',
 'Trung vị không phải trung bình của toàn bộ mảng.'],
 '''Nếu số lượng phần tử là lẻ, trung vị là một phần tử đúng ở giữa sau khi sắp xếp. Chẳng hạn một, hai, ba thì đáp án là hai. Nếu số lượng là chẵn, chẳng hạn một, hai, ba, bốn, thì chúng ta lấy trung bình của hai và ba, được hai phẩy năm. Đây là chỗ nhiều người nhầm giữa median và mean. Mean là trung bình tất cả giá trị; median là vị trí ở giữa của thứ tự. Với bài toán này, ta chỉ cần biết một hoặc hai phần tử giữa, không cần biết cả dãy đã gộp.''',46,'median'),
sc('05-constraints','02 / ĐỌC ĐỀ','Đọc đủ các ràng buộc',[
 '0 ≤ m ≤ 1000; 0 ≤ n ≤ 1000',
 '1 ≤ m+n ≤ 2000',
 '−10⁶ ≤ nums1[i], nums2[i] ≤ 10⁶',
 'Một mảng được phép rỗng; cả hai không thể cùng rỗng.'],
 '''Hãy quan sát ràng buộc vì chúng sinh ra các ca kiểm thử. Kích thước từng mảng từ không tới một nghìn, nhưng tổng ít nhất là một và nhiều nhất hai nghìn. Điều đó có nghĩa một trong hai mảng hoàn toàn có thể rỗng. Các giá trị số nguyên từ âm một triệu đến dương một triệu, nên có số âm, số không và số trùng nhau. Khi thử một giải pháp, chúng ta phải tự hỏi: điều gì xảy ra nếu bên trái không có phần tử nào? Nếu hai phần tử ở hai biên bằng nhau? Nếu tổng là số chẵn?''',50,'constraints'),
sc('06-stats','02 / ĐỌC ĐỀ','Độ khó và thống kê được kiểm chứng',[
 'Difficulty: HARD (LeetCode)',
 'Acceptance: 46,4% (Leetbot, snapshot 04/09/2026)',
 'Không suy ra số người giải từ lượt nộp.',
 'Accepted/Total submissions: chưa có số xác minh.'],
 '''LeetCode xếp bài này vào mức Hard. Bộ dữ liệu Leetbot cập nhật ngày bốn tháng chín năm hai nghìn không trăm hai mươi sáu ghi nhận tỷ lệ chấp nhận là bốn mươi sáu phẩy bốn phần trăm. Đây là ảnh chụp dữ liệu theo thời điểm, không phải một tỷ lệ trực tiếp ngay lúc bạn đang xem. Chúng ta chưa có con số đáng tin cậy về lượt nộp được chấp nhận và tổng lượt nộp tại cùng thời điểm, nên sẽ không tự tạo hai con số đó. Quan trọng hơn: lượt nộp là số lần thử, không phải số người.''',47,'stats'),
sc('07-ex1','03 / VÍ DỤ CHÍNH THỨC','Ví dụ 1 — tổng lẻ',[
 'nums1 = [1,3]   nums2 = [2]',
 'Hình dung gộp: [1,2,3]',
 'Output: 2.00000'],
 '''Với ví dụ đầu tiên, nums một là một và ba, nums hai chỉ có số hai. Nếu gộp để hình dung, ta được một, hai, ba. Tổng cộng ba phần tử, trung vị là hai, nên đầu ra hai chấm không không không không không. Trên màn hình, hãy nhìn số hai đứng giữa hai phía. Nhưng lưu ý: chúng ta chỉ gộp để hiểu đề, chưa phải thuật toán sẽ triển khai. Từ một ví dụ dễ, hãy tự đặt câu hỏi liệu có cách nào xác nhận số hai nằm giữa mà không cần tạo mảng mới?''',50,'ex1','', 'official_1'),
sc('08-ex2','03 / VÍ DỤ CHÍNH THỨC','Ví dụ 2 — tổng chẵn',[
 'nums1 = [1,2]   nums2 = [3,4]',
 'Hình dung gộp: [1,2,3,4]',
 'Output: 2.50000 = (2+3)/2'],
 '''Ví dụ thứ hai, nums một gồm một và hai, nums hai gồm ba và bốn. Sau khi hình dung theo thứ tự, ta có một, hai, ba, bốn. Có bốn phần tử, vì vậy không tồn tại một phần tử duy nhất nằm giữa. Hai giá trị trung tâm là hai và ba. Lấy tổng rồi chia hai được hai phẩy năm. Điều này cho ta một manh mối quan trọng: nếu tách dãy thành nửa trái và nửa phải, lời giải chỉ cần giá trị lớn nhất của nửa trái và nhỏ nhất của nửa phải.''',50,'ex2','', 'official_2'),
sc('09-examples-recap','03 / KIỂM TRA HIỂU','Hai ví dụ dẫn đến một điều kiện',[
 'Tổng lẻ → max(phía trái)',
 'Tổng chẵn → [max(trái)+min(phải)]/2',
 'Nửa trái phải chứa đúng số phần tử cần thiết.'],
 '''Hãy dừng ở đây một chút để tổng hợp. Ở ví dụ một, chúng ta chỉ cần giá trị lớn nhất phía trái. Ở ví dụ hai, cần thêm giá trị nhỏ nhất phía phải. Nhưng có một điều bắt buộc: phía trái phải chứa chính xác một nửa phần tử, hoặc nhiều hơn một phần tử nếu tổng là lẻ. Nếu số lượng phía trái sai, vị trí giữa cũng sai. Vậy nhiệm vụ mới của chúng ta không còn là gộp hai mảng. Nó trở thành tìm một đường cắt sao cho số lượng đúng và thứ tự hai bên không bị đảo lộn.''',46,'recap'),
sc('10-naive','04 / GIẢ THUYẾT ĐẦU','Cách dễ nhất: gộp rồi tìm giữa',[
 'Ghép và sort: O((m+n) log(m+n))',
 'Trộn hai mảng đã sort: O(m+n)',
 'Đúng về kết quả nhưng chưa đạt yêu cầu logarit.'],
 '''Khi gặp bài khó, đừng vội bỏ qua lời giải dễ nhất. Ta có thể nối hai mảng rồi sort; cách đó tốn thời gian cỡ tổng độ dài nhân logarit tổng độ dài. Vì hai mảng đã tăng dần, ta còn có thể dùng hai con trỏ để trộn chúng trong O của m cộng n. Đây là hai cách đúng về mặt đáp án. Chúng rất hữu ích để kiểm tra các ví dụ và làm bộ đối chiếu khi test. Nhưng đề bài đòi thời gian logarit, nên cả hai chưa phải giải pháp cuối. Phân biệt đúng và đạt yêu cầu là kỹ năng giải quyết vấn đề quan trọng.''',48,'naive'),
sc('11-reject','04 / LOẠI PHƯƠNG ÁN','Tại sao không duyệt đến giữa?',[
 'Không cần sắp xếp lại, nhưng vẫn phải đi từng phần tử.',
 'Nếu nửa giữa xa hàng nghìn vị trí, tuyến tính vẫn tuyến tính.',
 'Hãy tận dụng cấu trúc có thứ tự để bỏ qua cả nhóm.'],
 '''Một ý tưởng có vẻ tốt hơn: không tạo mảng mới mà chỉ dùng hai con trỏ, đi đến vị trí giữa rồi dừng lại. Cách này tiết kiệm bộ nhớ, nhưng số bước trong trường hợp xấu nhất vẫn tăng theo tổng kích thước. Vậy chúng ta thiếu điều gì? Tìm kiếm nhị phân hoạt động tốt khi mỗi phép so sánh cho phép loại bỏ một vùng lựa chọn lớn. Nếu có thể so sánh hai giá trị ngay sát đường cắt và biết nên dịch cắt trái hay phải, chúng ta sẽ tiến nhanh hơn nhiều. Đây là lý do phải đổi câu hỏi.''',47,'reject'),
sc('12-hints','05 / BA GỢI Ý','Tự suy nghĩ trước khi xem lời giải',[
 'Gợi ý 1: Ta có thật sự cần tạo mảng đã gộp?',
 'Gợi ý 2: Cắt hai mảng sao cho phía trái đủ số lượng?',
 'Gợi ý 3: Hai giá trị nào quyết định cắt có hợp lệ?'],
 '''Trước khi xem lời giải, bạn có ba gợi ý. Một: ta chỉ cần một hoặc hai số giữa, có nhất thiết phải xây dựng toàn bộ dãy sau khi gộp không? Hai: hãy tưởng tượng đặt một đường cắt trên mỗi mảng. Có cách nào khiến tổng số phần tử bên trái được cố định không? Ba: vì mỗi mảng đã sắp xếp, liệu chỉ cần quan sát hai giá trị ở mép đường cắt trên từng mảng là đủ để biết hai nửa có đúng thứ tự? Hãy thử vẽ hai đường cắt trên giấy. Đừng viết code, chỉ tìm một điều kiện có thể kiểm chứng.''',57,'hints'),
sc('13-pause','05 / TỰ GIẢI','10 GIÂY SUY NGHĨ',[
 'Điều kiện nào chứng minh toàn bộ bên trái ≤ toàn bộ bên phải?',
 'Không có lời thoại, không nhạc nền, đếm ngược đúng 10 giây.'],
 '',10,'think',True),
sc('14-reveal','06 / KHÁM PHÁ','Hai đường cắt, một lời giải',[
 'Chia mỗi mảng thành trái / phải',
 'Tổng số phần tử bên trái = (m+n+1)//2',
 'Tìm đường cắt thỏa thứ tự toàn cục.'],
 '''Hết thời gian suy nghĩ. Hãy xem điều gì xảy ra khi kẻ một đường dọc trên mỗi mảng. Bên trái mỗi đường cắt là một nhóm nhỏ đã sắp xếp, bên phải cũng vậy. Nếu hai nhóm trái cộng lại có đúng số phần tử cần thiết, và mọi giá trị bên trái không vượt quá mọi giá trị bên phải, thì điểm giữa đã được xác định. Điểm thú vị là ta không cần so sánh từng cặp phần tử. Mỗi mảng đã tăng dần, nên chỉ cần kiểm tra bốn giá trị ngay bên cạnh hai đường cắt.''',52,'partition'),
sc('15-smaller','06 / THIẾT KẾ','Chỉ tìm kiếm trên mảng ngắn hơn',[
 'A = mảng ngắn hơn; B = mảng dài hơn',
 'i = số phần tử A ở bên trái',
 'j = leftSize − i'],
 '''Ta luôn gọi A là mảng ngắn hơn và B là mảng dài hơn. Nếu ban đầu nums một dài hơn nums hai, hãy đổi tên hai biến; dữ liệu không cần thay đổi. Bây giờ, i là số phần tử của A nằm bên trái đường cắt. Vì tổng số phần tử phía trái phải cố định, j sẽ bằng leftSize trừ i. Như vậy, chỉ cần chọn i thì j được tính tự động. Chúng ta chỉ cần tìm kiếm nhị phân trên i từ không đến độ dài A, kể cả cắt trước phần tử đầu hoặc sau phần tử cuối.''',50,'partition'),
sc('16-four','06 / ĐIỀU KIỆN','Bốn số ở sát hai đường cắt',[
 'AL = A[i−1] ; AR = A[i]',
 'BL = B[j−1] ; BR = B[j]',
 'Cắt ở biên? Dùng −∞ hoặc +∞ thích hợp.'],
 '''Hãy đặt tên cho bốn giá trị. A trái, viết AL, là phần tử cuối ở nửa trái mảng A. A phải, viết AR, là phần tử đầu ở nửa phải mảng A. Tương tự BL và BR cho mảng B. Nếu cắt ngay đầu mảng thì phía trái trống, ta dùng âm vô cực làm giá trị thay thế. Nếu cắt ngay cuối mảng thì phía phải trống, ta dùng dương vô cực. Những giá trị đặc biệt này không phải dữ liệu thật; chỉ là cách viết gọn để không phải mở thêm nhiều nhánh xử lý rìa.''',52,'bounds'),
sc('17-invariant','06 / CHỨNG MINH','Khi nào đường cắt hợp lệ?',[
 'AL ≤ BR',
 'BL ≤ AR',
 'Hai điều kiện chéo + mảng có thứ tự ⇒ trái ≤ phải.'],
 '''Đây là điều kiện chính xác nhất trong bài. Đường cắt hợp lệ khi AL nhỏ hơn hoặc bằng BR, đồng thời BL nhỏ hơn hoặc bằng AR. Tại sao chỉ có hai bất đẳng thức? Bởi trong từng mảng, tất cả phần tử trái đã nhỏ hơn hoặc bằng phần tử phải của chính mảng đó. Chúng ta chỉ còn cần kiểm tra hai phía cắt chéo giữa hai mảng. Khi cả hai điều kiện đúng, phần tử lớn nhất bên trái là max của AL và BL; nhỏ nhất bên phải là min của AR và BR. Median đã nằm ngay trước mắt.''',52,'valid'),
sc('18-go-left','07 / BINARY SEARCH','Nếu AL quá lớn: dịch đường cắt sang trái',[
 'AL > BR ⇒ đã lấy quá nhiều phần tử từ A',
 'Giảm i bằng hi = i−1',
 'j tự tăng lên để giữ số phần tử bên trái.'],
 '''Giả sử AL lớn hơn BR. Điều đó có nghĩa chúng ta đã đưa một phần tử A quá lớn sang nửa trái, trong khi có một phần tử B nhỏ hơn nằm ở nửa phải. Đường cắt không thể đúng. Muốn sửa, ta phải lấy ít phần tử từ A ở phía trái hơn: giảm i bằng cách cập nhật hi thành i trừ một. Do j bằng leftSize trừ i, j tự động tăng. Chúng ta không phải đoán cả hai đường cắt. Mỗi lần cập nhật loại bỏ khoảng một nửa vùng tìm kiếm còn lại.''',49,'move_left','', 'move_left'),
sc('19-go-right','07 / BINARY SEARCH','Nếu BL quá lớn: dịch đường cắt sang phải',[
 'BL > AR ⇒ đã lấy quá ít phần tử từ A',
 'Tăng i bằng lo = i+1',
 'j tự giảm để giữ tổng phía trái.'],
 '''Bây giờ đổi tình huống: BL lớn hơn AR. Một phần tử của B nằm phía trái lại lớn hơn phần tử A nằm phía phải. Chúng ta đang lấy quá ít phần tử từ A sang trái. Vì vậy, tăng i bằng cách đặt lo bằng i cộng một; lúc đó j tự giảm. Hai hướng cập nhật hoàn toàn đối xứng. Bạn không cần nhớ hai dòng code như công thức bí hiểm. Chỉ cần hỏi bên nào có phần tử đang nằm sai phía, rồi sửa vị trí cắt để đưa nó về đúng nhóm.''',49,'move_right','', 'move_right'),
sc('20-walk1','08 / LẦN THEO THUẬT TOÁN','Chạy tay ví dụ chính thức số 1',[
 'A = [2], B = [1,3]',
 'leftSize = 2; thử i=0 rồi i=1',
 'Kết luận: median = 2.0'],
 '''Chúng ta sẽ lần theo thuật toán với ví dụ chính thức một. Vì nums hai chỉ có một số, ta dùng A bằng hai; B bằng một và ba. Tổng ba phần tử nên leftSize bằng hai. Ban đầu i bằng không, j bằng hai; khi ấy BL bằng ba lớn hơn AR bằng hai. Cần dịch i sang phải. Ở bước sau i bằng một và j bằng một. AL bằng hai, AR dương vô cực, BL bằng một, BR bằng ba. Cả hai điều kiện đều đúng. Tổng lẻ, lấy max của hai và một, kết quả hai.''',61,'trace','', 'official_1'),
sc('21-walk2','08 / LẦN THEO THUẬT TOÁN','Chạy tay ví dụ chính thức số 2',[
 'A = [1,2], B = [3,4]',
 'leftSize = 2; tìm điểm cắt hợp lệ',
 'Median = (max trái + min phải)/2 = 2.5'],
 '''Với ví dụ chính thức hai, A gồm một và hai, B gồm ba và bốn. Tổng bốn số nên leftSize bằng hai. Lần thử đầu i bằng một và j bằng một. AL bằng một, AR bằng hai, BL bằng ba, BR bằng bốn. BL lớn hơn AR, nên cần dịch i sang phải. Lần tiếp theo i bằng hai và j bằng không. AL bằng hai, AR là dương vô cực, BL là âm vô cực và BR bằng ba. Điều kiện hợp lệ. Tổng chẵn nên lấy max trái là hai, min phải là ba, trung bình bằng hai phẩy năm.''',60,'trace','', 'official_2'),
sc('22-empty','08 / TEST CẠNH BIÊN','Nếu một mảng hoàn toàn rỗng?',[
 'A = []  B = [5]',
 'i=0, j=1; AL=−∞, AR=+∞',
 'Median = 5.0'],
 '''Hãy kiểm tra trường hợp được đề cho phép nhưng không xuất hiện trong hai ví dụ chính thức. Mảng A trống, mảng B chỉ có số năm. Tìm kiếm trên A chỉ có một lựa chọn: i bằng không. Tổng một số nên leftSize bằng một, j bằng một. Các giá trị AL và AR lần lượt là âm và dương vô cực. Đường cắt hợp lệ ngay, và max phía trái chính là năm. Mảng rỗng không đòi thêm một thuật toán khác; bốn giá trị biên đã xử lý tình huống đó. Đây là lợi ích của việc thiết kế điều kiện tổng quát.''',49,'edge'),
sc('23-duplicates','08 / TEST CẠNH BIÊN','Số trùng và số âm có phá thuật toán?',[
 'A = [2,2]  B = [2,2] → 2.0',
 'A = [−10⁶]  B = [10⁶] → 0.0',
 'Dùng ≤, không dùng < ở điều kiện hợp lệ.'],
 '''Bây giờ, nếu cả hai mảng có những giá trị bằng nhau thì sao? Ví dụ hai mảng đều chứa hai, hai. Đường cắt vẫn hợp lệ vì hai điều kiện dùng nhỏ hơn hoặc bằng, không phải nhỏ hơn nghiêm ngặt. Median bằng hai. Với giá trị âm cực tiểu và dương cực đại theo giới hạn đề, trung vị của hai số là không. Cả hai ví dụ này nhắc chúng ta: các phép so sánh phải phản ánh đúng tính chất cho phép bằng nhau, và phải xét số âm. Một bài test tốt tìm điểm dễ quên của giả thuyết.''',47,'edge'),
sc('24-pseudocode','09 / TRƯỚC KHI CODE','Pseudocode: cách suy nghĩ đã thành quy trình',[
 '1. Đưa mảng ngắn hơn thành A.',
 '2. Binary Search số phần tử trái i.',
 '3. j=leftSize−i; đọc AL, AR, BL, BR.',
 '4. Hợp lệ: tính median; sai: dịch trái/phải.'],
 '''Trước khi viết Python, chúng ta nói lại thuật toán bằng lời. Bước một, đảm bảo A là mảng ngắn hơn. Bước hai, tính số phần tử phải nằm ở phía trái và đặt khoảng tìm kiếm i từ không đến độ dài A. Bước ba, ở mỗi lần thử lấy i chính giữa, tính j rồi đọc bốn số biên với vô cực nếu cần. Bước bốn, nếu hai điều kiện chéo đều đúng, tính trung vị và dừng. Nếu AL lớn hơn BR, cắt A sang trái; ngược lại, cắt A sang phải. Quy trình này phải rõ trước khi code xuất hiện.''',51,'pseudocode'),
sc('25-python1','10 / PYTHON 3','Python: chọn mảng nhỏ và đặt đường cắt',[
 'if len(a) > len(b): a, b = b, a',
 'left_size = (m+n+1)//2',
 'lo, hi = 0, m',
 'i=(lo+hi)//2; j=left_size−i'],
 '''Bây giờ mới đến Python ba. Ta nhận hai mảng và đổi chỗ biến nếu mảng đầu dài hơn. Lấy m và n là độ dài của A và B. left_size bằng tổng cộng một rồi chia nguyên cho hai, cách này tự xử lý trường hợp tổng lẻ. Đặt lo bằng không, hi bằng m. Trong vòng lặp, i là trung điểm của khoảng tìm kiếm, j bằng left_size trừ i. Chúng ta không lặp trên từng phần tử; chúng ta chỉ thay đổi số phần tử đứng bên trái đường cắt. Mỗi biến trong code đều đã có ý nghĩa từ phần hình ảnh.''',52,'code1'),
sc('26-python2','10 / PYTHON 3','Python: kiểm tra biên và chọn hướng',[
 'AL≤BR và BL≤AR → return median',
 'AL>BR → hi=i−1',
 'Ngược lại → lo=i+1',
 'Các giá trị trống được thay bằng ±∞.'],
 '''Trong thân vòng lặp, bốn biến a_left, a_right, b_left, b_right chỉ là các phần tử ở sát đường cắt. Khi cắt ra ngoài biên, dùng vô cực tương ứng. Nếu a_left không vượt b_right và b_left không vượt a_right, ta đã tìm đúng vị trí. Nếu tổng lẻ, trả về max của hai giá trị trái. Nếu tổng chẵn, lấy trung bình giữa max trái và min phải. Nếu chưa hợp lệ, so a_left với b_right để biết cần dịch trái hay dịch phải. Không có một bước nào cần sao chép hay sort lại dữ liệu.''',55,'code2'),
sc('27-narrated-trace','10 / PYTHON 3','Trace mã: biến thay đổi ra sao?',[
 'official_2: (i,j) = (1,1) → BL>AR',
 'lo: 0 → 2',
 '(i,j) = (2,0) → VALID → 2.5'],
 '''Hãy tưởng tượng đang chạy trình gỡ lỗi tại ví dụ thứ hai. Ban đầu lo không, hi hai, i một, j một. Dòng kiểm tra chéo cho thấy BL bằng ba lớn hơn AR bằng hai. Nhánh dịch phải chạy, làm lo từ không thành hai. Vòng lặp tiếp theo tính i bằng hai, j bằng không. Chúng ta đọc AL hai, AR dương vô cực, BL âm vô cực, BR ba. Hai bất đẳng thức đều đúng. Đến dòng kiểm tra tổng chẵn, hàm trả về hai phẩy năm. Đó là một chuỗi trạng thái thật của code, không phải hoạt cảnh tưởng tượng.''',57,'code_trace','', 'official_2'),
sc('28-complexity','11 / ĐÁNH GIÁ','Vì sao đáp án đạt O(log(m+n))?',[
 'Tìm trên mảng ngắn hơn: O(log(min(m,n)+1))',
 'Mỗi lần kiểm tra bốn giá trị: O(1)',
 'Bộ nhớ phụ: O(1)',
 'Không duyệt, không tạo mảng mới.'],
 '''Giờ hãy đánh giá hiệu quả. Vì i chỉ nằm từ không đến độ dài của mảng ngắn hơn, mỗi phép so sánh loại bỏ khoảng một nửa lựa chọn, số vòng lặp tăng theo logarit độ dài mảng ngắn. Mỗi vòng chỉ đọc bốn giá trị và thực hiện một lượng tính toán cố định, nên thời gian là O của logarit min m n cộng một. Nó nằm trong yêu cầu O logarit m cộng n của đề. Bộ nhớ phụ chỉ gồm vài biến và bốn giá trị biên nên O của một. Đừng nhầm O logarit số phần tử với O logarit giá trị số nguyên.''',50,'complexity'),
sc('29-lessons','12 / BÀI HỌC CHUYỂN GIAO','Tư duy có thể dùng ngoài LeetCode',[
 'Tìm phần thông tin thật sự cần thiết.',
 'Đổi bài toán thành một điều kiện có thể kiểm tra.',
 'Khai thác dữ liệu đã có cấu trúc.',
 'Dùng phản ví dụ để sửa giả thuyết.'],
 '''Nhìn lại toàn bộ hành trình. Ban đầu chúng ta nghĩ phải gộp hai mảng, nhưng thực tế chỉ cần tìm biên giữa hai nửa. Chúng ta thay một tác vụ lớn bằng một điều kiện kiểm tra bốn số. Chúng ta tận dụng thứ tự có sẵn thay vì làm lại từ đầu. Và chúng ta dùng các trường hợp mảng rỗng, số trùng, tổng chẵn hay lẻ để kiểm chứng. Đây là những thói quen áp dụng được khi tìm dữ liệu trong hệ thống, chọn một ngưỡng phân chia hoặc tối ưu quy trình. Giá trị lớn nhất của tập này không nằm ở việc nhớ i hay j.''',49,'lessons'),
sc('30-practice','13 / BÀI TẬP LIÊN QUAN','Ba bài luyện cách nghĩ tiếp theo',[
 'LeetCode #35 — Search Insert Position',
 'LeetCode #34 — Find First and Last Position of Element',
 'LeetCode #378 — Kth Smallest Element in a Sorted Matrix'],
 '''Để luyện tiếp, hãy thử ba bài. Bài ba mươi lăm, Search Insert Position, giúp bạn nhận ra binary search có thể tìm vị trí chèn chứ không chỉ tìm giá trị. Bài ba mươi bốn, Find First and Last Position of Element, luyện cách xác định ranh giới đúng khi có giá trị trùng. Bài ba trăm bảy mươi tám, Kth Smallest Element in a Sorted Matrix, mở rộng tư duy tìm phần tử theo thứ hạng mà không cần sort toàn bộ. Với mỗi bài, hãy tự đặt câu hỏi: điều kiện nào là đúng, và một phép kiểm tra cho phép loại bỏ những lựa chọn nào?''',54,'practice'),
sc('31-outro','KIEU STUDIO / THE ART OF CODING','Đừng nhớ code. Hãy nhớ cách tìm đường đi.',[
 'UNDERSTAND → HYPOTHESIZE → TEST → REFLECT',
 'Bài tập là công cụ, tư duy là kỹ năng mang theo.'],
 '''Kết thúc bài số bốn, ta đã biến một bài Hard thành một chuỗi câu hỏi nhỏ và kiểm chứng được. Nếu lần sau bạn quên code Python, điều đó không sao; hãy thử vẽ hai đường cắt, đặt bốn số ở biên, tự chứng minh điều kiện hợp lệ rồi viết lại. Đó là học để giải quyết vấn đề thật, chứ không phải thuộc lòng câu trả lời. Cảm ơn bạn đã học cùng Kieu Studio. Hẹn gặp ở bài thực hành tiếp theo của The Art of Coding.''',44,'outro'),
]
