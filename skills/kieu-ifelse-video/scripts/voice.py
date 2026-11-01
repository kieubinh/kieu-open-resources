#!/usr/bin/env python3
"""Local VoiceStudio narration with a blind check on every take (no fallback engine, resumable).

VoiceStudio can clip the last word of a take or add a stray syllable, and alignment against the script hides both.
A take passes only when ASR without any script prompt (whole take plus short windows) covers every scripted word, the
last two words are heard in the tail alone, and no short stray burst ends the take. Failing takes are re-read with new
seeds and the best one is kept. Old takes move to audio/chunks_v1. Run with the studio venv (numpy, faster-whisper).

Usage: voice.py --episode DIR --plan                 split docs/script.txt into audio/voice_ledger.json, edit it freely
       voice.py --episode DIR [--max-takes N] [--seed N] [--score-only] [name ...]
Report: audio/voice_qc.json. Settings: DIR/episode.json ("voice", "say").
"""
import argparse, difflib, hashlib, json, os, re, shutil, sys, tempfile, time, unicodedata, urllib.error, urllib.request, wave
from pathlib import Path

BASE = 'http://127.0.0.1:3900'
ONES = 'không một hai ba bốn năm sáu bảy tám chín'.split()
EXEMPT = {'nét', 'mi', 'crô', 'lu', 'ri', 'a', 'sê', 'rê', 'sép', 'xki', 'pi', 'ki', 'lô', 'mét'}   # names and loanwords ASR spells its own way


def chunks(text):
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s.strip()]
    out, cur = [], ''
    for s in sents:
        if cur and len(cur) + len(s) > 125:
            out.append(cur); cur = s
        else:
            cur = (cur + ' ' + s).strip()
        if len(cur) >= 85:
            out.append(cur); cur = ''
    if cur: out.append(cur)
    return out


def spoken(t, say):
    for a, b in say.items(): t = t.replace(a, b)
    return t


def api(path, payload=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload, ensure_ascii=False).encode() if payload else None,
                                 headers={'Content-Type': 'application/json'}, method='POST' if payload else 'GET')
    for attempt in range(5000):   # the local server answers 429/503 while another job holds it: wait, never switch engine
        try:
            with urllib.request.urlopen(req, timeout=1800) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or attempt == 4999: raise
            print(f'busy {e.code}, retry in 30 s', flush=True); time.sleep(30)


def below_1000(n, full=False):
    h, t, u = n // 100, n // 10 % 10, n % 10; out = []
    if h or full: out += [ONES[h], 'trăm']
    if t == 0 and u and (h or full): out.append('lẻ')
    if t == 1: out.append('mười')
    elif t: out += [ONES[t], 'mươi']
    if u: out.append('lăm' if u == 5 and t else ONES[u])
    return out


def read_number(n):
    if n == 0: return 'không'
    th, rest = n // 1000, n % 1000; out = []
    if th: out += below_1000(th) + ['nghìn']
    if rest or not th: out += below_1000(rest, full=bool(th))
    return ' '.join(out)


def toks(s):
    s = re.sub(r'(?<=\d)\s*[.,]\s*(?=\d{3}\b)', '', s.lower().replace('-', ' '))
    s = s.replace('%', ' phần trăm ')
    s = re.sub(r'\bkm\b', 'ki lô mét', s)
    s = re.sub(r'\d+', lambda m: ' ' + read_number(int(m.group())) + ' ', s)
    return re.findall(r'[\wÀ-ỹ]+', s)


def key(t):
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    for a, b in (('ngh', 'ng'), ('gh', 'g'), ('tr', 'ch'), ('gi', 'd'), ('qu', 'c')):
        if t.startswith(a): t = b + t[len(a):]
    return {'s': 'x', 'r': 'd', 'k': 'c'}.get(t[:1], t[:1]) + t[1:]


def same(a, b):
    a, b = key(a), key(b)
    return a == b or (min(len(a), len(b)) >= 3 and difflib.SequenceMatcher(a=a, b=b).ratio() >= 0.6)


def covered(want, heard):
    """Fuzzy longest common subsequence; returns the set of indices in want that were heard."""
    n, m = len(want), len(heard); T = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            T[i][j] = max(T[i + 1][j], T[i][j + 1], T[i + 1][j + 1] + 1 if same(want[i], heard[j]) else 0)
    i, j, got = 0, 0, set()
    while i < n and j < m:
        if same(want[i], heard[j]) and T[i][j] == T[i + 1][j + 1] + 1: got.add(i); i += 1; j += 1
        elif T[i + 1][j] >= T[i][j + 1]: i += 1
        else: j += 1
    return got


