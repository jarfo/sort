import unittest
from itertools import combinations
from pyeda.inter import exprvars, And
from cardinality2 import HMerge, HSort, SMerge, Card


class TestCardinalityModule(unittest.TestCase):

    def test_HMerge(self):
        a = exprvars('a', 2)
        b = exprvars('b', 2)
        c, _ = HMerge(a, b)
        self.assertEqual(str(c), "[d[0], c[1], c[2], e[1]]")

    def test_HSort(self):
        n = 4
        a = exprvars('a', n)
        c, _ = HSort(a)
        self.assertEqual(str(c), "[d[0], c[1], c[2], e[1]]")

    def test_SMerge(self):
        a = exprvars('a', 2)
        b = exprvars('b', 2)
        c, _ = SMerge(a, b)
        self.assertEqual(str(c), "[d[0], c[1], c[2]]")

    def test_Card(self):
        n = 11
        p = 3
        a = exprvars('a', n)
        c, s = Card(a, p+1)
        self.assertEqual("[dd[0], c[1], c[2], c[3]]", str(c))
        s.append(~c[p])
        for i in range(n+1):
            for v in combinations(a, i):
                g = s[:]
                vv = list(v) + [~x for x in a if x not in v]
                g = vv + g
                constraint = And(*g)
                point = constraint.satisfy_one()
                if i > p:
                    self.assertTrue(point is None)
                else:
                    self.assertFalse(point is None)
