import unittest
from util.count import count
from word import rot_and_rev, paths, stick, head, cycle, tail, net, sentence, sentences, network, networks
from network import Network


class TestWordModule(unittest.TestCase):

    def test_path(self):
        self.assertEqual(sorted(paths(0)), [''])
        self.assertEqual(sorted(paths(2)), ['12', '21'])
        self.assertEqual(sorted(paths(4)), ['1212', '1221', '2112', '2121'])

    def test_stick(self):
        self.assertEqual(sorted(stick(4)), ['1212', '1221', '2112'])

    def test_head(self):
        self.assertEqual(head(1), ['0'])
        self.assertEqual(head(5), ['01212', '01221', '02112', '02121'])

    def test_cycle(self):
        self.assertEqual(sorted(cycle(8)), ['12121212c', '12121221c', '12122121c', '12211221c'])
        asym10 = [w for w in cycle(10) if w != rot_and_rev(w.translate(str.maketrans('12','21')))]
        self.assertEqual(asym10, [])
        asym12 = [w for w in cycle(12) if w != rot_and_rev(w.translate(str.maketrans('12','21')))]
        self.assertEqual(asym12, ['121221122121c', '121221211221c'])
        asym14 = [w for w in cycle(14) if w != rot_and_rev(w.translate(str.maketrans('12','21')))]
        self.assertEqual(asym14, ['12121221122121c', '12121221211221c'])
        asym16 = [w for w in cycle(16) if w != rot_and_rev(w.translate(str.maketrans('12','21')))]
        self.assertEqual(asym16, [
            '1212121221122121c', '1212121221211221c', '1212122112122121c', '1212122112212121c',
            '1212122121121221c', '1212122121211221c', '1212211221122121c', '1212212112211221c'])
        asym32 = [w for w in cycle(32) if w != rot_and_rev(w.translate(str.maketrans('12','21')))]
        self.assertEqual(len(asym32), 960*2)
        asym36 = [w for w in cycle(36) if w != rot_and_rev(w.translate(str.maketrans('12','21')))]
        self.assertEqual(len(asym36), 3515*2)

    def test_tail(self):
        self.assertEqual(sorted(tail(2)), [])
        self.assertEqual(sorted(tail(4)), ['0120'])
        self.assertEqual(sorted(tail(6)), ['012120', '012210', '021120'])

    def test_net(self):
        self.assertEqual(net('121212c'), [[(0, 1), (2, 3), (4, 5)], [(0, 5), (1, 2), (3, 4)]])
        self.assertEqual(net('121212'),  [[(0, 1), (2, 3), (4, 5)], [(1, 2), (3, 4)]])
        self.assertEqual(net('0121212'), [[(0, 1), (2, 3), (4, 5)], [(0, 6), (1, 2), (3, 4)]])

    def test_sentence(self):
        self.assertEqual(sentence([[(0, 1), (2, 3), (4, 5)], [(0, 6), (1, 2), (3, 4)]]), ['0121212'])
        s = ['0', '012', '0120', '021', '1212', '1212c', '1221', '1221c', '12c', '2112']
        net = network(s)
        r = sentence(net, n=33)
        self.assertEqual(r, s)
        s, perm = sentence(net, n=33, permutation=True)
        self.assertEqual(perm, {i:i for i in range(33)})
        net = Network([
            [(0, 10), (1, 8), (2, 3), (4, 5), (6, 9)],
            [(0, 6), (1, 7), (2, 4), (3, 9), (5, 10)],
            [(0, 1), (3, 5), (4, 6), (7, 8), (9, 10)],
            [(0, 2), (1, 5), (4, 7), (6, 8)],
            [(1, 2), (3, 4), (5, 6), (7, 9), (8, 10)],
            [(1, 3), (2, 7), (4, 5), (8, 9)],
            [(2, 4), (5, 7), (6, 8)],
            [(2, 3), (4, 5), (6, 7), (8, 9)]])
        self.assertTrue(net.sorts(11))
        s, perm = sentence(net, permutation=True)
        net.permute(0, perm)
        net.standarize()
        self.assertEqual(net, [
            [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)],
            [(0, 6), (1, 3), (2, 4), (5, 7), (8, 10)],
            [(0, 8), (1, 5), (3, 7), (4, 6), (9, 10)],
            [(0, 2), (4, 9), (5, 8), (6, 10)],
            [(1, 4), (2, 5), (3, 9), (6, 8), (7, 10)],
            [(1, 2), (3, 5), (4, 6), (7, 9)],
            [(3, 4), (5, 6), (7, 8)],
            [(2, 3), (4, 5), (6, 7), (8, 9)]])
        self.assertTrue(net.sorts(11))

    def test_sentences(self):
        self.assertEqual(sorted(sentences(3, keep_redundant=True, keep_reflection=True, keep_empty=True)), [
            ['0', '0', '0'], ['0', '12'], ['0', '12c'], ['012'], ['021']])
        self.assertEqual(sorted(sentences(4, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), [
            ['12', '12'], ['12', '12c'], ['1212'], ['1212c'], ['1221'],
            ['1221c'], ['12c', '12c'], ['2112']])
        self.assertEqual(sorted(sentences(4, keep_redundant=True, keep_reflection=True, keep_empty=True)), [
            ['0', '0', '0', '0'], ['0', '0', '12'], ['0', '0', '12c'], ['0', '012'], ['0', '021'], ['0120'],
            ['12', '12'], ['12', '12c'], ['1212'], ['1212c'], ['1221'], ['1221c'], ['12c', '12c'], ['2112']])
        self.assertEqual(sorted(sentences(4, keep_redundant=True, keep_empty=True)), [
            ['0', '0', '0', '0'], ['0', '0', '12'], ['0', '0', '12c'], ['0', '012'], ['0120'],
            ['12', '12'], ['12', '12c'], ['1212'], ['1212c'], ['1221'], ['1221c'], ['12c', '12c']])
        self.assertEqual(sorted(sentences(4, keep_empty=True)), [
            ['0', '0', '0', '0'], ['0', '0', '12'], ['0', '012'], ['0120'],
            ['12', '12'], ['1212'], ['1212c'], ['1221'], ['1221c']])
        self.assertEqual(sorted(sentences(5, keep_empty=True)), [
            ['0', '0', '0', '0', '0'], ['0', '0', '0', '12'], ['0', '0', '012'], ['0', '0120'], ['0', '12', '12'],
            ['0', '1212'], ['0', '1212c'], ['0', '1221'], ['0', '1221c'], ['012', '12'],
            ['01212'], ['01221']])
        self.assertEqual(sorted(sentences(5)), [
            ['0', '0', '012'], ['0', '0120'],
            ['0', '1212'], ['0', '1212c'], ['0', '1221'], ['0', '1221c'], ['012', '12'],
            ['01212'], ['01221']])
        self.assertEqual(count(sentences(4, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), 8)
        self.assertEqual(count(sentences(16, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), 2627)
        self.assertEqual(count(sentences(17, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), 10187)
        self.assertEqual(count(sentences(18, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), 6422)
        self.assertEqual(count(sentences(19, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), 26796)

    def test_maximal_networks(self):
        self.assertEqual(list(networks(3, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), [
            [[(0, 1)], [(0, 2)]],
            [[(0, 1)], [(1, 2)]],
            [[(0, 1)], []],
            [[(0, 1)], [(0, 1)]]])
        self.assertEqual(count(networks(4, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), 8)
        self.assertEqual(count(networks(16, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), 2627)
        self.assertEqual(sorted(networks(4, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), [
            [[(0, 1), (2, 3)], []],
            [[(0, 1), (2, 3)], [(0, 1)]],
            [[(0, 1), (2, 3)], [(0, 1), (2, 3)]],
            [[(0, 1), (2, 3)], [(0, 2)]],
            [[(0, 1), (2, 3)], [(0, 2), (1, 3)]],
            [[(0, 1), (2, 3)], [(0, 3), (1, 2)]],
            [[(0, 1), (2, 3)], [(1, 2)]],
            [[(0, 1), (2, 3)], [(1, 3)]]])

    def test_saturated_networks(self):
        self.assertEqual(sorted(sentences(4, saturated=True, keep_reflection=True, keep_empty=True)), [['1212c'], ['1221c']])
        self.assertEqual(count(networks(16, saturated=True)), 211)
        self.assertEqual(count(networks(19, saturated=True, keep_reflection=True)), 2632)
        self.assertEqual(count(networks(19, saturated=True)), 1367)
        self.assertEqual(count(networks(31, saturated=True)), 167472)
        # self.assertEqual(count(networks(32, maximal=True, keep_reflection=True, saturated=True)), 138122)
        self.assertEqual(count(networks(32, saturated=True)), 73190) # 73191 in Codish2014quest
        # self.assertEqual(count(networks(40, maximal=True, keep_reflection=True, saturated=True)), 2792966)
        # self.assertEqual(count(networks(40, maximal=True, saturated=True)), 1429788) # 1429836 in Codish2014quest

    def test_networks(self):
        self.assertEqual(sorted(networks(3, keep_redundant=True, keep_reflection=True, keep_empty=True)), [
            [[], []],
            [[(0, 1)], []],
            [[(0, 1)], [(0, 1)]],
            [[(0, 1)], [(0, 2)]],
            [[(0, 1)], [(1, 2)]]])
        self.assertEqual(sorted(networks(4, keep_redundant=True, keep_reflection=True, keep_empty=True)), [
            [[], []],
            [[(0, 1)], []],
            [[(0, 1)], [(0, 1)]],
            [[(0, 1)], [(0, 2)]],
            [[(0, 1)], [(0, 3), (1, 2)]],
            [[(0, 1)], [(1, 2)]],
            [[(0, 1), (2, 3)], []],
            [[(0, 1), (2, 3)], [(0, 1)]],
            [[(0, 1), (2, 3)], [(0, 1), (2, 3)]],
            [[(0, 1), (2, 3)], [(0, 2)]],
            [[(0, 1), (2, 3)], [(0, 2), (1, 3)]],
            [[(0, 1), (2, 3)], [(0, 3), (1, 2)]],
            [[(0, 1), (2, 3)], [(1, 2)]],
            [[(0, 1), (2, 3)], [(1, 3)]]])
        self.assertEqual(sorted(networks(4, keep_reflection=True, keep_empty=True)), [
            [[], []],
            [[(0, 1)], []],
            [[(0, 1)], [(0, 2)]],
            [[(0, 1)], [(0, 3), (1, 2)]],
            [[(0, 1)], [(1, 2)]],
            [[(0, 1), (2, 3)], []],
            [[(0, 1), (2, 3)], [(0, 2)]],
            [[(0, 1), (2, 3)], [(0, 2), (1, 3)]],
            [[(0, 1), (2, 3)], [(0, 3), (1, 2)]],
            [[(0, 1), (2, 3)], [(1, 2)]],
            [[(0, 1), (2, 3)], [(1, 3)]]])
        self.assertEqual(sorted(networks(4, keep_empty=True)), [
            [[], []],
            [[(0, 1)], []],
            [[(0, 1)], [(0, 2)]],
            [[(0, 1)], [(0, 3), (1, 2)]],
            [[(0, 1), (2, 3)], []],
            [[(0, 1), (2, 3)], [(0, 2), (1, 3)]],
            [[(0, 1), (2, 3)], [(0, 3), (1, 2)]],
            [[(0, 1), (2, 3)], [(1, 2)]],
            [[(0, 1), (2, 3)], [(1, 3)]]])
        self.assertEqual(sorted(networks(5)), [
            [[(0, 1)], [(0, 2)]],
            [[(0, 1)], [(0, 3), (1, 2)]],
            [[(0, 1), (2, 3)], [(0, 2), (1, 3)]],
            [[(0, 1), (2, 3)], [(0, 3), (1, 2)]],
            [[(0, 1), (2, 3)], [(0, 4), (1, 2)]],
            [[(0, 1), (2, 3)], [(0, 4), (1, 3)]],
            [[(0, 1), (2, 3)], [(1, 2)]],
            [[(0, 1), (2, 3)], [(1, 3)]],
            [[(0, 1), (2, 3)], [(2, 4)]]])
        self.assertEqual(sorted(networks(5, keep_empty=True)), [
            [[], []],
            [[(0, 1)], []],
            [[(0, 1)], [(0, 2)]],
            [[(0, 1)], [(0, 3), (1, 2)]],
            [[(0, 1), (2, 3)], []],
            [[(0, 1), (2, 3)], [(0, 2), (1, 3)]],
            [[(0, 1), (2, 3)], [(0, 3), (1, 2)]],
            [[(0, 1), (2, 3)], [(0, 4), (1, 2)]],
            [[(0, 1), (2, 3)], [(0, 4), (1, 3)]],
            [[(0, 1), (2, 3)], [(1, 2)]],
            [[(0, 1), (2, 3)], [(1, 3)]],
            [[(0, 1), (2, 3)], [(2, 4)]]])
        self.assertEqual(sorted(networks(5, maximal=True, keep_redundant=True, keep_reflection=True, keep_empty=True)), [
            [[(0, 1), (2, 3)], []],
            [[(0, 1), (2, 3)], [(0, 1)]],
            [[(0, 1), (2, 3)], [(0, 1), (2, 3)]],
            [[(0, 1), (2, 3)], [(0, 1), (2, 4)]],
            [[(0, 1), (2, 3)], [(0, 1), (3, 4)]],
            [[(0, 1), (2, 3)], [(0, 2)]],
            [[(0, 1), (2, 3)], [(0, 2), (1, 3)]],
            [[(0, 1), (2, 3)], [(0, 2), (1, 4)]],
            [[(0, 1), (2, 3)], [(0, 3), (1, 2)]],
            [[(0, 1), (2, 3)], [(0, 3), (1, 4)]],
            [[(0, 1), (2, 3)], [(0, 4), (1, 2)]],
            [[(0, 1), (2, 3)], [(0, 4), (1, 3)]],
            [[(0, 1), (2, 3)], [(1, 2)]],
            [[(0, 1), (2, 3)], [(1, 3)]],
            [[(0, 1), (2, 3)], [(2, 4)]],
            [[(0, 1), (2, 3)], [(3, 4)]]])
        self.assertEqual(count(networks(6, keep_reflection=True, keep_empty=True)), 36)
        self.assertEqual(count(networks(7, keep_reflection=True, keep_empty=True)), 62)
        self.assertEqual(count(networks(8, keep_reflection=True, keep_empty=True)), 128)
        self.assertEqual(count(networks(9, keep_reflection=True, keep_empty=True)), 216)
        self.assertEqual(count(networks(16, keep_reflection=True, keep_empty=True)), 12055)
        self.assertEqual(count(networks(6, keep_empty=True)), 27)
        self.assertEqual(count(networks(16, keep_empty=True)), 6725)
