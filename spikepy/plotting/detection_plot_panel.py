"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy

from spikepy.plotting.spikepy_plot_panel import SpikepyPlotPanel
from spikepy.plotting import utils

from spikepy.common.config_manager import config_manager as config
from spikepy.common import program_text as pt

class DetectionPlotPanel(SpikepyPlotPanel):
    def __init__(self, parent, name):
        SpikepyPlotPanel.__init__(self, parent, name)

        pc = config['gui']['plotting']
        self.line_color = pc['detection']['filtered_trace_color']
        self.line_width = pc['detection']['filtered_trace_linewidth']

        
    def _basic_setup(self, trial_id):
        plot_panel = self._plot_panels[trial_id]
        plot_panel.clear()

        trial = self._trials[trial_id]
        # set the size of the plot properly
        num_traces = len(trial.raw_traces)
        num_rows = 1 + num_traces
        figheight = self._figsize[1] * num_rows
        figwidth  = self._figsize[0]
        plot_panel.set_minsize(figwidth, figheight)
        self._trial_renamed(trial_id=trial_id)

        # set up firing_rate and trace axes
        figure = plot_panel.figure
        plot_panel.axes['rate'] = figure.add_subplot(num_rows, 1, 1)
        plot_panel.axes['trace'] = []
        for i in xrange(len(trial.raw_traces)):
            trace_axes = figure.add_subplot(num_rows, 1, i+2)
            plot_panel.axes['trace'].append(trace_axes)

        canvas_size = plot_panel.GetMinSize()
        # adjust subplots to spikepy uniform standard
        config.default_adjust_subplots(figure, canvas_size)

        # tweek firing_rate axes and trace axes
        top = -config['gui']['plotting']['spacing']['title_vspace']
        bottom = config['gui']['plotting']['spacing']['axes_bottom']
        utils.adjust_axes_edges(plot_panel.axes['rate'], canvas_size,
                                bottom=bottom, top=top)

        nl_bottom = config['gui']['plotting']['spacing']['no_label_axes_bottom']
        for trace_axes in plot_panel.axes['trace'][:-1]:
            utils.adjust_axes_edges(trace_axes, canvas_size, bottom=nl_bottom)

        # label axes
        plot_panel.axes['rate'].set_xlabel(pt.PLOT_TIME)
        plot_panel.axes['rate'].set_ylabel(pt.SPIKE_RATE_AXIS, 
                                          multialignment='center')

        for i, trace_axes in enumerate(plot_panel.axes['trace']):
            if i+1 < num_traces:
                trace_axes.set_xticklabels([''],visible=False)
            trace_axes.set_ylabel('%s #%d' % (pt.TRACE, (i+1)))
        plot_panel.axes['trace'][-1].set_xlabel(pt.PLOT_TIME)

    def _pre_run(self, trial_id):
        pc = config['gui']['plotting']
        plot_panel = self._plot_panels[trial_id]
        trial = self._trials[trial_id]
        traces = trial.get_stage_data('detection_filter').results['traces']

        # clear and plot the traces
        num_traces = len(trial.raw_traces)
        for i, trace_axes in enumerate(plot_panel.axes['trace']):
            clear_tick_labels = False
            if i+1 < num_traces:
                clear_tick_labels = 'x_only'
            utils.clear_axes(trace_axes, clear_tick_labels=clear_tick_labels)
            trace_axes.plot(trial.times, traces[i],
                            color=self.line_color, 
                            linewidth=self.line_width, 
                            label=pt.FILTERED_TRACE_GRAPH_LABEL)
            trace_axes.set_xlim(trial.times[0], trial.times[-1])
            std = numpy.std(traces[i])

            for factor, linestyle in [(2,'solid'),(4,'dashed')]:
                trace_axes.axhline(std*factor, 
                                   color=pc['std_trace_color'], 
                                   linewidth=pc['std_trace_linewidth'], 
                                   label=r'$%d\sigma$' % factor,
                                   linestyle=linestyle)
                trace_axes.axhline(-std*factor, 
                                   color=pc['std_trace_color'], 
                                   linewidth=pc['std_trace_linewidth'], 
                                   linestyle=linestyle)
        axes = plot_panel.axes['trace'][0]
        try:
            axes.legend(loc='upper right', ncol=3, shadow=True, 
                        bbox_to_anchor=[1.03,1.1])
        except: #old versions of matplotlib don't have bbox_to_anchor
            axes.legend(loc='upper right', ncol=3)

    def _post_run(self, trial_id):
        pc = config['gui']['plotting']
        plot_panel = self._plot_panels[trial_id]
        rate_axes = plot_panel.axes['rate']

        utils.clear_axes(rate_axes)

        trial = self._trials[trial_id]
        spikes = trial.detection.results
        times = trial.times

        # plot the estimated firing rate
        bins = 70
        weight = (1000.0*bins)/times[-1]
        weights = numpy.array( [weight for s in spikes] )
        try:
            rate_axes.hist(spikes, range=(times[0], times[-1]), 
                                   bins=bins,
                                   weights=weights,
                                   ec='k',
                                   fc=self.line_color)
        except AttributeError: # catching old versions of matplotlib error.
            rate_axes.hist(spikes, range=(times[0], times[-1]), 
                                   bins=bins,
                                   ec='k',
                                   fc=self.line_color)
            rate_axes.set_ylabel('Spikes per bin')

        # print how many spikes were found.
        rate_axes.text(0.015, 0.925, pt.SPIKES_FOUND % len(spikes), 
                       verticalalignment='center',
                       horizontalalignment='left',
                       transform=rate_axes.transAxes)

        color=pc['detection']['raster_color']
        marker_size=pc['detection']['raster_height']
        markeredgewidth=pc['detection']['raster_width']
        # plot raster on rate plot
        raster_pos=pc['detection']['raster_pos_rate']
        utils.plot_raster_to_axes(spikes, rate_axes,
                                  bounds=(times[0], times[-1]),
                                  raster_pos=raster_pos,
                                  marker_size=marker_size,
                                  markeredgewidth=markeredgewidth,
                                  color=color)

        # clear old rasters, then plot rasters on traces
        raster_pos=pc['detection']['raster_pos_traces']
        for trace_axes in plot_panel.axes['trace']:
            if len(trace_axes.lines) == 6:
                trace_axes.lines[-1].remove()
            utils.plot_raster_to_axes(spikes, trace_axes,
                                      bounds=(times[0], times[-1]),
                                      raster_pos=raster_pos,
                                      marker_size=marker_size,
                                      markeredgewidth=markeredgewidth,
                                      color=color)
        
    def _plot_spikes(self, trial, figure, trial_id):
        pc = config['gui']['plotting']
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
                        color=pc['detection']['filtered_trace_color'], 
                        linewidth=pc['detection']['filtered_trace_linewidth'])

        raster_height_factor = 2.0
        raster_pos = pc['detection']['raster_pos_rate']
        if raster_pos == 'top':    spike_y = max(spike_axes.get_ylim())
        if raster_pos == 'botom':  spike_y = min(spike_axes.get_ylim())
        if raster_pos == 'center': 
            spike_y = 0.0
            raster_height_factor = 1.0
            
        spike_xs = accepted_spike_list
        spike_ys = [spike_y for spike_index in accepted_spike_list]
        spike_axes.plot(spike_xs, spike_ys, 
                        color=pc['detection']['raster_color'], 
                        linewidth=0, 
                        marker='|',
                        markersize=pc['detection']['raster_height']*
                          raster_height_factor,
                        markeredgewidth=pc['detection']['raster_width'])

        spike_axes.set_xlim(0.0, trial.times[-1])



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
    
