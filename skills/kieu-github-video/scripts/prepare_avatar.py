#!/usr/bin/env python3
"""Prepare the circular presenter avatar image for a Kieu video project (not committed to git).

Usage:
  python3 prepare_avatar.py --project <episode dir> [--image <portrait.png>] [--crop x,y,size]

Image resolution order: --image, $KIEU_AVATAR_IMAGE, then the approved Kieu Studio avatar at
<kieu-studio repo>/studio/assets/avatar_source.png (found via $KIEU_STUDIO_REPO or the sibling checkout).
The result is written to <project>/public/brand/kieu-avatar.png as a square 512x512 crop. The image is
git-ignored: a portrait of the founder must not be pushed to the public resources repository.

Also writes public/brand/kieu-avatar-nomouth.png (the mouth area replaced by feathered skin) and
src/avatar.mouth.json (mouth anchor: coordinates only) so the video can draw a lip-synced mouth over the face.
For a custom --image pass --mouth cx,cy,width[,tilt_deg] in the 512x512 crop (omit it to skip lip-sync).

Replace the approved stylised avatar with a likeness of Anthony Kieu by passing --image with an image he
supplied or approved; the face is cropped to a square around the head (use --crop to override).
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

APPROVED_RELATIVE = Path('studio/assets/avatar_source.png')
# Head box for the approved 1122x1402 source; scaled proportionally for other sizes.
DEFAULT_CROP = (0.294, 0.00, 0.392)  # left, top (fractions of width / height) and size (fraction of width)


# Mouth anchor of the approved avatar in its 512x512 head crop (cx, cy, mouth width, tilt in degrees).
APPROVED_MOUTH = (268, 405, 86, -4.0)


def _avg(px, x0: int, y0: int, x1: int, y1: int):
    n = (x1 - x0) * (y1 - y0)
    return tuple(sum(px[x, y][k] for x in range(x0, x1) for y in range(y0, y1)) / n for k in range(3))


def _make_mouthless_box(im: Image.Image, cx: int, cy: int, width: int) -> Image.Image:
    """Fallback without OpenCV: replace the lips/teeth with smooth skin interpolated row by row between the cheek skin on the left and right
    of the mouth (averaged over small windows), feathered into the face, so a drawn mouth can animate on top."""
    rx, ry = round(width * 0.86), round(width * 0.4)
    x0, y0 = cx - rx, cy + 2 - ry; w, h = 2 * rx, 2 * ry   # a rounded box a little low: stay clear of the nostrils
    px = im.load()
    left = [_avg(px, x0 - 9, y0 + j - 3, x0 - 3, y0 + j + 4) for j in range(h)]
    right = [_avg(px, x0 + w + 3, y0 + j - 3, x0 + w + 9, y0 + j + 4) for j in range(h)]
    patch = Image.new('RGB', (w, h)); d = patch.load()
    for j in range(h):
        for i in range(w):
            f = i / (w - 1)
            d[i, j] = tuple(round(left[j][k] + (right[j][k] - left[j][k]) * f) for k in range(3))
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((7, 6, w - 7, h - 6), radius=20, fill=255)
    out = im.copy(); out.paste(patch.filter(ImageFilter.GaussianBlur(3)), (x0, y0), mask.filter(ImageFilter.GaussianBlur(5)))
    return out


def make_mouthless(im: Image.Image, cx: int, cy: int, width: int) -> Image.Image:
    """Remove lips/teeth by OpenCV inpainting the pixels that differ from the surrounding skin (falls back to a skin
    patch when OpenCV/numpy are missing), so a drawn mouth can animate on top."""
    try:
        import cv2, numpy as np
    except ImportError:
        return _make_mouthless_box(im, cx, cy, width)
    arr = np.array(im.convert('RGB'))[:, :, ::-1].copy()
    rx, ry = round(width * 0.7), round(width * 0.4)
    x0, y0, x1, y1 = cx - rx, cy - ry + 2, cx + rx, cy + ry + 2
    roi = arr[y0:y1, x0:x1].astype(float)
    ring = np.concatenate([roi[0], roi[-1], roi[:, 0], roi[:, -1]]); ref = np.median(ring, axis=0)
    mask = (np.linalg.norm(roi - ref, axis=2) > 20).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    mask = cv2.dilate(mask, np.ones((7, 7), np.uint8), iterations=2)
    full = np.zeros(arr.shape[:2], np.uint8); full[y0:y1, x0:x1] = mask
    out = cv2.inpaint(arr, full, 7, cv2.INPAINT_TELEA)
    soft = (cv2.GaussianBlur(full, (0, 0), 5) / 255.0)[..., None]
    out = (out * (1 - 0.8 * soft) + cv2.GaussianBlur(out, (0, 0), 4) * 0.8 * soft).astype(np.uint8)
    return Image.fromarray(out[:, :, ::-1])


def find_default() -> Path | None:
    env = os.environ.get('KIEU_STUDIO_REPO')
    here = Path(__file__).resolve()
    roots = [Path(env)] if env else []
    roots += [p / 'kieu-studio' for p in here.parents] + [p.parent / 'kieu-studio' for p in here.parents]
    for r in roots:
        if (r / APPROVED_RELATIVE).is_file():
            return r / APPROVED_RELATIVE
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--image')
    ap.add_argument('--crop', help='x,y,size in source pixels')
    ap.add_argument('--mouth', help='cx,cy,width[,tilt_deg] of the mouth in the 512x512 crop (custom images only)')
    args = ap.parse_args()
    src = Path(args.image or os.environ.get('KIEU_AVATAR_IMAGE', '') or find_default() or '')
    if not src.is_file():
        raise SystemExit('No avatar image. Pass --image, set KIEU_AVATAR_IMAGE, or check out kieu-studio next to this repo.')
    im = Image.open(src).convert('RGB')
    w, h = im.size
    if args.crop:
        x, y, s = [int(v) for v in args.crop.split(',')]
    elif abs(w / h - 1) > 0.05:  # portrait/landscape source: crop the head; square sources are used whole
        x, y, s = round(DEFAULT_CROP[0] * w), round(DEFAULT_CROP[1] * h), round(DEFAULT_CROP[2] * w)
    else:
        x, y, s = 0, 0, min(w, h)
    s = min(s, w - x, h - y)
    out = Path(args.project) / 'public' / 'brand' / 'kieu-avatar.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    head = im.crop((x, y, x + s, y + s)).resize((512, 512), Image.LANCZOS)
    head.save(out)
    print(f'avatar -> {out} (crop {x},{y},{s} from {src.name}, {w}x{h})')
    anchor = None
    if args.mouth:
        v = [float(n) for n in args.mouth.split(',')]; anchor = (v[0], v[1], v[2], v[3] if len(v) > 3 else 0.0)
    elif not (args.image or os.environ.get('KIEU_AVATAR_IMAGE')):
        anchor = APPROVED_MOUTH   # only valid for the approved avatar
    if anchor:
        make_mouthless(head, int(anchor[0]), int(anchor[1]), int(anchor[2])).save(out.with_name('kieu-avatar-nomouth.png'))
        (Path(args.project) / 'src').mkdir(exist_ok=True)
        (Path(args.project) / 'src' / 'avatar.mouth.json').write_text(json.dumps(dict(cx=anchor[0], cy=anchor[1], width=anchor[2], tilt=anchor[3])))
        print('lip-sync: mouthless face + mouth anchor written')
    else:
        print('lip-sync: skipped (custom image without --mouth cx,cy,width)')


if __name__ == '__main__':
    sys.exit(main())
