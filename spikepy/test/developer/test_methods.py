#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
