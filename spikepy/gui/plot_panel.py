import matplotlib
matplotlib.use('WXAgg') # breaks pep-8 to put code here, but matplotlib 
                        #     requires this before importing wxagg backend
from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg as Canvas,
                                             NavigationToolbar2WxAgg as Toolbar)
from matplotlib.figure import Figure
import wx
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.pubsub import Publisher as pub

from .utils import get_bitmap_icon

class CustomToolbar(Toolbar):
    """
    A toolbar which has a button to enlarge the canvas, and shrink it.
    """
    def __init__(self, canvas, plot_panel, **kwargs):
        Toolbar.__init__(self, canvas, **kwargs)

        self.plot_panel = plot_panel

        self.ENLARGE_CANVAS_ID = wx.NewId()
        self.AddSimpleTool(self.ENLARGE_CANVAS_ID, 
                           get_bitmap_icon('arrow_out'),
                           shortHelpString='Enlarge Canvas',
                           longHelpString='Enlarge Figure Canvas')
        wx.EVT_TOOL(self, self.ENLARGE_CANVAS_ID, self._enlarge_canvas)

        self.SHRINK_CANVAS_ID = wx.NewId()
        self.AddSimpleTool(self.SHRINK_CANVAS_ID, 
                           get_bitmap_icon('arrow_in'),
                           shortHelpString='Shrink Canvas',
                           longHelpString='Shrink Figure Canvas')
        wx.EVT_TOOL(self, self.SHRINK_CANVAS_ID, self._shrink_canvas)
        self.EnableTool(self.SHRINK_CANVAS_ID, False)

    def _enlarge_canvas(self, event=None):
        plot_panel = self.plot_panel
        plot_panel._min_size_factor = min(plot_panel._min_size_factor+0.20, 4.0)
        if plot_panel._min_size_factor == 4.0:
            self.EnableTool(self.ENLARGE_CANVAS_ID, False)
        self.EnableTool(self.SHRINK_CANVAS_ID, True)
        new_min_size = (plot_panel._original_min_size[0] 
                            * plot_panel._min_size_factor,
                        plot_panel._original_min_size[1] 
                            * plot_panel._min_size_factor)
        plot_panel.SetMinSize(new_min_size)
        if hasattr(plot_panel.GetParent(), 'SetupScrolling'):
            plot_panel.GetParent().SetupScrolling()
        event.Skip()

    def _shrink_canvas(self, event=None):
        plot_panel = self.plot_panel
        plot_panel._min_size_factor = max(plot_panel._min_size_factor-0.20, 1.0)
        if plot_panel._min_size_factor == 1.0:
            self.EnableTool(self.SHRINK_CANVAS_ID, False)
        self.EnableTool(self.ENLARGE_CANVAS_ID, True)
        new_min_size = (plot_panel._original_min_size[0] 
                            * plot_panel._min_size_factor,
                        plot_panel._original_min_size[1] 
                            * plot_panel._min_size_factor)
        plot_panel.SetMinSize(new_min_size)
        if hasattr(plot_panel.GetParent(), 'SetupScrolling'):
            plot_panel.GetParent().SetupScrolling()
        event.Skip()

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
        self.canvas = Canvas(self, wx.ID_ANY, self.figure)
        self.toolbar = CustomToolbar(self.canvas, self)
        self.toolbar.Show(False)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        sizer.Add(self.canvas, 1, wx.EXPAND)
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
        self._original_min_size = min_size
        self._min_size_factor = 1.0

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
        self.Layout()

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
        self.Layout()
