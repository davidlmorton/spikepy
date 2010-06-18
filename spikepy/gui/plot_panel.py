import matplotlib
matplotlib.use( 'WXAgg' )
from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg as Canvas,
                                             NavigationToolbar2WxAgg as Toolbar)
from matplotlib.figure import Figure
import wx
from wx.lib.pubsub import Publisher as pub

class PlotPanel (wx.Panel):
    def __init__(self, parent, toolbar_visible=False, **kwargs):
        wx.Panel.__init__(self, parent)

        self.figure = Figure(**kwargs)
        self.canvas = Canvas(self, -1, self.figure)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()
        if toolbar_visible:
            self._show_toolbar(sizer)
        else:
            self._hide_toolbar(sizer)

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

    def _show_toolbar(self, sizer):
        self.toolbar.Show()
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        sizer.Layout()
        self._toolbar_visible = True

    def _hide_toolbar(self, sizer):
        self.toolbar.Show(False)
        sizer.Detach(self.toolbar)
        sizer.Layout()
        self._toolbar_visible = False

    def toggle_toolbar(self):
        sizer = self.GetSizer()
        if self._toolbar_visible:
            self._hide_toolbar(sizer)
        else:
            self._show_toolbar(sizer)
        

