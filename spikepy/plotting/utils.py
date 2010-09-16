"""
A collection of utility functions for the spikepy plotting.
"""
import wx
from matplotlib.ticker import MaxNLocator

def clear_axes(axes, clear_tick_labels=False):
    '''
    Clear the axes but not the x or ylabels
    '''
    xlabel = axes.get_xlabel()
    ylabel = axes.get_ylabel()
    axes.clear()
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    if clear_tick_labels:
        axes.set_xticklabels([''], visible=False)   
        axes.set_yticklabels([''], visible=False)   

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

def adjust_axes_edges(axes, canvas_size_in_pixels=None, 
                            top=0.0, 
                            bottom=0.0, 
                            left=0.0, 
                            right=0.0):
    '''
    Adjusts the axes edge positions relative to the center of the axes.
    If canvas_size_in_pixels is provided and not None then adjustments
        are in pixels, otherwise they are in percentage of the figure size.
    Returns:
        box         : the bbox for the axis after it has been adjusted.
    '''
    # adjust to percentages of canvas size.
    if canvas_size_in_pixels is not None: 
        left  /= canvas_size_in_pixels[0]
        right /= canvas_size_in_pixels[0]
        top    /= canvas_size_in_pixels[1]
        bottom /= canvas_size_in_pixels[1]
        
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
