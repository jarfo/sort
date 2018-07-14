from itertools import combinations
import unittest
from pyeda.inter import expr, exprvars, Or, And


def even(a):
    return [a[i] for i in range(0, len(a), 2)]


def odd(a):
    return [a[i] for i in range(1, len(a), 2)]


def HSort(a, prefix=''):
    n = len(a)
    if n == 1:
        return (a, [])
    if n == 2:
        return HMerge([a[0]], [a[1]], prefix)
    else:
        d0, s0 = HSort([a[i] for i in range(0, n//2)], prefix + 'd0')
        d1, s1 = HSort([a[i] for i in range(n//2, n)], prefix + 'd1')
        c, m = HMerge(d0, d1, prefix)
        return (c, s0 + s1 + m)


def HMerge(a, b, prefix=''):
    n = len(a)
    if n == 1:
        if prefix == '':
            prefix = 'c'
        c = exprvars(prefix, 2)
        s = [Or(~a[0], ~b[0], c[1]), ~a[0] | c[0], ~b[0] | c[0]]
        return (c, s)
    else:
        c = exprvars(prefix+'c', (1, 2*n-1))
        d, sd = HMerge(even(a), even(b), prefix+'d')
        e, se = HMerge(odd(a), odd(b), prefix+'e')
        v = [d[0]] + [x for x in c] + [e[-1]]
        sp = []
        for i in range(n-1):
            sp.append(Or(*(~d[i+1], ~e[i], c[2*i+2])))
            sp.append(~d[i+1] | c[2*i+1])
            sp.append(~e[i] | c[2*i+1])
        s = sd + se + sp
        return (v, s)


def SMerge(a, b, prefix=''):
    n = len(a)
    if n == 1:
        if prefix == '':
            prefix = 'c'
        c = exprvars(prefix, 2)
        s = [Or(~a[0], ~b[0], c[1]), ~a[0] | c[0], ~b[0] | c[0]]
        return (c, s)
    else:
        c = exprvars(prefix+'c', (1, n+1))
        d, sd = SMerge(even(a), even(b), prefix+'d')
        e, se = SMerge(odd(a), odd(b), prefix+'e')
        v = [d[0]] + list(c)
        sp = []
        for i in range(n//2):
            sp.append(Or(~d[i+1], ~e[i], c[2*i+2]))
            sp.append(~d[i+1] | c[2*i+1])
            sp.append(~e[i] | c[2*i+1])
        s = sd + se + sp
        return (v, s)


def Card2(a, k, prefix=''):
    n = len(a)
    if n == k:
        return HSort(a, prefix)
    else:
        d0, s0 = Card2([a[i] for i in range(0, k)], k, prefix + 'c0')
        d1, s1 = Card2([a[i] for i in range(k, n)], k, prefix + 'c1')
        c, m = SMerge(d0, d1, prefix)
        return (c[:-1], s0 + s1 + m)


def Card(a, p, prefix=''):
    k = 1 << (p-1).bit_length()
    n = ((len(a)-1)//k + 1)*k
    a = list(a) + [expr(False)]*(n - len(a))
    return Card2(a, k, prefix)
