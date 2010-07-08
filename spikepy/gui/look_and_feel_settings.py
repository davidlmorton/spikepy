import wx
import numpy

from .utils import rgb_to_matplotlib_color

base_size = numpy.array((1440, 900)) 

class LookAndFeelSettings(object):
    def __init__(self):
        # MAIN_FRAME_SIZE is a property below
        self.MAIN_FRAME_TITLE =\
                "Spikepy - A python-based spike sorting framework."
        self.MAIN_FRAME_STYLE = wx.DEFAULT_FRAME_STYLE

        self.STRATEGY_PANE_MIN_SIZE = numpy.array((320, 500))
        self.STRATEGY_PANE_TITLE = 'Strategy'
        self.STRATEGY_PANE_BORDER = 4
        self.STRATEGY_SUMMARY_BORDER = 3

        self.FILE_LISTCTRL_STYLE = wx.LC_REPORT|wx.LC_VRULES
        self.FILE_LISTCTRL_MIN_SIZE = numpy.array((200, 250))
        self.FILE_LISTCTRL_TITLE = 'Opened Files List'
        
        self.PLOT_FACECOLOR = rgb_to_matplotlib_color(255, 255, 255, 255)
        self.PLOT_DPS = 72.0
        self.PLOT_LINEWIDTH_1 = 1.5
        self.PLOT_LINEWIDTH_2 = 2.5
        self.PLOT_COLOR_1 = rgb_to_matplotlib_color(0, 0, 0)
        # a nice bluish color
        self.PLOT_COLOR_2 = rgb_to_matplotlib_color(69, 109, 255)
        self.SPIKE_RASTER_COLOR = rgb_to_matplotlib_color(0, 0, 0)

        self.PYSHELL_DIALOG_SIZE = (500,400)

        self.CONTROL_PANEL_BORDER = 1
        self._have_size_ratio = False
        self._base_dpi = 85.0
        
    def get_size_ratio(self):
        if self._have_size_ratio:
            return self._size_ratio
        else:
            # main frame size
            display_size = numpy.array(wx.GetDisplaySize())
            x_ratio = display_size[0]/float(base_size[0])
            y_ratio = display_size[1]/float(base_size[1])
            # default is to open using ~80% of the screen.
            self._have_size_ratio = True
            self._size_ratio = min(x_ratio, y_ratio)*0.8
            return self._size_ratio
        
    def get_main_frame_size(self):
        size_ratio = self.get_size_ratio()
        return size_ratio*base_size

    @property
    def PLOT_DPI(self):
        return self._base_dpi*self.get_size_ratio()

    @property
    def PLOT_FIGSIZE(self):
        size_left = self.MAIN_FRAME_SIZE - (self.STRATEGY_PANE_MIN_SIZE +
                                            self.FILE_LISTCTRL_MIN_SIZE)
        x_left = size_left[0]
        x_left_in_inches = x_left/self.PLOT_DPI
        width_to_height = 3.14
        y_in_inches = x_left_in_inches/width_to_height
        return numpy.array((x_left_in_inches, y_in_inches))*0.8

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
        return numpy.array(self.get_main_frame_size())

lfs = LookAndFeelSettings()
