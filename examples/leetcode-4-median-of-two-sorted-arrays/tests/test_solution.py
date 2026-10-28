import sys, random, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from solution import Solution
from trace import trace


def oracle(a,b):
    c=sorted(a+b)
    return (c[(len(c)-1)//2]+c[len(c)//2])/2.0

class TestMedian(unittest.TestCase):
    def test_official(self):
        s=Solution()
        self.assertEqual(s.findMedianSortedArrays([1,3],[2]),2.0)
        self.assertEqual(s.findMedianSortedArrays([1,2],[3,4]),2.5)
    def test_edge_cases(self):
        s=Solution()
        for a,b in [([],[5]),([2],[]),([1],[2]),([-1000000],[1000000]),([0,0],[0]),([2,2],[2,2]),([1,2,3,4,5],[6]),([1],[2,3,4,5,6])]:
            self.assertEqual(s.findMedianSortedArrays(a,b),oracle(a,b),(a,b))
    def test_differential_20000(self):
        r=random.Random(20261028);s=Solution()
        for _ in range(20000):
            m=r.randint(0,25);n=r.randint(0,25)
            if m+n==0:n=1
            a=sorted(r.randint(-1000000,1000000) for _ in range(m))
            b=sorted(r.randint(-1000000,1000000) for _ in range(n))
            self.assertEqual(s.findMedianSortedArrays(a,b),oracle(a,b),(a,b))
            t=trace(a,b)
            self.assertEqual(t[-1]['decision'],'valid')
            self.assertEqual(t[-1]['median'],oracle(a,b))
            self.assertLessEqual(len(t),10)

if __name__=='__main__':unittest.main()
