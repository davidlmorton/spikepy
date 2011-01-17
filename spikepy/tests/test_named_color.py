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

from spikepy.gui import utils

import unittest

class KnownColors(unittest.TestCase):
    known_colors = ( ("red",   [1,0,0]),
                     ("green", [0,1,0]),
                     ("blue",  [0,0,1])
                   )

    def test_named_color(self):
        '''
        named_color should give known rgb values given known color names.
        '''
        for name, rgb_val in self.known_colors:
            result = utils.named_color(name)
            self.assertEqual(rgb_val, result)

class BadInput(unittest.TestCase):
    def test_not_a_color(self):
        '''
        named_color should fail if given anything but a color name.
        '''
        self.assertRaises(ValueError, utils.named_color, 
                          "owl exterminators")


if __name__ == "__main__":
    unittest.main()
