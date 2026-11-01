#!/usr/bin/env python3
"""Apply the local fixes this channel needs to an installed 2D Studio kit. Re-run after every kit update.

Usage: patch_kit.py --studio DIR [--check]
The kit is not part of this repository. Fixes: worried and angry brow slopes were swapped; the subscribe badge ignored
the project language.
"""
import argparse, re, sys
from pathlib import Path

BROW = re.compile(r"(if \(ex\.brows === 'worried'\) \{ brow\(eyeX\[0\], )(-?)(r \* 0\.06\); brow\(eyeX\[1\], )(-?)(r \* 0\.06\); \})")
ANGRY = re.compile(r"(if \(ex\.brows === 'angry'\) \{ brow\(eyeX\[0\], )(-?)(r \* 0\.08\); brow\(eyeX\[1\], )(-?)(r \* 0\.08\); \})")
SUB = "'Subscribe'"; SUB_VI = "(E.cfg.lang === 'vi' ? 'Đăng ký' : 'Subscribe')"


def fix_rig(s):
    s = BROW.sub(lambda m: m[1] + m[3] + '-' + m[5], s)
    return ANGRY.sub(lambda m: m[1] + '-' + m[3] + m[5], s)


def fix_ui(s):
    return s if SUB_VI in s else s.replace(SUB, SUB_VI)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--studio', required=True); ap.add_argument('--check', action='store_true'); a = ap.parse_args()
    root = Path(a.studio); todo = 0
    for rel, fn in (('engine/rig2d.js', fix_rig), ('engine/ui2d.js', fix_ui)):
        p = root / rel; old = p.read_text(encoding='utf-8'); new = fn(old)
        if old == new: print('ok', rel); continue
        todo += 1
        if a.check: print('needs patch', rel)
        else: p.write_text(new, encoding='utf-8'); print('patched', rel)
    if a.check and todo: sys.exit(1)


if __name__ == '__main__':
    main()
