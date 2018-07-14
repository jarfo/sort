import unittest
from solver import search

# def search(n, d, s, u=0, epsilon=1/4, opt='d', solver='picosat', lprefix=None, wsize=0, task=None, nthreads=4)

class TestSolverModule(unittest.TestCase):

    def test_search_d(self):
        opt = 'd'
        for n, d, s in [(3, 3, 3), (4, 3, 5), (5, 5, 9), (6, 5, 12)]:
            net = search(n, d, s, opt=opt)
            self.assertTrue(net.sorts(n, log=True))
            self.assertEqual(net.depth(), d)
            self.assertEqual(net.size(), s)

            net = search(n, d-1, s, opt=opt)
            self.assertTrue(net, 'UNSATISFIABLE')
    
            net = search(n, d, s-1, opt=opt)
            self.assertTrue(net, 'UNSATISFIABLE')
    
            net = search(n, d, 0, opt=opt)
            print(net)
            self.assertTrue(net.sorts(n, log=True))
            self.assertEqual(net.depth(), d)

            net = search(n, d-1, 0, opt=opt)
            self.assertTrue(net, 'UNSATISFIABLE')

    def test_search_s(self):
        opt = 's'
        for n, s in [(3, 3), (4, 5), (5, 9), (6, 12)]:
            net = search(n, 0, s, opt=opt)
            print(net)
            self.assertTrue(net.sorts(n, log=True))
            self.assertEqual(net.size(), s)

            net = search(n, 0, s-1, opt=opt)
            self.assertTrue(net, 'UNSATISFIABLE')


