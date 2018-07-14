from __future__ import print_function
import unittest
import tempfile
import os.path
from dimacs import read


class TestDimacsModule(unittest.TestCase):

    def test_read(self):
        output = r"""
c Mem used                 : 7704.77     MB
c Total time               : 33950.85
s SATISFIABLE
v 1 -2 -3 -4 -5
v -23 -24 -25 -26
"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpfile = os.path.join(tmpdirname, "TestDimacsModule.read")
            with open(tmpfile, mode='wt') as tmp:
                print(output, file=tmp)
            self.assertEqual(read(tmpfile), (True, [1, -2, -3, -4, -5, -23, -24, -25, -26]))


if __name__ == '__main__':
    unittest.main()
