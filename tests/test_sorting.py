import unittest
from pyeda.inter import And, Or, expr
from sorting import (to_network, to_clauses, variables, once_depth, once_size, used, no_redundant, 
    last_layer, second_last_layer, no_adjacent_unused_channels, independent_in_previous_layers,
    ascending_order, all_adjacent, connectivity, sorts, sorts_forward_size, sorts_backward_size, 
    sorts_forward_depth, sorts_backward_depth)


def binomial(n, r):
    ''' Binomial coefficient 
        n! / (r! * (n - r)!)
    '''
    p = 1    
    for i in range(1, min(r, n - r) + 1):
        p *= n
        p //= i
        n -= 1
    return p

class TestSortingModule(unittest.TestCase):

    def assertEquivalent(self, a, b):
        self.assertEqual(len(a), len(b))
        for ca, cb in zip(a, b):
            self.assertTrue(ca.equivalent(cb))
    
    def test_to_clauses(self):
        n = 3
        d = 3
        net = [[(0, 1)], [(0, 2)], [(1, 2)]]
        g = variables(n, d)
        c = to_clauses(net, g, n)
        refc = [g[0,0,1], ~g[0,0,2], ~g[0,1,2], ~g[1,0,1], g[1,0,2], ~g[1,1,2], ~g[2,0,1], ~g[2,0,2], g[2,1,2]]
        self.assertEquivalent(c, refc)

    def test_once_depth(self):
        n = 2
        d = 1
        g = variables(n, d)
        self.assertEqual(once_depth(g, 2, 0), [g[0,0,1]])
        n = 10
        d = 1
        g = variables(n, d)        
        clauses = once_depth(g, n, 0)
        constraint = And(*clauses)
        self.assertEqual(len(clauses), 3*binomial(n,3) + 1)
        nsol = 0
        for r in range(0, n+1, 2):
            subtotal = 1
            fact = 1
            for t in range(0, r, 2):
                subtotal *= binomial(n - t, 2)
                fact *= (r - t) // 2
            nsol += subtotal // fact
        self.assertEqual(constraint.satisfy_count(), nsol - 1)

    def test_once_size(self):
        # n=2
        g = variables(2, 1)
        c = once_size(g, 2, 0)
        self.assertEquivalent(c, [g[0,0,1]])
        # n=3
        g = variables(3, 2)
        c = once_size(g, 3, 1)
        self.assertEquivalent(c, 
            [Or(~g[1,0,1], ~g[1,0,2]), 
             Or(~g[1,0,1], ~g[1,1,2]), 
             Or(~g[1,0,2], ~g[1,1,2]), 
             Or(g[1,0,1], g[1,0,2], g[1,1,2])])
        # n > 3
        n = 10
        d = 1
        g = variables(n, d)
        clauses = once_size(g, n, 0)
        constraint = And(*clauses)
        ncmp = binomial(n,2)
        nclauses = binomial(ncmp, 2) + 1
        self.assertEqual(len(clauses), nclauses)
        self.assertEqual(len(list(constraint.satisfy_all())), ncmp)

    def test_used(self):
        g = variables(5, 2)
        c = [used(g, 0, 4, 1, 1)]
        self.assertEquivalent(c, [Or(g[1,0,1], g[1,1,2], g[1,1,3])])

    def test_no_redundant(self):
        g = variables(3, 3)
        c = no_redundant(g, 3, 1)
        self.assertEquivalent(c, [Or(~g[0,0,1], ~g[1,0,1]), Or(~g[0,0,2], ~g[1,0,2]), Or(~g[0,1,2], ~g[1,1,2])])
        c = no_redundant(g, 3, 2)
        self.assertEquivalent(c, [Or(~g[1,0,1], ~g[2,0,1]), Or(~g[1,0,2], ~g[2,0,2]), Or(~g[1,1,2], ~g[2,1,2])])

    def test_last_layer(self):
        g = variables(4, 3)
        c = last_layer(g, 4, 3)
        self.assertEquivalent(c, [~g[2,0,2], ~g[2,0,3], ~g[2,1,3]])

    def test_second_last_layer(self):
        g = variables(5, 3)
        c = second_last_layer(g, 5, 3)
        self.assertEquivalent(c,
            [~g[1,0,4], 
             Or(~g[1,0,2], g[2,0,1], g[2,1,2]), 
             Or(~g[1,1,3], g[2,1,2], g[2,2,3]), 
             Or(~g[1,2,4], g[2,2,3], g[2,3,4]), 
             Or(~g[1,0,3], g[2,0,1]), 
             Or(~g[1,0,3], g[2,2,3]), 
             Or(~g[1,1,4], g[2,1,2]), 
             Or(~g[1,1,4], g[2,3,4])])

    def test_no_adjacent_unused_channels(self):
        g = variables(5, 3)
        c = no_adjacent_unused_channels(g, 5, 3)
        self.assertEquivalent(c, 
            [Or(g[2,0,1], g[2,1,2]), 
             Or(g[2,0,1], g[2,1,2], g[2,2,3]), 
             Or(g[2,1,2], g[2,2,3], g[2,3,4]), 
             Or(g[2,2,3], g[2,3,4])])

    def test_independent_in_previous_layers(self):
        g = variables(4, 3)
        c = independent_in_previous_layers(g, 4, 2)
        self.assertEquivalent(c, 
            [Or(g[1,0,1], g[1,0,2], g[1,0,3], g[1,1,2], g[1,1,3], ~g[2,0,1]), 
             Or(g[1,0,1], g[1,0,2], g[1,0,3], g[1,1,2], g[1,2,3], ~g[2,0,2]), 
             Or(g[1,0,1], g[1,0,2], g[1,0,3], g[1,1,3], g[1,2,3], ~g[2,0,3]), 
             Or(g[1,0,1], g[1,0,2], g[1,1,2], g[1,1,3], g[1,2,3], ~g[2,1,2]), 
             Or(g[1,0,1], g[1,0,3], g[1,1,2], g[1,1,3], g[1,2,3], ~g[2,1,3]), 
             Or(g[1,0,2], g[1,0,3], g[1,1,2], g[1,1,3], g[1,2,3], ~g[2,2,3])])

    def test_ascending_order(self):
        g = variables(5, 3)
        c = ascending_order(g, 5, 2)
        self.assertEquivalent(c, 
            [Or(~g[1,1,2], ~g[2,0,3]), 
             Or(~g[1,1,2], ~g[2,0,4]), 
             Or(~g[1,1,3], ~g[2,0,2]), 
             Or(~g[1,1,3], ~g[2,0,4]), 
             Or(~g[1,1,4], ~g[2,0,2]), 
             Or(~g[1,1,4], ~g[2,0,3]), 
             Or(~g[1,2,3], ~g[2,0,1]), 
             Or(~g[1,2,3], ~g[2,0,4]), 
             Or(~g[1,2,3], ~g[2,1,4]), 
             Or(~g[1,2,4], ~g[2,0,1]), 
             Or(~g[1,2,4], ~g[2,0,3]), 
             Or(~g[1,2,4], ~g[2,1,3]), 
             Or(~g[1,3,4], ~g[2,0,1]), 
             Or(~g[1,3,4], ~g[2,0,2]), 
             Or(~g[1,3,4], ~g[2,1,2])])

    def test_all_adjacent(self):
        g = variables(5, 3)
        c = all_adjacent(g, 5, 3)
        self.assertEquivalent(c, 
            [Or(g[0,0,1], g[1,0,1], g[2,0,1]), 
             Or(g[0,1,2], g[1,1,2], g[2,1,2]), 
             Or(g[0,2,3], g[1,2,3], g[2,2,3]), 
             Or(g[0,3,4], g[1,3,4], g[2,3,4])])

    def test_connectivity(self):
        n = 3
        d = 3
        g = variables(n, d)
        clauses = connectivity(g, n, d)
        for k in range(d):
            clauses += once_depth(g, n, k)
        for k in range(1, d):
            clauses += no_redundant(g, n, k)
        clauses += all_adjacent(g, n, d)
        constraint = And(*clauses)
        sol = {str(to_network(s, g, n, d)) for s in constraint.satisfy_all()}
        ref = {'[[(0, 2)], [(1, 2)], [(0, 1)]]', 
               '[[(1, 2)], [(0, 2)], [(0, 1)]]', 
               '[[(0, 2)], [(0, 1)], [(1, 2)]]', 
               '[[(1, 2)], [(0, 1)], [(1, 2)]]', 
               '[[(0, 1)], [(0, 2)], [(1, 2)]]', 
               '[[(1, 2)], [(0, 1)], [(0, 2)]]', 
               '[[(0, 1)], [(1, 2)], [(0, 2)]]', 
               '[[(0, 1)], [(1, 2)], [(0, 1)]]'}
        self.assertEqual(sol, ref)

    def test_sorts(self):
        for fsorts in [sorts, sorts_forward_size, sorts_backward_size, sorts_forward_depth, sorts_backward_depth]:
            n = 2
            d = 1
            g = variables(n, d)
            c = fsorts(g, n, 0, d, range(1<<n))
            constraint = And(*c)
            if constraint != expr(1):
                self.assertEqual(constraint, g[0,0,1])

            n = 3
            d = 3
            g = variables(n, d)
            c = fsorts(g, n, 0, d, range(1<<n))

            net1 = [[(0, 1)], [(1, 2)], [(0, 1)]]
            c1 = to_clauses(net1, g, n)

            net2 = [[(0, 1)], [(1, 2)], [(1, 2)]]
            c2 = to_clauses(net2, g, n)

            constraint = And(*(c + c1))
            sol = constraint.satisfy_one()
            self.assertTrue(sol is not None)

            constraint = And(*(c + c2))
            sol = constraint.satisfy_one()
            self.assertTrue(sol is None)

        for fsorts in [sorts, sorts_forward_depth, sorts_backward_depth]:
            n = 5
            d = 5
            g = variables(n, d)
            c = fsorts(g, n, 0, d, range(1<<n))

            net1 = [[(0, 1), (2, 3)], [(0, 2), (1, 3)], [(2, 4)], [(1, 2), (3, 4)], [(0, 1), (2, 3)]]
            c1 = to_clauses(net1, g, n)

            net2 = [[(0, 1), (2, 3)], [(0, 2), (1, 3)], [(2, 3)], [(1, 2), (3, 4)], [(0, 1), (2, 3)]]
            c2 = to_clauses(net2, g, n)

            constraint = And(*(c + c1))
            sol = constraint.satisfy_one()
            self.assertTrue(sol is not None)

            constraint = And(*(c + c2))
            sol = constraint.satisfy_one()
            self.assertTrue(sol is None)

        for fsorts in [sorts, sorts_forward_size, sorts_backward_size]:
            n = 5
            s = 9
            d = s
            g = variables(n, d)
            c = fsorts(g, n, 0, d, range(1<<n))

            net1 = [[(0, 1)], [(2, 3)], [(0, 2)], [(1, 3)], [(2, 4)], [(1, 2)], [(3, 4)], [(0, 1)], [(2, 3)]]
            c1 = to_clauses(net1, g, n)

            net2 = [[(0, 1)], [(2, 3)], [(0, 2)], [(1, 3)], [(2, 3)], [(1, 2)], [(3, 4)], [(0, 1)], [(2, 3)]]
            c2 = to_clauses(net2, g, n)

            constraint = And(*(c + c1))
            sol = constraint.satisfy_one()
            self.assertTrue(sol is not None)

            constraint = And(*(c + c2))
            sol = constraint.satisfy_one()
            self.assertTrue(sol is None)
