import heapq
from collections import deque
from math import inf

def two_sum(nums, target):
    pos = {}
    for i, x in enumerate(nums):
        if target - x in pos:
            return [pos[target - x], i]
        pos[x] = i

def max_area(h):
    l, r, best = 0, len(h) - 1, 0
    while l < r:
        best = max(best, min(h[l], h[r]) * (r - l))
        if h[l] < h[r]: l += 1
        else: r -= 1
    return best

def longest_unique(s):
    last, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if last.get(ch, -1) >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best

def subarray_sum(nums, k):
    count, s, ans = {0: 1}, 0, 0
    for x in nums:
        s += x
        ans += count.get(s - k, 0)
        count[s] = count.get(s, 0) + 1
    return ans

def first_true(lo, hi, ok):
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid): hi = mid
        else: lo = mid + 1
    return lo

def daily_temps(t):
    ans, st = [0] * len(t), []
    for i, x in enumerate(t):
        while st and t[st[-1]] < x:
            j = st.pop()
            ans[j] = i - j
        st.append(i)
    return ans

def bfs(start, goal, nbrs):
    q, seen, steps = deque([start]), {start}, 0
    while q:
        for _ in range(len(q)):
            u = q.popleft()
            if u == goal: return steps
            for v in nbrs(u):
                if v not in seen:
                    seen.add(v); q.append(v)
        steps += 1
    return -1

def subsets(nums):
    res = []
    def bt(start, path):
        res.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            bt(i + 1, path)
            path.pop()
    bt(0, [])
    return res

def kth_largest(nums, k):
    h = []
    for x in nums:
        heapq.heappush(h, x)
        if len(h) > k: heapq.heappop(h)
    return h[0]

def coin_change(coins, amount):
    dp = [0] + [inf] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] < inf else -1

def merge(iv):
    iv.sort()
    out = [iv[0][:]]
    for s, e in iv[1:]:
        if s <= out[-1][1]: out[-1][1] = max(out[-1][1], e)
        else: out.append([s, e])
    return out

def make_uf(n):
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb: return False
        parent[ra] = rb
        return True
    return find, union

assert two_sum([2,7,11,15], 9) == [0,1]
assert max_area([1,8,6,2,5,4,8,3,7]) == 49
assert longest_unique("abcabcbb") == 3 and longest_unique("pwwkew") == 3 and longest_unique("abba") == 2
assert subarray_sum([1,1,1], 2) == 2 and subarray_sum([1,2,3], 3) == 2
piles, h = [3,6,7,11], 8
assert first_true(1, max(piles), lambda k: sum((p + k - 1)//k for p in piles) <= h) == 4
assert daily_temps([73,74,75,71,69,72,76,73]) == [1,1,4,2,1,1,0,0]
assert bfs(0, 5, lambda u: [u+1, u*2]) == 4 and bfs(1, 8, lambda u: [u+1, u*2]) == 3
assert len(subsets([1,2,3])) == 8
assert kth_largest([3,2,1,5,6,4], 2) == 5
assert coin_change([1,2,5], 11) == 3 and coin_change([2], 3) == -1
assert merge([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]
find, union = make_uf(3)
assert union(0,1) and not union(1,0) and find(0) == find(1) != find(2)
print("all templates ok")
