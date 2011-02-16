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
import math
import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy

from spikepy.plotting.spikepy_plot_panel import SpikepyPlotPanel
from spikepy.plotting import utils
from spikepy.common import program_text as pt
from spikepy.common.config_manager import config_manager as config

class SummaryPlotPanel(SpikepyPlotPanel):
    def __init__(self, parent, name):
        SpikepyPlotPanel.__init__(self, parent, name)

    def _basic_setup(self, trial_id):
        plot_panel = self._plot_panels[trial_id]
        plot_panel.clear()

    def _pre_run(self, trial_id):
        pass

    def _post_run(self, trial_id):
        trial = self._trials[trial_id]
        plot_panel = self._plot_panels[trial_id]
        plot_panel.clear()
        figure = plot_panel.figure
        num_clusters = trial.get_num_clusters()

        self._setup_axes(trial, figure, trial_id, num_clusters)
        
        self._plot_rasters(trial, figure, trial_id, num_clusters)
        self._plot_averages_and_stds(trial, figure, trial_id)
        self._pot_isis(trial_id)


    def _setup_axes(self, trial, figure, trial_id, num_clusters):
        pc = config['gui']['plotting']['summary']
        plot_panel = self._plot_panels[trial_id]

        # make the figure canvas the correct size.
        num_srows = 3 + num_clusters
        num_trows = int(math.ceil(num_srows/2.0))
        num_srows = num_trows*2
        self._resize_canvas(num_trows, trial_id)

        canvas_size = plot_panel.GetMinSize()

        # --- RASTER AND TRACE AXES ---
        trace_axes = figure.add_subplot(num_trows, 1, 1)
        trace_axes.set_xticklabels([''], visible=False)
        trace_yaxis = trace_axes.get_yaxis()
        trace_yaxis.set_ticks_position('right')

        plot_width = (canvas_size[0] - pc['raster_left'] -
                                       pc['raster_right'])
        text_loc_percent = 1.0 + pc['right_ylabel']/plot_width
        trace_axes.text(text_loc_percent, 0.5, pt.TRACE_NUMBER,
                        verticalalignment='center',
                        horizontalalignment='left',
                        rotation='vertical',
                        transform=trace_axes.transAxes,
                        clip_on=False)
        plot_panel.axes['trace'] = trace_axes

        # --- AVERAGE AND STD AXES ---
        average_axes = figure.add_subplot(num_srows, 2, 5)
        average_axes.set_ylabel(pt.AVERAGE_SPIKE_SHAPES,
                                multialignment='center')
        average_axes.set_xlabel(pt.PLOT_TIME)
        plot_panel.axes['average'] = average_axes
        
        std_axes = figure.add_subplot(num_srows, 2, 6, sharex=average_axes)
        std_axes.set_ylabel(pt.SPIKE_STDS, multialignment='center')
        std_axes.set_xlabel(pt.PLOT_TIME)
        plot_panel.axes['std'] = std_axes

        # cluster and isi axes
        cluster_axes = []
        isi_axes = []
        isi_sub_axes = []
        for i in xrange(num_clusters):
            if i == 0:
                ca = figure.add_subplot(num_srows, 2, 6+2*i+1)
                ia = figure.add_subplot(num_srows, 2, 6+2*i+2)
            else:
                ca = figure.add_subplot(num_srows, 2, 6+2*i+1, sharex=ca)
                ia = figure.add_subplot(num_srows, 2, 6+2*i+2, sharex=ia)
                
            ia.set_ylabel(pt.COUNT_PER_BIN)

            cluster_axes.append(ca)
            isi_axes.append(ia)


        plot_panel.axes['cluster'] = cluster_axes
        plot_panel.axes['isi'] = isi_axes

        config.default_adjust_subplots(figure, canvas_size)

        for ia in isi_axes:
            isa = figure.add_axes(ia.get_position(), 
                                  axisbg=(1.0, 1.0, 1.0, 0.0))
            isi_sub_axes.append(isa)
        plot_panel.axes['isi_sub'] = isi_sub_axes

        # tweek trace/raster edges
        bottom = config['gui']['plotting']['spacing']['axes_bottom']
        right  = pc['raster_right']
        left   = pc['raster_left']
        top = -config['gui']['plotting']['spacing']['title_vspace']
        utils.adjust_axes_edges(trace_axes, canvas_size_in_pixels=canvas_size, 
                                top=top,
                                bottom=bottom,
                                right=right, 
                                left=left)

        # tweek edges
        left   = config['gui']['plotting']['spacing']['axes_left']
        utils.adjust_axes_edges(average_axes, 
                                canvas_size_in_pixels=canvas_size, 
                                bottom=bottom)
        utils.adjust_axes_edges(std_axes, canvas_size_in_pixels=canvas_size, 
                                left=left, bottom=bottom)

        nl_bottom = config['gui']['plotting']['spacing']['no_label_axes_bottom']
        for ca, ia, isa in zip(cluster_axes, isi_axes, isi_sub_axes):
            utils.adjust_axes_edges(ca, canvas_size, bottom=nl_bottom)
            utils.adjust_axes_edges(ia, canvas_size, left=left, 
                                                     bottom=nl_bottom)
            utils.adjust_axes_edges(isa, canvas_size, left=left, 
                                                     bottom=nl_bottom)

        isi_inset = config['gui']['plotting']['spacing']['isi_inset']
        for isa in isi_sub_axes:
            total_width = isa.get_position().width
            total_height = isa.get_position().height
            utils.adjust_axes_edges(isa, canvas_size, 
                    left=-0.35*total_width*canvas_size[0],
                    bottom=-0.35*total_height*canvas_size[1],
                    right=isi_inset, 
                    top=isi_inset)

        # clone trace_axes: raster_axes will be on top of trace axes.
        raster_axes = figure.add_axes(trace_axes.get_position(), 
                                      sharex=trace_axes)
        utils.make_a_raster_axes(raster_axes)
        raster_axes.set_frame_on(False)
        raster_yaxis = raster_axes.get_yaxis()
        raster_yaxis.set_ticks_position('left')
        raster_axes.set_xlabel(pt.PLOT_TIME)
        raster_axes.set_ylabel(pt.CLUSTER_NUMBER)
        plot_panel.axes['raster'] = raster_axes

    def _pot_isis(self, trial_id):
        pc = config['gui']['plotting']
        isi_axes = self._plot_panels[trial_id].axes['isi']
        isi_sub_axes = self._plot_panels[trial_id].axes['isi_sub']

        trial = self._trials[trial_id]
        times = trial.clustering.results['clustered_spike_times']

        cluster_numbers = sorted(times.keys())
        for cluster_number, axes, sub_axes in zip(cluster_numbers, 
                                                  isi_axes, 
                                                  isi_sub_axes):
            color = config.get_color_from_cycle(cluster_number)

            nt = numpy.array(sorted(times[cluster_number]))
            isi = nt[1:]-nt[:-1]

            axes.hist(isi, bins=70, 
                      range=(0.0, pc['summary']['upper_isi_bound2']),
                      fc=color, ec='w')
            utils.format_y_axis_hist(axes, minimum_max=20)
            axes.set_xlim(-5.0)

            isa_upper_range =  pc['summary']['upper_isi_bound1']
            sub_axes.hist(isi, bins=int(isa_upper_range), 
                      range=(0.0, isa_upper_range),
                      fc=color, ec='w')
            utils.format_y_axis_hist(sub_axes, minimum_max=20, fontsize=9)
            sub_axes.set_xlim(-0.15)

        axes.set_xlabel(pt.ISI)
        
    def _plot_rasters(self, trial, figure, trial_id, num_clusters):
        pc = config['gui']['plotting']
        trace_axes = self._plot_panels[trial_id].axes['trace']
        raster_axes = self._plot_panels[trial_id].axes['raster']

        # plot traces
        times = trial.times
        traces = trial.detection_filter.results['traces']
        
        trace_ticks = []
        trace_offsets = [-i*2*numpy.max(numpy.abs(traces)) 
                         for i in xrange(len(traces))]
        for trace, trace_offset in zip(traces, trace_offsets):
            utils.make_a_trace_axes(trace_axes)
            trace_axes.plot(times, trace+trace_offset, 
                            color=config.detection_color, 
                            label=pt.DETECTION_TRACE_GRAPH_LABEL,
                            alpha=pc['summary']['std_alpha'])
            trace_ticks.append(numpy.average(trace+trace_offset))
        trace_axes.set_yticks(trace_ticks)
        trace_axes.set_yticklabels(['%d' % i for i in xrange(len(traces))])
        # set the ylimits for the trace_axes and raster_axes
        utils.trace_autoset_ylim(trace_axes)
        final_ylim = trace_axes.get_ylim()
        raster_axes.set_ylim(*final_ylim, force_set=True)

        # plot rasters
        spike_times = trial.clustering.results['clustered_spike_times']
        keys = sorted(spike_times.keys())
        spike_y_list = numpy.linspace(max(final_ylim), min(final_ylim), 
                                      num_clusters+2)[1:-1]
        for key, spike_y in zip(keys, spike_y_list):
            spike_xs = spike_times[key]
            spike_ys = [spike_y for i in xrange(len(spike_xs))]
            raster_axes.plot(spike_xs, spike_ys, linewidth=0, marker='|',
                             markersize=pc['detection']['raster_height'],
                             markeredgewidth=pc['detection']['raster_width'],
                             color=config.get_color_from_cycle(key))
        # label raster_axes y ticks
        raster_axes.set_yticks(spike_y_list)
        raster_axes.set_yticklabels(['%d' % key for key in keys])

        # set xlim for trace and raster axes
        for axes in [trace_axes, raster_axes]:
            axes.set_xlim(times[0], times[-1])
    

    def _plot_averages_and_stds(self, trial, figure, trial_id):
        pc = config['gui']['plotting']
        windows = trial.get_clustered_spike_windows()
        averages_and_stds = self._get_averages_and_stds(windows)
        average_axes = self._plot_panels[trial_id].axes['average']
        std_axes = self._plot_panels[trial_id].axes['std']

        times = trial.detection.results['spike_window_xs']
        spike_width = (times[-1]-times[0])/len(trial.raw_traces)
        
        # grey patch behind multi-trode concatinated spike windows
        for i in range(len(trial.raw_traces)):
            if i%2:
                average_axes.axvspan(spike_width*i, 
                                     spike_width*i+spike_width, 
                                     ec='k', fc='k', alpha=0.065)
        for i in range(len(trial.raw_traces)):
            if i%2:
                std_axes.axvspan(spike_width*i, 
                                 spike_width*i+spike_width, 
                                 ec='k', fc='k', alpha=0.065)

        avg_min = None
        avg_max = None
        std_min = None
        std_max = None
        for cluster_num, (average, stds) in averages_and_stds.items():
            if average is None:
                continue # don't try to plot empty clusters
                    
            average_axes.fill_between(times, average+stds, average-stds,
                              color=config.get_color_from_cycle(cluster_num),
                              alpha=pc['summary']['std_alpha'])
            line = average_axes.plot(times, average,
                              color=config.get_color_from_cycle(cluster_num),
                              label=pt.SPECIFIC_CLUSTER_NUMBER % cluster_num)[0]
            average_axes.set_xlim(times[0], times[-1])
            # figure out min and max for ylims later
            this_avg_min = numpy.min(average-stds)
            if avg_min is None or this_avg_min < avg_min:
                avg_min = this_avg_min
            this_avg_max = numpy.max(average+stds)
            if avg_max is None or this_avg_max > avg_max:
                avg_max = this_avg_max


            this_std_min = numpy.min(stds)


            std_axes.plot(times, stds, 
                          color=config.get_color_from_cycle(cluster_num),
                          label=pt.SPECIFIC_CLUSTER_NUMBER % cluster_num)
            std_axes.set_xlim(times[0], times[-1])
            this_std_min = numpy.min(stds)
            if std_min is None or this_std_min < std_min:
                std_min = this_std_min
            this_std_max = numpy.max(stds)
            if std_max is None or this_std_max > std_max:
                std_max = this_std_max
        average_axes.set_ylim(avg_min-abs(avg_min)*0.1,
                              avg_max+abs(avg_max)*0.1)
        std_axes.set_ylim(std_min-abs(std_min)*0.1,
                          std_max+abs(std_max)*0.1)
        utils.set_axes_ticker(average_axes, axis='yaxis')
        utils.set_axes_ticker(std_axes, axis='yaxis')

        # plot clustered spike windows
        cluster_axes = self._plot_panels[trial_id].axes['cluster']
        cluster_nums = sorted(windows.keys())
        for cluster_num, axes in zip(cluster_nums, cluster_axes):
            color = config.get_color_from_cycle(cluster_num)
            num_windows = len(windows[cluster_num])
            axes.set_ylabel(pt.SPECIFIC_CLUSTER_NUMBER % cluster_num)
            if num_windows < 1:
                axes.text(0.5, 0.5, pt.CLUSTER_EMPTY,
                          fontsize=16,
                          verticalalignment='center',
                          horizontalalignment='center',
                          transform=axes.transAxes)
                axes.set_yticklabels([''], visible=False)
                continue # don't bother trying to plot empty clusters.

            # grey patch behind multi-trode concatinated spike windows
            spike_width = (times[-1]-times[0])/len(trial.raw_traces)
            for i in range(len(trial.raw_traces)):
                if i%2:
                    axes.axvspan(spike_width*i, spike_width*i+spike_width, 
                               ec='k', fc='k', alpha=0.065)

            for window in windows[cluster_num]:
                axes.plot(times, window, 
                          linewidth=pc['std_trace_linewidth'],
                          color=color, 
                          alpha=0.2) 
            avg_window = numpy.average(windows[cluster_num], axis=0)
            axes.plot(times, avg_window, 
                      linewidth=pc['bold_linewidth'],
                      color=color, 
                      alpha=1.0, 
                      label=pt.CLUSTER_SIZE % num_windows)
            axes.set_xlim(times[0], times[-1])
            axes.set_ylim(numpy.min(windows[cluster_num])*1.1, 
                          numpy.max(windows[cluster_num])*1.1)
            canvas_size = self._plot_panels[trial_id].GetMinSize()
            legend_offset = pc['spacing']['legend_offset']
            utils.add_shadow_legend(legend_offset, legend_offset, axes,
                                    canvas_size)
            utils.set_axes_ticker(axes, axis='yaxis')

        axes.set_xlabel(pt.PLOT_TIME)
    

    def _get_averages_and_stds(self, windows):
        return_dict = {}
        for key in windows.keys():
            if len(windows[key]) == 0:
                return_dict[key] = (None, None)
            else:
                stds     = numpy.std(windows[key],     axis=0)
                average  = numpy.average(windows[key], axis=0)
                return_dict[key] = (average, stds)
        return return_dict

