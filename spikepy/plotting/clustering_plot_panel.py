import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy

from spikepy.plotting.multi_plot_panel import MultiPlotPanel
from spikepy.gui.look_and_feel_settings import lfs
from spikepy.common import program_text as pt
from spikepy.plotting.utils import adjust_axes_edges, set_axes_num_ticks
from spikepy.common.utils import pca

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
        pub.subscribe(self._trial_altered, topic='TRIAL_CLUSTERED')
        pub.subscribe(self._trial_altered, topic='STAGE_REINITIALIZED')
        pub.subscribe(self._trial_renamed,  topic='TRIAL_RENAMED')

        self._trials        = {}
        self._feature_axes  = {}
        self._pca_axes_list = {}

    def _remove_trial(self, message=None):
        trial_id = message.data
        del self._trials[trial_id]
        if trial_id in self._feature_axes.keys():
            del self._feature_axes[trial_id]

    def _trial_added(self, message=None, trial=None):
        if message is not None:
            trial = message.data

        trial_id = trial.trial_id
        self._trials[trial_id] = trial
        figsize = (self._figsize[0], self._figsize[1]*2)
        self.add_plot(trial_id, figsize=figsize, 
                                facecolor=self._facecolor,
                                edgecolor=self._facecolor,
                                dpi=self._dpi)
        figure = self._plot_panels[trial_id].figure
        self._create_axes(trial, figure, trial_id)
        self._replot_panels.add(trial_id)

    def _trial_renamed(self, message=None):
        trial = message.data
        trial_id = trial.trial_id
        new_name = trial.display_name
        axes = self._feature_axes[trial_id]
        axes.set_title(pt.TRIAL_NAME+new_name)
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
        figure = self._plot_panels[trial_id].figure
        
        self._plot_features(trial, figure, trial_id)
        self._plot_pcas(trial, figure, trial_id)

        self.draw_canvas(trial_id)

    def _create_axes(self, trial, figure, trial_id):
        fa = self._feature_axes[trial_id] = figure.add_subplot(2,1,1)
        self._pca_axes_list[trial_id] = []
        for i in [1,2,3]:
            axes = figure.add_subplot(2,3,3+i)
            self._pca_axes_list[trial_id].append(axes)
        canvas_size = self._plot_panels[trial_id].GetMinSize()
        lfs.default_adjust_subplots(figure, canvas_size)
        adjust_axes_edges(fa, canvas_size, bottom=lfs.AXES_BOTTOM)
        # give room for yticklabels on pca plots
        adjust_axes_edges(self._pca_axes_list[trial_id][0], canvas_size,
                          right=2*lfs.AXES_LEFT/3)
        adjust_axes_edges(self._pca_axes_list[trial_id][1], canvas_size,
                          left=lfs.AXES_LEFT/3)
        adjust_axes_edges(self._pca_axes_list[trial_id][1], canvas_size,
                          right=lfs.AXES_LEFT/3)
        adjust_axes_edges(self._pca_axes_list[trial_id][2], canvas_size,
                          left=2*lfs.AXES_LEFT/3)

    def _plot_pcas(self, trial, figure, trial_id):
        for i, axes in enumerate(self._pca_axes_list[trial_id]):
            axes.clear()

        if trial.clustering.results is not None:
            features, pc, var = trial.get_clustered_features(pca_rotated=True)
        else:
            return

        feature_numbers = sorted(features.keys())
        for feature_number in feature_numbers:
            rotated_features = features[feature_number]
            pct_var = [tvar/sum(var)*100.0 for tvar in var]
            trf = rotated_features.T

            pc_x = [2,3,3] # which pc is associated with what axis.
            pc_y = [1,1,2]
            color = lfs.get_color_from_cycle(feature_number)
            for i, axes in enumerate(self._pca_axes_list[trial_id]):
                axes.set_ylabel(pt.PCA_LABEL % (pc_y[i], pct_var[pc_y[i]-1], '%'))
                axes.set_xlabel(pt.PCA_LABEL % (pc_x[i], pct_var[pc_x[i]-1], '%'))
                axes.plot(trf[pc_x[i]-1], trf[pc_y[i]-1], color=color,
                                          linewidth=0, marker='.')

        for i, axes in enumerate(self._pca_axes_list[trial_id]):
            set_axes_num_ticks(axes, axis='both', num=4)

    def _plot_features(self, trial, figure, trial_id):
        axes = self._feature_axes[trial_id]
        axes.clear()
        trial_name = trial.display_name
        axes.set_title(pt.TRIAL_NAME+trial_name)
        axes.set_ylabel(pt.FEATURE_AMPLITUDE)
        axes.set_xlabel(pt.FEATURE_INDEX)

        if trial.clustering.results is not None:
            features = trial.get_clustered_features()
        else:
            return

        axes.set_autoscale_on(True)
        feature_numbers = sorted(features.keys())
        for feature_number in feature_numbers:
            color = lfs.get_color_from_cycle(feature_number)
            num_features = len(features[feature_number])
            avg_feature = numpy.average(features[feature_number], axis=0)
            axes.plot(avg_feature, linewidth=lfs.PLOT_LINEWIDTH_1,
                               color=color, alpha=1.0, 
                               label=pt.AVERAGE_OF % num_features)
            for feature in features[feature_number]:
                axes.plot(feature, linewidth=lfs.PLOT_LINEWIDTH_4,
                               color=color, alpha=0.2) 
        axes.legend(loc='upper right')
