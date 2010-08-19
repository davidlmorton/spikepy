
import wx

import scipy.signal as scisig

from spikepy.gui.named_controls import NamedChoiceCtrl
from spikepy.gui.plot_panel import PlotPanel
from spikepy.gui.look_and_feel_settings import lfs
from .simple_fir import make_fir_filter
from wx.lib.scrolledpanel import ScrolledPanel

class DetailsPanel(ScrolledPanel):
    def __init__(self, parent, trial, stage_name, **kwargs):
        ScrolledPanel.__init__(self, parent, **kwargs)
        self._dpi       = lfs.PLOT_DPI
        self._figsize   = lfs.PLOT_FIGSIZE
        self._facecolor = lfs.PLOT_FACECOLOR

        stage_data = trial.get_stage_data(stage_name)
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

        # ---- Windowing function stuff ----
        window_selecter_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        window_selecter_label = wx.StaticText(self, 
                                    label="Select windowing functions to view:")
        flag = wx.ALIGN_LEFT|wx.ALL|wx.EXPAND
        border = 3
        window_selecter_sizer.Add(window_selecter_label, proportion=0, 
                                  flag=flag, border=border) 
        windowing_axis = figure.add_subplot(2, 2, 3)
        window_resolution = 100
        window_names = ["boxcar", "triang", "Blackman", "Hamming", "Hanning", 
                        "Bartlett", "Parzen", "Bohman", "Blackman-Harris", 
                        "Nuttall", "Barthann"]
        windows = {}
        window_checkboxes = {}
        for name in window_names:
            formatted_name = name.lower().replace("-","")
            windows[name] = scisig.get_window(formatted_name, window_resolution)
            window_checkboxes[name] = wx.CheckBox(self, label=name)
            self.Bind(wx.EVT_CHECKBOX, self._replot_windowing_functions, 
                      window_checkboxes[name])
            window_selecter_sizer.Add(window_checkboxes[name], flag=flag, 
            border=border)

        windowing_axis.legend(loc="lower right")        

        # ---- Frequency response stuff ----
        frequencies, freq_responses = scisig.freqz(kernel)
        
        freq_response_axis = figure.add_subplot(2, 2, 2)
        log10_freq_responses = scisig.log10 (abs(freq_responses))
        freq_response_axis.plot(frequencies, log10_freq_responses)

        plot_panel.canvas.draw()

        # ---- Set up sizer ----
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(plot_panel)
        sizer.Add(window_selecter_sizer)
        self.SetSizer(sizer)

        self.SetupScrolling()

        # ---- Make Variables Accessible ---- 
        self.windowing_axis = windowing_axis
        self.window_checkboxes = window_checkboxes
        self.windows = windows
        self.plot_panel = plot_panel

    def _replot_windowing_functions(self, event=None):
        '''
        Clear the axis used for plotting the windowing functions and replot the
        windowing functions that are checked.
        '''
        self.windowing_axis.clear()
        for window_name, window_checkbox in self.window_checkboxes.items():
            if window_checkbox.IsChecked():
                window = self.windows[window_name]
                self.windowing_axis.plot(window, label=window_name)
        self.plot_panel.canvas.draw()
