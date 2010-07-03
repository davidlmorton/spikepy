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
        
        # PLOT_COLOR_1 and 2 are properties below
        self.PLOT_LINEWIDTH_1 = 1.5
        self.PLOT_LINEWIDTH_2 = 2.5

        self.CONTROL_PANEL_BORDER = 0
        
    def get_main_frame_size(self):
        # main frame size
        display_size = numpy.array(wx.GetDisplaySize())
        x_ratio = display_size[0]/float(base_size[0])
        y_ratio = display_size[1]/float(base_size[1])
        # default is to open using ~80% of the screen.
        size_ratio = min(x_ratio, y_ratio)*0.8
        return size_ratio*base_size

    @property
    def TEXT_CTRL_BORDER(self):
        return self.CHOICE_BORDER

    @property
    def CHOICE_BORDER(self):
        if wx.Platform == '__WXMAC__':
            return 2
        else:
            return 1

    @property
    def MAIN_FRAME_SIZE(self):
        return self.get_main_frame_size()

    @property
    def PLOT_COLOR_1(self):
        from .utils import named_color, wx_to_matplotlib_color
        return named_color('black')

    @property
    def PLOT_COLOR_2(self):
        from .utils import named_color, wx_to_matplotlib_color
        color = wx_to_matplotlib_color(*wx.SystemSettings_GetColour(
                wx.SYS_COLOUR_HIGHLIGHT).Get())
        # make color a little darker
        color = [max(0, channel-0.10) for channel in color]
        return color

lfs = LookAndFeelSettings()
