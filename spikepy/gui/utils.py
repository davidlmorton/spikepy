"""
A collection of utility functions for the spikepy gui.
"""
import os

import wx
from wx.lib.pubsub import Publisher as pub

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

def wx_to_matplotlib_color(r, g, b, a=0):
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

"""
class StaticBoxText(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent)

        static_box = wx.StaticBox(self, **kwargs)
        static_box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        self.text = wx.StaticText(self)
        self.border = 10
        static_box_sizer.Add(self.text, proportion=1, flag=wx.ALL|wx.EXPAND, 
                             border=self.border)
    
        sizer = wx.BoxSizer()
        sizer.Add(static_box_sizer, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)

    def SetText(self, text):
        self.text.SetLabel(text)
            self.strategy_summary.select_stage(new_page_num+1)
"""

class NamedChoiceCtrl(wx.Panel):
    def __init__(self, parent, name="", choices=[], bar_width=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.name = wx.StaticText(self, label=name)
        if bar_width == None and len(choices) > 0:
            bar_width_in_characters = max(map(len, choices))
            bar_width = bar_width_in_characters*8
            self.choice = wx.Choice(self, choices=choices) 
        elif bar_width == None and len(choices) == 0:
            self.choice = wx.Choice(self, choices=choices)
        else:
            self.choice = wx.Choice(self, choices=choices)
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(self.name, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.choice, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL)
        
        self.SetSizer(sizer)

    def GetStringSelection(self):
        return self.choice.GetStringSelection()

    def SetStringSelection(self, string):
        return self.choice.SetStringSelection(string)

class NamedTextCtrl(wx.Panel):
    def __init__(self, parent, name="", **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.name = wx.StaticText(self, label=name)
        self.text_ctrl = wx.TextCtrl(self, size=(50,-1))
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(self.name, proportion=0, 
                  flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.text_ctrl, proportion=1, 
                  flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)

        self.SetSizer(sizer)

    def GetValue(self):
        return self.text_ctrl.GetValue()

