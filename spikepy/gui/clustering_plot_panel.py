from collections import defaultdict
import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy
import scipy

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel
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
        pub.subscribe(self._trial_altered, topic='TRIAL_EXTRACTIONED')
        pub.subscribe(self._trial_altered, topic='TRIAL_EXTRACTION_FILTERED')
        pub.subscribe(self._trial_altered, topic='TRIAL_DETECTIONED')
        pub.subscribe(self._trial_altered, topic='TRIAL_DETECTION_FILTERED')
        pub.subscribe(self._trial_altered, topic='TRIAL_CLUSTERINGED')

        self._trials = {}
        self._fig_cleared = True

    def _remove_trial(self, message=None):
        fullpath = message.data
        del self._trials[fullpath]

    def _trial_added(self, message=None, trial=None):
        if message is not None:
            trial = message.data

        fullpath = trial.fullpath
        self._trials[fullpath] = trial
        self.add_plot(fullpath, figsize=self._figsize, 
                                facecolor=self._facecolor,
                                edgecolor=self._facecolor,
                                dpi=self._dpi)
        self._replot_panels.add(fullpath)

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
        if trial.clustering.results is not None:
            num_clusters = len(trial.clustering.results.keys())
            num_cluster_combinations = nchoosek(num_clusters, 2)
            old_minsize = self._plot_panels[fullpath].GetMinSize()
            figwidth = self._figsize[0]
            figheight = self._figsize[1]*(num_cluster_combinations+2)
            figure = self._plot_panels[fullpath].figure

            if old_minsize[1] != figheight or self._fig_cleared:
                self._fig_cleared = False
                self._plot_panels[fullpath].set_minsize(figwidth, 
                                                        figheight)
                figure.clear()
                self._adjust_subplots(self._plot_panels[fullpath].GetMinSize(),
                                      figure)
                self._setup_axes(trial, figure, fullpath, 
                                 num_cluster_combinations, num_clusters)
            
            self._plot_rasters(trial, figure, fullpath, 
                               num_cluster_combinations, num_clusters)
            self._plot_clusters(trial, figure, fullpath, 
                                num_cluster_combinations)
            self._plot_distances(trial, figure, fullpath, 
                                 num_cluster_combinations)

            self.draw_canvas(fullpath)
        else:
            if not self._fig_cleared:
                figure = self._plot_panels[fullpath].figure
                figure.clear()
                self._fig_cleared = True
                self.draw_canvas(fullpath)

    def _setup_axes(self, trial, figure, fullpath, ncc, num_clusters):
        # --- RASTER AND TRACE AXES ---
        raster_axes = figure.add_subplot(ncc+2, 1, 1)
        raster_yaxis = raster_axes.get_yaxis()
        raster_yaxis.set_ticks_position('left')
        raster_axes.set_xlabel(pt.PLOT_TIME)
        raster_axes.set_ylabel('Cluster ID')
        # trace_axes will be on top of raster_axes
        trace_axes = figure.add_axes(raster_axes.get_position(), 
                                     axisbg=(1.0, 1.0, 1.0, 0.0),
                                     sharex=raster_axes)
        filename = os.path.split(fullpath)[1]
        trace_axes.set_title(filename)
        trace_yaxis = trace_axes.get_yaxis()
        trace_yaxis.set_ticks_position('right')
        trace_axes.text(1.04, 0.5, 'Trace Number',
                        verticalalignment='center',
                        horizontalalignment='left',
                        rotation='vertical',
                        transform=trace_axes.transAxes,
                        clip_on=False)

        right = -0.015
        left  = -0.04 
        for axes in [trace_axes, raster_axes]:
            adjust_axes_edges(axes, bottom=self.bottom, 
                              right=right, left=left)

        self.trace_axes  = trace_axes
        self.raster_axes = raster_axes

        # --- AVG AND STD AXES ---
        average_axes = figure.add_subplot(ncc+2, 2, 3)
        average_axes.set_ylabel('Spike Averages')
        average_axes.set_xlabel(pt.PLOT_TIME)
        
        std_axes = figure.add_subplot(ncc+2, 2, 4, sharex=average_axes)
        std_axes.set_ylabel("Spike STDs")
        std_axes.set_xlabel(pt.PLOT_TIME)

        self.average_axes = average_axes
        self.std_axes     = std_axes

        
    def _adjust_subplots(self, canvas_size, figure):
        left   = lfs.PLOT_LEFT_BORDER / canvas_size[0]
        right  = 1.0 - lfs.PLOT_RIGHT_BORDER / canvas_size[0]
        top    = 1.0 - lfs.PLOT_TOP_BORDER / canvas_size[1]
        bottom = lfs.PLOT_BOTTOM_BORDER / canvas_size[1]
        figure.subplots_adjust(hspace=0.025, left=left, right=right, 
                               bottom=bottom, top=top)
        self.bottom = bottom
        self.top    = top
        
    def _plot_rasters(self, trial, figure, fullpath, ncc, num_clusters):
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
                                 alpha=0.35)
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

        
    def _plot_clusters(self, trial, figure, fullpath, ncc):
        averages, stds = self._get_averages_and_stds(trial)
        
        for cluster_num, average in averages.items():
            self.average_axes.plot(trial.times[:len(average)], average,
                              label='Cluster %d' % cluster_num)

        for cluster_num, std in stds.items():
            self.std_axes.plot(trial.times[:len(std)], std, 
                          label='Cluster %d' % cluster_num)


    def _get_averages_and_stds(self, trial):
        times = trial.clustering.results
        feature_list  = trial.extraction.results['features']
        feature_times = trial.extraction.results['feature_times']
        features = defaultdict(list)
        for cluster_num, time_list in times.items():
            for time in time_list:
                feature_list_index = feature_times.index(time) 
                features[cluster_num].append(feature_list[feature_list_index])
        stds = {}
        averages = {}
        for key in features.keys():
            features[key] = numpy.array(features[key])
            stds[key]     = numpy.std(features[key],     axis=0)
            averages[key] = numpy.average(features[key], axis=0)
        return averages, stds

    def _plot_distances(self, trial, figure, fullpath, ncc):
        pass


def nchoosek(n, k):
    f = scipy.factorial
    return f(n)/(f(k)*f(n-k))
