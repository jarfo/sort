import time
import subprocess
import argparse
import ast
import sys
from pyeda.inter import Or, And, exprvars, expr2dimacscnf, ConjNormalForm

from cardinality import Card
from network import Network
from sorting import (variables, valid_size, valid_depth, valid_depth1, valid_size1, sorts, sorts, sorts_forward_size, sorts_backward_size, 
    sorts_forward_depth, sorts_backward_depth, window_size, to_network)
from halver import to_ehalver, valid_ehalver, halver, Halver
import dimacs


tproc = time.process_time()
tmono = time.monotonic()

def elapsed_time(m="Elapsed time:"):
    return "(Process: {:.2f} s, Elapsed: {:.2f} s)".format(time.process_time() - tproc, time.monotonic() - tmono)

def search(n, d, s, u=0, epsilon=1/4, opt='d', solver='picosat', lprefix=None, wsize=0, task=None, nthreads=4):

    if wsize <= 0:
        wsize = n + wsize

    print("n:", n, "d:", d, "s:", s, "u:", u, "opt:", opt, "solver:", solver,
          "wsize:", wsize, "task:", task, "prefix:", lprefix, "nthreads:", nthreads, file=sys.stderr)

    if opt.startswith('h'):
        # Comparator variables
        g = variables(n, d)
        
        # Empty prefix
        c_prefix = []

        # valid constraints
        c_valid = valid_depth1(g, n, d)

        # size constraints
        if s:
            ncard = s
            gcard = [g[k, i, j] for i in range(n) for j in range(i+1, n) for k in range(d)]
            c, c_size = Card(gcard, ncard + 1, prefix='g_')
            if len(c) > ncard:
                c_size += [~c[ncard]]
        else:
            c_size = []

        c_sorts = halver(g, n, 0, d, epsilon)

    elif opt.startswith('e'):
        m = n//2
        g = exprvars('g', d*m, m)
        c_valid = valid_ehalver(g, n, d)
        c_prefix = [g[i, m+i] for i in range(m)]
        d0 = 1
        c_size = []
        net = Network(to_ehalver(c_prefix, g, n, d0))
        xlist = net.outputs(n, range(1<<n))
        c_sorts = halver(g, n, d0, d, epsilon, xlist)

    elif opt.startswith('s1'):
        d = s
        g = variables(n, d)
        c_prefix = []
        c_valid = valid_size1(g, n, d)
        c_size = []
        c_sorts = sorts_backward_size(g, n, 0, d, [], u)

    elif opt.startswith('s'):
        d = s
        g = variables(n, d)

        if lprefix is None:
            lprefix  = [[(0, 1)]]
            c_prefix = [g[k, i, j] if (i, j) in layer else ~g[k, i, j] for k, layer in enumerate(lprefix) for i in range(n-1) for j in range(i+1, n)]
            if n > 3:
                c_prefix.append(Or(g[1, 0, 2], g[1, 2, 3]))
        else:
            c_prefix = [g[k, i, j] if (i, j) in layer else ~g[k, i, j] for k, layer in enumerate(lprefix) for i in range(n-1) for j in range(i+1, n)]
        net = Network(lprefix)
        d0 = len(net)

        c_valid = valid_size(g, n, d0, d)

        c_size = []

        inputs = net.not_sorted(n)
        inputs = [x for x in inputs if window_size(x, n) > 2 and window_size(x, n) <= wsize]
        xlist = net.outputs(n, inputs)

        print("d0:", d0, "len(xlist):", len(xlist), file=sys.stderr)
        c_sorts = sorts(g, n, d0, d, xlist)

    elif opt.startswith('d1'):
        g = variables(n, d)

        c_valid = valid_depth1(g, n, d)

        c_prefix = []

        if s:
            c, c_size = Card([g[k, i, j] for i in range(0, n) for j in range(i+1, n) for k in range(d)], s+1, prefix='g_')
            c_size += [~c[s]]
        else:
            c_size = []

        c_sorts = sorts_backward_depth(g, n, 0, d, None, u)

    else:
        # Comparator variables
        g = variables(n, d)

        # Prefix constraints
        if lprefix is None:
            lprefix  = [[(i, n-i-1) for i in range(n//2)]]
        sprefix = sum(len(layer) for layer in lprefix)
        c_prefix = [g[k, i, j] if (i, j) in layer else ~g[k, i, j] for k, layer in enumerate(lprefix) for i in range(n-1) for j in range(i+1, n)]
        net = Network(lprefix)
        d0 = len(net)

        # valid constraints
        c_valid = valid_depth(g, n, d0, d, s)

        # size constraints
        if s:
            ncard = s - sprefix
            gcard = [g[k, i, j] for i in range(n) for j in range(i+1, n) for k in range(d0, d)]
            c, c_size = Card(gcard, ncard + 1, prefix='g_')
            if len(c) > ncard:
                c_size += [~c[ncard]]
        else:
            c_size = []

        inputs = net.not_sorted(n)
        inputs = [x for x in inputs if window_size(x, n) > 2 and window_size(x, n) <= wsize]
        xlist = net.outputs(n, inputs)
        print("d0:", d0, "len(xlist):", len(xlist), file=sys.stderr)
        c_sorts = sorts(g, n, d0, d, xlist)

    print("c_valid:  ", len(c_valid), elapsed_time(), file=sys.stderr)
    print("c_prefix: ", len(c_prefix), elapsed_time(), file=sys.stderr)
    print("c_size:   ", len(c_size),  elapsed_time(), file=sys.stderr)
    print("c_sorts:  ", len(c_sorts), elapsed_time(), file=sys.stderr)
    clauses = c_valid + c_prefix + c_sorts + c_size
    constraint = And(*clauses)
    print("Is cnf?", constraint.is_cnf(), "Size: ", len(clauses), elapsed_time(), file=sys.stderr)

    while True:
        if solver == "picosat":
            point = constraint.satisfy_one()
            res = point is not None
        else:
            litmap, cnf = expr2dimacscnf(constraint)
            task = task if task is not None else int(time.monotonic())
            dimacscnf = "dimacscnf_{}.txt".format(task)
            litmapcnf = "litmap_{}.txt".format(task)
            with open(dimacscnf, "wt") as fp:
                print(cnf, file=fp)
            with open(litmapcnf, "wt") as fp:
                print(litmap, file=fp)
            ofile = "output_{}_{}_{}_{}.txt".format(n, d, s, task)
            with open(ofile+".log", "wt") as out:
                if solver == "minisat":
                    subprocess.call(["minisat", dimacscnf, ofile], stdout=out)
                elif solver == "glucose":
                    subprocess.call(["../../glucose-syrup-4.1/simp/glucose_release", "-model", dimacscnf], stdout=out)
                elif solver == "glucose-syrup":
                    subprocess.call(["../../glucose-syrup-4.1/parallel/glucose-syrup_release", "-nthreads={}".format(nthreads), "-model", dimacscnf, ofile], stdout=out)
                else:
                    subprocess.call(["../../cryptominisat-5.0.1/cryptominisat5", "-t", str(nthreads), dimacscnf], stdout=out)
            if solver == "minisat":
                res, soln = dimacs.read(ofile, minisat=True)
            else:
                res, soln = dimacs.read(ofile+".log")
            point = ConjNormalForm.soln2point(soln, litmap)

        print("len(point): ", len(point) if point else None, elapsed_time(), file=sys.stderr)

        if res is None:
            return 'UNDETERMINED'
        elif not res:
            return 'UNSATISFIABLE'
        else:
            if opt.startswith('h'):
                net = Halver(to_network(point, g, n, d))
                return net
            elif opt.startswith('e'):
                net = Halver(to_ehalver(point, g, n, d))
                return net
            else:
                net = to_network(point, g, n, d)
                xnew = net.not_sorted(n, log=False)
            
                if len(xnew) == u or opt not in ['d', 's']:
                    return net
                else:
                    m = 16
                    print("Unsorted:", len(xnew), file=sys.stderr)
                    new_clauses = sorts(g, n, d0, d, xnew[:m])
                    clauses += new_clauses
                    constraint = And(*clauses)


def main():
    parser = argparse.ArgumentParser(description='Optimal sorting networks.')
    parser.add_argument('-n', '--channels', type=int, default=4)
    parser.add_argument('-d', '--depth', type=int, default=3)
    parser.add_argument('-s', '--size', type=int, default=0)
    parser.add_argument('-u', '--exceptions', type=int, default=0)
    parser.add_argument('-e', '--epsilon', metavar='eps', type=float, default=1/4)
    parser.add_argument('-o', '--opt', type=str, default='d')
    parser.add_argument('-l', '--solver', type=str, default='picosat')
    parser.add_argument('-p', '--prefix', type=str, default=None)
    parser.add_argument('-w', '--window', type=int, default=0)
    parser.add_argument('-t', '--task', type=str, default=None)
    parser.add_argument('-c', '--nthreads', type=int, default=4)

    args = parser.parse_args()

    if args.prefix is not None:
        prfx = args.prefix.lower()
        if prfx.startswith('green'):
            n = args.channels
            ginfo = prfx.split(',')
            nlayers = int(ginfo[1]) if len(ginfo) == 2 else (n-1).bit_length()
            prefix = []
            for p in range(nlayers):
                d = 1<<p
                prefix.append([(i+j, i+j+d) for j in range(0, n-d, 2*d) for i in range(0, d) if i+j+d < n])
        else:
            prefix = ast.literal_eval(args.prefix)
    else:
        prefix = None

    net = search(args.channels, args.depth, args.size, args.exceptions, args.epsilon, args.opt, args.solver, prefix, args.window, args.task, args.nthreads)

    print(net, file=sys.stderr)
    if not isinstance(net, str):
        print("Size:", net.size(), "Depth:", net.depth(), file=sys.stderr)
        if args.opt.startswith('h') or args.opt.startswith('e'):
            print("halver(args.epsilon)?", net.is_halver(args.channels, args.epsilon, log=True))
        else:
            xnew = net.not_sorted(args.channels, log=True)
            print("sorts?", len(xnew) == 0, file=sys.stderr)

    print(net)

if __name__ == '__main__':
    main()
