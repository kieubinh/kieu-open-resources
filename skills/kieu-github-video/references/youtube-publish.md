# Publishing GitHub Radar videos to YouTube (only when the owner asks)

Worked out on 2026-10-30 for GR01-GR03 (channel KIEU STUDIO, Studio in Vietnamese). Nothing here is automatic: uploading,
making public and creating playlists each need the owner's request in chat. A request to "upload" means **Private**;
"công khai" is a separate, explicit go-ahead.

## 1. Metadata per video

**Title** (<= 100 chars): hook question + what fixes it + series tag, e.g. `AI báo 20 lỗ hổng: bao nhiêu cái là thật? Skill bảo mật của Cloudflare | GitHub Radar #1`. The question is the same hook as the cold open; never promise what the video does not show.

**Description** (< 5000 chars, no `<` `>`), in this order:
1. 2-3 sentence hook (the cold open, then the repo and one-line promise).
2. `Trong video (GitHub Radar, mỗi tập chỉ một repo):` + 4 bullets (growth, why/problem, how, usage + cost + ideas).
3. `⏱ Chương` from the real WAV timeline: `KIEU_EPISODE=gr01 python3 skills/kieu-github-video/scripts/youtube_chapters.py --project <ep> --first "Mở đầu: <hook>"` (first chapter at 0:00, >= 3 chapters, >= 10 s each).
4. `🔗 Liên kết`: repo, author's docs/blog, `https://kieu.app`.
5. `⚠ Cần cân nhắc:` the same caveat as the `value` scene.
6. `📊 Nguồn số liệu:` totals from the GitHub API, gains from GitHub Trending, snapshot date, "số sao đo sự chú ý, không đo chất lượng".
7. `🤖 Công khai:` voice and avatar are AI generated (local VoiceStudio, Narrator 03); illustrations drawn by Kieu Studio.
8. 3-5 hashtags last (`#GitHubRadar #AIAgent #<Topic> #KieuStudio`); YouTube shows the first three above the title.

**Tags**: 9-11 lowercase phrases (series, repo, owner, topic, `ai agent`, `github trending`, `kieu studio`), under 500 chars. Commit the last tag with a trailing comma.

Keep the text in `docs/YOUTUBE_METADATA.md` (title, tags, description, video link, visibility) so the next episode copies it.

## 2. Thumbnail (1280x720, < 2 MB PNG)
`assets/thumb.tsx` + `assets/thumb-index.ts` (copy to `src/`): a separate Remotion entry that does not touch `root.tsx`.
```bash
npx remotion still src/thumb-index.ts Thumb out.png --props='{"l1":"AI BÁO","l2":"20 LỖ HỔNG","l3":"THẬT HAY GIẢ?","col":"#57ecd0","repo":"cloudflare/security-audit-skill","stars":"52.530","chip":"×2,2 trong 30 ngày","icon":"shield","badge":"GITHUB RADAR · TẬP 1"}'
```
Recipe that worked: 2-3 huge lines (<= 14 chars each, first white, second in the episode colour, auto-fit), badge `GITHUB RADAR · TẬP N` top-left, the circular avatar with a coloured ring and glow right, a star-count chip (real numbers from the manifest) under it, a topic icon badge, repo pill bottom-left. Colours: teal `#57ecd0`, amber `#ffcc73`, blue `#76aaff`. Always look at the PNG: no line may touch the avatar ring (keep `fit` width <= 700). The thumbnail uses the approved avatar from `public/brand/` (never commit it) and only numbers that appear in the video.

## 3. Upload in Studio with the Claude-in-Chrome bridge
`file_upload` accepts at most **10 MB per call, summed across a batch**, so a 35-40 MB MP4 goes in pieces, one `file_upload` call per piece (not in a batch):
1. `scripts/split_for_upload.sh <video.mp4> <scratch>/chunks p1` (9 MB parts, verifies reassembly).
2. Open `https://studio.youtube.com/channel/<id>/videos/upload?d=ud` (the upload dialog). Run JS to add a collector input, then find its ref (it is the file input that is *not* the dialog's):
   ```js
   window.__parts = []; const i = document.createElement('input'); i.type = 'file'; i.id = '__chunk_in';
   i.style.cssText = 'position:fixed;left:0;top:0;width:10px;height:10px;opacity:0.01;z-index:99999';
   document.body.appendChild(i); i.onchange = () => { if (i.files[0]) window.__parts.push(i.files[0]); };
   ```
3. `find` the file inputs, `file_upload` part a, b, c ... into the collector one call each (do not navigate the page in between).
4. Check names and the summed size equal the original, then hand the file to Studio's own input:
   ```js
   const f = new File(window.__parts, 'GR01_github_radar_<repo>.mp4', {type: 'video/mp4'});
   const inp = [...document.querySelectorAll('input[type=file]')].find(x => x.id !== '__chunk_in');
   const dt = new DataTransfer(); dt.items.add(f); inp.files = dt.files; inp.dispatchEvent(new Event('change', {bubbles: true}));
   ```
5. In the details step: click the title box, `cmd+a`, type the title; click the description and type it (emoji and newlines work with the `type` action); upload the thumbnail into the thumbnail file input with `file_upload`; radio "Không, nội dung này không dành cho trẻ em"; "Hiện thêm" then **"Có, đã dùng AI"** for altered/synthetic content (voice + avatar), tags box. Verify with JS: `[...document.querySelectorAll('tp-yt-paper-radio-button')].filter(x=>x.getAttribute('aria-checked')==='true').map(x=>x.getAttribute('name'))` should list `VIDEO_MADE_FOR_KIDS_NOT_MFK`, `VIDEO_HAS_ALTERED_CONTENT_YES`.
6. Next x3 to the visibility step. **Studio pre-selects Công khai there**: click Riêng tư first (screenshot to confirm), then Lưu. Never click Xuất bản unless the owner said to publish.
7. Do the next video from a fresh `.../upload?d=ud` navigation (new collector input, new refs).

Do not use a localhost HTTP server for the bytes: Chrome's local-network permission prompt blocks the page's `fetch` until a human allows it.

## 4. Make public, then playlist (separate go-aheads)
- Public: open `https://studio.youtube.com/video/<id>/edit`, click the visibility button, Công khai (leave "Đặt ở chế độ Công chiếu ngay" unchecked), Xong, Lưu. Read the video id from the list (`a[href*="/video/"]`); `I`/`l` look alike in screenshots, so take it from the DOM.
- Playlist: Nội dung -> Danh sách phát -> Tạo -> Danh sách phát mới. Name `GitHub Radar · Tiếng Việt` (same pattern as `Problem Solving · Tiếng Việt`), description (what the series is + the episodes + the data-date and AI disclosure), visibility Công khai, order **Ngày xuất bản (cũ nhất)**, language **Tiếng Việt** (typing in the language box picks the wrong language; open the list and click the option). Create, then Thêm video -> Chọn video hiện có -> search `GitHub Radar` -> tick the videos -> Xong. Add every later episode and Short to the same playlist.
- Studio deep links (`/playlists`) can show an error page on first load; go through the Nội dung tab instead.

## 5. After publishing
Say in the reply which numbers were not re-checked on the publish date and that the audio was not listened to by the agent. Record links in `docs/YOUTUBE_METADATA.md`.
