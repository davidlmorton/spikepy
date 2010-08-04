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
        figure = self._plot_panels[fullpath].figure
        if trial.clustering.results is not None:
            num_clusters = len(trial.clustering.results.keys())
            num_cluster_combinations = nchoosek(num_clusters, 2)
            
            self._plot_rasters(trial,   figure, fullpath, 
                               num_cluster_combinations)
            self._plot_clusters(trial,  figure, fullpath, 
                                num_cluster_combinations)
            self._plot_distances(trial, figure, fullpath, 
                                 num_cluster_combinations)

            self.draw_canvas(fullpath)

    def _plot_rasters(self, trial, figure, fullpath, ncc):
        raster_axes = figure.add_subplot(ncc+2, 1, 1)
        pass
        
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
