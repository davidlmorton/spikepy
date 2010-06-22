import wx
from .plot_panel import PlotPanel
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel

class MultiPlotPanel(ScrolledPanel):
    def __init__(self, parent, toolbar_visible=False, **kwargs):
        """
        A panel which holds multiple similar PlotPanels. Right-click will
            toggle showing a toolbar with PlotPanels.
        Subscribes to pubsub message: 
            'SHOW_PLOT' to alter which PlotPanel
                is visible.  (data=new_panel_key)
            'FILE_CLOSED' to destroy PlotPanels after the file they are
                associated with is closed.
        """
        ScrolledPanel.__init__(self, parent)

        self._plot_panels = {}
        self._plot_panels['DEFAULT'] = PlotPanel(self, 
                                                toolbar_visible=toolbar_visible,
                                                **kwargs)
        self._currently_shown = 'DEFAULT'
        self._toolbar_visible = toolbar_visible 

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._plot_panels['DEFAULT'], 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetupScrolling()

        self.Bind(wx.EVT_CONTEXT_MENU, self._toggle_toolbar)
        pub.subscribe(self._show_plot, topic='SHOW_PLOT')
        pub.subscribe(self._remove_plot, topic='REMOVE_PLOT')

    def _remove_plot(self, message):
        removed_panel_key = message.data
        self._show_plot(new_panel_key='DEFAULT')
        self._plot_panels[removed_panel_key].Destroy()
        del self._plot_panels[removed_panel_key]

    def _toggle_toolbar(self, event):
        for plot_panel in self._plot_panels.values():
            plot_panel.toggle_toolbar()
        if self._toolbar_visible: 
            self._toolbar_visible = False
        else: 
            self._toolbar_visible = True

    def _show_plot(self, message=None, new_panel_key=None):
        if new_panel_key is None:
            new_panel_key = message.data
        if new_panel_key not in self._plot_panels.keys():
            raise RuntimeError('Plot associated with "%s" does not exist.' %
                                new_panel_key)
        shown_plot_panel = self._plot_panels[self._currently_shown]
        self.GetSizer().Detach(shown_plot_panel)
        shown_plot_panel.Show(False)

        self._currently_shown = new_panel_key
        showing_plot_panel = self._plot_panels[new_panel_key]
        self.GetSizer().Add(showing_plot_panel, 1, wx.EXPAND)
        showing_plot_panel.Show(True)
        self.Layout()

