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
import wx
from matplotlib.ticker import MaxNLocator

from spikepy.common.config_manager import config_manager as config

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
        spike_y = 0.0
        raster_height_factor = 1.0
    else:
        spike_y = raster_pos # raster_pos is a y value.
    marker_size *= raster_height_factor

    spike_ys = [spike_y for t in spike_times]

    axes.plot(spike_times, spike_ys, marker='|', 
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
