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
import pylab
import numpy

from spikepy.plotting_utils.make_into_signal_axes import make_into_signal_axes  

def plot_signals_in_depth(axes, signals, depths_um, times_ms, 
        colors=['b', 'r', 'g', 'c', 'm', 'k'],
        ascending=True, 
        xlim=None,
        ylim=None,
        shade=False,
        alpha=None,
        group_legend=None,
        separation='6 stds'):
    '''
        signals: Either a list of arrays, or a single array.
    '''

    # check inputs
    if isinstance(signals, list) or isinstance(signals, tuple):
        if alpha is None:
            alpha = min(1.0, max(1.0/len(signals)+0.30, 0.25))
        if signals[0].ndim == 1:
            assert len(signals) == len(depths_um)
            assert len(signals[0]) == len(times_ms)
            mode = 'list_of_1d'
        else:
            assert signals[0].shape == (len(depths_um), len(times_ms))
            mode = 'list_of_2d'
    else:
        if alpha is None:
            alpha = 1.0
        if signals.ndim == 1:
            assert len(depths_um) == 1
            assert len(signals) == len(times_ms)
            mode = 'single_1d'
            signals = [signals]
        else:
            assert signals.shape == (len(depths_um), len(times_ms))
            mode = 'single_2d'
            signals = [signals]

    # parse separation
    if isinstance(separation, str):
        try:
            separation_std = float(separation.split()[0])
        except:
            raise RuntimeError(
                    'separation, if a string, must be of the form "%f stds"')
        separation = numpy.std(signals)*separation_std

    make_into_signal_axes(axes)

    if ascending: factor = 1.0
    else: factor = -1.0
    offsets = [factor*separation*i for i in range(len(depths_um))]

    y_min = y_max = 0
    if mode in ['list_of_1d', 'single_1d']:
        y_min, y_max = _plot_signals(axes, signals, times_ms, offsets, alpha, 
                colors, shade, y_min, y_max, group_legend)
    else:
        for ti, t in enumerate(signals):
            if ti != 0:
                group_legend = None
            y_min, y_max = _plot_signals(axes, t, times_ms, offsets, alpha, 
                    colors, shade, y_min, y_max, group_legend)

    if xlim is not None:
        axes.set_xlim(xlim)
    else:
        rangex = abs(times_ms[-1]-times_ms[0])
        axes.set_xlim(times_ms[0]-0.06*rangex, times_ms[-1]+0.06*rangex)

    if ylim is not None:
        axes.set_ylim(ylim)
    else:
        y_range = abs(y_max - y_min)
        axes.set_ylim(y_min-0.08*y_range, y_max+0.05*y_range)

    axes.set_yticks(offsets)
    y_labels = [r'%d' % d for d in depths_um[1:]]
    y_labels.insert(0, r'%d $\mu$m' % depths_um[0])
    axes.set_yticklabels(y_labels)
    axes.get_yaxis().set_ticks_position('right')
    return separation


def _plot_signals(axes, signals, times_ms, offsets, alpha, colors, 
        shade, y_min, y_max, group_legend):
    for si, s in enumerate(signals):
        color = colors[si % len(colors)]
        this_s = s+offsets[si]
        if si != 0:
            group_legend = None
        axes.signal_plot(times_ms, this_s, color=color, alpha=alpha,
                label=group_legend)
        if shade:
            axes.fill_between(times_ms, this_s, offsets[si], 
                    where=this_s > offsets[si], color=color, alpha=alpha*0.75)
        y_min = min(numpy.min(this_s), y_min)
        y_max = max(numpy.max(this_s), y_max)
    return y_min, y_max
            
        
    
    
    
