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
import math

from wx.lib.pubsub import Publisher as pub
import wx
import numpy

from spikepy.plotting.multi_plot_panel import MultiPlotPanel
from spikepy.common import program_text as pt
from spikepy.plotting.utils import adjust_axes_edges, set_axes_num_ticks
from spikepy.common.utils import pca
from spikepy.common.config_manager import config_manager as config
from spikepy import projection_utils as pu

class ClusteringPlotPanel(MultiPlotPanel):
    def __init__(self, parent, name):
        pconfig = config['gui']['plotting']
        self._dpi       = pconfig['dpi']
        self._figsize   = config.get_size('figure')
        self._facecolor = pconfig['face_color']
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
        self._pca_axes      = {}
        self._pro_axes      = {}

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
        figsize = (self._figsize[0], self._figsize[1])
        self.add_plot(trial_id, figsize=figsize, 
                                facecolor=self._facecolor,
                                edgecolor=self._facecolor,
                                dpi=self._dpi)
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
        self._create_axes(trial, figure, trial_id)
        
        self._plot_features(trial, figure, trial_id)
        self._plot_pcas(trial, figure, trial_id)
        self._plot_pros(trial, figure, trial_id)

        self.draw_canvas(trial_id)

    def _set_plot_size(self, num_rows, trial_id):
        plot_panel = self._plot_panels[trial_id]
        new_min_size = (plot_panel._original_min_size[0],
                        plot_panel._original_min_size[1] * num_rows)
        plot_panel.SetMinSize(new_min_size)
        if hasattr(plot_panel.GetParent(), 'SetupScrolling'):
            plot_panel.GetParent().SetupScrolling()

    def _create_axes(self, trial, figure, trial_id):
        results = trial.clustering.results
        if results is not None:
            num_clusters = trial.get_num_clusters()
            num_pros = pu.num_projection_combinations(num_clusters)
            num_rows = 2*(int(math.ceil(num_pros/2.0))+1)
        else:
            num_clusters = 1
            num_pros = 0
            num_rows = 4
        num_cols = 2
        self._set_plot_size(num_rows/2, trial_id)
        figure.clear()
        fa = self._feature_axes[trial_id] = figure.add_subplot(num_rows/2,
                                                               num_cols,1)
        pca = self._pca_axes[trial_id] = figure.add_subplot(num_rows/2, 
                                                            num_cols, 2)
        self._pro_axes[trial_id] = []
        for i in range(num_pros):
            self._pro_axes[trial_id].append(figure.add_subplot(num_rows, 
                                                               num_cols, i+5))

        canvas_size = self._plot_panels[trial_id].GetMinSize()
        config.default_adjust_subplots(figure, canvas_size)

        axes_left = config['gui']['plotting']['spacing']['axes_left']
        axes_bottom = config['gui']['plotting']['spacing']['axes_bottom']
        # give room for yticklabels on pca plot
        adjust_axes_edges(pca, canvas_size,
                          left=2*axes_left/3)
        adjust_axes_edges(fa, canvas_size,
                          right=axes_left/3)
        # raise all subplots bottom up a bit, for labels
        adjust_axes_edges(pca, canvas_size, bottom=axes_bottom)
        adjust_axes_edges(fa, canvas_size, bottom=axes_bottom)
        for i, pro_axes in enumerate(self._pro_axes[trial_id]):
            left = 0.0
            right = 0.0
            bottom = axes_bottom
            if i%2==0:
                right = axes_left/2.0
            else:
                left = axes_left/2.0
            adjust_axes_edges(pro_axes, canvas_size, left=left, 
                                                     right=right,
                                                     bottom=bottom)

    def _plot_pcas(self, trial, figure, trial_id):
        axes = self._pca_axes[trial_id]
        axes.clear()

        if trial.clustering.results is not None:
            features, pc, var = trial.get_clustered_features(pca_rotated=True)
        else:
            return

        feature_numbers = sorted(features.keys())
        for feature_number in feature_numbers:
            rotated_features = features[feature_number]
            if len(rotated_features) < 1:
                continue # don't try to plot empty clusters.
            trf = rotated_features.T

            color = config.get_color_from_cycle(feature_number)
            axes.plot(trf[0], trf[1], color=color,
                                      linewidth=0,
                                      marker='.')

        pct_var = [tvar/sum(var)*100.0 for tvar in var]
        axes.set_xlabel(pt.PCA_LABEL % (1, pct_var[0], '%'))
        axes.set_ylabel(pt.PCA_LABEL % (2, pct_var[1], '%'))

        set_axes_num_ticks(axes, axis='both', num=4)

    def _plot_features(self, trial, figure, trial_id):
        axes = self._feature_axes[trial_id]
        axes.clear()

        axes.set_ylabel(pt.FEATURE_AMPLITUDE)
        axes.set_xlabel(pt.FEATURE_INDEX)

        if trial.clustering.results is not None:
            features = trial.get_clustered_features()
        else:
            return

        axes.set_autoscale_on(True)
        feature_numbers = sorted(features.keys())
        pc = config['gui']['plotting']
        for feature_number in feature_numbers:
            color = config.get_color_from_cycle(feature_number)
            num_features = len(features[feature_number])
            if num_features < 1:
                continue # don't bother trying to plot empty clusters.
            avg_feature = numpy.average(features[feature_number], axis=0)
            axes.plot(avg_feature, 
                      linewidth=pc['bold_linewidth'],
                      color=color, 
                      alpha=1.0, 
                      label=pt.AVERAGE_OF % num_features)
            for feature in features[feature_number]:
                axes.plot(feature, 
                          linewidth=pc['std_trace_linewidth'],
                          color=color, 
                          alpha=0.2) 
        #axes.legend(loc='upper right')

    def _plot_pros(self, trial, figure, trial_id):
        if trial.clustering.results is not None:
            features = trial.get_clustered_features()
            results = trial.clustering.results
        else:
            return

        combos = pu.get_projection_combinations(results.keys())
        for combo, axes in zip(combos, self._pro_axes[trial_id]):
            i, j = combo
            axes.clear()

            axes.set_autoscale_on(True)
            pc = config['gui']['plotting']

            if len(features[i]) < 1 or len(features[j]) < 1:
                empty_cluster = j
                if len(features[i]) < 1:
                    empty_cluster = i
                axes.set_xlabel('Cluster %d vs %d (cluster %d is empty)' %
                                (i, j, empty_cluster))
                continue # don't try doing gaussian fits on single point or no point clusters.

            p1, p2 = pu.projection(features[i], features[j])
            axes.hist(p1, bins=8, fc=config.get_color_from_cycle(i), ec='k')
            axes.hist(p2, bins=8, fc=config.get_color_from_cycle(j), ec='k')

            if len(features[i]) < 2 or len(features[j]) < 2:
                axes.set_xlabel('Cluster %d vs %d (unknown overlap)' %
                                (i, j))
                continue # don't try doing gaussian fits on single point or no point clusters.

            x, y1, y2 = pu.get_both_gaussians(p1, p2, num_points=100)
            ylow, yhigh = axes.get_ylim()
            axes.plot(x, y1*yhigh*0.8, color='k', linewidth=2.0)
            axes.plot(x, y2*yhigh*0.8, color='k', linewidth=2.0)

            axes.set_ylabel('')
            axes.set_xlabel('Cluster %d vs %d (%3.1f%s overlap)' %
                            (i, j, 100.0*pu.get_overlap(p1, p2), '%'))

