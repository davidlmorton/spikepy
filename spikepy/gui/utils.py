"""
A collection of utility functions for the spikepy gui.
"""
import os

import wx

gui_folder  = os.path.split(__file__)[0]
icon_folder = os.path.join(gui_folder, 'icons')

def get_bitmap_icon(name):
    icon_files = os.listdir(icon_folder)
    for file in icon_files:
        if os.path.splitext(file)[0].lower() == name.lower():
            image = wx.Image(os.path.join(icon_folder, file))
            return image.ConvertToBitmap()
    raise RuntimeError("Cannot find image named %s in icons folder." % name)
    
