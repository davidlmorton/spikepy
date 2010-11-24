"""
A collection of utility functions for the spikepy gui.
"""
import os
import copy
import cPickle

import wx
from wx.lib.pubsub import Publisher as pub
import numpy

def get_bitmap_image(name):
    try:
        command = 'from spikepy.gui.images import %s_image as spi' % name
        exec(command)
        image = eval('spi.%s.Image' % name)
        return image.ConvertToBitmap()
    except:
        raise RuntimeError("Cannot find image named %s in images folder." % name)

def normalize_rgb_color(r, g, b, a=0):
    '''return a color given its rgb values, in normalized rgb format.'''
    color = [chanel/255. for chanel in [r, g, b, a]]
    return color

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

