import unittest
from network import Network


class TestNetworkModule(unittest.TestCase):

    def test_read(self):
        n = 17
        net = Network()
        net.read([
            [6, 12], [5, 10], [8, 13], [1, 15], [3, 17], [2, 16], [4, 9], [7, 14], 
            [4, 11], [9, 14], [5, 8], [10, 13], [1, 3], [15, 17], [2, 7], [11, 16], 
            [4, 6], [12, 14], [1, 5], [13, 17], [2, 4], [14, 16], [1, 2], [16, 17], 
            [3, 10], [8, 15], [6, 11], [7, 12], [6, 8], [7, 9], [9, 11], [3, 4], [9, 15], 
            [10, 12], [13, 14], [5, 7], [11, 15], [5, 6], [8, 10], [12, 14], [2, 3], 
            [15, 16], [2, 9], [14, 16], [2, 5], [3, 6], [12, 15], [14, 15], [3, 5], 
            [7, 13], [10, 13], [4, 11], [4, 9], [7, 8], [11, 13], [4, 7], [4, 5], 
            [13, 14], [11, 12], [6, 7], [12, 13], [5, 6], [8, 9], [9, 10], [7, 9], 
            [10, 12], [6, 8], [10, 11], [7, 8], [9, 10], [8, 9]], first=1)
        self.assertEqual(net.channels(), 17)
        self.assertEqual(net.depth(), 22)
        self.assertEqual(net.size(), 71)
        self.assertTrue(net.sorts(n, log=True))

    def test_sorts(self):
        net = Network([[(0, 1), (2, 3), (4, 5)], [(1, 6), (3, 5)], [(0, 3), (2, 4), (5, 6)],
                       [(0, 2), (1, 4), (3, 5)], [(1, 2), (3, 4)], [(0, 1), (2, 3), (4, 5)]])
        self.assertTrue(net.sorts(7, log=True))
        net = Network([[(0, 1), (2, 3), (4, 5)], [(1, 6), (3, 5)], [(0, 3), (2, 4), (5, 6)],
                       [(0, 2), (1, 4), (3, 5)], [(1, 2), (3, 4)], [(0, 1), (2, 3), (4, 5)]])
        self.assertFalse(net.sorts(8, log=False))
        net = Network([[(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)], [(0, 3), (1, 4), (5, 8), (6, 9)],
                       [(0, 2), (3, 6), (7, 9)], [(0, 1), (2, 4), (5, 7), (8, 9)],
                       [(1, 2), (3, 5), (4, 6), (7, 8)], [(1, 3), (2, 5), (4, 7), (6, 8)],
                       [(2, 3), (6, 7)], [(3, 4), (5, 6)], [(4, 5)]])
        self.assertTrue(net.sorts(10))

    def test_latex(self):
        net = Network([[(0, 1), (2, 3), (4, 5)], [(1, 6), (3, 5)], [(0, 3), (2, 4), (5, 6)],
                       [(0, 2), (1, 4), (3, 5)], [(1, 2), (3, 4)], [(0, 1), (2, 3), (4, 5)]])
        self.assertEqual(net.latex(),
r"""
\begin{figure}[htb]
    \centering
    \begin{sortingnetwork}{7}{0.7}
        \nodeconnection{ {0, 1}, {2, 3}, {4, 5}}
        \addtocounter{sncolumncounter}{2}
        \nodeconnection{ {1, 6}}
        \nodeconnection{ {3, 5}}
        \addtocounter{sncolumncounter}{2}
        \nodeconnection{ {0, 3}, {5, 6}}
        \nodeconnection{ {2, 4}}
        \addtocounter{sncolumncounter}{2}
        \nodeconnection{ {0, 2}, {3, 5}}
        \nodeconnection{ {1, 4}}
        \addtocounter{sncolumncounter}{2}
        \nodeconnection{ {1, 2}, {3, 4}}
        \addtocounter{sncolumncounter}{2}
        \nodeconnection{ {0, 1}, {2, 3}, {4, 5}}
    \end{sortingnetwork}
    \caption{Optimal filter on $7$ channels with $6$ layers and $16$ comparators}
    \label{fig:optimal7}
\end{figure}
""")

    def test_standarize(self):
        net = Network([[(4, 1), (3, 2)], [(1, 3), (2, 4)], [(1, 2), (3, 4)]])
        net.standarize()
        self.assertEqual(net, [[(1, 4), (2, 3)], [(1, 3), (2, 4)], [(1, 2), (3, 4)]])

    def test_reflected(self):
        net = Network([[(0, 1)], [(1, 2)], [(0, 1), (2, 3)]])
        self.assertEqual(net.reflected(), [[(2, 3)], [(1, 2)], [(0, 1), (2, 3)]])
