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

"""
A collection of utility functions for the spikepy plotting.
"""
import bisect
from types import MethodType
import uuid

import wx
from matplotlib.ticker import MaxNLocator
import numpy

from spikepy.common.config_manager import config_manager as config

def is_iterable(x):
    return hasattr(x, '__len__')

def signal_fold(times, signal):
    '''
    This function will take the signal (assumed longer than times) and
        flip it back and forth.  It is designed to make matplotlib plot
        multiple lines faster (since they will be one line after the fold)
    '''
    result = []
    t_result = []
    if hasattr(signal, 'shape') and len(signal.shape) == 1:
        num_chunks = int(len(signal)/len(times))
        if num_chunks > 1:
            for i in xrange(num_chunks):
                start = 2*i
                end   = 2*i+len(times)
                this_chunk = signal[start:end]
                if i%2:
                    result.append(numpy.flipud(this_chunk))
                    t_result.append(numpy.flipud(times))
                else:
                    result.append(this_chunk)
                    t_result.append(times)

    elif is_iterable(signal[0]):
        num_chunks = len(signal)
        if num_chunks > 1:
            for i in xrange(num_chunks):
                this_chunk = signal[i]
                if i%2:
                    result.append(numpy.flipud(this_chunk))
                    t_result.append(numpy.flipud(times))
                else:
                    result.append(this_chunk)
                    t_result.append(times)
    else:
        raise RuntimeError('Signal must be a 1D array or a 2D array.')

    result = numpy.hstack(result)
    t_result  = numpy.hstack(t_result)
        
    return t_result, result



def downsample_for_plot(times, signal, tmin, tmax, num_samples=1000):
    imin = bisect.bisect_left(times, tmin)
    if imin > 0:
        imin -= 1 # get previous point, even if not plotted
    imax = bisect.bisect_right(times, tmax) + 1

    signal_slice = signal[imin:imax]
    times_slice = times[imin:imax]
    slice_len = len(signal_slice)

    if slice_len >= 2*num_samples:
        chunk_size = slice_len/num_samples
        times_list = times_slice[::chunk_size]
        num_chunks = len(times_list)
        new_times = numpy.empty(num_chunks*2, dtype=numpy.float64)
        new_signal = numpy.empty(num_chunks*2, dtype=numpy.float64)
        for i in xrange(num_chunks):
            start = i*chunk_size
            end   = start+chunk_size-1
            chunk_min = numpy.min(signal_slice[start:end])
            chunk_max = numpy.max(signal_slice[start:end])
            new_times[2*i]    = times_list[i]
            new_times[2*i+1]  = times_list[i]
            new_signal[2*i]   = chunk_min
            new_signal[2*i+1] = chunk_max
    else:
        return times_slice, signal_slice

    return new_times, new_signal

def trace_set_xlim(axes, tmin=None, tmax=None, **kwargs):
    '''
    This set_xlim function replaces the usual matplotlib axes set_xlim
        function.  It will redraw the traces after having downsampled
        them.
    '''
    # don't do anything if locked.
    if hasattr(axes, '_trace_xlim_locked'):
        if axes._trace_xlim_locked:
            return

    # parse inputs
    if tmax is None and is_iterable(tmin):
        tmin, tmax = tmin

    if hasattr(axes, '_trace_times'):
        for t_id in axes._trace_draw_order:
            # don't replot if bounds didn't actually change.
            xmin, xmax = axes.get_xlim()
            if xmin == tmin and xmax == tmax and\
               t_id in axes._trace_lines.keys():
                continue

            # delete existing lines
            if t_id in axes._trace_lines.keys():
                axes._trace_lines[t_id].remove()
                del axes._trace_lines[t_id]

            # downsample
            new_times, new_trace = downsample_for_plot(axes._trace_times[t_id], 
                                                       axes._traces[t_id],
                                                       tmin, tmax)
            # lock --> plot --> unlock
            axes._trace_xlim_locked = True
            line = axes._old_plot(new_times, new_trace, *axes._trace_args[t_id], 
                                                  **axes._trace_kwargs[t_id])[0]
            axes._trace_xlim_locked = False

            # save this line so we can remove it later.
            axes._trace_lines[t_id] = line

    # actually change the xlimits
    axes._old_set_xlim(tmin, tmax, **kwargs)

