import matplotlib
matplotlib.use( 'WXAgg' )
from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg as Canvas,
                                             NavigationToolbar2WxAgg as Toolbar)
from matplotlib.figure import Figure
import wx
from wx.lib.pubsub import Publisher as pub

class PlotPanel (wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent)

        self.figure = Figure(**kwargs)
        self.canvas = Canvas(self, -1, self.figure)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()
        self.toolbar.Show(False)
        self._toolbar_visible = False

        figheight = self.figure.get_figheight()
        figwidth  = self.figure.get_figwidth()
        dpi       = self.figure.get_dpi()
        toolbar_size = self.toolbar.GetSize()
        min_size = (dpi*figwidth+toolbar_size[0], 
                    dpi*figheight+toolbar_size[1])
        self.SetMinSize(min_size)

        pub.subscribe(self._toggle_toolbar, topic="TOGGLE TOOLBAR")

    def _toggle_toolbar(self, message):
        if (message.data is None or 
            self is message.data):
            self._do_toolbar_toggling()

    def _do_toolbar_toggling(self):
        sizer = self.GetSizer()
        if self._toolbar_visible:
            sizer.Detach(self.toolbar)
            self.toolbar.Show(False)
            self._toolbar_visible = False
        else:
            self.toolbar.Show()
            sizer.Add(self.toolbar, 0, wx.EXPAND)
            self._toolbar_visible = True
        sizer.Layout()
        

