import wx
from .plot_panel import PlotPanel
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel

class MultiPlotPanel(ScrolledPanel):
    def __init__(self, parent, **kwargs):
        ScrolledPanel.__init__(self, parent)

        self._plot_panels = {}
        self._plot_panels['DEFAULT'] = PlotPanel(self, **kwargs)
        self._currently_shown = 'DEFAULT'
        self._kwargs = kwargs

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._plot_panels['DEFAULT'], 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetupScrolling()

        self.Bind(wx.EVT_CONTEXT_MENU, self._toggle_toolbar_on_current_plot)
        pub.subscribe(self._show_plot, topic='SHOW PLOT')

    def _toggle_toolbar_on_current_plot(self, event):
        pub.sendMessage(topic='TOGGLE TOOLBAR', 
                        data=self._plot_panels[self._currently_shown])

    def _show_plot(self, message):
        new_panel_key = message.data
        if new_panel_key not in self._plot_panels.keys():
            self._setup_new_plot(new_panel_key)
        shown_plot_panel = self._plot_panels[self._currently_shown]
        self.GetSizer().Detach(shown_plot_panel)
        shown_plot_panel.Show(False)

        self._currently_shown = new_panel_key
        showing_plot_panel = self._plot_panels[new_panel_key]
        self.GetSizer().Add(showing_plot_panel, 1, wx.EXPAND)
        showing_plot_panel.Show(True)
        self.Layout()

    def add_plot_panel(self, plot_panel, key):
        self._plot_panels[key] = plot_panel

    def _setup_new_plot(self, new_plot_key):
        pass #needs to be defined in sub-classes
