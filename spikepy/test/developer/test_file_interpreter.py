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

from spikepy.developer.file_interpreter import FileInterpreter

class TestDataInterpreter(unittest.TestCase):
    def test_class_variables(self):
        fi = FileInterpreter()
        self.assertTrue(hasattr(fi, 'extentions'))
        self.assertTrue(hasattr(fi.extentions, '__iter__'))
        self.assertTrue(hasattr(fi, 'priority'))

    def test_read_data_file(self):
        fi = FileInterpreter()
        self.assertRaises(NotImplementedError, fi.read_data_file, None)


if __name__ == '__main__':
    unittest.main()
