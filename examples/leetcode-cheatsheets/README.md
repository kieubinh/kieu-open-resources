# Cheatsheet một trang cho video LeetCode

Mỗi video có một PDF A4 một trang (hình minh hoạ, cách làm, code Python 3, độ phức tạp, bẫy hay gặp, bài luyện tiếp). PDF nằm ở [`docs/cheatsheets/leetcode/`](../../docs/cheatsheets/leetcode/); bản HTML gốc nằm trong `examples/<video>/cheatsheet/`.

Dựng lại cả ba (cần Google Chrome):

```sh
python3 examples/leetcode-cheatsheets/build.py
```

`build.py` chạy code in trên trang với các ví dụ của đề, vẽ hình từ kết quả chạy thật của thuật toán, chọn cỡ chữ lớn nhất còn vừa một trang, và báo lỗi nếu nội dung chạm chân trang hoặc PDF quá một trang.
