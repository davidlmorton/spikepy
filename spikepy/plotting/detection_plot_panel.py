import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy
from scipy import signal as scisig

from spikepy.plotting.multi_plot_panel import MultiPlotPanel
from spikepy.plotting.utils import adjust_axes_edges, clear_axes

from spikepy.gui.look_and_feel_settings import lfs
from spikepy.gui import program_text as pt

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
        pub.subscribe(self._remove_trial,   topic="REMOVE_PLOT")
        pub.subscribe(self._trial_added,    topic='TRIAL_ADDED')
        pub.subscribe(self._trial_altered,  topic='TRIAL_SPIKE_DETECTED')
        pub.subscribe(self._trial_filtered, topic='TRIAL_FILTERED')
        pub.subscribe(self._trial_altered,  topic="STAGE_REINITIALIZED")
        pub.subscribe(self._trial_renamed,  topic='TRIAL_RENAMED')

        self._trials     = {}
        self._trace_axes = {}
        self._spike_axes = {}

    def _remove_trial(self, message=None):
        trial_id = message.data
        del self._trials[trial_id]
        if trial_id in self._trace_axes.keys():
            del self._trace_axes[trial_id]
        if trial_id in self._spike_axes.keys():
            del self._spike_axes[trial_id]

    def _trial_added(self, message=None, trial=None):
        if message is not None:
            trial = message.data

        trial_id = trial.trial_id
        self._trials[trial_id] = trial
        num_traces = len(trial.raw_traces)
        # make room for multiple traces and a spike-rate plot.
        figsize = (self._figsize[0], self._figsize[1]*(num_traces+1))
        self.add_plot(trial_id, figsize=figsize, 
                                facecolor=self._facecolor,
                                edgecolor=self._facecolor,
                                dpi=self._dpi)
        figure = self._plot_panels[trial_id].figure
        self._create_axes(trial, figure, trial_id)
        self._replot_panels.add(trial_id)
    
    def _trial_renamed(self, message=None):
        trial = message.data
        trial_id = trial.trial_id
        new_name = trial.display_name
        spike_axes = self._spike_axes[trial_id]
        spike_axes.set_title(pt.TRIAL_NAME+new_name)
        self.draw_canvas(trial_id)
        
    def _trial_filtered(self, message=None):
        trial, stage_name = message.data
        if stage_name == 'detection_filter':
            self._trial_altered(message=message, force=True)

    def _trial_altered(self, message=None, force=False):
        trial, stage_name = message.data
        if stage_name != self.name and not force:
            return
        trial_id = trial.trial_id
        if trial_id == self._currently_shown:
            self.plot(trial_id)
            if trial_id in self._replot_panels:
                self._replot_panels.remove(trial_id)
        else:
            self._replot_panels.add(trial_id)

    def plot(self, trial_id):
        trial = self._trials[trial_id]
        figure = self._plot_panels[trial_id].figure
        
        self._plot_filtered_traces(trial, figure, trial_id)
        self._plot_spikes(trial, figure, trial_id)

        self.draw_canvas(trial_id)

    def _create_axes(self, trial, figure, trial_id):
        traces = trial.raw_traces
        for i, trace in enumerate(traces):
            if i==0:
                self._trace_axes[trial_id] = [
                        figure.add_subplot(len(traces)+1, 1, i+2)]
                top_axes = self._trace_axes[trial_id][0]
            else:
                self._trace_axes[trial_id].append(
                        figure.add_subplot(len(traces)+1, 
                                           1, i+2,
                                           sharex=top_axes,
                                           sharey=top_axes))
            axes = self._trace_axes[trial_id][-1]
            axes.set_ylabel('%s #%d' % (pt.TRACE, (i+1)))
            if i+1 < len(traces): #all but the last trace
                # make the x/yticklabels dissapear
                axes.set_xticklabels([''],visible=False)
                axes.set_yticklabels([''],visible=False)

        axes.set_xlabel(pt.PLOT_TIME)

        # lay out subplots
        canvas_size = self._plot_panels[trial_id].GetMinSize()
        lfs.default_adjust_subplots(figure, canvas_size)

        # --- add axis for spike plot ---
        self._spike_axes[trial_id] = figure.add_subplot(
                len(self._trace_axes[trial_id])+1, 1, 1)
        spike_axes = self._spike_axes[trial_id]
        self.setup_spike_axes_labels(spike_axes, trial_id)
        
        bottom = lfs.AXES_BOTTOM
        adjust_axes_edges(spike_axes, canvas_size_in_pixels=canvas_size,
                                      bottom=bottom)

    def setup_spike_axes_labels(self, spike_axes, trial_id):
        spike_axes.set_xlabel(pt.PLOT_TIME)
        spike_axes.set_ylabel(pt.SPIKE_RATE_AXIS, multialignment='center')
        trial = self._trials[trial_id]
        new_name = trial.display_name
        spike_axes.set_title(pt.TRIAL_NAME+new_name)

    def _plot_filtered_traces(self, trial, figure, trial_id):
        if trial.detection_filter.results is not None:
            traces = trial.detection_filter.results
        else:
            return
        times = trial.times

        trace_axes = self._trace_axes[trial_id]
        for trace, axes in zip(traces, trace_axes):
            clear_tick_labels = axes is not trace_axes[-1]  
            clear_axes(axes, clear_tick_labels=clear_tick_labels)

            axes.plot(times, trace, color=lfs.PLOT_COLOR_2, 
                             linewidth=lfs.PLOT_LINEWIDTH_2, 
                             label=pt.DETECTION_TRACE_GRAPH_LABEL)
            ymax = numpy.max(numpy.abs(trace))
            axes.set_ylim(ymin=-ymax*1.1, ymax=ymax*1.4)
            std = numpy.std(trace)

            for factor, linestyle in [(2,'solid'),(4,'dashed')]:
                axes.axhline(std*factor, color=lfs.PLOT_STD_LINE_COLOR, 
                                  linewidth=lfs.PLOT_STD_LINEWIDTH, 
                                  label=r'$%d\sigma$' % factor,
                                  linestyle=linestyle)
                axes.axhline(-std*factor, color=lfs.PLOT_STD_LINE_COLOR, 
                                  linewidth=lfs.PLOT_STD_LINEWIDTH, 
                                  linestyle=linestyle)
        try:
            axes.legend(loc='upper right', ncol=3, shadow=True, 
                        bbox_to_anchor=[1.03,1.1])
        except: #old versions of matplotlib don't have bbox_to_anchor
            axes.legend(loc='upper right', ncol=3)
            

    def _plot_spikes(self, trial, figure, trial_id):
        # remove old lines if present.
        spike_axes = self._spike_axes[trial_id]
        spike_axes.clear()
        self.setup_spike_axes_labels(spike_axes, trial_id)

        if trial.detection.results is not None:
            spikes = trial.detection.results
        else:
            while self._spike_axes[trial_id].lines:
                del(self._spike_axes[trial_id].lines[0])
            return # this trial has never been spike detected.
        times = trial.times

        for spike_list, axes in zip(spikes, self._trace_axes[trial_id]):
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
                                 markeredgewidth=lfs.SPIKE_RASTER_WIDTH,
                                 label=pt.SPIKES_GRAPH_LABEL)

        # --- plot spike rate ---
        width = 50.0
        required_proportion = 0.75
        accepted_spike_list = get_accepted_spike_list(trial.detection.results, 
                                                      trial.sampling_freq, 
                                                      width,
                                                      required_proportion)
        #spike_rate = get_spike_rate(accepted_spike_list, width, 
        #                            trial.sampling_freq, 
        #                            len(trial.detection_filter.results[0]))

        bin_width = 100.0
        spikes, bin_points = bin_spikes(accepted_spike_list, trial.times[-1], 
                                        bin_width=bin_width, 
                                        bin_alignment='middle')

            
        spike_axes.plot(bin_points, spikes*1000.0/bin_width, 
                        color=lfs.PLOT_COLOR_2, linewidth=lfs.PLOT_LINEWIDTH_2)

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
                                markeredgewidth=lfs.SPIKE_RASTER_WIDTH,
                                markersize=lfs.SPIKE_RASTER_HEIGHT*
                                            raster_height_factor)

        spike_axes.set_xlim(0.0, trial.times[-1])

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