def trace_set_ylim(axes, *args, **kwargs):
    '''
    This set_ylim function replaces the normal matplotlib set_ylim function
     it will not allow the ylimits to change unless you pass force_set=True.
    '''
    if 'force_set' in kwargs.keys(): 
        del kwargs['force_set']
        axes._old_set_ylim(*args, **kwargs)

def trace_autoset_ylim(axes):
    if hasattr(axes, '_trace_times'):
        all_min = 0
        all_max = 0
        for t_id in axes._traces.keys():
            ymin = numpy.min(axes._traces[t_id])
            ymax = numpy.max(axes._traces[t_id])
            if ymin < all_min: 
                all_min = ymin
            if ymax > all_max:
                all_max = ymax
        axes.set_ylim(all_min*1.05, all_max*1.05)

def trace_plot(axes, times, trace, *args, **kwargs):
    this_trace_id = uuid.uuid4()
    if 'replace_trace_id' in kwargs:
        replace_trace_id = kwargs['replace_trace_id']
        del kwargs['replace_trace_id']
        if hasattr(axes, '_trace_times'):
            if replace_trace_id in axes._trace_lines.keys():
                # delete the line first.
                axes._trace_lines[replace_trace_id].remove()
                del axes._trace_lines[replace_trace_id]
                del axes._traces[replace_trace_id]
                del axes._trace_times[replace_trace_id]
                del axes._trace_kwargs[replace_trace_id]
                del axes._trace_args[replace_trace_id]
                axes._trace_draw_order.remove(replace_trace_id)
            else:
                raise RuntimeError('Cannot replace trace, trace_id %s does not exist' % replace_trace_id)
        else:
            raise RuntimeError('Cannot relace a trace because none exist.')
    else:
        if not hasattr(axes, '_trace_times'):
            axes._trace_times = {}
            axes._traces = {}
            axes._trace_lines = {}
            axes._trace_kwargs = {}
            axes._trace_draw_order = []
            axes._trace_args = {}

    # add the new trace
    axes._traces[this_trace_id] = trace
    axes._trace_times[this_trace_id] = times
    axes._trace_kwargs[this_trace_id] = kwargs
    axes._trace_draw_order.append(this_trace_id)
    axes._trace_args[this_trace_id] = args
    axes.set_xlim(times[0], times[-1])
    return this_trace_id

def make_a_trace_axes(axes):
    # monkey-patch the axes.set_ylim and axes.set_xlim functions
    if not hasattr(axes, '_old_plot'):
        axes._old_plot = axes.plot
        axes.plot      = MethodType(trace_plot, axes, axes.__class__)
        axes._old_set_xlim = axes.set_xlim
        axes.set_xlim = MethodType(trace_set_xlim, axes, axes.__class__)

def make_a_raster_axes(axes):
    # monkey-patch the axes.set_ylim function
    if not hasattr(axes, '_old_set_ylim'):
        axes._old_set_ylim = axes.set_ylim
        axes.set_ylim = MethodType(trace_set_ylim, axes, axes.__class__)

def clear_figure(figure):
    '''
    Clear the figure, but keep the texts
    '''
    previous_texts = figure.texts
    figure.clear()
    figure.texts = previous_texts

