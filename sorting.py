from pyeda.inter import Or, And, Implies, Equal, expr, exprvars, exprzeros, exprones
from cardinality import Card
from network import Network, vsort

TRUE = expr(True)
FALSE = expr(False)

def to_expr(d, n):
    return tuple(map(expr, reversed("{0:0{1}b}".format(d, n))))

def to_network(point, g, n, d):
    if point is not None:
        net = Network(
            [[(i, j) for i in range(n) for j in range(i + 1, n) if g[k, i, j] in point and point[g[k, i, j]]] for k in range(d)])
        return net
    else:
        return None

def to_clauses(net, g, n):
    c = []
    for k, layer in enumerate(net):
        c += [g[k, i, j] if (i, j) in layer else ~g[k, i, j] for i in range(n-1) for j in range(i+1, n)]
    return c

def display_flow(point, n, d, xset):
    if point is not None:
        pset = {str(k): v for k, v in point.items()}
        for m, x in enumerate(xset):
            y = sorted(x)
            for i in range(n):
                vrow = ["v{}[{},{}]".format(m, k, i) for k in range(d)]
                print("".join(map(str, [x[i]] + [pset[v] if v in pset else x[i] for v in vrow])), y[i])
            print()

def variables(n, d):
    return exprvars('g', d, n, n)

def once_depth(g, n, k):
    clauses_from = [~g[k, i, j] | ~g[k, i, l] for j in range(n) for l in range(j) for i in range(l)]
    clauses_to = [~g[k, j, i] | ~g[k, l, i] for j in range(n) for l in range(j + 1, n) for i in range(l + 1, n)]
    clauses_to_from = [~g[k, j, i] | ~g[k, i, l] for j in range(n) for i in range(j + 1, n) for l in range(i + 1, n)]
    once = [Or(*[g[k, i, j] for i in range(n) for j in range(i + 1, n)])]
    c = clauses_from + clauses_to + clauses_to_from + once
    return c

def once_size(g, n, k):
    c = [~g[k, i, j] | ~g[k, l, m] for i in range(n - 1) for j in range(i + 1, n) for l in range(i, n) for m in range(l + 1, n)
         if (i != l) or (j < m)]
    c.append(Or(*[g[k, i, j] for i in range(n) for j in range(i + 1, n)]))
    return c

def no_redundant(g, n, k):
    c = [~g[k - 1, i, j] | ~g[k, i, j] for i in range(n) for j in range(i + 1, n)]
    return c

# Non-redundant comparators in the last layer has to be of the form (i,i+1) [Codish et al. 2015, Lemma 4]
def last_layer(g, n, d):
    c = [~g[d - 1, i, j] for i in range(n) for j in range(i + 2, n)]
    return c

# Non-redundant comparators in the next to last layer has to be of the form (i,i+1) (i,i+2) or (i,i+3) [Codish et al. 2015, Corollary 2]
def second_last_layer(g, n, d):
    c = [~g[d - 2, i, j] for i in range(n) for j in range(i + 4, n)]
    c += [Or(~g[d - 2, i, i + 2], g[d - 1, i, i + 1], g[d - 1, i + 1, i + 2]) for i in range(n - 2)]
    c += [~g[d - 2, i, i + 3] | g[d - 1, k, k + 1] for i in range(n - 3) for k in (i, i + 2)]
    return c

# No adjacent unused channels [Codish et al. 2015, Lemma 7] (last layer normal form, optimal-depth only)
def no_adjacent_unused_channels(g, n, d):
    c = [g[d - 1, 0, 1] | g[d - 1, 1, 2]]
    c += [Or(g[d - 1, i - 1, i], g[d - 1, i, i + 1], g[d - 1, i + 1, i + 2]) for i in range(1, n - 2)]
    c += [g[d - 1, n - 3, n - 2] | g[d - 1, n - 2, n - 1]]
    return c

# Keep independent comparators in previous layers (not compatible with previous llnf restriction)
def independent_in_previous_layers(g, n, k):
    c = [Implies(g[k, i, j], used(g, 0, n, k - 1, i) | used(g, 0, n, k - 1, j)).to_cnf() for i in range(n) for j in range(i + 1, n)]
    return c

# Keep independent comparators in ascending order (optimal-size only)
def ascending_order(g, n, k):
    c = [~g[k - 1, i, j] | ~g[k, l, m] for i in range(n) for j in range(i + 1, n) for l in range(i) for m in
         range(l + 1, n) if m != j and m != i]
    return c

# A sorting networks has all the adjacent comparators
def all_adjacent(g, n, d):
    c = [Or(*[g[k, i, i + 1] for k in range(d)]) for i in range(n - 1)]
    return c

