"""Produce code-faithful, machine-verifiable traces for video animations."""
from typing import Sequence


def trace(a: Sequence[int], b: Sequence[int]):
    a, b = list(a), list(b)
    swapped = len(a) > len(b)
    if swapped:
        a, b = b, a
    m, n = len(a), len(b)
    left_size = (m + n + 1)//2
    lo, hi = 0, m
    steps=[]
    while lo<=hi:
        i=(lo+hi)//2; j=left_size-i
        al=a[i-1] if i else float('-inf')
        ar=a[i] if i<m else float('inf')
        bl=b[j-1] if j else float('-inf')
        br=b[j] if j<n else float('inf')
        assert 0<=j<=n
        if al<=br and bl<=ar:
            decision='valid'
            median=float(max(al,bl)) if (m+n)%2 else (max(al,bl)+min(ar,br))/2
        elif al>br:
            decision='move_left';median=None
        else:
            decision='move_right';median=None
        def json_num(x):
            if x==float('-inf'): return '-∞'
            if x==float('inf'): return '+∞'
            return x
        steps.append(dict(a=a,b=b,swapped=swapped,m=m,n=n,leftSize=left_size,
            lo=lo,hi=hi,i=i,j=j,AL=json_num(al),AR=json_num(ar),BL=json_num(bl),BR=json_num(br),
            decision=decision,median=median))
        if decision=='valid':break
        if decision=='move_left':hi=i-1
        else:lo=i+1
    return steps

if __name__=='__main__':
    import json
    from pathlib import Path
    cases={
        'official_1':[[1,3],[2]],
        'official_2':[[1,2],[3,4]],
        'move_right':[[1,2,3],[7,8,9,10]],
        'move_left':[[8,9,10],[1,2,3,4]],
        'empty':[[],[1]],
        'duplicates':[[2,2],[2,2]],
    }
    path=Path(__file__).resolve().parents[1]/'src'/'traces.json'
    path.write_text(json.dumps({k:trace(*v) for k,v in cases.items()},ensure_ascii=False,indent=2)+'\n')
    print(path)
