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

from collections import defaultdict

import numpy


def cluster_data(clusters, data):
    '''
        Given the cluster identities and data return a dictionary keyed on
    cluster identity with data in the form of a numpy array.
    '''
    adict = defaultdict(list)
    for cluster_id, thing in zip(clusters, data):
        if cluster_id == -1:
            adict['Rejected'].append(thing)
        else:
            adict[cluster_id].append(thing)

    for key in adict.keys():
        adict[key] = numpy.array(adict[key])

    return dict(adict)
    
