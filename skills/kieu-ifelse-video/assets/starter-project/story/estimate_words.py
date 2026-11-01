#!/usr/bin/env python3
"""Draft timeline before the real voice exists: 0.235 s per syllable plus pauses, then 1.1x."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; SPEED = 1.1
text = (ROOT / 'input/script.txt').read_text(encoding='utf-8').strip(); t, out = 0.3, []
for tok in text.split():
    n = len(re.findall(r'[^\W\d_]+|\d+', tok)); d = 0.235 * n / SPEED
    out.append({'word': tok, 'start': round(t, 3), 'end': round(t + d, 3)}); t += d
    t += 0.45 if tok.endswith('...') else 0.32 if tok[-1] in '.!?' else 0.1 if tok[-1] in ',:' else 0.02
(ROOT / 'timeline').mkdir(exist_ok=True); (ROOT / 'timeline/words.json').write_text(json.dumps({'words': out}, ensure_ascii=False))
p = ROOT / 'config.json'; cfg = json.loads(p.read_text(encoding='utf-8')); cfg['duration'] = round(t + 2.5, 2)
p.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding='utf-8'); print('estimated', cfg['duration'])
