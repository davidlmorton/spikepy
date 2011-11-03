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

from wx.lib.pubsub import Publisher as pub
import wx
import numpy

from spikepy.plotting.spikepy_plot_panel import SpikepyPlotPanel
from spikepy.plotting import utils
from spikepy.common import program_text as pt
from spikepy.common.config_manager import config_manager as config

class FilterPlotPanel(SpikepyPlotPanel):
    def __init__(self, parent, session, name):
        SpikepyPlotPanel.__init__(self, parent, session, name)

        pc = config['gui']['plotting']
        if name == 'detection_filter':
            self.line_color = config.detection_color
            self.line_width = pc['detection']['filtered_trace_linewidth']
            self.prefix = 'df'

        if name == 'extraction_filter':
            self.prefix = 'ef'
            self.line_color = config.extraction_color
            self.line_width = pc['extraction']['filtered_trace_linewidth']

    def _get_resources(self, trial_id):
        trial = self.get_trial(trial_id)
        info_dict = {}
        info_dict['pre_traces'] = trial.pf_traces
        info_dict['pre_sampling_freq'] = trial.pf_sampling_freq
        info_dict['pre_psd'] = trial.pf_psd
        info_dict['pre_freqs'] = trial.pf_freqs

        info_dict['filtered_traces'] = getattr(trial, '%s_traces' % self.prefix)
        info_dict['filtered_sampling_freq'] = getattr(trial, 
                '%s_sampling_freq' % self.prefix)
        info_dict['filtered_psd'] = getattr(trial, '%s_psd' % self.prefix)
        info_dict['filtered_freqs'] = getattr(trial, '%s_freqs' % self.prefix)
        return info_dict

    def _get_change_ids(self, trial_id):
        resources = self._get_resources(trial_id)
        change_ids = {}
        for name, resource in resources.items():
            change_ids[name] = resource.change_info['change_id']
        return change_ids

    def replot(self, trial_id):
        trial = self.get_trial(trial_id)
        plot_panel = self._plot_panel 
        plot_panel.clear()

        if self._should_replot(trial_id):
            self._setup_axes(trial, plot_panel)
            self._pre_run(trial, plot_panel)
            self._post_run(trial, plot_panel)

            # at end, keep track of change_ids
            self._change_ids = self._get_change_ids(trial_id)

    def _setup_axes(self, trial, plot_panel):
        # set the size of the plot properly.
        num_rows = 1 + trial.num_channels
        self._resize_canvas(num_rows)
        
        # set up psd axes and trace axes
        figure = plot_panel.figure
        plot_panel.axes['psd'] = psd_axes = figure.add_subplot(num_rows, 1, 1)
        utils.set_axes_ticker(psd_axes, axis='yaxis')
        plot_panel.axes['trace'] = []
        for i in xrange(trial.num_channels):
            if i == 0:
                trace_axes = figure.add_subplot(num_rows, 1, i+2)
            else:
                trace_axes = figure.add_subplot(num_rows, 1, i+2,
                                                sharex=trace_axes,
                                                sharey=trace_axes)
                
            utils.set_axes_ticker(trace_axes, axis='yaxis')
            plot_panel.axes['trace'].append(trace_axes)

        canvas_size = plot_panel.GetMinSize()
        # adjust subplots to spikepy uniform standard
        config.default_adjust_subplots(figure, canvas_size)

        # tweek psd axes and trace axes
        top = -config['gui']['plotting']['spacing']['title_vspace']
        bottom = config['gui']['plotting']['spacing']['axes_bottom']
        utils.adjust_axes_edges(plot_panel.axes['psd'], canvas_size,
                                bottom=bottom, top=top)

        nl_bottom = config['gui']['plotting']['spacing']['no_label_axes_bottom']
        for trace_axes in plot_panel.axes['trace'][:-1]:
            utils.adjust_axes_edges(trace_axes, canvas_size, bottom=nl_bottom)

        # label axes
        plot_panel.axes['psd'].set_ylabel(pt.PSD_Y_AXIS_LABEL, 
                                          multialignment='center')
        plot_panel.axes['psd'].set_xlabel(pt.PSD_X_AXIS_LABEL)

        for i, trace_axes in enumerate(plot_panel.axes['trace']):
            trace_axes.set_ylabel('%s #%d' % (pt.TRACE, (i+1)))
        plot_panel.axes['trace'][-1].set_xlabel(pt.PLOT_TIME)
            
    def _pre_run(self, trial, plot_panel):
        pc = config['gui']['plotting']
        resources = self._get_resources(trial.trial_id)
        Pxx = resources['pre_psd'].data
        freqs = resources['pre_freqs'].data
        plotted_Pxx = 10*numpy.log10(Pxx)
        
        # clear and plot the psd
        psd_axes = plot_panel.axes['psd']
        utils.clear_axes(psd_axes)
        psd_axes.plot(freqs, plotted_Pxx, 
                      label=pt.RAW,
                      linewidth=pc['std_trace_linewidth'], 
                      color='k')
        utils.set_axes_ticker(psd_axes, axis='yaxis')
        plot_panel.draw()

        # clear and plot the traces
        raw_traces = resources['pre_traces'].data
        sampling_freq = resources['pre_sampling_freq'].data
        times = trial.get_times(raw_traces, sampling_freq)
        
        num_traces = len(raw_traces)
        for i, trace_axes in enumerate(plot_panel.axes['trace']):
            utils.clear_axes(trace_axes)
            utils.make_a_trace_axes(trace_axes)
            trace_axes.plot(times, raw_traces[i],
                            color='k', 
                            linewidth=pc['std_trace_linewidth'], 
                            label=pt.RAW)
            trace_axes.set_xlim(times[0], times[-1])
            utils.trace_autoset_ylim(trace_axes)
            utils.set_axes_ticker(trace_axes, axis='yaxis')
            plot_panel.draw()

    def _post_run(self, trial, plot_panel):
        pc = config['gui']['plotting']

        resources = self._get_resources(trial.trial_id)
        Pxx = resources['filtered_psd'].data
        freqs = resources['filtered_freqs'].data

        # plot psd
        if Pxx is not None:
            plotted_Pxx = 10*numpy.log10(Pxx)
            psd_axes = plot_panel.axes['psd']
            psd_axes.plot(freqs, plotted_Pxx, 
                          label=pt.FILTERED_TRACE_GRAPH_LABEL, 
                          linewidth=self.line_width, 
                          color=self.line_color)
            utils.set_axes_ticker(psd_axes, axis='yaxis')
            plot_panel.draw()

        # clear and plot the traces
        filtered_traces = resources['filtered_traces'].data
        sampling_freq = resources['filtered_sampling_freq'].data

        if filtered_traces is not None:
            times = trial.get_times(filtered_traces, sampling_freq)
            
            num_traces = len(filtered_traces)
            for i, trace_axes in enumerate(plot_panel.axes['trace']):
                trace_axes.plot(times, filtered_traces[i],
                                color=self.line_color, 
                                linewidth=self.line_width, 
                                label=pt.FILTERED_TRACE_GRAPH_LABEL)
                trace_axes.set_xlim(times[0], times[-1])
                utils.trace_autoset_ylim(trace_axes)
                utils.set_axes_ticker(trace_axes, axis='yaxis')
                plot_panel.draw()
                
            top_trace_axes = plot_panel.axes['trace'][0]
            canvas_size = plot_panel.GetMinSize()
            legend_offset = pc['spacing']['legend_offset']
            utils.add_shadow_legend(legend_offset, legend_offset, 
                    top_trace_axes, canvas_size)
            plot_panel.draw()

