
import bisect
from types import MethodType
import uuid

import wx
from matplotlib.ticker import MaxNLocator
import numpy

from spikepy.common.config_manager import config_manager as config
from spikepy.common import program_text as pt

def create_times_array(traces, sampling_freq):
    dt = (1.0/sampling_freq)
    return numpy.arange(0, traces.shape[1], dtype=traces.dtype)*dt

def is_iterable(x):
    return hasattr(x, '__len__')

def plot_limited_num_spikes(axes, x, ys, set_ranking=0, 
                                         info_anchor=(0.97, 0.03),
                                         info_va='bottom',
                                         info_ha='right',
                                         **kwargs):
    trace_limit = config['gui']['plotting']['trace_limit']
    num_diff = min(4, trace_limit/2)
    num_ys = len(ys)
    if trace_limit < num_ys:
        # too many traces to plot, find most extreme traces to plot
        good_indexes = set(numpy.arange(0, len(ys), trace_limit/num_diff))
        for i in range(num_diff-1):
            bad_ys = ys[numpy.array(list(good_indexes), dtype=numpy.int32)]
            resids = numpy.sum(ys-numpy.average(bad_ys, axis=0), axis=1)
            sorted_indexes = list(numpy.argsort(resids))
            while len(good_indexes) < (i+2)*trace_limit/num_diff:
                good_indexes.add(sorted_indexes.pop())
        plotable_ys = ys[numpy.array(list(good_indexes), dtype=numpy.int32)]

        # print how many were displayed.
        if 'color' not in kwargs.keys():
            kwargs['color'] = 'k'
        axes.text(info_anchor[0], info_anchor[1]+(set_ranking*0.08), 
                  pt.SPIKES_SHOWN % len(plotable_ys),
                  fontsize=10,
                  verticalalignment=info_va,
                  horizontalalignment=info_ha,
                  color=kwargs['color'],
                  transform=axes.transAxes)
    else:
        plotable_ys = ys
    for y in plotable_ys:
        axes.plot(x, y, **kwargs)

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
        return (x/float(canvas_size_in_pixels[0]), 
                y/float(canvas_size_in_pixels[1]))
    elif x is not None:
        return x/float(canvas_size_in_pixels[0])
    elif y is not None:
        return y/float(canvas_size_in_pixels[1])

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