def bin_spikes(spike_list, total_time, bin_width=50.0, bin_alignment="middle"):
    """
    A function to return a list of bins and a list of the number of spikes in 
        each bin.
    Inputs:
        spike_list        : the list of times at which spikes were detected
        total_time        : the length (of time) of the trace from which the 
                            spikes were detected
        bin_width         : how much time one bin should correspond to
        bin_alignment     : the location of a bin that the bin time corresponds 
                            to ('beginning', 'middle', or 'end')

    Returns:
        spikes            : an array of the number of spikes in each bin
        bin_points        : an array of bin times
    """
    low  = 0.0
    high = 0.0
    def is_between(value):
        return low <= value <= high

    bins = numpy.arange(0.0, total_time, bin_width)
    spikes = []
    for i in xrange(len(bins)-1):
        low  = bins[i]
        high = bins[i+1]
        spike_count = len(filter(is_between, spike_list))
        spikes.append(spike_count)
    # final bin
    low = bins[-1]
    high = total_time
    spike_count = len(filter(is_between, spike_list))
    spikes.append(spike_count)
    bin_shift_dict = {"beginning": 0.0, "middle": 0.5, "end": 1.0}
    bin_points = bins + bin_width*bin_shift_dict[bin_alignment]
    return numpy.array(spikes), bin_points
    