# -*- coding: utf-8 -*-
""" Encondings of cardinality constraints
Based on the encoding into SAT proposed by:
Abío, Ignasi, Robert Nieuwenhuis, Albert Oliveras, and Enric Rodríguez-Carbonell. 
"A parametric approach for smaller and better encodings of cardinality constraints." 
In International Conference on Principles and Practice of Constraint Programming, pp. 80-96. Springer, Berlin, Heidelberg, 2013.
"""

from pyeda.inter import exprvars, Or


def even(a):
    return [a[i] for i in range(0, len(a), 2)]


def odd(a):
    return [a[i] for i in range(1, len(a), 2)]


def comp(x1, x2, y1, y2):
    return [Or(~x1, ~x2, y2), ~x1 | y1, ~x2 | y1]


def Sort(a, prefix=''):
    n = len(a)
    if n == 1:
        return (a, [])
    if n == 2:
        return Merge([a[0]], [a[1]], prefix)
    else:
        l = n//2
        d0, s0 = Sort([a[i] for i in range(0, l)], prefix + 'd0')
        d1, s1 = Sort([a[i] for i in range(l, n)], prefix + 'd1')
        c, m = Merge(d0, d1, prefix)
        return (c, s0 + s1 + m)


def Merge(a, b, prefix=''):
    na = len(a)
    nb = len(b)
    if na == 0:
        return (b, [])
    elif nb == 0:
        return (a, [])
    elif na == 1 and nb == 1:
        if prefix == '':
            prefix = 'c'
        c = exprvars(prefix, 2)
        s = comp(a[0], b[0], c[0], c[1])
        return (c, s)
    else:
        d, sd = Merge(even(a), even(b), prefix+'d')
        e, se = Merge(odd(a), odd(b), prefix+'e')

    if (na % 2) == (nb % 2):
        nc = na+nb-2
        c = exprvars(prefix+'c', (1, nc+1))
        if (na % 2) == 0:
            v = [d[0]] + list(c) + [e[-1]]
        else:
            v = [d[0]] + list(c) + [d[-1]]
    else:
        nc = na+nb-1
        c = exprvars(prefix+'c', (1, nc+1))
        v = [d[0]] + list(c)

    sp = []
    for i in range(nc//2):
        sp += comp(d[i+1], e[i], c[2*i+1], c[2*i+2])
    s = sd + se + sp
    return (v, s)


def SMerge(a, b, nc, prefix=''):
    a = a[:nc]
    b = b[:nc]
    na = len(a)
    nb = len(b)
    if na == nb == nc == 1:
        if prefix == '':
            prefix = 'c'
        c = exprvars(prefix, 1)
        s = [~a[0] | c[0], ~b[0] | c[0]]
        return (c, s)
    elif (na + nb) <= nc:
        return Merge(a, b, prefix)
    else:
        c = exprvars(prefix+'c', (1, nc))
        d, sd = SMerge(even(a), even(b), (nc+1)//2+1, prefix+'d')
        e, se = SMerge(odd(a), odd(b), (nc+1)//2, prefix+'e')
        v = [d[0]] + list(c)
        sp = []
        for i in range((nc-1)//2):
            sp += comp(d[i+1], e[i], c[2*i+1], c[2*i+2])
        if nc % 2 == 0:
            sp += [~d[-1] | c[-1], ~e[-1] | c[-1]]
        s = sd + se + sp
        return (v, s)


def Card(a, m, prefix=''):
    n = len(a)
    if n <= m:
        return Sort(a, prefix)
    else:
        l = n//2
        d0, s0 = Card([a[i] for i in range(0, l)], m, prefix + 'c0')
        d1, s1 = Card([a[i] for i in range(l, n)], m, prefix + 'c1')
        c, s2 = SMerge(d0, d1, m, prefix)
        return (c, s0 + s1 + s2)
