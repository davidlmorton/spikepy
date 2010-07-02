import wx
import numpy

base_size = numpy.array((1440, 900)) 

class LookAndFeelSettings(object):
    def __init__(self):
        # MAIN_FRAME_SIZE is a property below
        self.MAIN_FRAME_TITLE =\
                "Spikepy - A python-based spike sorting framework."
        self.MAIN_FRAME_STYLE = wx.DEFAULT_FRAME_STYLE

        self.STRATEGY_PANE_MIN_SIZE = (320, 500)
        self.STRATEGY_PANE_TITLE = 'Strategy'
        self.STRATEGY_PANE_BORDER = 4
        self.STRATEGY_SUMMARY_BORDER = 3

        self.FILE_LISTCTRL_STYLE = wx.LC_REPORT|wx.LC_VRULES
        self.FILE_LISTCTRL_MIN_SIZE = (200, 250)
        self.FILE_LISTCTRL_TITLE = 'Opened Files List'
        

    def get_main_frame_size(self):
        # main frame size
        display_size = numpy.array(wx.GetDisplaySize())
        x_ratio = display_size[0]/float(base_size[0])
        y_ratio = display_size[1]/float(base_size[1])
        # default is to open using ~80% of the screen.
        size_ratio = min(x_ratio, y_ratio)*0.8
        return size_ratio*base_size

    @property
    def MAIN_FRAME_SIZE(self):
        return self.get_main_frame_size()

lfs = LookAndFeelSettings()
