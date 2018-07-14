from itertools import product, combinations_with_replacement
from collections import Counter


def paths(n):
    for channels in product(['12', '21'], repeat=n//2):
        yield "".join(channels)


def stick(n):
    assert n % 2 == 0
    return [w for w in paths(n) if w <= w[::-1]]


def head(n):
    assert n % 2 == 1
    return ['0' + w for w in paths(n-1)]


def tail(n):
    assert n % 2 == 0
    return ['0' + w + '0' for w in stick(n-2) if n > 2]


def nchannels(word):
    n = len(word)
    return n if word[-1] != 'c' else n - 1
    
    
def rot_and_rev(wordc, channels=None):
    n = len(wordc) - 1
    c = wordc[-1]
    word = wordc[:-1]

    wrd2 = word + word
    rev2 = wrd2[::-1]
    if channels is None:
        wrd = min(wrd2[k:k+n] for k in range(0, n-1, 2))
        rev = min(rev2[k:k+n] for k in range(0, n-1, 2))
        return min(wrd, rev) + c
    else:
        chn2 = channels + channels
        rch2 = chn2[::-1]
        wrd = min((wrd2[k:k+n] + c, chn2[k:k+n]) for k in range(0, n-1, 2))
        rev = min((rev2[k:k+n] + c, rch2[k:k+n]) for k in range(0, n-1, 2))
        return min(wrd, rev)


def cycle(n):
    assert n >= 2
    assert n % 2 == 0
    rwords = ['12' + w + 'c' for w in paths(n-2)]
    return [w for w in rwords if w <= rot_and_rev(w)]

    
def net(word):
    layers = [[], []]

    n = len(word)
    if word[-1] == 'c':
        n -= 1
        cycle = True
    else:
        cycle = False

    if word[-1] != '0':
        layers[0] = [(i, i+1) for i in range(0, n-1, 2)]
    else:
        layers[0] = [(i, i+1) for i in range(0, n-3, 2)]

    first = 1
    last = n - 1
    if word[0] == '0':
        first = 2
        if n > 1:
            layers[1].append((int(word[1]) - 1, n - 1))
            if word[-1] == '0':
                last = n - 2
                layers[1].append((n - 5 + int(word[last]), n - 2))


    for k in range(first, last, 2):
        p = (k - first)
        layers[1].append((p + int(word[k]) - 1, p + int(word[k+1]) + 1))

    if cycle:
        layers[1].append((0, n - 3 + int(word[last])))

    layers[1] = sorted(layers[1])

    return layers


def network(sentence):
    cnet = [[], []]
    n = 0
    for word in sorted(sentence, reverse=True):
        new_n = nchannels(word)
        new_net = net(word)
        cnet[0] += [(i+n, j+n) for i, j in new_net[0]]
        cnet[1] += [(i+n, j+n) for i, j in new_net[1]]
        n += new_n
    return cnet


def sentence(net, n=0, permutation=False):
    if len(net) < 2:
        net.append([])
    cochannel = [dict(), dict()]
    channel = dict()
    # unused in first layer
    unused = []
    for i, j in net[0]:
        channel[i] = '1'
        channel[j] = '2'
        cochannel[0][i] = j
        cochannel[0][j] = i
        n = max(n, i+1, j+1)

    for i, j in net[1]:
        if i not in channel:
            channel[i] = '0'
            unused.append(i)
        if j not in channel:
            channel[j] = '0'
            unused.append(j)
        cochannel[1][i] = j
        cochannel[1][j] = i
        n = max(n, i+1, j+1)

    visited = set()
    def word(i):
        chan = []
        while i is not None and i not in visited:
            chan.append(i)
            visited.add(i)
            if i in unused:
                i = cochannel[1][i]
            else:
                i = cochannel[0][i]
                chan.append(i)
                visited.add(i)
                i = cochannel[1][i] if i in cochannel[1] else None

        word = ''.join(channel[i] for i in chan)
        return word, chan

    sp = []
    # head and tail words
    for i in unused:
        if not i in visited:
            w, c = word(i)
            if w[-1] == '0' and w[::-1] < w:
                w = w[::-1]
                c = c[::-1]
            sp.append((w, c))

    # stick words
    for i, j in net[0]:
        # search unused channels in second layer
        if i in cochannel[1]:
            i = j
        if not i in visited and not i in cochannel[1]:
            w, c = word(i)
            if w[::-1] < w:
                w = w[::-1]
                c = c[::-1]
            sp.append((w, c))

    # cycle words
    for i, j in net[0]:
        if not i in visited:
            w, c = word(i)
            sp.append(rot_and_rev(w + 'c', c))

    # unused channels
    for i in range(n):
        if i not in cochannel[0] and i not in cochannel[1]:
            sp.append(('0', [i]))

    sp = sorted(sp)
    s = [w for w, c in sp]

    if permutation:
        perm = {}
        index = 0
        for w, c in reversed(sp):
            n = index + nchannels(w)
            count = 0
            for i, (letter, ch) in enumerate(zip(w, c)):
                if letter == '0':
                    if i == 0:
                        perm[ch] = n-1
                    else:
                        perm[ch] = n-2
                elif letter == '1':
                    perm[ch] = index
                    count += 1
                else:
                    perm[ch] = index + 1
                    count += 1

                if count == 2:
                    index += 2
                    count = 0
            index = n

        return s, perm
    else:
        return s


def reflected(sentence):
    s = []
    for word in sentence:
        word = word.translate(str.maketrans('12','21'))
        if word[-1] == 'c':
            # cycle
            word = rot_and_rev(word)
        elif word[0] != '0' or word[-1] == '0':
            # stick or tail
            word = min(word, word[::-1])
        s.append(word)
    return sorted(s)


def partitions(n, I=1):
    yield (n,)
    for i in range(I, n//2 + 1):
        for p in partitions(n-i, i):
            yield (i,) + p


def sets(n, maximal=True, redundant=False):
    if n%2 == 1:
        words = head(n)
    else:
        words = stick(n)
        if redundant or n > 2:
            words += cycle(n)
        if not maximal:
            words += tail(n)
    return words

def is_empty(sentence):
    for word in sentence:
        if word != '0' and word != '12':
            return False
    return True


def is_saturated(sentence):
    nwords = len(sentence)
    nheads = 0
    ncycles = 0
    nzeroes = 0
    n12s = 0
    last = 0
    for word in sentence:
        if word == '0':
            # zero
            nzeroes += 1
            nheads += 1
        elif word[0] == '0' and word[-1] == '0':
            # no tails in maximal networks
            return False
        elif word[0] == '0':
            # count heads
            nheads += 1
            if last:
                if word[-1] != last:
                    # Every head or stick ends with the same index
                    return False
            else:
                last = word[-1]
        elif word[-1] == 'c':
            # count cycles
            ncycles += 1
        elif word == '12':
            n12s += 1
        elif len(word) == 4:
            # No stick has length 4
            return False
        elif word[0] != word[-1]:
            # Every stick begins and ends with the same symbol
            return False
        elif last:
            if word[-1] != last:
                # Every head or stick ends with the same index
                return False
        else:
            last = word[-1] 

    if nheads > 1:
        # less than one head in maximal networks
        return False
    if (n12s or nzeroes) and ncycles != nwords - 1:
        # I contains '0' or '12' then all other words are cycles
        return False
    return True 
    
    
def sentences(n, maximal=False, saturated=False, keep_redundant=False, keep_reflection=False, keep_empty=False):
    maximal = maximal or saturated
    for partition in partitions(n):
        counter = Counter(partition)
        nheads = sum(p%2 for p in partition)
        if maximal and nheads > 1:
            continue
        combs = [combinations_with_replacement(sets(size, maximal, keep_redundant), nsize) for size, nsize in counter.most_common()]
        for comb in product(*combs):
            sentence = sorted([word for wset in comb for word in wset])
            if saturated and not is_saturated(sentence):
                continue
            if not keep_empty and is_empty(sentence):
                continue
            if keep_reflection or tuple(sentence) <= tuple(reflected(sentence)):    
                yield sentence


def networks(*args, **kwargs):
    for sentence in sentences(*args, **kwargs):
        yield network(sentence)


if __name__ == '__main__':

    if 0:
        print("|H^1_n|", end=' ')
        a=(0, 1)
        print(a[0], end=',')
        print(a[1], end=',')
        for i in range(3, 20, 1):
            print(i*(i-3) + 4, end=',')
        print()
        exit()
        
        from network import Network
        from numpy.random import permutation
        s = sorted(['0120','012','1221','1221c'])
        snet = Network(network(s))
        graph = snet.reflected().latex(simple=True)
        print(graph)
        print(s)
    #    p = permutation(snet.channels())
    #    perm = {i:p[i] for i in range(snet.channels())}
    #    snet.permute(0, perm)
    #    snet.standarize()
    #    graph = snet.reflected().latex(simple=True)
        graph = snet.latex(simple=True)
        print(graph)
        sr = reflected(s)
        print(sr)
        snet = Network(network(sr))
        graph = snet.reflected().latex(simple=True)
        print(graph)
        print(min(tuple(s), tuple(sr)))
        exit(0)

        from util.count import count
        print("head:", end=' ')
        for i in range(1, 6, 2):
            print(count(head(i)), end=',')
        print()
        print("tail:", end=' ')
        for i in range(2, 33, 2):
            print(count(tail(i)), end=',')
        print()
        print("stick:", end=' ')
        for i in range(2, 33, 2):
            print(count(stick(i)), end=',')
        print()
        print("cycle:", end=' ')
        for i in range(2, 33, 2):
            print(count(cycle(i)), end=',')
        print()

        n = 5
        sent=''
        for j, s in sorted(enumerate(sentences(n, keep_redundant=True, keep_reflection=True))):
            sent += '$\\sent{{({})}}$'.format(','.join(s))
            snet = Network(network(s))
            graph = snet.reflected().latex(simple=True, n=n)
            print(graph, end='')

            if j%5 < 4:
                sent += ' & '
                print('    &')
            else:
                print('    \\\\')
                print(sent)
                sent = ''
                print('    \\\\')
                print('    \\\\')
        if sent != '':
            print('    \\\\')
            print(sent)
        exit(0)
        
        from network import Network
        for i in range(2, 9, 2):
            words = cycle(i)
            for j, w in enumerate(words):
                if j > 0: print('    &')
                s = [w]
                n = Network(network(s))
                print(n.reflected().latex(simple=True))
            print('    \\\\')
            for j, w in enumerate(words):
                if j > 0: print(' &' , end='')
                print('$\\sent{{{}}}$'.format(w) , end='')
            print('    \\\\')
            print('    \\\\')
        exit(0)

    from util.count import count
    print("head:", end=' ')
    for i in range(1, 32, 2):
        print(count(head(i)), end=',')
    print()
    print("tail:", end=' ')
    for i in range(2, 33, 2):
        print(count(tail(i)), end=',')
    print()
    print("stick:", end=' ')
    for i in range(2, 33, 2):
        print(count(stick(i)), end=',')
    print()
    print("cycle:", end=' ')
    for i in range(2, 33, 2):
        print(count(cycle(i)), end=',')
    print()


    endstr = ' & '
    nmin = 18
    nmax = 27
    fmt = lambda x: '{:,}'.format(x).replace(',', '{,}')

    print("|G_n|", end=endstr)
    a=(1, 2)
    for i in range(3, nmax, 1):
        a = a[-1], a[-1] + (i-1)*a[-2]
        if n >= nmin:
            print(fmt(a[-1]), end=endstr)
    print()

    print("|R(H_n)|", end=endstr)
    for i in range(nmin, nmax, 1):
        print(fmt(count(sentences(i, keep_redundant=True, keep_empty=True, keep_reflection=True))), end=endstr)
    print()

    print("|R(T_n)|", end=endstr)
    for i in range(nmin, nmax, 1):
        print(fmt(count(sentences(i, keep_reflection=True))), end=endstr)
    print()

    print("|R(T'_n)|", end=endstr)
    for i in range(nmin, nmax, 1):
        print(fmt(count(sentences(i, keep_reflection=False))), end=endstr)
    print()

    print("|R(G_n)|", end=endstr)
    for i in range(nmin, nmax, 1):
        print(fmt(count(sentences(i, maximal=True, keep_redundant=True, keep_empty=True, keep_reflection=True))), end=endstr)
    print()

    print("|R(S_n)|", end=endstr)
    for i in range(nmin, nmax, 1):
        print(fmt(count(sentences(i, saturated=True, keep_reflection=True))), end=endstr)
    print()

    print("|R(S'_n)|", end=endstr)
    for i in range(nmin, nmax, 1):
        print(fmt(count(sentences(i, saturated=True, keep_reflection=False))), end=endstr)
    print()
