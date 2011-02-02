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

from spikepy.plotting.spikepy_plot_panel import SpikepyPlotPanel
from spikepy.plotting import utils
from spikepy.common import program_text as pt
from spikepy.common.config_manager import config_manager as config
from spikepy import projection_utils as pu

class ClusteringPlotPanel(SpikepyPlotPanel):
    def __init__(self, parent, name):
        SpikepyPlotPanel.__init__(self, parent, name)

    def _basic_setup(self, trial_id):
        plot_panel = self._plot_panels[trial_id]
        plot_panel.clear()

    def _pre_run(self, trial_id):
        pass

    def _post_run(self, trial_id):
        trial = self._trials[trial_id]
        figure = self._plot_panels[trial_id].figure
        self._create_axes(trial, figure, trial_id)
        
        self._plot_features(trial, figure, trial_id)
        self._plot_pcas(trial, figure, trial_id)
        self._plot_pros(trial, figure, trial_id)

    def _set_plot_size(self, num_rows, trial_id):
        plot_panel = self._plot_panels[trial_id]
        new_min_size = (self._figsize[0],
                        self._figsize[1] * num_rows)
        plot_panel.set_minsize(new_min_size[0], new_min_size[1])

    def _create_axes(self, trial, figure, trial_id):
        # figure out how large the canvas should be
        results = trial.clustering.results
        if results is not None:
            num_clusters = trial.get_num_clusters()
            num_pros = pu.num_projection_combinations(num_clusters)
            num_srows = 2 + int(math.ceil(num_pros/2.0))
        else:
            num_clusters = 1
            num_pros = 0
            num_srows = 2
        num_trows = int(math.ceil(num_srows/2.0))
        num_cols = 2
        self._set_plot_size(num_trows, trial_id)
        utils.clear_figure(figure)
        self._trial_renamed(trial_id=trial_id)

        # add subplots
        plot_panel = self._plot_panels[trial_id]
        pca = plot_panel.axes['pca'] = figure.add_subplot(num_trows, 
                                                          num_cols, 2)
        utils.set_axes_ticker(pca, axis='xaxis', prune=None)
        utils.set_axes_ticker(pca, axis='yaxis')

        fa = plot_panel.axes['feature'] = figure.add_subplot(num_trows,
                                                             num_cols,1)
        utils.set_axes_ticker(fa, axis='yaxis')

        plot_panel.axes['pro'] = []
        for i in range(num_pros):
            plot_panel.axes['pro'].append(figure.add_subplot(num_srows, 
                                                             num_cols, i+5))

        canvas_size = self._plot_panels[trial_id].GetMinSize()
        config.default_adjust_subplots(figure, canvas_size)

        # tweek axes edges
        axes_left = config['gui']['plotting']['spacing']['axes_left']
        axes_bottom = config['gui']['plotting']['spacing']['axes_bottom']
        title_vspace = config['gui']['plotting']['spacing']['title_vspace']
        #     give room for yticklabels on pca plot
        utils.adjust_axes_edges(pca, canvas_size,
                          left=2*axes_left/3, 
                          top=-title_vspace)
        utils.adjust_axes_edges(fa, canvas_size,
                          right=axes_left/3,
                          top=-title_vspace)
        #     raise all subplots bottom up a bit, for labels
        utils.adjust_axes_edges(pca, canvas_size, bottom=axes_bottom)
        utils.adjust_axes_edges(fa, canvas_size, bottom=axes_bottom)
        for i, pro_axes in enumerate(plot_panel.axes['pro']):
            left = 0.0
            right = 0.0
            bottom = axes_bottom
            if i%2==0:
                right = axes_left/2.0
            else:
                left = axes_left/2.0
            utils.adjust_axes_edges(pro_axes, canvas_size, left=left, 
                                                     right=right,
                                                     bottom=bottom)

    def _plot_pcas(self, trial, figure, trial_id):
        axes = self._plot_panels[trial_id].axes['pca']

        features, pc, var = trial.get_clustered_features(pca_rotated=True)

        feature_numbers = sorted(features.keys())
        for feature_number in feature_numbers:
            rotated_features = features[feature_number]
            num_features = len(rotated_features)
            if len(rotated_features) < 1:
                continue # don't try to plot empty clusters.
            trf = rotated_features.T

            color = config.get_color_from_cycle(feature_number)
            axes.plot(trf[0], trf[1], color=color,
                                      linewidth=0,
                                      marker='o',
                                      markersize=5,
                                      markeredgewidth=0)

        pct_var = [tvar/sum(var)*100.0 for tvar in var]
        pca_colors = config.pca_colors
        axes.set_xlabel(pt.PCA_LABEL % (1, pct_var[0], '%'), 
                        color=pca_colors[0])
        axes.set_ylabel(pt.PCA_LABEL % (2, pct_var[1], '%'), 
                        color=pca_colors[1])


    def _plot_features(self, trial, figure, trial_id):
        axes = self._plot_panels[trial_id].axes['feature']

        axes.set_ylabel(pt.FEATURE_AMPLITUDE)
        axes.set_xlabel(pt.FEATURE_INDEX)

        features = trial.get_clustered_features()

        feature_numbers = sorted(features.keys())
        pc = config['gui']['plotting']
        for i, feature_number in enumerate(feature_numbers):
            color = config.get_color_from_cycle(feature_number)
            num_features = len(features[feature_number])
            if num_features < 1:
                continue # don't bother trying to plot empty clusters.
            feature_xs = [a for a in range(len(features[feature_number][0]))]

            for feature in features[feature_number]:
                axes.plot(feature_xs, feature, 
                          linewidth=pc['std_trace_linewidth'],
                          color=color, 
                          alpha=0.2) 
            avg_feature = numpy.average(features[feature_number], axis=0)
            if i == 0:
                label = pt.CLUSTER_SIZE % num_features
            else:
                label = '%d' % num_features
            axes.plot(feature_xs, avg_feature, 
                      linewidth=pc['bold_linewidth'],
                      color=color, 
                      label=label,
                      alpha=1.0) 
            axes.set_xlim(feature_xs[0],feature_xs[-1])

        canvas_size = self._plot_panels[trial_id].GetMinSize()
        legend_offset = config['gui']['plotting']['spacing']['legend_offset']
        utils.add_shadow_legend(legend_offset, legend_offset, axes, canvas_size,                                ncol=9, loc='lower left')


    def _plot_pros(self, trial, figure, trial_id):
        features = trial.get_clustered_features()
        results = trial.clustering.results
        plot_panel = self._plot_panels[trial_id]

        combos = pu.get_projection_combinations(results.keys())
        for combo, axes in zip(combos, plot_panel.axes['pro']):
            i, j = combo
            pc = config['gui']['plotting']

            if len(features[i]) < 1 or len(features[j]) < 1:
                empty_cluster = j
                if len(features[i]) < 1:
                    empty_cluster = i
                axes.set_xlabel('Cluster %d vs %d (cluster %d is empty)' %
                                (i, j, empty_cluster))
                continue # don't try doing gaussian fits on single point or no point clusters.

            p1, p2 = pu.projection(features[i], features[j])
            bounds = pu.get_bounds(p1, p2)
            h1 = axes.hist(p1, range=bounds, bins=23, 
                          fc=config.get_color_from_cycle(i), ec='k')
            h2 = axes.hist(p2, range=bounds, bins=23, 
                          fc=config.get_color_from_cycle(j), ec='k')

            if len(features[i]) < 2 or len(features[j]) < 2:
                axes.set_xlabel('Cluster %d vs %d (unknown overlap)' %
                                (i, j))
                continue # don't try doing gaussian fits on single point or no point clusters.

            x, y1, y2 = pu.get_both_gaussians(p1, p2, num_points=300)
            ymax = numpy.max( numpy.hstack([h1[0], h2[0]]) )*1.05

            axes.plot(x, y1*ymax*0.8, color='k', linewidth=2.0)
            axes.plot(x, y2*ymax*0.8, color='k', linewidth=2.0)

            axes.set_xlim(*bounds)
            axes.set_ylim(0, ymax)
            utils.format_y_axis_hist(axes)

            axes.set_ylabel('')
            axes.set_xlabel('Cluster %d vs %d (%3.1f%s overlap)' %
                            (i, j, 100.0*pu.get_overlap(p1, p2), '%'))

