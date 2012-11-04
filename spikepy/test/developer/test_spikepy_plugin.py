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

from spikepy.developer.spikepy_plugin import SpikepyPlugin
from spikepy.common.valid_types import ValidInteger


class SampleSpikepyPlugin(SpikepyPlugin):
    a = ValidInteger(min=0, max=1, default=0)
    b = ValidInteger(min=-10, max=-1, default=-10)


class TestSpikepyPlugin(unittest.TestCase):
    def test_get_parameter_attributes(self):
        plugin = SampleSpikepyPlugin()
        attrs = plugin.get_parameter_attributes()
        expected = {'a':plugin.a, 'b':plugin.b}
        self.assertEquals(attrs, expected)

    def test_get_parameter_defaults(self):
        plugin = SampleSpikepyPlugin()
        defaults = plugin.get_parameter_defaults()
        expected = {'a':0, 'b':-10}
        self.assertEquals(defaults, expected)

    def test_validate_parameters(self):
        plugin = SampleSpikepyPlugin()
        valid_parameters = {'a':1, 'b':-5}
        invalid_parameters = {'a':1, 'b':-5.5}
        self.assertEquals(plugin.validate_parameters(valid_parameters), None)
        self.assertRaises(Exception, plugin.validate_parameters, 
                invalid_parameters)


if __name__ == '__main__':
    unittest.main()
