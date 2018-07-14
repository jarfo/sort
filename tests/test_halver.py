import unittest
from halver import Halver


class TestHalverModule(unittest.TestCase):

    def test_is_halver(self):
        n = 12
        net = Halver([
            [(0, 4), (1, 2), (3, 9), (5, 10), (6, 11), (7, 8)],
            [(0, 6), (1, 3), (2, 8), (4, 7), (9, 11)],
            [(2, 5), (3, 4), (6, 10), (7, 9)],
            [(4, 6), (5, 7)]])
        self.assertEqual(net.channels(), n)
        self.assertEqual(net.depth(), 4)
        self.assertEqual(net.size(), 17)
        self.assertTrue(net.is_halver(n, epsilon=1/4))
        self.assertFalse(net.is_halver(n, epsilon=1/5))
