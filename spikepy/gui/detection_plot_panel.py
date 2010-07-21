import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy
from scipy import signal as scisig

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel
from .utils import rgb_to_matplotlib_color
from .look_and_feel_settings import lfs
from . import program_text as pt

class DetectionPlotPanel(MultiPlotPanel):
    def __init__(self, parent, name):
        self._dpi       = lfs.PLOT_DPI
        self._figsize   = lfs.PLOT_FIGSIZE
        self._facecolor = lfs.PLOT_FACECOLOR
        self.name       = name
        MultiPlotPanel.__init__(self, parent, figsize=self._figsize,
                                              facecolor=self._facecolor,
                                              edgecolor=self._facecolor,
                                              dpi=self._dpi)
        pub.subscribe(self._remove_trial,  topic="REMOVE_PLOT")
        pub.subscribe(self._trial_added,   topic='TRIAL_ADDED')
        pub.subscribe(self._trial_altered, topic='TRIAL_DETECTIONED')
        pub.subscribe(self._trial_altered, topic="TRIAL_DETECTION_FILTERED")

        self._trials     = {}
        self._trace_axes = {}
        self._spike_axes = {}

    def _remove_trial(self, message=None):
        full_path = message.data
        del self._trials[full_path]
        del self._trace_axes[full_path]
        del self._spike_axes[fullpath]

    def _trial_added(self, message=None, trial=None):
        if message is not None:
            trial = message.data

        fullpath = trial.fullpath
        self._trials[fullpath] = trial
        num_traces = len(trial.raw_traces)
        # make room for multiple traces and a spike-rate plot.
        figsize = (self._figsize[0], self._figsize[1]*(num_traces+1))
        self.add_plot(fullpath, figsize=figsize, 
                                facecolor=self._facecolor,
                                edgecolor=self._facecolor,
                                dpi=self._dpi)

    def _trial_altered(self, message=None):
        trial = message.data
        fullpath = trial.fullpath
        if fullpath == self._currently_shown:
            self.plot(fullpath)
            if fullpath in self._replot_panels:
                self._replot_panels.remove(fullpath)
        else:
            self._replot_panels.add(fullpath)

    def plot(self, fullpath):
        trial = self._trials[fullpath]
        figure = self._plot_panels[fullpath].figure
        
        if (fullpath not in self._trace_axes.keys() and
                trial.detection_filter.results is not None):
            self._create_axes(trial, figure, fullpath)
        self._plot_filtered_traces(trial, figure, fullpath)
        self._plot_spikes(trial, figure, fullpath)

        self.draw_canvas(fullpath)

    def _create_axes(self, trial, figure, fullpath):
        traces = trial.detection_filter.results
        for i, trace in enumerate(traces):
            if i==0:
                self._trace_axes[fullpath] = [
                        figure.add_subplot(len(traces)+1, 1, i+2)]
                top_axes = self._trace_axes[fullpath][0]
            else:
                self._trace_axes[fullpath].append(
                        figure.add_subplot(len(traces)+1, 
                                           1, i+2,
                                           sharex=top_axes,
                                           sharey=top_axes))
            axes = self._trace_axes[fullpath][-1]
            axes.set_ylabel('%s #%d' % (pt.TRACE, (i+1)))
            if i+1 < len(traces): #all but the last trace
                # make the x/yticklabels dissapear
                axes.set_xticklabels([''],visible=False)
                axes.set_yticklabels([''],visible=False)

        axes.set_xlabel(pt.PLOT_TIME)

        # lay out subplots
        canvas_size = self._plot_panels[fullpath]._original_min_size
        left   = lfs.PLOT_LEFT_BORDER / canvas_size[0]
        right  = 1.0 - lfs.PLOT_RIGHT_BORDER / canvas_size[0]
        top    = 1.0 - lfs.PLOT_TOP_BORDER / canvas_size[1]
        bottom = lfs.PLOT_BOTTOM_BORDER / canvas_size[1]
        figure.subplots_adjust(hspace=0.025, left=left, right=right, 
                               bottom=bottom, top=top)

        # --- add axis for spike plot ---
        self._spike_axes[fullpath] = figure.add_subplot(
                len(self._trace_axes[fullpath])+1, 1, 1)
        spike_axes = self._spike_axes[fullpath]
        spike_axes.set_xlabel(pt.PLOT_TIME)
        spike_axes.set_ylabel(pt.SPIKE_RATE_AXIS)
        title = os.path.split(fullpath)[1]
        spike_axes.set_title(title)
        
        # move raster plot's bottom edge up a bit
        box = spike_axes.get_position()
        box.p0 = (box.p0[0], box.p0[1]+bottom)
        spike_axes.set_position(box)
        

    def _plot_filtered_traces(self, trial, figure, fullpath):
        if trial.detection_filter.results is not None:
            traces = trial.detection_filter.results
        else:
            return
        times = trial.times

        for trace, axes in zip(traces, self._trace_axes[fullpath]):
            while axes.lines:
                del(axes.lines[0])     
            axes.plot(times, trace, color=lfs.PLOT_COLOR_2, 
                             linewidth=lfs.PLOT_LINEWIDTH_2, 
                             label=pt.DETECTION_TRACE_GRAPH_LABEL)

    def _plot_spikes(self, trial, figure, fullpath):
        if trial.detection.results is not None:
            spikes = trial.detection.results
        else:
            while self._spike_axes[fullpath].lines:
                del(self._spike_axes[fullpath].lines[0])
            return # this trial has never been spike detected.
        times = trial.times

        for spike_list, axes in zip(spikes, self._trace_axes[fullpath]):
            axes.set_autoscale_on(False)
            lines = axes.get_lines()
            # check if raster is already plotted
            if len(lines) == 2:
                del(axes.lines[1])
            
            raster_height_factor = 2.0
            raster_pos = lfs.SPIKE_RASTER_ON_TRACES_POSITION
            if raster_pos == 'top':    spike_y = max(axes.get_ylim())
            if raster_pos == 'botom':  spike_y = min(axes.get_ylim())
            if raster_pos == 'center': 
                spike_y = 0.0
                raster_height_factor = 1.0
            spike_xs = spike_list
            spike_ys = [spike_y for spike_index in spike_list]
            axes.plot(spike_xs, spike_ys, color=lfs.SPIKE_RASTER_COLOR, 
                                 linewidth=0, 
                                 marker='|',
                                 markersize=lfs.SPIKE_RASTER_HEIGHT*
                                            raster_height_factor,
                                 label=pt.SPIKES_GRAPH_LABEL)

        # --- plot spike rate ---
        width = 50.0
        required_proportion = 0.75
        accepted_spike_list = get_accepted_spike_list(trial.detection.results, 
                                                      trial.sampling_freq, 
                                                      width,
                                                      required_proportion)
        spike_rate = get_spike_rate(accepted_spike_list, width, 
                                    trial.sampling_freq, 
                                    len(trial.detection_filter.results[0]))
        spike_axes = self._spike_axes[fullpath]

        # remove old lines if present.
        while spike_axes.lines:
            del spike_axes.lines[0]
            
        spike_axes.plot(times, spike_rate, color=lfs.PLOT_COLOR_2, 
                                    linewidth=lfs.PLOT_LINEWIDTH_2)

        raster_height_factor = 2.0
        raster_pos = lfs.SPIKE_RASTER_ON_RATE_POSITION
        if raster_pos == 'top':    spike_y = max(spike_axes.get_ylim())
        if raster_pos == 'botom':  spike_y = min(spike_axes.get_ylim())
        if raster_pos == 'center': 
            spike_y = 0.0
            raster_height_factor = 1.0
            
        spike_xs = accepted_spike_list
        spike_ys = [spike_y for spike_index in accepted_spike_list]
        spike_axes.plot(spike_xs, spike_ys, 
                                color=lfs.SPIKE_RASTER_COLOR,
                                linewidth=0.0,
                                marker='|',
                                markersize=lfs.SPIKE_RASTER_HEIGHT*
                                            raster_height_factor)

