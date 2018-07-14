import sys
from pyeda.inter import expr, exprvars, Or, Implies, Equal
from network import vsort, Network, to_bit
from sorting import forward_depth

TRUE = expr(True)
FALSE = expr(False)

class Halver(Network):
    def is_halver(self, n, epsilon, log=False):
        maxeps = 0
        for x in range(1<<n):
            y = self.output(x)
            if get_epsilon(n, y) > epsilon:
                maxeps = get_epsilon(n, y)
                if log:
                    print(to_bit(x, n), '->', to_bit(y, n), '(eps={})'.format(maxeps), 'Fails', file=sys.stderr)
                return False
            elif get_epsilon(n, y) > maxeps:
                maxeps = get_epsilon(n, y)
                if log:
                    print(to_bit(x, n), '->', to_bit(y, n),  '(eps={})'.format(maxeps), file=sys.stderr)

        return True

def to_ehalver(point, g, n, d):
    assert g.ndim == 2
    m = n//2
    if point is not None:
        if type(point) is list:
            pairs = [[(i, j+m) for i in range(m) for j in range(m) if g[k+i, j] in point] for k in range(0, d*m, m)]
        else:
            pairs = [[(i, j+m) for i in range(m) for j in range(m) if g[k+i, j] in point and point[g[k+i, j]]] for k in range(0, d*m, m)]
        return Halver(pairs)
    else:
        return None

def halver_output(n, epsilon, v):
    m = n//2
    nonesA = 0
    nonesB = 0
    for i in range(m):
        nonesB += v>>i & 1
    for i in range(m, n):
        nonesA += v>>i & 1
    k = nonesA + nonesB
    if k <= m:
        maxA = epsilon*k
        return nonesA <= maxA
    else:
        maxB = epsilon*(n-k)
        return (m - nonesB) <= maxB

def get_epsilon(n, v):
    m = n//2
    nonesA = 0
    nonesB = 0
    for i in range(m):
        nonesB += v>>i & 1
    for i in range(m, n):
        nonesA += v>>i & 1
    k = nonesA + nonesB
    if k == 0 or k == n:
        return 0
    elif k <= m:
        return nonesA/k
    else:
        return (m - nonesB)/(n - k)

# Update for halver (expander type)
def forward_ehalver(g, n, k, v, s, t):
    m = n//2
    c2 = []
    type1 = set()
    type3 = set()
    i = k % m
    imask = 1<<i
    for j in range(m):
        jmask = 1<<(j+m)
        if (not (v & imask)) and (v & jmask):
            type1.add(j)
        elif (v & imask) and (not (v & jmask)):
            w = v + jmask - imask
            c2.append(Implies(g[k, j], Equal(t[v], s[v] | s[w])).to_cnf())
        else:
            type3.add(j)

    if len(type1) > 0:
        cmp1 = [g[k, j] for j in range(m) if j not in type1]
        c1 = [Or(*(cmp1 + [~t[v]]))]
    else:
        c1 = []

    if len(type3) > 0:
        cmp3 = [g[k, j] for j in range(m) if j not in type3]
        c3 = [Or(*(cmp3 + [~t[v], s[v]])), Or(*(cmp3 + [t[v], ~s[v]]))]
    else:
        c3 = []

    return c1 + c2 + c3

def halver(g, n, kf, kl, epsilon, xlist=None):
    ninputs = 1 << n

    # input vectors
    xset = set(xlist) if xlist is not None else set(range(ninputs))
    input = [TRUE if v in xset or v == vsort(v) else FALSE for v in range(ninputs)]

    # output vectors
    o = exprvars('o', ninputs)
    output = [TRUE if v == vsort(v) else o[v] if halver_output(n, epsilon, v) else FALSE for v in range(ninputs)]

    d = kl - kf
    c = []

    if g.ndim == 2:
        # ehalvers (opt = 'e')
        m = n//2
        d = d*m
        kf = kf*m
        if d == 0:
            return [Equal(input[v], output[v]).to_cnf() for v in range(ninputs)]
        elif d == 1:
            for v in range(ninputs):
                c += forward_ehalver(g, n, kf, v, input, output)
        elif d > 1:
            s = exprvars('s', d - 1, ninputs)

            # first layer
            tk = s[0]
            for v in range(ninputs):
                c += forward_ehalver(g, n, kf, v, input, tk)

            # intermediate layers
            for k in range(1, d - 1):
                sk = s[k - 1]
                tk = s[k]
                for v in range(ninputs):
                    c += forward_ehalver(g, n, kf + k, v, sk, tk)

            # last layer
            sk = s[d - 2]
            for v in range(ninputs):
                c += forward_ehalver(g, n, kf + d - 1, v, sk, output)

    else:
        # halvers (opt = 'h')
        aux = exprvars('ly', d, n-2, ninputs) if n>2 else [None]
        if d == 1:
            c += forward_depth(g, n, kf, input, output, aux[0])
        else:
            s = exprvars('s', d - 1, ninputs)
            c += forward_depth(g, n, kf, input, s[0], aux[0])
            for k in range(1, d - 1):
                c += forward_depth(g, n, kf + k, s[k - 1], s[k], aux[k])
            c += forward_depth(g, n, kf + d - 1, s[d - 2], output, aux[d-1])

    return c
    
# valid ehalvers (opt = 'e')
def valid_ehalver(g, n, d):
    m = n//2
    c = []
    for k in range(0, d*m, m):
        for i in range(m):
            c += [~g[k + i, j] | ~g[k + i, l] for j in range(m) for l in range(j + 1, m)]
            c += [~g[k + j, i] | ~g[k + l, i] for j in range(m) for l in range(j + 1, m)]
            c.append(Or(*[g[k + i, j] for j in range(m)]))
    return c

if __name__ == '__main__':
    # Halvers
    halvers = [
        [[(0, 4), (1, 2), (3, 9), (5, 10), (6, 11), (7, 8)], [(0, 6), (1, 3), (2, 8), (4, 7), (9, 11)], [(2, 5), (3, 4), (6, 10), (7, 9)], [(4, 6), (5, 7)]],
        [[(0, 9), (1, 10), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (8, 17)], [(0, 13), (1, 12), (2, 14), (3, 11), (4, 17), (5, 16), (6, 9), (7, 15), (8, 10)], [(0, 17), (1, 13), (2, 15), (3, 10), (4, 14), (5, 9), (6, 11), (7, 12), (8, 16)], [(0, 15), (1, 9), (2, 16), (3, 14), (4, 10), (5, 17), (6, 12), (7, 13), (8, 11)]]
    ]

    for nlist in halvers:
        net = Halver(nlist)
        n = max(max(c) for layer in net for c in layer) + 1 if len(nlist) else 2
        assert net.is_halver(n=n, epsilon=0.25, log=True)
        print(net.latex(n=n))