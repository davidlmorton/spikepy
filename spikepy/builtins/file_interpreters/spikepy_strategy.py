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
from spikepy.developer.file_interpreter import FileInterpreter, Trial,\
        Strategy

class SpikepyStrategy(FileInterpreter):
    def __init__(self):
        self.name = 'Spikepy Strategy'
        self.extentions = ['.strategy']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''A previously saved spikepy strategy.'''

    def read_data_file(self, fullpath):
        strategy = Strategy.from_file(fullpath)
        strategy.fullpath = None
        return [strategy]
