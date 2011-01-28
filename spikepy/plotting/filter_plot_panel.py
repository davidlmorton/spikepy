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
            self.line_color = pc['detection']['filtered_trace_color']
            self.line_width = pc['detection']['filtered_trace_linewidth']
        if name == 'extraction_filter':
            self.line_color = pc['extraction']['filtered_trace_color']
            self.line_width = pc['extraction']['filtered_trace_linewidth']

    def _basic_setup(self, trial_id):
        plot_panel = self._plot_panels[trial_id]
        plot_panel.clear()

        trial = self._trials[trial_id]
        # set the size of the plot properly.
        num_traces = len(trial.raw_traces)
        num_rows = 1 + num_traces
        figheight = self._figsize[1] * num_rows
        figwidth  = self._figsize[0]
        plot_panel.set_minsize(figwidth, figheight)
        self._trial_renamed(trial_id=trial_id)
        
        # set up psd axes and trace axes
        figure = plot_panel.figure
        plot_panel.axes['psd'] = figure.add_subplot(num_rows, 1, 1)
        plot_panel.axes['trace'] = []
        for i in xrange(len(trial.raw_traces)):
            trace_axes = figure.add_subplot(num_rows, 1, i+2)
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
            if i+1 < num_traces:
                trace_axes.set_xticklabels([''],visible=False)
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
                      color=pc['std_trace_color'])

        # clear and plot the traces
        num_traces = len(trial.raw_traces)
        for i, trace_axes in enumerate(plot_panel.axes['trace']):
            clear_tick_labels = False
            if i+1 < num_traces:
                clear_tick_labels = 'x_only'
            utils.clear_axes(trace_axes, clear_tick_labels=clear_tick_labels)
            trace_axes.plot(trial.times, trial.raw_traces[i],
                            color=pc['std_trace_color'], 
                            linewidth=pc['std_trace_linewidth'], 
                            label=pt.RAW)
            trace_axes.set_xlim(trial.times[0], trial.times[-1])

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

        # clear old filtered traces (if they exist) and plot new
        for i, trace_axes in enumerate(plot_panel.axes['trace']):
            num_lines = len(trace_axes.get_lines())
            if num_lines == 2:
                trace_axes.lines[-1].remove()
            trace_axes.plot(trial.times, filtered_traces[i],
                            color=self.line_color, 
                            linewidth=self.line_width, 
                            label=pt.FILTERED_TRACE_GRAPH_LABEL)

        top_trace_axes = plot_panel.axes['trace'][0]
        try:
            top_trace_axes.legend(loc='upper right', ncol=2, shadow=True, 
                                  bbox_to_anchor=[1.03,1.1])
        except: #old versions of matplotlib don't have bbox_to_anchor
            psd_axes.legend(loc='lower right')

