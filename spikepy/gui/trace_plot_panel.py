import matplotlib
import wx
from .plot_panel import PlotPanel
from wx.lib.pubsub import Publisher as pub

class TracePlotPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        # initiate plotter
        wx.Panel.__init__(self, parent, **kwargs)
        pub.subscribe(self._show_trace_plot, topic='SHOW TRACE PLOT')
        self._plot_panels = {}# keyed on fullpath
        self._plot_panels['DEFAULT'] = PlotPanel(self)
        self._currently_shown = 'DEFAULT'

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_CONTEXT_MENU, self._toggle_this_toolbar)

    def _toggle_this_toolbar(self, event):
        pub.sendMessage(topic='TOGGLE TOOLBAR', 
                        data=self._plot_panels[self._currently_shown])

    def _show_trace_plot(self, message):
        fullpath = message.data
        if fullpath not in self._plot_panels.keys():
            pub.sendMessage(topic='SETUP NEW TRACE PLOT', 
                            data=(fullpath,PlotPanel(self), self))
        shown_plot_panel = self._plot_panels[self._currently_shown]
        self.GetSizer().Detach(shown_plot_panel)
        shown_plot_panel.Show(False)

        self._currently_shown = fullpath
        showing_plot_panel = self._plot_panels[self._currently_shown]
        self.GetSizer().Add(showing_plot_panel, 1, wx.EXPAND)
        self.Layout()
        showing_plot_panel.Show(True)

    def add_plot_panel(self, plot_panel, fullpath):
        self._plot_panels[fullpath] = plot_panel
        
    def setup_dressings(self, axes, sampling_freq):
        '''Sets up the xlabel/ylabel/title of this axis'''
        axes.set_xlabel("Sample Number\n(sample rate = %d Hz)" %
                        sampling_freq)
        axes.set_ylabel("(data collection units, mV?)")
        axes.set_title("Voltage Trace")
