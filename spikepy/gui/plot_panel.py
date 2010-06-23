import matplotlib
matplotlib.use('WXAgg') # breaks pep-8 to put code here, but matplotlib 
                        #     requires this before importing wxagg backend
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
            show_toolbar()      : to show the toolbar
            hide_toolbar()      : to hide the toolbar
        Subscribes to:
            'TOGGLE_TOOLBAR'    : if data=None or data=self will toggle the
                                  visible state of the toolbar
            'SHOW_TOOLBAR'      : if data=None or data=self will show the
                                  toolbar
            'HIDE_TOOLBAR'      : if data=None or data=self will hide the
                                  toolbar
        """
        wx.Panel.__init__(self, parent)

        self.figure = Figure(**kwargs)
        self.canvas = Canvas(self, -1, self.figure)
        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Show(False)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        self.SetSizer(sizer)

        figheight = self.figure.get_figheight()
        figwidth  = self.figure.get_figwidth()
        dpi       = self.figure.get_dpi()
        # compensate for toolbar height, even if not visible, to keep
        #   it from riding up on the plot when it is visible and the
        #   panel is shrunk down.
        toolbar_height = self.toolbar.GetSize()[1]
        min_size = (dpi*figwidth, dpi*figheight+toolbar_height)
        self.SetMinSize(min_size)

        self._toolbar_visible = toolbar_visible
        if toolbar_visible:
            self.show_toolbar()
        else:
            self.hide_toolbar()

        pub.subscribe(self._toggle_toolbar, topic="TOGGLE_TOOLBAR")
        pub.subscribe(self._show_toolbar,   topic="SHOW_TOOLBAR")
        pub.subscribe(self._hide_toolbar,   topic="HIDE_TOOLBAR")

    # --- TOGGLE TOOLBAR ----
    def _toggle_toolbar(self, message):
        if (message.data is None or 
            self is message.data):
            self.toggle_toolbar()

    def toggle_toolbar(self):
        '''
        Toggle the visible state of the toolbar.
        '''
        if self._toolbar_visible:
            self.hide_toolbar()
        else:
            self.show_toolbar()

    # --- SHOW TOOLBAR ----
    def _show_toolbar(self, message):
        if (message.data is None or 
            self is message.data):
            self.show_toolbar()

    def show_toolbar(self):
        '''
        Make the toolbar visible.
        '''
        self.toolbar.Show(True)
        self._toolbar_visible = True
        self.GetSizer().Layout()

    # --- HIDE TOOLBAR ----
    def _hide_toolbar(self, message):
        if (message.data is None or 
            self is message.data):
            self.hide_toolbar()

    def hide_toolbar(self):
        '''
        Make toolbar invisible.
        '''
        self.toolbar.Show(False)
        self._toolbar_visible = False
        self.GetSizer().Layout()