def plot_raster_to_axes(spike_times, axes, 
                        bounds=None, 
                        force_bounds=True,
                        raster_pos='center',
                        marker_size=20,
                        **kwargs):
    raster_height_factor = 2.0
    if raster_pos == 'top':    
        spike_y = max(axes.get_ylim())
    elif raster_pos == 'bottom':  
        spike_y = min(axes.get_ylim())
    elif raster_pos == 'center': 
        spike_y = numpy.average(axes.get_ylim())
        raster_height_factor = 1.0
    else:
        spike_y = raster_pos # raster_pos is a y value.
    marker_size *= raster_height_factor

    spike_ys = [spike_y for t in spike_times]

    if hasattr(axes, '_old_plot'): # in case is a trace_axes
        plt_fn = axes._old_plot
    else:
        plt_fn = axes.plot
    return_value = plt_fn(spike_times, spike_ys, 
                           marker='|', 
                           markersize=marker_size,
                           linewidth=0,
                           **kwargs)
    prev_xlim = axes.get_xlim()
    if force_bounds:
        lb = bounds[0]
        ub = bounds[1]
    else:
        lb = min(bounds[0], prev_xlim[0])
        ub = max(bounds[1], prev_xlim[1])
    axes.set_xlim(lb, ub)
    return return_value

def clear_axes(axes, clear_tick_labels=False):
    '''
    Clear the axes but not the x or ylabels
    '''
    xlabel = axes.get_xlabel()
    ylabel = axes.get_ylabel()
    axes.clear()
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    if clear_tick_labels == True:
        axes.set_xticklabels([''], visible=False)   
        axes.set_yticklabels([''], visible=False)   
    elif clear_tick_labels == 'y_only':
        axes.set_yticklabels([''], visible=False)   
    elif clear_tick_labels == 'x_only':
        axes.set_xticklabels([''], visible=False)   
    # remove extra data potentially put there by a trace_axes
    if hasattr(axes, '_trace_times'):
        del axes._trace_times
        del axes._traces
        del axes._trace_lines
        del axes._trace_kwargs
        del axes._trace_args
        del axes._trace_draw_order
    if hasattr(axes, '_post_trace_id'):
        del axes._post_trace_id
    if hasattr(axes, '_trace_xlim_locked'):
        del axes._trace_xlim_locked

def set_title(figure=None, old_text_obj=None, canvas_size_in_pixels=None, 
              new_name=None):
    if old_text_obj is not None and old_text_obj in figure.texts:
        figure.texts.remove(old_text_obj)
    title_vspace = config['gui']['plotting']['spacing']['title_vspace']
    text_y = 1.0 - as_fraction(y=title_vspace, 
                               canvas_size_in_pixels=canvas_size_in_pixels)
    text_x = 0.5
    fontsize = config['gui']['plotting']['title_fontsize']
    return figure.text(text_x, text_y, new_name, 
                       fontsize=fontsize,
                       horizontalalignment='center',
                       verticalalignment='center')

def set_axes_ticker(axes, axis='both', nbins=7, steps=[1,2,5,10], 
                    prune='lower', **kwargs):
    '''
    Sets the number of labeled ticks on the specified axis of the axes.
    Inputs:
        axes        : a matplotlib Axes2D object
        axis        : a string with either 'xaxis', 'yaxis', or 'both'
        nbins       : the number of tickmarks you want on the specified axis.
        steps       : something the MaxNLocator needs to make good choices.
        prune       : leave off a tick, one of 'lower', 'upper', 'both' or None
        **kwargs    : passed on to MaxNLocator
    Returns: None
    '''
    try:
        if axis == 'xaxis' or axis == 'both':
            axes.xaxis.set_major_locator(MaxNLocator(nbins=nbins, 
                                                     steps=steps, 
                                                     prune=prune,
                                                     **kwargs))
        if axis == 'yaxis' or axis == 'both':
            axes.yaxis.set_major_locator(MaxNLocator(nbins=nbins,
                                                     steps=steps,
                                                     prune=prune,
                                                     **kwargs))
    except: # more bullshit with Matplotlib versions.
        pass
        

def as_fraction(x=None, y=None, canvas_size_in_pixels=None):
    if x is not None and y is not None:
        return x/canvas_size_in_pixels[0], y/canvas_size_in_pixels[1]
    elif x is not None:
        return x/canvas_size_in_pixels[0]
    elif y is not None:
        return y/canvas_size_in_pixels[1]

