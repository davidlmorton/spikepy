
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
    if hasattr(panel, 'Layout'):
        if hasattr(panel, 'SendSizeEvent'):
            panel.SendSizeEvent()
        panel.Layout()
        if hasattr(panel, 'SendSizeEvent'):
            panel.SendSizeEvent()
        if hasattr(panel, 'GetParent'):
            recursive_layout(panel.GetParent())

def named_color(name):
    '''return a color given its name, in normalized rgb format.'''
    prenormalized_color = wx.NamedColor(name).Get()
    if -1 not in prenormalized_color:
        color = [chanel/255. for chanel in prenormalized_color]
        return color
    else: 
        raise ValueError, "%s is not in wx.TheColourDatabase" % name

