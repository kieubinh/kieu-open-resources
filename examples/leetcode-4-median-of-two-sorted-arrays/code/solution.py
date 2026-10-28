"""LeetCode #4: binary-search a valid median partition, O(log(min(m,n))) time."""
from typing import List


class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        a, b = nums1, nums2
        if len(a) > len(b):
            a, b = b, a

        m, n = len(a), len(b)
        left_size = (m + n + 1) // 2
        lo, hi = 0, m
        while lo <= hi:
            i = (lo + hi) // 2  # count of a values in left partition
            j = left_size - i   # count of b values in left partition

            a_left = a[i - 1] if i else float('-inf')
            a_right = a[i] if i < m else float('inf')
            b_left = b[j - 1] if j else float('-inf')
            b_right = b[j] if j < n else float('inf')

            if a_left <= b_right and b_left <= a_right:
                if (m + n) % 2:
                    return float(max(a_left, b_left))
                return (max(a_left, b_left) + min(a_right, b_right)) / 2.0
            if a_left > b_right:
                hi = i - 1
            else:
                lo = i + 1
        raise AssertionError('Inputs must be sorted, and total length >= 1')