def load(p):
    import numpy as np
    with wave.open(str(p)) as w:
        sr, ch = w.getframerate(), w.getnchannels(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return sr, x.reshape(-1, ch).mean(1) if ch > 1 else x


def hear(model, sr, x):
    import numpy as np
    f = tempfile.mktemp(suffix='.wav')
    with wave.open(f, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    s, _ = model.transcribe(f, language='vi', beam_size=5, condition_on_previous_text=False, vad_filter=False, temperature=0)
    t = ' '.join(a.text.strip() for a in s); os.unlink(f); return toks(t)


def end_burst(e):
    """A short sound alone after a pause at the very end of a take is the engine's stray syllable."""
    import numpy as np
    on = e > 0.012; idx = np.where(on)[0]
    if len(idx) == 0: return False
    end = idx[-1]; i = end
    while i > 0 and on[max(0, i - 12):i].any(): i -= 1
    gap = i - 1 - (np.where(on[:i])[0][-1] if on[:i].any() else 0)
    return bool((end - i) * 0.01 < 0.3 and gap * 0.01 > 0.1)


def score(model, path, text):
    import numpy as np
    sr, x = load(path); want = toks(text); hop = int(sr * 0.01)
    e = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(0, len(x) - hop, hop)]); on = np.where(e > 0.006)[0]
    burst = end_burst(e)
    x = x[on[0] * hop:(on[-1] + 2) * hop]; pad = np.zeros(int(sr * 0.5), np.float32); got = covered(want, hear(model, sr, x))
    for t in np.arange(0, max(0.1, len(x) / sr - 1.0), 2.0):
        got |= covered(want, hear(model, sr, np.concatenate([pad, x[int(t * sr):int((t + 3.5) * sr)], pad])))
    missing = [want[i] for i in range(len(want)) if i not in got and want[i] not in EXEMPT]
    tail = hear(model, sr, np.concatenate([x[-int(sr * 2.2):], pad]))
    last = [i for i in range(len(want) - 2, len(want)) if want[i] not in EXEMPT]
    tail_cut = len(covered(want[-2:], tail)) < 2 and bool(last)
    end = np.sqrt((x[-int(sr * 0.05):] ** 2).mean()) / e.max(); trail = (len(e) - 1 - on[-1]) * 0.01
    abrupt = bool(trail < 0.03 and end > 0.08)
    return {'missing': missing, 'tail_cut': tail_cut, 'abrupt': abrupt, 'stray': burst, 'cost': len(missing) * 2 + 3 * tail_cut + abrupt + 3 * burst}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('names', nargs='*'); ap.add_argument('--episode', required=True); ap.add_argument('--plan', action='store_true')
    ap.add_argument('--score-only', action='store_true'); ap.add_argument('--max-takes', type=int, default=5); ap.add_argument('--seed', type=int, default=1000)
    a = ap.parse_args(); ep = Path(a.episode); cfg = json.loads((ep / 'episode.json').read_text(encoding='utf-8')); V = cfg['voice']; say = cfg.get('say', {})
    lp = ep / 'audio/voice_ledger.json'; qp = ep / 'audio/voice_qc.json'; d = ep / 'audio/chunks'; old = ep / 'audio/chunks_v1'; tmp = ep / 'audio/takes'
    for p in (d, old, tmp): p.mkdir(parents=True, exist_ok=True)
    if a.plan:
        C = chunks((ep / 'docs/script.txt').read_text(encoding='utf-8'))
        L = {f'{i:03}.wav': {'text': c, 'spoken': spoken(c, say)} for i, c in enumerate(C, 1)}
        if lp.exists(): sys.exit('ledger exists; edit it by hand or delete it first')
        lp.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding='utf-8'); print(len(L), 'chunks ->', lp); return
    if V['id'] not in {p.get('id') for p in json.loads(api('/profiles'))}: sys.exit('VOICE GATE BLOCKED; no fallback')
    from faster_whisper import WhisperModel
    L = json.loads(lp.read_text(encoding='utf-8')); Q = json.loads(qp.read_text()) if qp.exists() else {}; model = WhisperModel('small', device='cpu', compute_type='int8')
    for n in sorted(a.names or L):
        text = L[n]['spoken']
        if Q.get(n, {}).get('pass') and not a.names: continue
        s = score(model, d / n, text) if (d / n).exists() else {'cost': 99}
        print(n, 'current', s, flush=True); Q[n] = {**s, 'pass': s['cost'] == 0, 'take': 'current'}
        if s['cost'] and not a.score_only:
            best, cost = None, s['cost']
            for t in range(a.max_takes):
                body = {'model': V.get('model', 'tts-1'), 'voice': V['id'], 'input': text, 'response_format': 'wav', 'language': V.get('language', 'vi'),
                        'seed': a.seed + t, 'duration': round(len(text.split()) / 3.0 + 1.2, 1)}
                t0 = time.time(); blob = api('/v1/audio/speech', body)
                if blob[:4] != b'RIFF': sys.exit(f'bad WAV for {n}')
                f = tmp / f'{n[:-4]}_{a.seed + t}.wav'; f.write_bytes(blob); r = score(model, f, text)
                print(n, 'take', t, r, f'{time.time() - t0:.0f}s', flush=True)
                if r['cost'] < cost: best, cost, s = f, r['cost'], r
                if r['cost'] == 0: break
            if best:
                if (d / n).exists() and not (old / n).exists(): shutil.copy2(d / n, old / n)
                shutil.copy2(best, d / n); sr, x = load(best)
                L[n].update(seconds=round(len(x) / sr, 2), key=hashlib.sha256(text.encode()).hexdigest()); lp.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding='utf-8')
                Q[n] = {**s, 'pass': s['cost'] == 0, 'take': best.name}
        qp.write_text(json.dumps(Q, ensure_ascii=False, indent=1), encoding='utf-8')
    bad = {k: v for k, v in Q.items() if not v['pass']}
    print('DONE', len(Q), 'checked,', len(bad), 'not clean:', bad, flush=True)


if __name__ == '__main__':
    main()
