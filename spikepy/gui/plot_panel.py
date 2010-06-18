import matplotlib
matplotlib.use( 'WXAgg' )
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as Toolbar
from matplotlib.figure import Figure
import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel
import utils

WHITE = (255,255,255)

class PlotPanel (wx.Panel):
    """The PlotPanel has a Figure and a Canvas. OnSize events simply set a 
    flag, and the actual resizing of the figure triggered by an Idle event."""
    def __init__(self, parent, surround_color=WHITE, dpi=None, 
                 min_size_inches=(3,3), **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.figure = Figure(dpi=dpi, figsize=min_size_inches)

        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self._set_surround_color(surround_color)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas,1,wx.GROW)
        self.SetSizer(sizer)
        pub.subscribe(self._toggle_toolbar, topic="TOGGLE TOOLBAR")
        self._toolbar_visible = False

        """
        self.Bind(wx.EVT_SIZE, self._delayed_resize)
        self._should_resize = True

    def _delayed_resize(self, event):
        if self._should_resize:
            self._should_resize = False
            wx.CallLater(100, self._resize)
        event.Skip()

    def _resize(self):
        self._should_resize = True
        self.canvas_panel.SetupScrolling()
        """

    def _do_toolbar_toggling(self):
        sizer = self.GetSizer()
        if self._toolbar_visible:
            sizer.Detach(self.toolbar)
            self.toolbar.Disable()
            self.toolbar.Show(False)
            self._toolbar_visible = False
        else:
            if not hasattr(self, 'toolbar'):
                self.toolbar = Toolbar(self.canvas)
                self.toolbar.Realize()
            else:
                self.toolbar.Enable()
                self.toolbar.Show()
            sizer.Add(self.toolbar, 0 , wx.LEFT | wx.EXPAND)
            self._toolbar_visible = True
        sizer.Layout()
        
    def _toggle_toolbar(self, message):
        if message.data is not None and self is not message.data:
            return
        self._do_toolbar_toggling()

    def _set_surround_color(self, rgb):
        """Set figure and canvas colours to be the same."""
        if rgb is None:
            rgb = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        self.canvas.SetBackgroundColour(rgb)
        self.figure.set_facecolor(norm_rgb(rgb))


def norm_rgb(rgb, num_shades=256):
    return_rgb = [channel/float(num_shades-1) for channel in rgb]
    return return_rgb
