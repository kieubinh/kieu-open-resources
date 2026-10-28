"""Run with python3 -m unittest scripts/solution_test.py"""
import re, random, unittest
try:
    from .solution import Solution
except ImportError:
    from solution import Solution

class SolutionTest(unittest.TestCase):
    def test_official(self):
        f=Solution().isMatch
        self.assertFalse(f("aa","a"))
        self.assertTrue(f("aa","a*"))
        self.assertTrue(f("ab",".*"))
    def test_more_cases(self):
        f=Solution().isMatch
        for s,p,expected in [("aab","c*a*b",True),
            ("mississippi","mis*is*p*.",False),("","a*",True),
            ("aaa","a*a",True),("ab",".*c",False)]:
            self.assertEqual(f(s,p),expected,(s,p))
    def test_randomized(self):
        f=Solution().isMatch
        rng=random.Random(42)
        for _ in range(2400):
            p="".join(rng.choice("ab.")+("*" if rng.random()<.4 else "")
                 for k in range(rng.randint(1,8)))
            s="".join(rng.choice("ab") for k in range(rng.randint(0,9)))
            self.assertEqual(f(s,p),re.fullmatch(p,s) is not None,(s,p))
if __name__=="__main__":unittest.main()
