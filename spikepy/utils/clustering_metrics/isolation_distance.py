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
import numpy

def isolation_distance(clustered_mahalanobis_squared_dict):
    cmsd = clustered_mahalanobis_squared_dict 

    return_dict = {}
    for key in cmsd.keys():
        if key is not 'Rejected':
            other_distances = [cmsd[key][k] for k in cmsd.keys() if
                    k not in [key, 'Rejected']]
            other_distances = numpy.sort(numpy.hstack(other_distances))
            if len(other_distances) >= len(cmsd[key][key]):
                return_dict[key] = other_distances[len(cmsd[key][key])]
            else:
                return_dict[key] = -1.0
    return return_dict