def get_accepted_spike_list(spikes, samling_freq, width, required_proportion):
    '''
    Gather the spikes which occur across <reqired_proportion> of electrodes
    within <width> of spikes on the other electrodes.
    '''
    return spikes[0] # FIXME flesh out and put into detection code.


def get_spike_rate(spike_list, width, sampling_rate, num_samples):
    binary_spike_train = numpy.zeros(num_samples, dtype=numpy.float64)
    dt = (1.0/sampling_rate)*1000.0
    for spike in spike_list:
        binary_spike_train[int(spike/dt)] = 1.0
    kernel = gaussian_kernel(width, sampling_rate)
    return scisig.convolve(kernel, binary_spike_train, mode='same')*1000.0


def gaussian_kernel(width, sampling_rate):
    "width in (ms), sampling_rate in (Hz)"
    # -3*width to 3*width will get more than 99.7% of strength
    samples_per_ms = sampling_rate/1000.0
    num_samples = samples_per_ms * 6.0 * width
    if not num_samples%2: # ensure odd num_samples
        num_samples += 1
    x_values = numpy.linspace(-3.0*width, 3.0*width, num_samples)
    result = gaussian(x_values, width)
    result /= (numpy.sum(result)/num_samples)*6.0*width # normalize
    return result


def gaussian(x, width):
    peak = 1.0/numpy.sqrt(2*numpy.pi*width**2)
    exponent = -x**2/(2*width**2)
    return peak * numpy.exp(exponent)
    
