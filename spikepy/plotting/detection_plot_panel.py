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
        self.line_color = config.detection_color
        self.line_width = pc['detection']['filtered_trace_linewidth']

        
    def _basic_setup(self, trial_id):
        plot_panel = self._plot_panels[trial_id]
        plot_panel.clear()

        trial = self._trials[trial_id]
        # set the size of the plot properly
        num_traces = len(trial.raw_traces)
        num_trows = 1 + num_traces
        num_srows = num_trows * 2
        figheight = self._figsize[1] * num_trows
        figwidth  = self._figsize[0]
        plot_panel.set_minsize(figwidth, figheight)
        self._trial_renamed(trial_id=trial_id)

        # set up the spike windows and isi axes
        figure = plot_panel.figure
        plot_panel.axes['spikes'] = sa = figure.add_subplot(num_srows, 2, 1)
        utils.set_axes_ticker(sa, axis='yaxis')
        plot_panel.axes['isi'] = ia = figure.add_subplot(num_srows, 2, 2)

        # set up firing_rate and trace axes
        plot_panel.axes['rate'] = ra = figure.add_subplot(num_srows, 1, 2)
        plot_panel.axes['trace'] = []
        for i in xrange(len(trial.raw_traces)):
            trace_axes = figure.add_subplot(num_trows, 1, i+2, 
                                            sharex=plot_panel.axes['rate'])
            utils.set_axes_ticker(trace_axes, axis='yaxis')
            plot_panel.axes['trace'].append(trace_axes)

        canvas_size = plot_panel.GetMinSize()
        # adjust subplots to spikepy uniform standard
        config.default_adjust_subplots(figure, canvas_size)

        # tweek the spike windows and isi axes
        bottom = config['gui']['plotting']['spacing']['axes_bottom']
        left   = config['gui']['plotting']['spacing']['axes_left']
        top = -config['gui']['plotting']['spacing']['title_vspace']
        utils.adjust_axes_edges(sa, canvas_size, top=top)
        utils.adjust_axes_edges(ia, canvas_size, left=left, top=top)

        # add the isi sub-subplot
        isa = figure.add_axes(ia.get_position(), 
                              axisbg=(1.0, 1.0, 1.0, 0.0))
        plot_panel.axes['isi_sub'] = isa

        # tweek the isi sub-subplot
        isi_inset = config['gui']['plotting']['spacing']['isi_inset']
        total_width = isa.get_position().width
        total_height = isa.get_position().height
        utils.adjust_axes_edges(isa, canvas_size, 
                left=-0.35*total_width*canvas_size[0],
                bottom=-0.35*total_height*canvas_size[1],
                right=isi_inset, 
                top=isi_inset)

        # tweek firing_rate axes and trace axes
        nl_bottom = config['gui']['plotting']['spacing']['no_label_axes_bottom']
        utils.adjust_axes_edges(ra, canvas_size,
                                top=bottom, bottom=2*nl_bottom)

        for trace_axes in plot_panel.axes['trace'][:-1]:
            utils.adjust_axes_edges(trace_axes, canvas_size, bottom=nl_bottom)

        # label axes
        sa.set_xlabel(pt.PLOT_TIME)
        sa.set_ylabel(pt.SPIKES_GRAPH_LABEL)
        ia.set_xlabel(pt.ISI)
        ia.set_ylabel(pt.COUNT_PER_BIN)
        ra.set_xticklabels([''],visible=False)
        ra.set_ylabel(pt.SPIKE_RATE_AXIS, multialignment='center')

        for i, trace_axes in enumerate(plot_panel.axes['trace']):
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
            utils.clear_axes(trace_axes)
            trace_axes.plot(trial.times, traces[i],
                            color=self.line_color, 
                            linewidth=self.line_width, 
                            label=pt.FILTERED_TRACE_GRAPH_LABEL)
            std = numpy.std(traces[i])

            for factor, linestyle in [(2,'solid'),(4,'dashed')]:
                trace_axes.axhline(std*factor, 
                                   color='k', 
                                   linewidth=pc['std_trace_linewidth'], 
                                   label=r'$%d\sigma$' % factor,
                                   linestyle=linestyle)
                trace_axes.axhline(-std*factor, 
                                   color='k', 
                                   linewidth=pc['std_trace_linewidth'], 
                                   linestyle=linestyle)
            trace_axes.set_xlim(trial.times[0], trial.times[-1])
            utils.set_axes_ticker(trace_axes, axis='yaxis') 
        top_trace_axes = plot_panel.axes['trace'][0]
        canvas_size = plot_panel.GetMinSize()
        legend_offset = pc['spacing']['legend_offset']
        utils.add_shadow_legend(legend_offset, legend_offset, top_trace_axes,
                                canvas_size)

    def _post_run(self, trial_id):
        pc = config['gui']['plotting']
        plot_panel = self._plot_panels[trial_id]
        sa = plot_panel.axes['spikes']
        ia = plot_panel.axes['isi']
        isa = plot_panel.axes['isi_sub']
        rate_axes = plot_panel.axes['rate']

        utils.clear_axes(rate_axes)
        utils.clear_axes(sa)
        utils.clear_axes(ia)
        utils.clear_axes(isa)

        trial = self._trials[trial_id]
        spikes = trial.detection.results['spike_times']
        times = trial.times
        bounds = (times[0], times[-1])

        # plot spike windows
        spike_window_ys = trial.detection.results['spike_window_ys']
        spike_window_xs = trial.detection.results['spike_window_xs']

        # grey patch behind multi-trode concatinated spike windows
        spike_width = (spike_window_xs[-1]-spike_window_xs[0])/\
                      len(trial.raw_traces)
        for i in range(len(trial.raw_traces)):
            if i%2:
                sa.axvspan(spike_width*i, spike_width*i+spike_width, 
                           ec='k', fc='k', alpha=0.065)

        for window in spike_window_ys:
            sa.plot(spike_window_xs, window, color=self.line_color,
                                             linewidth=0.5,
                                             alpha=0.3)
        utils.set_axes_ticker(sa, axis='yaxis')
        sa.set_xlim(spike_window_xs[0], spike_window_xs[-1])
        sa.set_ylim(numpy.min(spike_window_ys)*1.1, 
                    numpy.max(spike_window_ys)*1.1)

        # plot the isi and isi_sub
        isi = spikes[1:] - spikes[:-1]

        ia.hist(isi, bins=70, 
                  range=(0.0, pc['summary']['upper_isi_bound2']),
                  fc='k', ec='w')
        utils.format_y_axis_hist(ia, minimum_max=20)
        ia.set_xlim(-5.0)

        isa_upper_range =  pc['summary']['upper_isi_bound1']
        isa.hist(isi, bins=int(isa_upper_range),
                  range=(0.0, isa_upper_range),
                  fc='k', ec='w')
        utils.format_y_axis_hist(isa, minimum_max=20, fontsize=9)
        isa.set_xlim(-0.15)

        # plot the estimated firing rate
        bins = 70
        weight = (1000.0*bins)/times[-1]
        weights = numpy.array( [weight for s in spikes] )
        try:
            rate_axes.hist(spikes, range=bounds,
                                   bins=bins,
                                   weights=weights,
                                   ec='w',
                                   fc=self.line_color)
        except AttributeError: # catching old versions of matplotlib error.
            rate_axes.hist(spikes, range=bounds,
                                   bins=bins,
                                   ec='w',
                                   fc=self.line_color)
            rate_axes.set_ylabel(pt.SPIKES_PER_BIN)

        utils.format_y_axis_hist(rate_axes, minimum_max=10)

        # print how many spikes were found.
        rate_axes.text(0.015, 1.025, pt.SPIKES_FOUND % len(spikes), 
                       verticalalignment='bottom',
                       horizontalalignment='left',
                       transform=rate_axes.transAxes)

        color='k'
        marker_size=pc['detection']['raster_height']
        markeredgewidth=pc['detection']['raster_width']
        # plot raster on rate plot
        raster_pos=pc['detection']['raster_pos_rate']
        utils.plot_raster_to_axes(spikes, rate_axes,
                                  bounds=bounds,
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
                                      bounds=bounds,
                                      raster_pos=raster_pos,
                                      marker_size=marker_size,
                                      markeredgewidth=markeredgewidth,
                                      color=color)
            trace_axes.set_xlim(*bounds)
            utils.set_axes_ticker(trace_axes, axis='yaxis')
        