# Connectivity update
def kupdate(g, n, k, i, p, w):
    c = [Implies(~used(g, 0, n, k, i), Equal(p[m, i], w[m, i])).to_cnf() for m in range(n)]
    c += [Implies(g[k, j, i], Equal(p[m, i] | p[m, j], w[m, i])).to_cnf() for m in range(n) for j in range(i)]
    c += [Implies(g[k, i, j], Equal(p[m, i] | p[m, j], w[m, i])).to_cnf() for m in range(n) for j in range(i + 1, n)]
    return c

# Connectivity constraint
def connectivity(g, n, d):
    kini = exprzeros(n, n)
    kend = exprones(n, n)
    c = []
    for i in range(n):
        kini[i, i] = expr(1)
    if d == 1:
        for i in range(n):
            c += kupdate(g, n, 0, i, kini, kend)
    else:
        km = exprvars('km', d - 1, n, n)
        for i in range(n):
            c += kupdate(g, n, 0, i, kini, km[0])
        for k in range(1, d - 1):
            for i in range(n):
                c += kupdate(g, n, k, i, km[k - 1], km[k])
        for i in range(n):
            c += kupdate(g, n, d - 1, i, km[d - 2], kend)
    return c

# used
def used(g, first, last, k, i):
    c = [g[k, i, j] for j in range(i + 1, last)] + [g[k, j, i] for j in range(first, i)]
    return Or(*c)

# oneDown Ehlers and Müller 2015
def oneDown(g, k, i, j):
    c = [g[k, l, j] for l in range(i, j)]
    return Or(*c)
    
# oneUp Ehlers and Müller 2015
def oneUp(g, k, i, j):
    c = [g[k, i, l] for l in range(i + 1, j)]
    return Or(*c)
    
# sorts_x update
def update(g, first, last, k, i, v, w):
    c = []
    c += [Or(~v[i], oneDown(g, k, first, i), w).to_cnf()]
    c += [Or(v[i], oneUp(g, k, i, last), ~w).to_cnf()]
    c += [Or(used(g, first, last, k, i), Equal(w, v[i])).to_cnf()]
    c += [Implies(g[k, j, i], Equal(w, v[j] & v[i])).to_cnf() for j in range(first, i)]
    c += [Implies(g[k, i, j], Equal(w, v[j] | v[i])).to_cnf() for j in range(i + 1, last)]
    return c

# sorts a single input
def sorts_x(g, n, kf, kl, x):
    y = vsort(x)
    if x == y:
        return []
    c = []
    first = 0
    last = n
    while x & (1<<first):
        first += 1
    while not (x & (1<<(last - 1))):
        last -= 1

    d = kl - kf
    xl = to_expr(x, n)
    yl = to_expr(y, n)
    if d == 0:
        pass
    elif d == 1:
        for i in range(first, last):
            c += update(g, first, last, kf, i, xl, yl[i])
    else:
        v = exprvars('v{}'.format(x), d - 1, (first, last))
        for i in range(first, last):
            c += update(g, first, last, kf, i, xl, v[0, i])
        for k in range(1, d - 1):
            for i in range(first, last):
                c += update(g, first, last, kf + k, i, v[k - 1], v[k, i])
        for i in range(first, last):
            c += update(g, first, last, kf + d - 1, i, v[d - 2], yl[i])
    return c

# Standard sort encoding (depth and size)
def sorts(g, n, kf, kl, xset):
    c = []
    for x in xset:
        c += sorts_x(g, n, kf, kl, x)
    return c


# Update for sorts_forward_size
def forward_size(g, n, k, v, s, t):
    c2 = []
    type1 = set()
    type3 = set()
    for i in range(n-1):
        for j in range(i+1, n):
            imask = 1<<i
            jmask = 1<<j
            if (not (v & imask)) and (v & jmask):
                type1.add((i, j))
            elif (v & imask) and (not (v & jmask)):
                w = v + jmask - imask
                c2.append(Implies(g[k, i, j], Equal(t[v], s[v] | s[w])).to_cnf())
            else:
                type3.add((i, j))

    if len(type1) > 0:
        cmp1 = [g[k, i, j] for i in range(n-1) for j in range(i+1, n) if (i, j) not in type1]
        c1 = [Or(*(cmp1 + [~t[v]]))]
    else:
        c1 = []

    if len(type3) > 0:
        cmp3 = [g[k, i, j] for i in range(n-1) for j in range(i+1, n) if (i, j) not in type3]
        c3 = [Or(*(cmp3 + [~t[v], s[v]])), Or(*(cmp3 + [t[v], ~s[v]]))]
    else:
        c3 = []
    return c1 + c2 + c3

