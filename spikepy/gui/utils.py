"""
A collection of utility functions for the spikepy gui.
"""
import os

import wx
from wx.lib.pubsub import Publisher as pub

from . import program_text as pt

gui_folder  = os.path.split(__file__)[0]
icon_folder = os.path.join(gui_folder, 'icons')

def recursive_layout(panel):
    if panel is not None:
        panel.Layout()
        recursive_layout(panel.GetParent())

def named_color(name):
    '''return a color given its name, in normalized rgb format.'''
    color = [chanel/255. for chanel in wx.NamedColor(name).Get()]
    return color

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
    raise RuntimeError(pt.MISSING_IMAGE_ERROR % name)

class HashableDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __hash__(self):
        sorted_keys = sorted(self.keys())
        key_value_list = [(key, self[key]) 
                          for key in sorted_keys]
        hashable_thing = tuple(key_value_list)
        return hash(hashable_thing)


        

