
import wx

import scipy.signal as scisig

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
        
        #---- Kernel Stuff ----
        kernel = make_fir_filter(sampling_freq, critical_freq, kernel_window, 
                                 taps, kind, **kwargs)
        hamming_kernel = make_fir_filter(sampling_freq, critical_freq, 
                                 "hamming", taps, kind, **kwargs)
        boxcar_kernel = make_fir_filter(sampling_freq, critical_freq, "boxcar", 
                                 taps, kind, **kwargs)
        triang_kernel = make_fir_filter(sampling_freq, critical_freq, "triang", 
                                 taps, kind, **kwargs)
        blackman_kernel = make_fir_filter(sampling_freq, critical_freq, 
                                 "blackman", taps, kind, **kwargs)

        kernel_axes = figure.add_subplot(2, 2, 1)
        kernel_axes.plot(kernel, label="kernel")
        kernel_axes.plot(hamming_kernel, label="hamming")
        kernel_axes.plot(boxcar_kernel, label="boxcar")
        kernel_axes.plot(triang_kernel, label="triang")
        kernel_axes.plot(blackman_kernel, label="blackman")
        kernel_axes.legend(loc="upper right")
        print kernel_axes.__class__

        #---- Windowing function stuff ----

        

        frequencies, frequency_responses = scisig.freqz(kernel)
        freq_response_axis = figure.add_subplot(2, 2, 2)
        freq_response_axis.plot(frequencies, frequency_responses)
        plot_panel.canvas.draw()

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(plot_panel)
        self.SetSizer(sizer)
        self.SetupScrolling()
