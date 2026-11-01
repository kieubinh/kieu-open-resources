#!/usr/bin/env python3
"""Measure a Vietnamese "Nếu Như" narration script and its title against the channel's targets.

Usage: audit_script.py script.txt [--title "Nếu ...?"] [--strict]
--strict exits 1 when a hard limit is missed. Soft targets are only reported.
"""
import argparse, re, sys

TARGETS = {'ellipsis': (18, 25), 'questions': (15, 20), 'ban_per_100': (4.0, 5.0)}


def words(s):
    return len(re.findall(r'[^\W\d_]+|\d+', s))


def sentences(t):
    return [x.strip() for x in re.split(r'(?<=[.!?:])\s+', t) if x.strip()]


def audit(text):
    t = text.strip(); s = sentences(t); n = words(t); L = [words(x) for x in s]
    ban = len(re.findall(r'\b[Bb]ạn\b', t))
    return {'syllables': n, 'sentences': len(s), 'avg_sentence': round(n / max(1, len(s)), 2),
            'short_share': round(sum(x <= 6 for x in L) / max(1, len(L)), 2), 'longest': max(L, default=0),
            'ellipsis': t.count('...'), 'questions': t.count('?'), 'ban_per_100': round(ban / max(1, n) * 100, 2),
            'digits': re.findall(r'\d+', t), 'over_20': [x for x in s if words(x) > 20],
            'paragraphs': len([p for p in t.split('\n') if p.strip()]),
            'quotes': len(re.findall(r'["“”]', t))}


def hard_failures(r):
    fails = []
    if not 1150 <= r['syllables'] <= 1600: fails.append(f"length {r['syllables']} outside 1150-1600")
    if r['paragraphs'] != 1: fails.append('script must be one paragraph')
    if r['quotes']: fails.append('no quotation marks around dialogue')
    if [d for d in r['digits'] if not re.fullmatch(r'(1\d|20)\d\d', d)]: fails.append('spell numbers as words (years may stay digits)')
    return fails


def title_failures(title):
    fails = []
    if not title.startswith('Nếu'): fails.append('title must start with "Nếu"')
    if not title.endswith('?'): fails.append('title must end with "?"')
    if not 6 <= words(title) <= 10: fails.append(f'title has {words(title)} syllables, want 6-10')
    if title.isupper(): fails.append('title must not be all caps')
    return fails


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('script'); ap.add_argument('--title'); ap.add_argument('--strict', action='store_true')
    a = ap.parse_args(); r = audit(open(a.script, encoding='utf-8').read())
    for k, v in r.items():
        tgt = TARGETS.get(k); print(k, v, f'(target {tgt[0]}-{tgt[1]})' if tgt else '')
    if not 1300 <= r['syllables'] <= 1500: print('note: syllables outside the 1300-1500 target')
    fails = hard_failures(r) + (title_failures(a.title) if a.title else [])
    for f in fails: print('FAIL', f)
    if a.strict and fails: sys.exit(1)


if __name__ == '__main__':
    main()
