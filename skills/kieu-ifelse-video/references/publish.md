# Publishing for @NeuNhuPhim

Channel id `UC5XjxC7YXhtemY1c7njkCGA`. Follow `skills/kieu-github-video/references/youtube-publish.md` for the Chrome bridge (10 MB per `file_upload`, collector input, Riêng tư before Lưu). Each step needs the owner's request: upload means Private, public and playlists are separate. Never enter the owner's phone number or credentials.

## Differences from GitHub Radar
- **Upload:** split into 9 MB parts. A 144 MB file is 16 parts. Sort `window.__parts` by name and compare size and SHA-256 with the original in the browser before handing the file to Studio.
- **Filename** becomes the draft title, so use an ASCII name, then set title and description with `document.execCommand('insertText', ...)`.
- **Metadata:** from `YOUTUBE_METADATA.md`. Set video language to Tiếng Việt before adding captions.
- **Captions:** Các thành phần của video → Phụ đề → Thêm → Tải tệp lên → the dialog exposes `#captions-file-loader`. `file_upload` into it directly, do not click Tiếp tục, then Xong.
- **Thumbnail:** Studio silently drops a custom thumbnail while the channel is not phone-verified, and no error appears. The owner verifies at https://www.youtube.com/verify. Afterwards use `#file-loader` on the video's edit page.
- **Disclosure:** confirm `VIDEO_MADE_FOR_KIDS_NOT_MFK` and `VIDEO_HAS_ALTERED_CONTENT_YES` on the edit page after saving.

## Channel branding
Studio: `.../editing/profile`, one page for banner, picture and description, then Xuất bản. After publishing, the page may still block navigation with a "Leave site?" dialog even though Hủy and Xuất bản are greyed out; close the tab and verify on the public channel page.

Render with `assets/brand/brand.js` in a 1440p project, then check before uploading:
- **Banner 2560×1440:** phones keep only the middle 1546×423 (x 507-2053, y 508-932). Title, diacritics and figures all stay inside, and figures stand on the ridge, not in the sky.
- **Logo 800×800:** crop the centre 1440×1440. YouTube cuts it to a circle and shows it at 48-98 px, so preview it masked at those sizes.
