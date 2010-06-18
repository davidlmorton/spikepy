import matplotlib
matplotlib.use( 'WXAgg' )
from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg as Canvas,
                                             NavigationToolbar2WxAgg as Toolbar)
from matplotlib.figure import Figure
import wx
from wx.lib.pubsub import Publisher as pub

class PlotPanel (wx.Panel):
    def __init__(self, parent, toolbar_visible=False, **kwargs):
        """
        A panel which contains a matplotlib figure with (optionally) a 
            toolbar to zoom/pan/ect.
        Inputs:
            parent              : the parent frame/panel
            toolbar_visible     : the initial state of the toolbar
            **kwargs            : arguments passed on to 
                                  matplotlib.figure.Figure
        Introduces:
            figure              : a matplotlib figure
            canvas              : a FigureCanvasWxAgg from matplotlib's
                                  backends
            toggle_toolbar()    : to toggle the visible state of the toolbar
        Subscribes to:
            'TOGGLE TOOLBAR'    : if data=None or data=self will toggle the
                                  visible state of the toolbar
        """
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
        min_size = (dpi*figwidth, dpi*figheight)
        self.SetMinSize(min_size)

        pub.subscribe(self._toggle_toolbar, topic="TOGGLE TOOLBAR")

    def _toggle_toolbar(self, message):
        if (message.data is None or 
            self is message.data):
            self.toggle_toolbar()

    def toggle_toolbar(self):
        '''
        Toggle the visible state of the toolbar.
        '''
        sizer = self.GetSizer()
        if self._toolbar_visible:
            self._hide_toolbar(sizer)
        else:
            self._show_toolbar(sizer)

    def _show_toolbar(self, sizer):
        self.toolbar.Show()
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        self._toolbar_visible = True
        sizer.Layout()

    def _hide_toolbar(self, sizer):
        self.toolbar.Show(False)
        sizer.Detach(self.toolbar)
        self._toolbar_visible = False
        sizer.Layout()