# sorts_forward_size keeps track of the set of output vectors at each step (size only)
def sorts_forward_size(g, n, kf, kl, xlist):
    ninputs = 1 << n
    xset = set(xlist)
    input = [TRUE if v in xset or v == vsort(v) else FALSE for v in range(ninputs)]
    output = [TRUE if v == vsort(v) else FALSE for v in range(ninputs)]

    d = kl - kf
    c = []
    if d == 1:
        for v in range(ninputs):
            c += forward_size(g, n, kf, v, input, output)
    else:
        s = exprvars('s', d - 1, ninputs)
        for v in range(ninputs):
            c += forward_size(g, n, kf, v, input, s[0])
        for k in range(1, d - 1):
            for v in range(ninputs):
                c += forward_size(g, n, kf + k, v, s[k - 1], s[k])
        for v in range(ninputs):
            c += forward_size(g, n, kf + d - 1, v, s[d - 2], output)
    return c


# Update for sorts_backward_size
def backward_size(g, n, k, v, s, t):
    c = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            imask = 1<<i
            jmask = 1<<j
            if (not (v & imask)) and (v & jmask):
                w = v + imask - jmask
                c.append(Implies(g[k, i, j], Equal(t[v], s[w])).to_cnf())
            else:
                c.append(Implies(g[k, i, j], Equal(t[v], s[v])).to_cnf())
    return c

# sorts_backward_size keeps track of the unsorted input vectors at each step (size only)
def sorts_backward_size(g, n, kf, kl, xlist, s=0):
    ninputs = 1 << n
    c = []
    xset = set(xlist)
    
    # Input: TRUE for each input that is not sorted
    input = [TRUE if v != vsort(v) else FALSE for v in range(ninputs)]

    # Output variables
    o = exprvars('o', ninputs)
    if s == 0:
        # All sorted: 0 if already sorted by a prefix
        output = [0 if v in xset else o[v] for v in range(ninputs)]
    elif isinstance(s, (list, set)):
        # Exceptions: 1 to keep inputs in s unsorted
        output = [1 if v in s else 0 for v in range(ninputs)]
    else:
        # Fixed number of exceptions (unsorted inputs)
        output = o
        if s == 1:
            c_size = [Or(*output)]
            c_size += [~output[i] | ~output[j] for i in range(ninputs) for j in range(i+1, ninputs)]
        elif s > 1:
            card, c_size = Card(output, s+1)
            c_size += [~card[s]]
        c += c_size
    d = kl - kf
    # Backward layer iteration
    if d == 1:
        for v in range(ninputs):
            c += backward_size(g, n, kf, v, input, output)
    else:
        s = exprvars('s', d - 1, ninputs)
        for v in range(ninputs):
            c += backward_size(g, n, kl-1, v, input, s[0])
        for k in range(1, d - 1):
            for v in range(ninputs):
                c += backward_size(g, n, kl - k - 1, v, s[k - 1], s[k])
        for v in range(ninputs):
            c += backward_size(g, n, kl - d, v, s[d - 2], output)
    return c


# Update for sorts_forward_depth
def forward_depth(g, n, k, s, t, aux):
    c = []
    for i in range(n - 1):
        ninputs = 1 << n
        next = t if i == n - 2 else aux[i]
        prev = s if i == 0 else aux[i - 1]
        for v in range(ninputs):
            if v == vsort(v):
                c.append(next[v])
                continue
            cnot = []
            for j in range(i + 1, n):
                imask = 1<<i
                jmask = 1<<j
                if (not (v & imask)) and (v & jmask):
                    c.append(Implies(g[k, i, j], ~next[v]).to_cnf())
                    cnot.append(~g[k, i, j])
                elif (v & imask) and (not (v & jmask)):
                    w = v + jmask - imask
                    c.append(Implies(g[k, i, j], Equal(next[v], prev[v] | prev[w])).to_cnf())
                    cnot.append(~g[k, i, j])
            if len(cnot) > 0:
                c.append(Implies(And(*cnot), Equal(next[v], prev[v])).to_cnf())
            else:
                c.append(Equal(next[v], prev[v]).to_cnf())
    return c

#  sorts_forward_depth keeps track of the unsorted input vectors at each step (depth only)
def sorts_forward_depth(g, n, kf, kl, xlist, s=0):
    ninputs = 1 << n
    c = []
    xset = set(xlist)
    input = [TRUE if v in xset or v == vsort(v) else FALSE for v in range(ninputs)]
    output = [TRUE if v == vsort(v) else FALSE for v in range(ninputs)]
    d = kl - kf
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


