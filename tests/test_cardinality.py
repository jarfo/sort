import unittest
from itertools import combinations
from pyeda.inter import exprvars, And
from cardinality import Merge, Sort, SMerge, Card


class TestCardinalityModule(unittest.TestCase):

    def test_Merge(self):
        a = exprvars('a', 2)
        b = exprvars('b', 2)
        c, _ = Merge(a, b)
        self.assertEqual(str(c), "[d[0], c[1], c[2], e[1]]")

    def test_Sort(self):
        n = 4
        a = exprvars('a', n)
        c, _ = Sort(a)
        self.assertEqual(str(c), "[d[0], c[1], c[2], e[1]]")

    def test_SMerge(self):
        a = exprvars('a', 2)
        b = exprvars('b', 2)
        c, _ = SMerge(a, b, 3)
        self.assertEqual(str(c), "[d[0], c[1], c[2]]")

    def test_Card(self):
        # p = 3
        c, s = Card(exprvars('a', 10), 4)
        self.assertEqual("[dd[0], c[1], c[2], c[3]]", str(c))
        # Large range
        for n in range(1,12):
            for p in range(0, n):
                a = exprvars('a', n)
                c, s = Card(a, p+1)
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


if __name__ == '__main__':
    unittest.main()
