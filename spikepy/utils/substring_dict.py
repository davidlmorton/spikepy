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

class SubstringDict(dict):
    '''
        A dictionary whose elements can be fetched either by giving the full
    key or a unique subset of the key.  Raises a KeyError if the key provided
    isn't a unique subset of any key.
    '''
    def __getitem__(self, key):
        if key in self.keys():
            return dict.__getitem__(self, key)
        else:
            pkeys = []
            for skey in self.keys():
                if key in skey:
                    pkeys.append(skey)
            if len(pkeys) == 1:
                return dict.__getitem__(self, pkeys[0])
            else:
                raise KeyError("%s is an invalid key." % key)
