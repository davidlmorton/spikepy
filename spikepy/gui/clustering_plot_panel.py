from collections import defaultdict

from wx.lib.pubsub import Publisher as pub
import wx
import numpy
import scipy

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel
from .look_and_feel_settings import lfs
from . import program_text as pt

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
            self._plot_panels[fullpath].set_minsize(self._figsize[0], 
                              self._figsize[1]*(num_cluster_combinations+2))
            figure = self._plot_panels[fullpath].figure
            figure.clear()
            self._adjust_subplots(self._plot_panels[fullpath])
            
            self._plot_rasters(trial,   figure, fullpath, 
                               num_cluster_combinations, num_clusters)
            self._plot_clusters(trial,  figure, fullpath, 
                                num_cluster_combinations)
            self._plot_distances(trial, figure, fullpath, 
                                 num_cluster_combinations)

            self.draw_canvas(fullpath)

    def _adjust_subplots(self, plot_panel):
        canvas_size = plot_panel._original_min_size
        figure = plot_panel.figure
        left   = lfs.PLOT_LEFT_BORDER / canvas_size[0]
        right  = 1.0 - lfs.PLOT_RIGHT_BORDER / canvas_size[0]
        top    = 1.0 - lfs.PLOT_TOP_BORDER / canvas_size[1]
        bottom = lfs.PLOT_BOTTOM_BORDER / canvas_size[1]
        figure.subplots_adjust(hspace=0.025, left=left, right=right, 
                               bottom=bottom, top=top)
        

    def _plot_rasters(self, trial, figure, fullpath, ncc, num_clusters):
        raster_axes = figure.add_subplot(ncc+2, 1, 1)

        times = trial.times
        traces = trial.detection_filter.results
        std = numpy.std(traces)
        for i, trace in enumerate(traces):
            raster_axes.plot(times, trace-i*20*std, color=lfs.PLOT_COLOR_2, 
                                 linewidth=lfs.PLOT_LINEWIDTH_2, 
                                 label=pt.DETECTION_TRACE_GRAPH_LABEL,
                                 alpha=0.4)

        
        times = trial.clustering.results
        ylim = raster_axes.get_ylim()
        spike_y_list = numpy.linspace(ylim[1], ylim[0], num_clusters+2)[1:-1]

        keys = sorted(times.keys())
        for key, spike_y in zip(keys, spike_y_list):
            spike_ys = [spike_y for i in xrange(len(times[key]))]
            spike_xs = times[key]
            raster_axes.plot(spike_xs, spike_ys, linewidth=0, marker='|',
                             markersize=lfs.SPIKE_RASTER_HEIGHT,
                             markeredgewidth=lfs.SPIKE_RASTER_WIDTH,
                             color=lfs.SPIKE_RASTER_COLOR)
            

        
    def _plot_clusters(self, trial, figure, fullpath, ncc):
        averages, stds = self._get_averages_and_stds(trial)
        
        average_axes = figure.add_subplot(ncc+2, 2, 3)
        for cluster_num, average in averages.items():
            average_axes.plot(average, label='Cluster %d' % cluster_num)

        std_axes = figure.add_subplot(ncc+2, 2, 4)
        for cluster_num, std in stds.items():
            std_axes.plot(std, label='Cluster %d' % cluster_num)


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
