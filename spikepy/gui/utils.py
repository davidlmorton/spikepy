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

