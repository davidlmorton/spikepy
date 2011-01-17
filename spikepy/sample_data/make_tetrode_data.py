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

# takes a normal 4 column wessel-lab formatted text file and makes it 
#  a tetrode file by repeating the data column 3 more times (data column=0)
import sys

filename = sys.argv[1]

with open(filename, 'r') as infile: 
    with open(filename+'.tet', 'w') as outfile:
        for line in infile.readlines():
            tokens = line.split()
            # repeat first column 3 more times.
            for i in [0, 0, 0]:
                tokens.insert(i, tokens[0])
            for token in tokens:
                outfile.write( token + '    ')
            outfile.write('\n')
    

