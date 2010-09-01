from collections import defaultdict
import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy
import scipy

from .multi_plot_panel import MultiPlotPanel
from .look_and_feel_settings import lfs
from . import program_text as pt
from .utils import adjust_axes_edges

class ClusteringPlotPanel(MultiPlotPanel):
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
        pub.subscribe(self._trial_altered, topic='STAGE_REINITIALIZED')
        pub.subscribe(self._trial_altered, topic='TRIAL_CLUSTERED')
        pub.subscribe(self._trial_renamed,  topic='TRIAL_RENAMED')

        self._trials = {}
        self._fig_cleared = True
        self._trace_axes = defaultdict(lambda :None)

    def _remove_trial(self, message=None):
        trial_id = message.data
        del self._trials[trial_id]

    def _trial_added(self, message=None, trial=None):
        if message is not None:
            trial = message.data

        trial_id = trial.trial_id
        self._trials[trial_id] = trial
        self.add_plot(trial_id, figsize=self._figsize, 
                                facecolor=self._facecolor,
                                edgecolor=self._facecolor,
                                dpi=self._dpi)
        self._replot_panels.add(trial_id)

    def _trial_renamed(self, message=None):
        trial = message.data
        trial_id = trial.trial_id
        if self._trace_axes[trial_id] is not None:
            new_name = trial.display_name
            trace_axes = self._trace_axes[trial_id]
            trace_axes.set_title(pt.TRIAL_NAME+new_name)
            self.draw_canvas(trial_id)

    def _trial_altered(self, message=None):
        trial, stage_name = message.data
        if stage_name != self.name:
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
        if trial.clustering.results is not None:
            num_clusters = len(trial.clustering.results.keys())
            num_cluster_combinations = nchoosek(num_clusters, 2)
            old_minsize = self._plot_panels[trial_id].GetMinSize()
            figwidth = self._figsize[0]
            figheight = self._figsize[1]*(num_cluster_combinations+2)
            figure = self._plot_panels[trial_id].figure

            if old_minsize[1] != figheight or self._fig_cleared:
                self._fig_cleared = False
                self._plot_panels[trial_id].set_minsize(figwidth, 
                                                        figheight)
                figure.clear()
                canvas_size = self._plot_panels[trial_id].GetMinSize()
                lfs.default_adjust_subplots(figure, canvas_size)
                self._setup_axes(trial, figure, trial_id, canvas_size, 
                                 num_cluster_combinations, num_clusters)
            
            self._plot_rasters(trial, figure, trial_id, 
                               num_cluster_combinations, num_clusters)
            self._plot_clusters(trial, figure, trial_id, 
                                num_cluster_combinations)
            self._plot_distances(trial, figure, trial_id, 
                                 num_cluster_combinations)

            self.draw_canvas(trial_id)
        else:
            if not self._fig_cleared:
                figure = self._plot_panels[trial_id].figure
                figure.clear()
                self._fig_cleared = True
                self._trace_axes[trial_id] = None
                self.draw_canvas(trial_id)

    def _setup_axes(self, trial, figure, trial_id, canvas_size,  
                    ncc, num_clusters):
        # --- RASTER AND TRACE AXES ---
        raster_axes = figure.add_subplot(ncc+2, 1, 1)
        raster_yaxis = raster_axes.get_yaxis()
        raster_yaxis.set_ticks_position('left')
        raster_axes.set_xlabel(pt.PLOT_TIME)
        raster_axes.set_ylabel(pt.CLUSTER_NUMBER)
        # trace_axes will be on top of raster_axes
        trace_axes = figure.add_axes(raster_axes.get_position(), 
                                     axisbg=(1.0, 1.0, 1.0, 0.0),
                                     sharex=raster_axes)
        trial = self._trials[trial_id]
        new_name = trial.display_name
        trace_axes.set_title(pt.TRIAL_NAME+new_name)
        self._trace_axes[trial_id] = trace_axes
        trace_yaxis = trace_axes.get_yaxis()
        trace_yaxis.set_ticks_position('right')
        plot_width = (canvas_size[0] - lfs.CLUSTER_RASTER_LEFT -
                                       lfs.CLUSTER_RASTER_RIGHT)
        text_loc_percent = 1.0 + lfs.CLUSTER_RIGHT_YLABEL/plot_width
        trace_axes.text(text_loc_percent, 0.5, pt.TRACE_NUMBER,
                        verticalalignment='center',
                        horizontalalignment='left',
                        rotation='vertical',
                        transform=trace_axes.transAxes,
                        clip_on=False)

        bottom = lfs.AXES_BOTTOM 
        right  = lfs.CLUSTER_RASTER_RIGHT
        left   = lfs.CLUSTER_RASTER_LEFT 
        for axes in [trace_axes, raster_axes]:
            adjust_axes_edges(axes, canvas_size_in_pixels=canvas_size, 
                                    bottom=bottom, right=right, left=left)

        self.trace_axes  = trace_axes
        self.raster_axes = raster_axes

        # --- AVG AND STD AXES ---
        average_axes = figure.add_subplot(ncc+2, 2, 3)
        average_axes.set_ylabel(pt.AVERAGE_SPIKE_SHAPES)
        average_axes.set_xlabel(pt.PLOT_TIME)
        
        std_axes = figure.add_subplot(ncc+2, 2, 4, sharex=average_axes)
        std_axes.set_ylabel(pt.SPIKE_STDS)
        std_axes.set_xlabel(pt.PLOT_TIME)

        self.average_axes = average_axes
        self.std_axes     = std_axes

        left   = lfs.AXES_LEFT 
        adjust_axes_edges(std_axes, canvas_size_in_pixels=canvas_size, 
                                    left=left)

    def _plot_rasters(self, trial, figure, trial_id, ncc, num_clusters):
        trace_axes = self.trace_axes
        raster_axes = self.raster_axes

        times = trial.times
        traces = trial.detection_filter.results
        
        trace_ticks = []
        trace_offsets = [-i*2*numpy.max(numpy.abs(traces)) 
                         for i in xrange(len(traces))]
        for trace, trace_offset in zip(traces, trace_offsets):
            trace_axes.plot(times, trace+trace_offset, color=lfs.PLOT_COLOR_2, 
                                 label=pt.DETECTION_TRACE_GRAPH_LABEL,
                                 alpha=lfs.CLUSTER_STD_ALPHA)
            trace_ticks.append(numpy.average(trace+trace_offset))
        old_ylim = trace_axes.get_ylim()
        ysize = max(old_ylim) - min(old_ylim) 
        trace_axes.set_yticks(trace_ticks)
        trace_axes.set_yticklabels(['%d' % i for i in xrange(len(traces))])
        spike_times = trial.clustering.results
        keys = sorted(spike_times.keys())
        ylim = trace_axes.get_ylim()
        raster_axes.set_ylim(ylim)
        spike_y_list = numpy.linspace(max(ylim), min(ylim), 
                                      num_clusters+2)[1:-1]
        for key, spike_y in zip(keys, spike_y_list):
            spike_xs = spike_times[key]
            spike_ys = [spike_y for i in xrange(len(spike_xs))]
            trace_axes.plot(spike_xs, spike_ys, linewidth=0, marker='|',
                             markersize=lfs.SPIKE_RASTER_HEIGHT,
                             markeredgewidth=lfs.SPIKE_RASTER_WIDTH,
                             color=lfs.SPIKE_RASTER_COLOR)
        # label raster_axes y ticks
        raster_axes.set_yticks(spike_y_list)
        raster_axes.set_yticklabels(['%d' % key for key in keys])
    
        raster_axes.set_xlabel(pt.PLOT_TIME)

        old_ylim = trace_axes.get_ylim()
        ysize = max(old_ylim) - min(old_ylim) 
        final_ylim = (old_ylim[0]-0.20*ysize,
                      old_ylim[1]+0.20*ysize)
        for axes in [trace_axes, raster_axes]:
            axes.set_ylim(final_ylim)

        
    def _plot_clusters(self, trial, figure, trial_id, ncc):
        averages_and_stds = self._get_averages_and_stds(trial)
        
        for cluster_num, (average, stds) in averages_and_stds.items():
            times = numpy.arange(0,len(average))*(trial.dt/3.0)
            line = self.average_axes.plot(times, average,
                              label=pt.SPECIFIC_CLUSTER_NUMBER % cluster_num)[0]
            color = line.get_color()
            self.average_axes.fill_between(times, 
                                                  average+stds,
                                                  average-stds,
                                                  color=color,
                                                  alpha=lfs.CLUSTER_TRACE_ALPHA)

            self.std_axes.plot(times, stds, 
                          label=pt.SPECIFIC_CLUSTER_NUMBER % cluster_num)


    def _get_averages_and_stds(self, trial):
        times = trial.clustering.results
        feature_list  = trial.extraction.results['features']
        feature_times = trial.extraction.results['feature_times']
        features = defaultdict(list)
        for cluster_num, time_list in times.items():
            for time in time_list:
                feature_list_index = feature_times.index(time) 
                features[cluster_num].append(feature_list[feature_list_index])
        return_dict = {}
        for key in features.keys():
            features[key] = numpy.array(features[key])
            stds     = numpy.std(features[key],     axis=0)
            average  = numpy.average(features[key], axis=0)
            return_dict[key] = (average, stds)
        return return_dict

    def _plot_distances(self, trial, figure, trial_id, ncc):
        pass


def nchoosek(n, k):
    f = scipy.factorial
    return f(n)/(f(k)*f(n-k))
