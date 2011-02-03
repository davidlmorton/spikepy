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
from spikepy.plotting import signal_utils 
from spikepy.common import program_text as pt
from spikepy.common.config_manager import config_manager as config

class FilterPlotPanel(SpikepyPlotPanel):
    def __init__(self, parent, name):
        SpikepyPlotPanel.__init__(self, parent, name)

        pc = config['gui']['plotting']
        if name == 'detection_filter':
            self.line_color = config.detection_color
            self.line_width = pc['detection']['filtered_trace_linewidth']
        if name == 'extraction_filter':
            self.line_color = config.extraction_color
            self.line_width = pc['extraction']['filtered_trace_linewidth']

    def _basic_setup(self, trial_id):
        plot_panel = self._plot_panels[trial_id]
        plot_panel.clear()

        trial = self._trials[trial_id]
        # set the size of the plot properly.
        num_traces = len(trial.raw_traces)
        num_rows = 1 + num_traces
        self._resize_canvas(num_rows, trial_id)
        
        # set up psd axes and trace axes
        figure = plot_panel.figure
        plot_panel.axes['psd'] = psd_axes = figure.add_subplot(num_rows, 1, 1)
        utils.set_axes_ticker(psd_axes, axis='yaxis')
        plot_panel.axes['trace'] = []
        for i in xrange(len(trial.raw_traces)):
            if i == 0:
                trace_axes = figure.add_subplot(num_rows, 1, i+2)
            else:
                trace_axes = figure.add_subplot(num_rows, 1, i+2,
                                                sharex=trace_axes)
                
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
            
    def _pre_run(self, trial_id):
        pc = config['gui']['plotting']
        plot_panel = self._plot_panels[trial_id]
        trial = self._trials[trial_id]

        # calculate psd to be plotted.
        Pxx, freqs = signal_utils.psd(trial.raw_traces.flatten(),
                                      trial.sampling_freq,
                                      pc['filtering']['psd_freq_resolution'])
        plotted_Pxx = 10*numpy.log10(Pxx)
        
        # clear and plot the psd
        psd_axes = plot_panel.axes['psd']
        utils.clear_axes(psd_axes)
        psd_axes.plot(freqs, plotted_Pxx, 
                      label=pt.RAW,
                      linewidth=pc['std_trace_linewidth'], 
                      color='k')
        utils.set_axes_ticker(psd_axes, axis='yaxis')

        # clear and plot the traces
        num_traces = len(trial.raw_traces)
        for i, trace_axes in enumerate(plot_panel.axes['trace']):
            clear_tick_labels = False
            utils.clear_axes(trace_axes)
            trace_axes.plot(trial.times, trial.raw_traces[i],
                            color='k', 
                            linewidth=pc['std_trace_linewidth'], 
                            label=pt.RAW)
            trace_axes.set_xlim(trial.times[0], trial.times[-1])
            utils.set_axes_ticker(trace_axes, axis='yaxis')

    def _post_run(self, trial_id):
        pc = config['gui']['plotting']
        plot_panel = self._plot_panels[trial_id]
        trial = self._trials[trial_id]

        # calculate psd to be plotted.
        filtered_traces = trial.get_stage_data(self.name).results['traces']
        Pxx, freqs = signal_utils.psd(filtered_traces.flatten(),
                                      trial.sampling_freq,
                                      pc['filtering']['psd_freq_resolution'])
        plotted_Pxx = 10*numpy.log10(Pxx)

        # clear old filtered psd (if exists) and plot new
        psd_axes = plot_panel.axes['psd']
        num_lines = len(psd_axes.get_lines())
        if num_lines == 2:
            psd_axes.lines[-1].remove()
        psd_axes.plot(freqs, plotted_Pxx, 
                      label=pt.FILTERED_TRACE_GRAPH_LABEL, 
                      linewidth=self.line_width, 
                      color=self.line_color)
        utils.set_axes_ticker(psd_axes, axis='yaxis')

        # clear old filtered traces (if they exist) and plot new
        for i, trace_axes in enumerate(plot_panel.axes['trace']):
            num_lines = len(trace_axes.get_lines())
            if num_lines == 2:
                trace_axes.lines[-1].remove()
            trace_axes.plot(trial.times, filtered_traces[i],
                            color=self.line_color, 
                            linewidth=self.line_width, 
                            label=pt.FILTERED_TRACE_GRAPH_LABEL)
            trace_axes.set_xlim(trial.times[0], trial.times[-1])
            utils.set_axes_ticker(trace_axes, axis='yaxis')
            

        top_trace_axes = plot_panel.axes['trace'][0]
        canvas_size = plot_panel.GetMinSize()
        legend_offset = pc['spacing']['legend_offset']
        utils.add_shadow_legend(legend_offset, legend_offset, top_trace_axes,
                                canvas_size)

