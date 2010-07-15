import wx

from spikepy.gui.plot_panel import PlotPanel
from spikepy.gui.look_and_feel_settings import lfs

class ExtrasPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

