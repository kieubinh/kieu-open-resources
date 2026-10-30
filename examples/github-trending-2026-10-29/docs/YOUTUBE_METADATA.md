# YouTube metadata (uploaded 2026-10-30 as Private, then set Public by the owner request the same day)

Thumbnails: `npx remotion still src/thumb-index.ts Thumb out.png --props=...` (see `src/thumb.tsx`). Set visibility to Public only after listening to the audio, re-checking the star numbers on the publish date, and editorial approval.

Upload settings used in YouTube Studio: not made for kids, no age restriction, **altered or synthetic content = Yes** (AI voice and avatar), visibility Private. Studio defaults the visibility radio to Public, so select Private before saving.

Playlist (Public, oldest first, Vietnamese): **GitHub Radar · Tiếng Việt** with GR01, GR02, GR03; Studio: https://studio.youtube.com/playlist/PLKlBjj04ymF4/videos. Add each new episode and its Short to it.

## GR01 · https://youtu.be/WAJluVd6cq0 (Public since 2026-10-30)
**Title:** AI báo 20 lỗ hổng: bao nhiêu cái là thật? Skill bảo mật của Cloudflare | GitHub Radar #1

**Tags:** github radar, security audit skill, cloudflare, ai agent, coding agent, claude code, bảo mật, lỗ hổng bảo mật, github trending, kieu studio

**Description:**

```
Bạn nhờ AI agent tìm lỗ hổng bảo mật, vài phút sau nó trả về hai mươi phát hiện, cái nào cũng trông rất thuyết phục. Vậy bao nhiêu cái là thật? Cloudflare có một câu trả lời: security-audit-skill, bắt mỗi phát hiện phải tự chứng minh mình.

Trong video (GitHub Radar, mỗi tập chỉ một repo):
• Con số tăng trưởng: hơn 52 nghìn sao, gấp 2,2 lần trong 30 ngày (theo GitHub Trending)
• Vì sao Cloudflare làm ra nó, và bài toán agent vừa tìm vừa tự chấm bài của chính mình
• Cách hoạt động: sáu giai đoạn, người săn lỗi và người kiểm tách biệt
• Cách dùng, cái giá (token, sandbox) và bốn ý tưởng ứng dụng

⏱ Chương
0:00 Mở đầu: AI báo 20 lỗ hổng, bao nhiêu là thật?
0:32 Con số tăng trưởng
1:05 Vì sao Cloudflare làm ra nó
1:35 Bài toán cụ thể
2:06 Cách hoạt động
2:36 Cách sử dụng
3:06 Cái được và cái giá
3:32 Bốn ý tưởng ứng dụng
4:00 Tóm lại

🔗 Liên kết
Repo: https://github.com/cloudflare/security-audit-skill
Bài viết của Cloudflare: https://blog.cloudflare.com/build-your-own-vulnerability-harness
Kieu Studio: https://kieu.app

⚠ Cần cân nhắc: nhiều agent nghĩa là tốn token; bước build hoặc chạy mã cần sandbox do hệ điều hành thực thi; chỉ quét mã bạn được phép kiểm tra.

📊 Nguồn số liệu: tổng sao lấy từ GitHub API, mức tăng từ trang GitHub Trending, chụp ngày 29/10/2026. Số sao đo sự chú ý, không đo chất lượng; hãy kiểm tra lại trước khi cài.
🤖 Công khai: giọng đọc và avatar trong video do AI tạo (VoiceStudio chạy trên máy, Narrator 03). Hình minh hoạ do Kieu Studio vẽ.

#GitHubRadar #AIAgent #SecurityAudit #Cloudflare #KieuStudio
```

## GR02 · https://youtu.be/TvnWZfB09Oo (Public since 2026-10-30)
**Title:** Trang web do AI làm sao cứ giống nhau? Impeccable trị thế nào | GitHub Radar #2

**Tags:** github radar, impeccable, paul bakaus, ai slop, thiết kế giao diện, web design, ai agent, coding agent, claude code, github trending, kieu studio

**Description:**

