"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest

import numpy
from spikepy.utils.collapse_event_times import collapse_event_times as cet

test_data = \
        [[1.0, 1.01, 1.2],
        [],
              [0.99, 1.21, 1.3],
              [],
                    [1.19, 1.31],
                    [],
                          [1.29]]

class TestCollapseEventTimes(unittest.TestCase):
    def test_min_num_channels(self):
        #    If min_num_channels is greater than the number of channels in 
        # event_times then just return the flattened list of event_times.
        flattened_data = numpy.array([0.99, 1.0, 1.01, 1.19, 1.2, 1.21, 
                1.29, 1.3, 1.31])
        results = cet(test_data, 100, 0.2)
        print 'testing %s expected to be %s' % (results, flattened_data)
        self.assertEqual(flattened_data.shape, results.shape)
        self.assertTrue(numpy.equal(flattened_data, results).all())
        print 'passed'

        # same as if min_num_channels is 1
        results = cet(test_data, 1, 0.001) # peak drift ignored
        print 'testing %s expected to be %s' % (results, flattened_data)
        self.assertEqual(flattened_data.shape, results.shape)
        self.assertTrue(numpy.equal(flattened_data, results).all())
        print 'passed'

        results = cet(test_data, 1, 4) # peak drift ignored
        print 'testing %s expected to be %s' % (results, flattened_data)
        self.assertEqual(flattened_data.shape, results.shape)
        self.assertTrue(numpy.equal(flattened_data, results).all())
        print 'passed'

    def test_peak_width(self):
        self.assertRaises(AssertionError, cet, test_data, 1, -1)

        expected_results = numpy.array([1.0, 1.2, 1.3])
        results = cet(test_data, 2, 0.021)
        print 'testing %s expected to be %s' % (results, expected_results)
        self.assertEqual(expected_results.shape, results.shape)
        self.assertTrue(numpy.equal(expected_results, results).all())
        print 'passed'

        # 1.0 not on three channels, but two, even though it has three
        # elements within 0.2 sec of one another in flattened list.
        expected_results = numpy.array([1.2, 1.3])
        results = cet(test_data, 3, 0.021)
        print 'testing %s expected to be %s' % (results, expected_results)
        self.assertEqual(expected_results.shape, results.shape)
        self.assertTrue(numpy.equal(expected_results, results).all())
        print 'passed'

        # with larger peak_width
        expected_results = numpy.array([1.0])
        results = cet(test_data, 3, 0.4)
        print 'testing %s expected to be %s' % (results, expected_results)
        self.assertEqual(expected_results.shape, results.shape)
        self.assertTrue(numpy.equal(expected_results, results).all())
        print 'passed'

        # with medium peak_width
        expected_results = numpy.array([1.0, 1.3])
        results = cet(test_data, 3, 0.25)
        print 'testing %s expected to be %s' % (results, expected_results)
        self.assertEqual(expected_results.shape, results.shape)
        self.assertTrue(numpy.equal(expected_results, results).all())
        print 'passed'

        # with tricky peak_width
        expected_results = numpy.array([1.0, 1.2])
        results = cet(test_data, 3, 0.20)
        print 'testing %s expected to be %s' % (results, expected_results)
        self.assertEqual(expected_results.shape, results.shape)
        self.assertTrue(numpy.equal(expected_results, results).all())
        print 'passed'

if __name__ == '__main__':
    unittest.main()
