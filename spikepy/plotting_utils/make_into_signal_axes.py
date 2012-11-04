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

from types import MethodType
import uuid

import numpy

from spikepy.plotting_utils.downsample_for_plot import downsample_for_plot 
from spikepy.plotting_utils.general import is_iterable

def signal_set_xlim(axes, tmin=None, tmax=None, **kwargs):
    '''
        This set_xlim function replaces the usual matplotlib axes set_xlim
    function.  It will redraw the signals after having downsampled them.
    '''
    # don't do anything if locked.
    if axes._are_axes_locked:
        return
    axes.lock_axes()

    # parse inputs
    if tmax is None and is_iterable(tmin):
        tmin, tmax = tmin

    if hasattr(axes, '_signal_times'):
        for s_id in axes._signal_draw_order:
            # don't replot if bounds didn't actually change.
            xmin, xmax = axes.get_xlim()
            if xmin == tmin and xmax == tmax and\
               s_id in axes._signal_lines.keys():
                continue

            # delete existing lines
            if s_id in axes._signal_lines.keys():
                axes._signal_lines[s_id].remove()
                del axes._signal_lines[s_id]

            # downsample
            new_signal, new_times = downsample_for_plot(
                    axes._signals[s_id],
                    axes._signal_times[s_id], 
                    tmin, tmax, axes._signal_num_samples)

            line = axes.plot(new_times, new_signal, 
                    *axes._signal_args[s_id],                    
                    **axes._signal_kwargs[s_id])[0]

            # save this line so we can remove it later.
            axes._signal_lines[s_id] = line

    axes.unlock_axes()

    # actually change the xlimits
    axes._pre_signal_set_xlim(tmin, tmax, **kwargs)


def signal_set_ylim(axes, *args, **kwargs):
    # don't do anything if locked.
    if axes._are_axes_locked:
        return
    axes._pre_signal_set_ylim(*args, **kwargs)

    if hasattr(axes, '_live_updating_scalebars'):
        axes.lock_axes()
        axes._create_x_scale_bar(axes)
        axes._create_y_scale_bar(axes)
        axes.unlock_axes()

def get_signal_yrange(axes, padding=0.05):
    all_min = 0
    all_max = 0
    for s_id in axes._signals.keys():
        ymin = numpy.min(axes._signals[s_id])
        ymax = numpy.max(axes._signals[s_id])
        if ymin < all_min: 
            all_min = ymin
        if ymax > all_max:
            all_max = ymax
    padding = abs(all_max - all_min)*(padding+1.0)
    return(all_min - padding, all_max + padding)

def signal_plot(axes, times, signal, *args, **kwargs):
    this_signal_id = uuid.uuid4()
    if 'replace_signal_id' in kwargs:
        replace_signal_id = kwargs['replace_signal_id']
        del kwargs['replace_signal_id']
        if hasattr(axes, '_signal_times'):
            if replace_signal_id in axes._signal_lines.keys():
                # delete the line first.
                axes._signal_lines[replace_signal_id].remove()
                del axes._signal_lines[replace_signal_id]
                del axes._signals[replace_signal_id]
                del axes._signal_times[replace_signal_id]
                del axes._signal_kwargs[replace_signal_id]
                del axes._signal_args[replace_signal_id]
                axes._signal_draw_order.remove(replace_signal_id)
            else:
                raise RuntimeError('Cannot replace signal, signal_id %s does not exist' % replace_signal_id)
        else:
            raise RuntimeError('Cannot relace a signal because none exist.')
    else:
        if not hasattr(axes, '_signal_times'):
            axes._signal_times = {}
            axes._signals = {}
            axes._signal_lines = {}
            axes._signal_kwargs = {}
            axes._signal_draw_order = []
            axes._signal_args = {}

    # add the new signal
    axes._signals[this_signal_id] = signal
    axes._signal_times[this_signal_id] = times
    axes._signal_kwargs[this_signal_id] = kwargs
    axes._signal_draw_order.append(this_signal_id)
    axes._signal_args[this_signal_id] = args
    axes.set_xlim(axes.get_xlim())
    return this_signal_id

def unlock_axes(axes):
    axes._are_axes_locked = False

def lock_axes(axes):
    axes._are_axes_locked = True

def make_into_signal_axes(axes, num_samples=1500):
    '''
        Turn axes into an axis which can plot signals efficiently.  It will
    automatically downsample signals so they draw fast and don't fail to show
    extrema properly.

    Inputs:
        axes: The axes you want to make into a signal_axes.
        num_samples: The number (approx) of samples in downsampled signals.
    Adds Attributes:
        signal_plot: Behaves just like plot, except it expects signals.
        get_signal_yrange: Returns a tuple that can be passed to 
                axes.set_ylim() to show all signal data on plot.
        **monkeypatches set_xlim to handle downsampling of signals on the fly.
    Returns:
        None
    '''
    if not hasattr(axes, '_is_signal_axes'):
        axes._is_signal_axes = True
        axes.signal_plot = MethodType(signal_plot, axes, axes.__class__)
        axes.get_signal_yrange = MethodType(get_signal_yrange, axes, 
                axes.__class__)
        axes._pre_signal_set_xlim = axes.set_xlim
        axes.set_xlim = MethodType(signal_set_xlim, axes, axes.__class__)

        axes._pre_signal_set_ylim = axes.set_ylim
        axes.set_ylim = MethodType(signal_set_ylim, axes, axes.__class__)

        axes.lock_axes = MethodType(lock_axes, axes, axes.__class__)
        axes.unlock_axes = MethodType(unlock_axes, axes, axes.__class__)

        axes._are_axes_locked = False

        axes._signal_num_samples = num_samples 
