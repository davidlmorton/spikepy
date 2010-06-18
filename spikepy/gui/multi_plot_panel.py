import wx
from .plot_panel import PlotPanel
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel

class MultiPlotPanel(ScrolledPanel):
    def __init__(self, parent, toolbar_visible=False, **kwargs):
        """
        A panel which holds multiple similar PlotPanels. Right-click will
            toggle showing a toolbar with PlotPanels.
        Publishes pubsub message:
            self._new_plot_message to have subscriber generate a new plot and
                add it to the set of plots available. (data=(new_panel_key, 
                                                             PlotPanel(),
                                                             self))
        Subscribes to pubsub message: 
            'SHOW PLOT' to alter which PlotPanel
                is visible.  (data= new_panel_key)
        """
        ScrolledPanel.__init__(self, parent)

        self._plot_panels = {}
        self._plot_panels['DEFAULT'] = PlotPanel(self, 
                                                toolbar_visible=toolbar_visible,
                                                **kwargs)
        self._currently_shown = 'DEFAULT'
        self._toolbar_visible = toolbar_visible 
        self._kwargs = kwargs
        self._new_plot_message = 'SETUP NEW X-X PLOT' #override in subclass

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._plot_panels['DEFAULT'], 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetupScrolling()

        self.Bind(wx.EVT_CONTEXT_MENU, self._toggle_toolbar)
        pub.subscribe(self._show_plot, topic='SHOW PLOT')

    def _toggle_toolbar(self, event):
        for plot_panel in self._plot_panels.values():
            plot_panel.toggle_toolbar()
        if self._toolbar_visible: 
            self._toolbar_visible = False
        else: 
            self._toolbar_visible = True

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

    def _setup_new_plot(self, new_panel_key): 
        pub.sendMessage(topic=self._new_plot_message, 
                        data=(new_panel_key, 
                              PlotPanel(self, 
                                        toolbar_visible=self._toolbar_visible,
                                        **self._kwargs),
                              self))