def as_fraction_axes(x=None, y=None, axes=None,
                     canvas_size_in_pixels=None):
    try:
        bbox = axes.get_position()
        height = bbox.height
        width  = bbox.width
    except:
        return

    height *= canvas_size_in_pixels[1]
    width *= canvas_size_in_pixels[0]

    if x is not None and y is not None:
        return float(x/width), float(y/height)
    elif x is not None:
        return float(x/width)
    elif y is not None:
        return float(y/height)

def add_shadow_legend(x, y, axes, canvas_size, ncol=100, loc='lower right'):
    x_frac, y_frac = as_fraction_axes(x, y, axes, canvas_size)
    if loc=='lower left':
        bbox_to_anchor=[x_frac, 1.0-y_frac]
    else:
        bbox_to_anchor=[1.0+x_frac, 1.0-y_frac]

    try:
        axes.legend(loc=loc,
                    shadow=True,
                    ncol=ncol,
                    bbox_to_anchor=bbox_to_anchor)
    except:
        return

def set_tick_fontsize(axes, fontsize=12):
    for ticklabel in axes.get_yticklabels():
        ticklabel.set_size(fontsize)
    for ticklabel in axes.get_xticklabels():
        ticklabel.set_size(fontsize)

def format_y_axis_hist(axes, minimum_max=None, fontsize=None):
    ylim = axes.get_ylim()
    y_max = int(ylim[1]+1)
    if minimum_max is not None:
        if y_max < minimum_max:
            y_max = minimum_max
    if y_max % 2:
        y_max = int(y_max)+1 # force y_max is even.
    y_mid = y_max/2

    axes.set_ylim(0, y_max)
    axes.set_yticks([y_mid, y_max])
    if fontsize is not None:
        set_tick_fontsize(axes, fontsize)
    
def adjust_axes_edges(axes, canvas_size_in_pixels=None, 
                            top=0.0, 
                            bottom=0.0, 
                            left=0.0, 
                            right=0.0):
    '''
    Adjusts the axes edge positions relative to the center of the axes.
        POSITIVE -> OUTWARD or growing the axes
        NEGATIVE -> INWARD or shrinking the axes
    If canvas_size_in_pixels is provided and not None then adjustments
        are in pixels, otherwise they are in percentage of the figure size.
    Returns:
        box         : the bbox for the axis after it has been adjusted.
    '''
    # adjust to percentages of canvas size.
    if canvas_size_in_pixels is not None: 
        left, top = as_fraction(left, top, canvas_size_in_pixels)
        right, bottom = as_fraction(right, bottom, canvas_size_in_pixels)
        
    'Moves given edge of axes by a fraction of the figure size.'
    box = axes.get_position()
    if top is not None:
        box.p1 = (box.p1[0], box.p1[1]+top)
    if bottom is not None:
        box.p0 = (box.p0[0], box.p0[1]-bottom)
    if left is not None:
        box.p0 = (box.p0[0]-left, box.p0[1])
    if right is not None:
        box.p1 = (box.p1[0]+right, box.p1[1])
    axes.set_position(box)
    return box

class PlotPanelPrintout(wx.Printout):
    # pep-8 is broken in this class because the wx print framework requires 
    #     overwriting specific methods in Printout subclasses
    def __init__(self, canvas):
        wx.Printout.__init__(self)
        self.canvas = canvas
        
    def OnPrintPage(self, page):
        dc = self.GetDC()
        canvas = self.canvas

        canvas_width, canvas_height = canvas.GetSize()
        horizontal_margins = canvas_width / 17.0
        vertical_margins = canvas_width / 17.0

        (dc_width, dc_height) = dc.GetSizeTuple()

        width_scale = (float(dc_width) - 2*horizontal_margins)/canvas_width
        height_scale = (float(dc_height) - 2*vertical_margins)/canvas_height

        good_scale = min(width_scale, height_scale)

        x_pos = (dc_width - canvas_width*good_scale)/2
        y_pos = (dc_height - canvas_height*good_scale)/2

        dc.SetUserScale(good_scale, good_scale)
        dc.SetDeviceOrigin(int(x_pos), int(y_pos))
        

        self.canvas.draw(drawDC=dc)
