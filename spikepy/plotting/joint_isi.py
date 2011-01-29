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

def joint_isi(spike_times, axes=None, **kwargs):
    if not isinstance(spike_times, numpy.ndarray):
        spike_times = numpy.array(spike_times)
    isi = spike_times[1:] - spike_times[:-1]

    if axes is None:
        return isi[:-1], isi[1:]
    else:
        axes.plot(isi[:-1], isi[1:], linewidth=0, marker='.', **kwargs)
