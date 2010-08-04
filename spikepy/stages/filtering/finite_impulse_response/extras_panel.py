
import wx

from spikepy.gui.plot_panel import PlotPanel
from spikepy.gui.look_and_feel_settings import lfs
from .simple_fir import make_fir_filter
from wx.lib.scrolledpanel import ScrolledPanel

class ExtrasPanel(ScrolledPanel):
    def __init__(self, parent, trial, stage_name, **kwargs):
        ScrolledPanel.__init__(self, parent, **kwargs)
        self._dpi       = lfs.PLOT_DPI
        self._figsize   = lfs.PLOT_FIGSIZE
        self._facecolor = lfs.PLOT_FACECOLOR

        stage_data = getattr(trial, stage_name.lower().replace(' ', '_'))
        settings = stage_data.settings
        results = stage_data.results
        plot_panel = PlotPanel(self, figsize=self._figsize, 
                                     facecolor=self._facecolor,
                                     edgecolor=self._facecolor,
                                     dpi=self._dpi,
                                     toolbar_visible=False)
        
        figure = plot_panel.figure
        traces = results

        sampling_freq = trial.sampling_freq
        critical_freq = settings['critical_freq']
        kernel_window = settings['window_name']
        taps          = settings['taps']
        kind          = settings['kind']

        kernel = make_fir_filter(sampling_freq, critical_freq, kernel_window, 
                                 taps, kind, **kwargs)

        axes = figure.add_subplot(1, 1, 1)

        axes.plot([1,2,3])
        plot_panel.canvas.draw()

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(plot_panel)
        self.SetSizer(sizer)
        self.SetupScrolling()
