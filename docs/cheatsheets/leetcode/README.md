# Cheatsheet LeetCode — một trang cho mỗi video

Tài liệu miễn phí của Kieu Studio đi kèm các video giải LeetCode bằng tiếng Việt. Mỗi file là một trang A4: hình minh hoạ, cách làm, code Python 3, độ phức tạp, bẫy hay gặp và bài luyện tiếp.

| Bài | PDF | Video |
|---|---|---|
| #44 Wildcard Matching | [Tải PDF](Kieu-Studio_LeetCode-44_Wildcard-Matching_cheatsheet.pdf) | [youtu.be/s44HW8mGVzU](https://youtu.be/s44HW8mGVzU) |
| #10 Regular Expression Matching | [Tải PDF](Kieu-Studio_LeetCode-10_Regular-Expression-Matching_cheatsheet.pdf) | [youtu.be/jw15lSSuizM](https://youtu.be/jw15lSSuizM) |
| #4 Median of Two Sorted Arrays | [Tải PDF](Kieu-Studio_LeetCode-4_Median-of-Two-Sorted-Arrays_cheatsheet.pdf) | [youtu.be/mQ2V4bk37IM](https://youtu.be/mQ2V4bk37IM) |

## Kiểm chứng

Code in trên mỗi trang được chạy với các ví dụ chính thức của đề trước khi xuất PDF. Số liệu trong hình lấy từ việc chạy thuật toán thật. Ví dụ `"aab"` / `"c*a*b"` (#10) và hai mảng `[1,3,8,9]` / `[2,4,5,7]` (#4) là ví dụ minh hoạ của Kieu Studio, không phải ví dụ chính thức.

## Dựng lại

```sh
python3 examples/leetcode-cheatsheets/build.py
```

Cần Google Chrome (xuất PDF). HTML gốc nằm trong `examples/<video>/cheatsheet/`.

Đề bài thuộc về LeetCode ([leetcode.com](https://leetcode.com)). Hình, giải thích và code của Kieu Studio được phát hành theo giấy phép MIT của repo này.