```
Bạn đã bao giờ nhìn một trang web do AI làm và nghĩ: mình thấy cái này ở đâu rồi? Font giống nhau, gradient tím xanh giống nhau, thẻ nằm trong thẻ. Impeccable của Paul Bakaus cho agent một bộ từ vựng thiết kế để chỉ đạo, đánh giá và phát hiện những mẫu đó.

Trong video (GitHub Radar, mỗi tập chỉ một repo):
• Con số tăng trưởng: gần 95 nghìn sao, thêm hơn 26% trong 30 ngày, tốc độ tuần qua gần gấp đôi (theo GitHub Trending)
• Năm dấu hiệu của giao diện "AI slop" và vì sao lệnh "làm cho nổi bật hơn" quá mơ hồ
• Cách hoạt động: ngữ cảnh, 24 lệnh có tên, 62 quy tắc phát hiện không cần LLM
• Cách dùng, cái giá (hook, telemetry) và bốn ý tưởng ứng dụng

⏱ Chương
0:00 Mở đầu: trang này mình thấy ở đâu rồi?
0:35 Con số tăng trưởng
1:03 Vì sao tác giả làm ra nó
1:28 Bài toán cụ thể
1:58 Cách hoạt động
2:32 Cách sử dụng
3:01 Cái được và cái giá
3:32 Bốn ý tưởng ứng dụng
4:00 Tóm lại

🔗 Liên kết
Repo: https://github.com/pbakaus/impeccable
Tài liệu: https://impeccable.style/docs
Kieu Studio: https://kieu.app

⚠ Cần cân nhắc: trong Claude Code, hook đã cài vẫn chạy ngay cả khi bạn từ chối lệnh của model, hãy xem hook trước khi chạy không giám sát; có telemetry ẩn danh, tắt được bằng lệnh hoặc biến môi trường.

📊 Nguồn số liệu: tổng sao lấy từ GitHub API, mức tăng từ trang GitHub Trending, chụp ngày 29/10/2026. Số sao đo sự chú ý, không đo chất lượng; hãy kiểm tra lại trước khi cài.
🤖 Công khai: giọng đọc và avatar trong video do AI tạo (VoiceStudio chạy trên máy, Narrator 03). Hình minh hoạ do Kieu Studio vẽ.

#GitHubRadar #Impeccable #AIAgent #WebDesign #KieuStudio
```

## GR03 · https://youtu.be/9XZYEgfhKl4 (Public since 2026-10-30)
**Title:** Agent quên sạch mỗi sáng? claude-mem cho AI trí nhớ bền vững | GitHub Radar #3

**Tags:** github radar, claude-mem, claude code, trí nhớ ai, ai agent, coding agent, mcp, github trending, kieu studio

**Description:**

```
Sáng nay bạn mở lại dự án và bảo agent: tiếp tục việc hôm qua. Nó hỏi lại: dự án này cấu trúc thế nào? Claude-mem tự ghi lại những gì agent làm trong mỗi phiên và đưa đúng phần cần thiết trở lại phiên sau, để bạn không phải giải thích lần thứ mười.

Trong video (GitHub Radar, mỗi tập chỉ một repo):
• Con số tăng trưởng: hơn 104 nghìn sao, thêm khoảng 10% trong 30 ngày (theo GitHub Trending)
• Vì sao mỗi phiên mới là một trang giấy trắng, và cách nhớ mà không đốt token (tiết lộ dần)
• Cách hoạt động: hook vòng đời, worker cục bộ, SQLite và Chroma, ba công cụ MCP
• Cách dùng, cái giá (dữ liệu được ghi lại) và bốn ý tưởng ứng dụng

⏱ Chương
0:00 Mở đầu: hôm qua chúng ta làm gì nhỉ?
0:31 Con số tăng trưởng
1:03 Vì sao tác giả làm ra nó
1:29 Bài toán cụ thể
1:57 Cách hoạt động
2:28 Cách sử dụng
2:59 Cái được và cái giá
3:22 Bốn ý tưởng ứng dụng
3:47 Tóm lại

🔗 Liên kết
Repo: https://github.com/thedotmack/claude-mem
Tài liệu: https://docs.claude-mem.ai/
Kieu Studio: https://kieu.app

⚠ Cần cân nhắc: hook ghi lại hoạt động công cụ của agent, hãy xem dữ liệu nào được lưu, lưu ở đâu, có đồng bộ đám mây không; trình cài có thể mời đăng nhập (bỏ qua được); dùng thẻ private cho phần nhạy cảm.

📊 Nguồn số liệu: tổng sao lấy từ GitHub API, mức tăng từ trang GitHub Trending, chụp ngày 29/10/2026. Số sao đo sự chú ý, không đo chất lượng; hãy kiểm tra lại trước khi cài.
🤖 Công khai: giọng đọc và avatar trong video do AI tạo (VoiceStudio chạy trên máy, Narrator 03). Hình minh hoạ do Kieu Studio vẽ.

#GitHubRadar #ClaudeMem #ClaudeCode #AIAgent #KieuStudio
```
