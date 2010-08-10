import wx
import numpy

from .utils import rgb_to_matplotlib_color

base_size = numpy.array((1440, 900)) 

# look and feel settings must be a class because some of the 'settings'
#   require a wx.app to have been created before they can be calculated.
#   Those settings are made into properties so we can delay that calculation.
class LookAndFeelSettings(object):
    def __init__(self):
        # MAIN_FRAME_SIZE is a property below
        self.MAIN_FRAME_STYLE = wx.DEFAULT_FRAME_STYLE
        self.METHOD_EXTRAS_FRAME_STYLE = wx.DEFAULT_FRAME_STYLE
        self._have_size_ratio = False

        self.STRATEGY_PANE_MIN_SIZE = numpy.array((350, 500))
        self.STRATEGY_PANE_BORDER = 4
        self.STRATEGY_SUMMARY_BORDER = 3
        self.STRATEGY_WAIT_TIME = 350 # in ms

        self.FILE_LISTCTRL_STYLE = wx.LC_REPORT|wx.LC_VRULES
        self.FILE_LISTCTRL_MIN_SIZE = numpy.array((200, 150))
        
        self.PLOT_FACECOLOR = rgb_to_matplotlib_color(255, 255, 255, 255)
        self.PLOT_LINEWIDTH_1 = 1.5
        self.PLOT_LINEWIDTH_2 = 2.5
        self.PLOT_LINEWIDTH_3 = 2.5
        self.PLOT_LINEWIDTH_4 = 0.7 # for features
        self.PLOT_COLOR_1 = rgb_to_matplotlib_color(0, 0, 0)
        # a nice bluish color
        self.PLOT_COLOR_2 = rgb_to_matplotlib_color(69, 109, 255)
        self.PLOT_COLOR_2_light = '#87CEFF'
        # amber/orange
        self.PLOT_COLOR_3 = rgb_to_matplotlib_color(255, 189, 63)
        self.SPIKE_RASTER_COLOR = rgb_to_matplotlib_color(0, 0, 0)
        self.SPIKE_RASTER_ON_TRACES_POSITION = 'center' # top, bottom, or center
        self.SPIKE_RASTER_ON_RATE_POSITION   = 'bottom' # top, bottom, or center
        self.SPIKE_RASTER_WIDTH              = 1.5

        # general plot values
        self.NO_LABEL_AXES_LEFT   = -7.0 # pixels
        self.NO_LABEL_AXES_BOTTOM = -7.0 # pixels
        self.AXES_LEFT   = -75.0 # pixels
        self.AXES_BOTTOM = -40.0 # pixels

        self.PLOT_LEFT_BORDER  = plb = 90.0 # pixels
        self.PLOT_RIGHT_BORDER = prb = 25.0 # pixels
        self.PLOT_TOP_BORDER         = 35.0 # pixels
        self.PLOT_BOTTOM_BORDER      = 35.0 # pixels
        self.PLOT_DPI = 72.0

        # cluster plot panel specifics
        self.CLUSTER_RIGHT_YLABEL = 25.0 # pixels
        self.CLUSTER_RASTER_RIGHT = prb-45.0 # pixels
        self.CLUSTER_RASTER_LEFT  = plb-45.0 # pixels
        self.CLUSTER_STD_ALPHA    = 0.35 
        self.CLUSTER_TRACE_ALPHA  = 0.14

        self.PYSHELL_DIALOG_SIZE = (500, 400)

        self.CONTROL_PANEL_BORDER = 0
        
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

    def get_results_frame_size(self):
        # FIXME this assumes default layout.
        size = self.MAIN_FRAME_SIZE
        size[0] -= self.FILE_LISTCTRL_MIN_SIZE[0]
        size[0] -= self.STRATEGY_PANE_MIN_SIZE[0]
        return size
        
    def get_main_frame_size(self):
        size_ratio = self.get_size_ratio()
        return size_ratio*base_size

    @property
    def PLOT_MIN_SIZE_X(self):
        return 0.84*self.get_results_frame_size()[0]

    @property
    def PLOT_MIN_SIZE_Y(self):
        return self.get_results_frame_size()[1]*0.70

    @property
    def PLOT_FIGSIZE(self):
        size_left = self.MAIN_FRAME_SIZE - self.STRATEGY_PANE_MIN_SIZE
        x_left = size_left[0]
        x_left_in_inches = x_left/self.PLOT_DPI
        width_to_height = 3.14
        y_in_inches = x_left_in_inches/width_to_height
        return numpy.array((x_left_in_inches, y_in_inches))*0.8

    @property
    def SPIKE_RASTER_HEIGHT(self):
        return int(self.MAIN_FRAME_SIZE[1]/45.0) # in pixels

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
        
    @property
    def PREFERENCES_FRAME_SIZE(self):
        # FIXME change this once we decide what we size we want for the 
        #       preferences frame
        return numpy.array(self.get_main_frame_size())

    @property
    def METHOD_EXTRAS_FRAME_SIZE(self):
        # FIXME change this once we decide what we size we want for the 
        #       method extras frame
        return numpy.array(self.get_main_frame_size())

    def default_adjust_subplots(self, figure, canvas_size_in_pixels):
        '''
        Adjust the figure's subplot parameters according to the defaults in
        look and feel settings.
        '''
        left   = self.PLOT_LEFT_BORDER / canvas_size_in_pixels[0]
        right  = 1.0 - self.PLOT_RIGHT_BORDER / canvas_size_in_pixels[0]
        top    = 1.0 - self.PLOT_TOP_BORDER / canvas_size_in_pixels[1]
        bottom = self.PLOT_BOTTOM_BORDER / canvas_size_in_pixels[1]
        figure.subplots_adjust(hspace=0.03, wspace=0.03, 
                               left=left, right=right, 
                               bottom=bottom, top=top)

lfs = LookAndFeelSettings()