# Update for sorts_backward_depth
def backward_depth(g, n, k, s, t, aux):
    c = []
    for i in range(n - 1):
        ninputs = 1 << n
        next = t if i == n - 2 else aux[i]
        prev = s if i == 0 else aux[i - 1]
        for v in range(ninputs):
            cnot = []
            for j in range(i + 1, n):
                imask = 1<<i
                jmask = 1<<j
                if (not (v & imask)) and (v & jmask):
                    w = v + imask - jmask
                    c.append(Implies(g[k, i, j], Equal(next[v], prev[w])).to_cnf())
                    cnot.append(~g[k, i, j])
            if len(cnot) > 0:
                c.append(Implies(And(*cnot), Equal(next[v], prev[v])).to_cnf())
            else:
                c.append(Equal(next[v], prev[v]).to_cnf())
    return c

#  sorts_backward_depth keeps track of the unsorted input vectors at each step (depth only)
def sorts_backward_depth(g, n, kf, kl, xlist=None, s=0):
    ninputs = 1 << n
    if xlist is None:
        xlist = range(ninputs)
    xset = set(xlist)
    c = []
    # FALSE for each input that is not sorted
    input = [TRUE if v != vsort(v) else FALSE for v in range(ninputs)]
    # all sorted
    o = exprvars('o', ninputs)
    if s == 0:
        output = [FALSE if v in xset else o[v] for v in range(ninputs)]
    elif isinstance(s, (list, set)):
        output = [TRUE if v in s else FALSE for v in range(ninputs)]
    else:
        output = o
        if s == 1:
            c_size = [Or(*output)]
            c_size += [~output[i] | ~output[j] for i in range(ninputs) for j in range(i+1, ninputs)]
        elif s > 1:
            card, c_size = Card(output, s+1, prefix='o_')
            c_size += [~card[s]]
        c += c_size
    d = kl - kf
    aux = exprvars('ly', d, n-2, ninputs) if n>2 else [None]
    if d == 1:
        c += backward_depth(g, n, kf, input, output, aux[0])
    else:
        s = exprvars('s', d - 1, ninputs)
        c += backward_depth(g, n, kl-1, input, s[0], aux[0])
        for k in range(1, d - 1):
            c += backward_depth(g, n, kl - k - 1, s[k - 1], s[k], aux[k])
        c += backward_depth(g, n, kl - d, s[d - 2], output, aux[d-1])
    return c


# Window size (Bundala 2014)
def window_size(x, n):
    first = 0
    last = n
    while x & (1 << first):
        first += 1
    while not (x & (1 << (last - 1))):
        last -= 1
    return last - first

# SAT encoding of valid fixed-depth sorting networks
def valid_depth(g, n, d0, d, s):
    clauses = []
    for k in range(d):
        clauses += once_depth(g, n, k)
    for k in range(1, d):
        clauses += no_redundant(g, n, k)
    for k in range(d0+1, d):
        clauses += independent_in_previous_layers(g, n, k)
    clauses += all_adjacent(g, n, d)
    # clauses += connectivity(g, n, d)
    clauses += last_layer(g, n, d)
    clauses += second_last_layer(g, n, d)
    if s == 0:
        clauses += no_adjacent_unused_channels(g, n, d)    # Not used for optimal fixed-size networks
    return clauses

# SAT encoding of valid fixed-depth exception networks
def valid_depth1(g, n, d):
    clauses = []
    for k in range(d):
        clauses += once_depth(g, n, k)
    for k in range(1, d):
        clauses += no_redundant(g, n, k)
        clauses += independent_in_previous_layers(g, n, k)
    return clauses

# SAT encoding of valid fixed-size sorting networks
def valid_size(g, n, d0, d):
    clauses = []
    for k in range(d):
        clauses += once_size(g, n, k)
    for k in range(1, d):
        clauses += no_redundant(g, n, k)
    for k in range(d0+1, d):
        clauses += ascending_order(g, n, k)
    clauses += all_adjacent(g, n, d)
    # clauses += connectivity(g, n, d)
    clauses += last_layer(g, n, d)
    clauses += second_last_layer(g, n, d)
    return clauses

# SAT encoding of valid fixed-size exception networks
def valid_size1(g, n, d):
    clauses = []
    for k in range(d):
        clauses += once_size(g, n, k)
    for k in range(1, d):
        clauses += no_redundant(g, n, k)
        clauses += ascending_order(g, n, k)
    return clauses
