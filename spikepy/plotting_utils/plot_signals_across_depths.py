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
import bisect

import pylab
import numpy

from scipy.signal import interpolate

def plot_signals_across_depths(axes, signal, depths_um, times_ms, times_list, 
        colors=['b', 'r', 'g', 'c', 'm', 'k'],
        interpolation='cubic',
        ls=':',
        legend=[],
        room_at_top=0.3,
        shade=0.0):

    ymin = ymax = 0
    for ti, time in enumerate(sorted(times_list)):
        slice_index = bisect.bisect_left(times_ms, time)
        signal_slice = signal.T[slice_index]
    
        islice_fn = interpolate.interp1d(depths_um, signal_slice, 
                kind=interpolation)

        idepths = numpy.linspace(depths_um[0], depths_um[-1], 200)
        islice = islice_fn(idepths)
    

        this_color = colors[ti % len(colors)]
        axes.plot(depths_um, signal_slice, linewidth=0, 
                color=this_color,
                marker='o')

        if shade > 0:
            axes.fill_between(idepths, 0.0, 
                    islice, where=islice>=0.0, color=this_color, alpha=0.7)

        if legend:
            axes.plot(idepths, islice,
                    color=this_color, ls=ls, label=legend[ti])
        else:
            axes.plot(idepths, islice, color=this_color, ls=ls)

        ymin = min(numpy.min(islice), ymin)
        ymax = max(numpy.max(islice), ymax)

    rangex = abs(depths_um[-1]-depths_um[0])
    axes.set_xlim(depths_um[0]-0.01*rangex, depths_um[-1]+0.01*rangex)
    maxy = max(abs(ymin), abs(ymax))
    yrange = 2.0*maxy
    axes.set_ylim(-maxy-0.05*yrange, 
            maxy+0.05*yrange+room_at_top*yrange)

    if legend:
        axes.legend(loc='upper left')

    return (min(islice), max(islice))

     
        
    
    
    
