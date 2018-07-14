import sys
from random import shuffle


class Permutation(dict):
    def __missing__(self, key):
        res = self[key] = key
        return res

def to_bit(d, n):
    return "{0} ({0:0{1}b})".format(d, n)

def vsort(v:int):
    return int("".join(sorted("{:b}".format(v))), 2)

class Network(list):
    def read(self, str, format='ll', first=0):
        self.clear()
        layer = []
        used_channels = set()
        for i, j in str:
            if i in used_channels or j in used_channels:
                self.append(layer)
                layer = []
                used_channels.clear()
            layer.append((i - first, j - first))
            used_channels.update((i, j))
        if layer:
            self.append(layer)
        return self

    def save(self, format='ehlers', **kwargs):
        for ilayer, layer in enumerate(self):
            for cmp in layer:
                print('{0};{1};{2};'.format(ilayer, cmp[0], cmp[1]), end='', **kwargs)
        print()

    def latex(self, simple=False, n=0):
        n = self.channels(n)
        figure = ""
        if not simple:
            figure += "\n"
            figure += "\\begin{figure}[htb]\n"
            figure += "    \\centering\n"
        figure += "    \\begin{sortingnetwork}{" + str(n) + "}{0.7}\n"
        for ilayer, layer in enumerate(self):
            layer_list = [""] if len(layer) else []
            used_inputs = [set()]
            for c in layer:
                i = 0
                while c[0] in used_inputs[i] or c[1] in used_inputs[i]:
                    i += 1
                    if i >= len(used_inputs):
                        layer_list.append("")
                        used_inputs.append(set())
                if len(layer_list[i]) > 0:
                     layer_list[i] += ", "
                layer_list[i] += "{" + str(c[0]) + ", " + str(c[1]) + "}"
                for l in range(c[0], c[1]):
                    used_inputs[i].add(l)
            for l in layer_list:
                figure += "        \\nodeconnection{ " + l + "}\n"
            if ilayer != len(self) - 1:
                figure += "        \\addtocounter{{sncolumncounter}}{{{}}}\n".format(2 if len(self[ilayer+1]) else 3)
        figure += "    \\end{sortingnetwork}\n"
        if not simple:
            figure += "    \\caption{Optimal filter on $" + str(n) + "$ channels"
            figure += " with $" + str(len(self)) + "$ layers"
            figure += " and $" + str(sum(len(layer) for layer in self)) + "$ comparators}\n"
            figure += "    \\label{fig:optimal" + str(n) + "}\n"
            figure += "\\end{figure}\n"

        return figure
        
    def svg(self):
        scale = 1
        xscale = scale * 35
        yscale = scale * 20

        inner_result = ''
        x = 0
        n = 0
        for layer in self:
            used_inputs = set()
            x += xscale
            for c in layer:
                if c[0] in used_inputs or c[1] in used_inputs:
                    x += xscale / 3
                y0 = yscale + c[0] * yscale
                y1 = yscale + c[1] * yscale
                inner_result += "<circle cx='%s' cy='%s' r='%s' style='stroke:black;stroke-width:1;fill=yellow' />" % (
                x, y0, 3)
                inner_result += "<line x1='%s' y1='%s' x2='%s' y2='%s' style='stroke:black;stroke-width:%s' />" % (
                x, y0, x, y1, 1)
                inner_result += "<circle cx='%s' cy='%s' r='%s' style='stroke:black;stroke-width:1;fill=yellow' />" % (
                x, y1, 3)
                for l in range(c[0], c[1]):
                    used_inputs.add(l)
                n = max(n, c[0], c[1])

        w = x + xscale
        n += 1
        h = (n + 1) * yscale
        result = "<?xml version='1.0' encoding='utf-8'?>"
        result += "<!DOCTYPE svg>"
        result += "<svg width='%spx' height='%spx' xmlns='http://www.w3.org/2000/svg'>" % (w, h)
        for i in range(0, n):
            y = yscale + i * yscale
            result += "<line x1='%s' y1='%s' x2='%s' y2='%s' style='stroke:black;stroke-width:%s' />" % (0, y, w, y, 1)
        result += inner_result
        result += "</svg>"
        return result

    def output(self, x):
        for layer in self:
            for c in layer:
                imask = 1 << c[0]
                jmask = 1 << c[1]
                if (x & jmask) and (not (x & imask)):
                    x += imask - jmask
        return x

    def outputs(self, n:int, input=None):
        if input is None:
            input = range(1<<n)
        outs = {self.output(x) for x in input}
        return list(outs)

    def sorts(self, n, log=False):
        for x in range(1<<n):
            if self.output(x) != vsort(x):
                if log:
                    print(to_bit(x, n), '->', to_bit(self.output(x), n), 'Fails', file=sys.stderr)
                return False
        return True

    def not_sorted(self, n, log=False):
        shuffled = list(range(1<<n))
        shuffle(shuffled)
        xlist = []
        for d in shuffled:
            if self.output(d) != vsort(d):
                if log:
                    print(to_bit(d, n), '->', to_bit(self.output(d), n), 'Fails')
                xlist.append(d)
        return xlist

    def channels(self, n=0):
        if n == 0:
            if self.size() == 0:
                n = 1
            else:
                n = max(max(i, j) for layer in self for i, j in layer) + 1
        return n

    def depth(self):
        return len(self)

    def size(self):
        return sum(len(layer) for layer in self)

    def permute(self, first, p):
        perm = Permutation(p)
        for k in range(first, self.depth()):
            layer = self[k]
            for m in range(len(layer)):
                i, j = layer[m]
                layer[m] = (perm[i], perm[j])

    def standarize(self):
        for k in range(self.depth()):
            layer = self[k]
            for m in range(len(layer)):
                i, j = layer[m]
                if i > j:
                    self.permute(k+1, {i:j, j:i})
                    layer[m] = (j, i)
            self[k] = sorted(self[k])

    def reflected(self, n=0):
        n = self.channels(n)
        return Network([sorted((n - 1 - j, n - 1 - i) for i, j in layer) for layer in self])

    def maxpath(self, n=0):
        n = self.channels(n)
        cn = (c for layer in self for c in layer)
        max = 0
        for k in range(n):
            nmax = 0
            nmin = 0
            imax = k
            imin = k
            # Follow max path
            for i, j in cn:
                if i == imax:
                    nmax += 1
                    imax = j
                elif j == imax:
                    nmax += 1

                if i == imin:
                    nmin += 1
                elif j == imin:
                    nmin += 1
                    imin = i
            if nmin  > max:
                max = nmin
            if nmax > max:
                max = nmax
        return max
