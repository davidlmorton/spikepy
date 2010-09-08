"""
A collection of utility functions for the spikepy gui.
"""
import os
import copy
import cPickle

import wx
from wx.lib.pubsub import Publisher as pub
import numpy
from numpy.linalg import svd
from matplotlib.ticker import MaxNLocator

gui_folder  = os.path.split(__file__)[0]
icon_folder = os.path.join(gui_folder, 'icons')

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
    
def recursive_layout(panel):
    if panel is not None:
        panel.Layout()
        recursive_layout(panel.GetParent())

def named_color(name):
    '''return a color given its name, in normalized rgb format.'''
    prenormalized_color = wx.NamedColor(name).Get()
    if -1 not in prenormalized_color:
        color = [chanel/255. for chanel in prenormalized_color]
        return color
    else: 
        raise ValueError, "%s is not in wx.TheColourDatabase" % name

def rgb_to_matplotlib_color(r, g, b, a=0):
    '''return a color given its rgb values, in normalized rgb format.'''
    color = [chanel/255. for chanel in [r, g, b, a]]
    return color

def get_bitmap_icon(name):
    icon_files = os.listdir(icon_folder)
    for file in icon_files:
        if os.path.splitext(file)[0].lower() == name.lower():
            image = wx.Image(os.path.join(icon_folder, file))
            return image.ConvertToBitmap()
    raise RuntimeError("Cannot find image named %s in icons folder." % name)

class HashableDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __hash__(self):
        sorted_keys = sorted(self.keys())
        key_value_list = [(key, self[key]) 
                          for key in sorted_keys]
        hashable_thing = tuple(key_value_list)
        return hash(hashable_thing)


def make_dict_hashable(unhashable_dict):
    for key in unhashable_dict.keys():
        if (isinstance(unhashable_dict[key], dict) and 
            not isinstance(unhashable_dict[key], HashableDict)):
            unhashable_dict[key] = HashableDict(unhashable_dict[key])
            make_dict_hashable(unhashable_dict[key])

def strip_unicode(dictionary):
    striped_dict = {}
    for key, value in dictionary.items():
        striped_dict[str(key)] = copy.deepcopy(value)
    return striped_dict 

def load_pickle(path):
    with open(path) as ifile:
        pickled_thing = cPickle.load(ifile)
    return pickled_thing
    
class SinglePanelFrame(wx.Frame):
    # After creating an instance of this class, create a panel with the frame
    # instance as its parent.
    def __init__(self, parent, id=wx.ID_ANY, title='', size=(50, 50), 
                 style=wx.DEFAULT_FRAME_STYLE, is_modal=True):
        wx.Frame.__init__(self, parent, title=title, size=size, style=style)
        if is_modal:
            self.MakeModal(True)
        self.Bind(wx.EVT_CLOSE, self._close_frame)
    
    def _close_frame(self, message=None):
        self.MakeModal(False)
        self.Destroy()

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


def pca(P):
    """
    Use singular value decomposition to determine the optimal
    rotation of the basis to view data from.

    Input:
    P          : an m x n array of input data
                (m trials, n measurements)
                (m rows  , n columns)

    Return value are
    signals     : rotated view of the data.
    pc          : each row is a principal component
    var         : the variance associated with each pc
                   this is the bias corrected variance using 
                   m-1 instead of m.
    """
    # first we need to zero mean the data
    m,n = P.shape
    column_means = sum(P,0) / m
    zmP = P - column_means

    # generate the Y vector we will decompose
    Y = zmP / numpy.sqrt(m-1)

    # do the singular value decomposition
    u,s,pc = svd(Y)
    # find the variance along each principal axis
    var = s**2

    # The transformed data
    signals = numpy.dot(pc,P.T).T

    return signals, pc, var

