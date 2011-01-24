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
    axes.set_xlim(min(bounds[0], prev_xlim[0]),
                  max(bounds[1], prev_xlim[1]))

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

def set_axes_num_ticks(axes, axis='both', num=5):
    '''
    Sets the number of labeled ticks on the specified axis of the axes.
    Inputs:
        axes        : a matplotlib Axes2D object
        axis        : a string with either 'xaxis', 'yaxis', or 'both'
        num         : the number of tickmarks you want on the specified axis.
    Returns: None
    '''
    if axis == 'xaxis' or axis == 'both':
        # NOTE the MaxNLocator sets the maximum number of *intervals*
        #  so the max number of ticks will be one more.
        axes.xaxis.set_major_locator(MaxNLocator(num-1))
    if axis == 'yaxis' or axis == 'both':
        axes.yaxis.set_major_locator(MaxNLocator(num-1))

def as_fraction(x=None, y=None, canvas_size_in_pixels=None):
    if x is not None and y is not None:
        return x/canvas_size_in_pixels[0], y/canvas_size_in_pixels[1]
    elif x is not None:
        return x/canvas_size_in_pixels[0]
    elif y is not None:
        return y/canvas_size_in_pixels[1]

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
