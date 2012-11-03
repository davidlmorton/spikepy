
import unittest

from spikepy.developer.methods import SpikepyMethod

class TestSpikepyMethod(unittest.TestCase):
    def test_class_variables(self):
        sm = SpikepyMethod()
        self.assertTrue(hasattr(sm, 'is_pooling'))
        self.assertTrue(hasattr(sm, 'silent_pooling'))
        self.assertTrue(hasattr(sm, 'unpool_as'))
        self.assertTrue(hasattr(sm, 'is_stochastic'))
        self.assertTrue(hasattr(sm, 'requires'))
        self.assertTrue(hasattr(sm.requires, '__iter__'))
        self.assertTrue(hasattr(sm, 'provides'))
        self.assertTrue(hasattr(sm.provides, '__iter__'))

    def test_run(self):
        sm = SpikepyMethod()
        self.assertRaises(NotImplementedError, sm.run)


if __name__ == '__main__':
    unittest.main()
