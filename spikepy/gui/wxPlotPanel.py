import matplotlib
matplotlib.use( 'WXAgg' )
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as Toolbar
from matplotlib.figure import Figure
import wx
from wx.lib.pubsub import Publisher as pub

WHITE = (255,255,255)

class PlotPanel (wx.Panel):
    """The PlotPanel has a Figure and a Canvas. OnSize events simply set a 
    flag, and the actual resizing of the figure triggered by an Idle event."""
    def __init__(self, parent, surround_color=WHITE, dpi=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.figure = Figure(dpi=dpi, figsize=(0.5,0.5))
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self._set_surround_color(surround_color)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas,1,wx.EXPAND)
        self.SetSizer(sizer)
        pub.subscribe(self._toggle_toolbar, topic="TOGGLE TOOLBAR")
        self._toolbar_visible = False

    def _toggle_toolbar(self, message):
        if message.data is not None and self is not message.data:
            return
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

    def _set_surround_color(self, rgbtuple):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        self.canvas.SetBackgroundColour( wx.Colour( *rgbtuple ) )

    def draw(self): 
        pass

