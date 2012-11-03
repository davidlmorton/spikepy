
import unittest

from spikepy.developer.visualization import Visualization

class TestSpikepyMethod(unittest.TestCase):
    def test_class_variables(self):
        v = Visualization()
        self.assertTrue(hasattr(v, 'name'))
        self.assertTrue(hasattr(v, 'requires'))
        self.assertTrue(hasattr(v.requires, '__iter__'))
        self.assertTrue(hasattr(v, 'found_under_tab'))

    def test__plot(self):
        v = Visualization()
        self.assertRaises(NotImplementedError, v._plot, None, None)


if __name__ == '__main__':
    unittest.main()
