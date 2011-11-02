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
from spikepy.common import projection_utils as pu

class ClusteringPlotPanel(SpikepyPlotPanel):
    def __init__(self, parent, session, name):
        SpikepyPlotPanel.__init__(self, parent, session, name)

    def _basic_setup(self, trial_id):
        plot_panel = self._plot_panels[trial_id]
        plot_panel.clear()

    def _pre_run(self, trial_id):
        pass

    def _post_run(self, trial_id):
        trial = self._trials[trial_id]
        plot_panel = self._plot_panels[trial_id]
        figure = plot_panel.figure
        self._create_axes(trial, figure, trial_id)
        plot_panel.draw()
        
        self._plot_features(trial, figure, trial_id)
        self._plot_pcas(trial, figure, trial_id)
        self._plot_pros(trial, figure, trial_id)

    def _create_axes(self, trial, figure, trial_id):
        plot_panel = self._plot_panels[trial_id]

        # figure out how large the canvas should be
        results = trial.clustering.results
        if results is not None:
            num_clusters = trial.get_num_clusters()
            num_pros = pu.num_projection_combinations(num_clusters)
            num_srows = 3 + num_pros
        else:
            num_clusters = 1
            num_pros = 0
            num_srows = 3
        num_trows = int(math.ceil(num_srows/2.0))
        num_srows = num_trows*2
        self._resize_canvas(num_trows, trial_id)
        utils.clear_figure(figure)
        self._trial_renamed(trial_id=trial_id)

        # set up feature axes and pca axes
        plot_panel.axes['feature'] = fa = figure.add_subplot(num_trows, 1, 1)
        plot_panel.axes['pca'] = []
        for i in xrange(3):
            axes = figure.add_subplot(num_trows, 3, i+4)
            plot_panel.axes['pca'].append(axes)

        # set up projection axes
        plot_panel.axes['pro_feature'] = []
        plot_panel.axes['pro'] = []
        for k in range(num_pros):
            pf_axes = figure.add_subplot(num_srows, 2, 7+2*k)
            plot_panel.axes['pro_feature'].append(pf_axes)
            p_axes = figure.add_subplot(num_srows, 2, 8+2*k)
            plot_panel.axes['pro'].append(p_axes)

        canvas_size = plot_panel.GetMinSize()
        # adjust subplots to spikepy uniform standard
        config.default_adjust_subplots(figure, canvas_size)

        # adjust axes into place.
        e = 1/4.0
        utils.adjust_axes_edges(fa, (1.0, num_trows*1.0), bottom=-e)
        for pca_axes in plot_panel.axes['pca']:
            utils.adjust_axes_edges(pca_axes, (1.0, num_trows*1.0), 
                                    top=e, bottom=-2*e)

        # tweek psd axes and trace axes
        top = -config['gui']['plotting']['spacing']['title_vspace']
        nl_bottom = config['gui']['plotting']['spacing']['no_label_axes_bottom']
        bottom = config['gui']['plotting']['spacing']['axes_bottom']
        utils.adjust_axes_edges(plot_panel.axes['feature'], canvas_size,
                                bottom=nl_bottom, top=top)

        left = config['gui']['plotting']['spacing']['axes_left']
        outter = (2.0*left)/3.0
        inner = left/3.0
        pca_axes = plot_panel.axes['pca']
        utils.adjust_axes_edges(pca_axes[0], canvas_size, right=outter, 
                                top=bottom-nl_bottom, bottom=bottom)
        utils.adjust_axes_edges(pca_axes[1], canvas_size, right=inner, 
                                left=inner, top=bottom-nl_bottom,
                                bottom=bottom)
        utils.adjust_axes_edges(pca_axes[2], canvas_size, left=outter,
                                top=bottom-nl_bottom,
                                bottom=bottom)

        # tweek pro and pro_feature axes
        for p_axes, pf_axes in zip(plot_panel.axes['pro'], 
                                   plot_panel.axes['pro_feature']):
            utils.adjust_axes_edges(pf_axes, canvas_size, right=left/2,
                                    bottom=bottom)
            utils.adjust_axes_edges(p_axes, canvas_size, left=left/2,
                                    bottom=bottom)

        # label axes
        plot_panel.axes['feature'].set_ylabel(pt.FEATURE_AMPLITUDE)

        self.pc_y = [2,3,3] # which pc is associated with what axis.
        self.pc_x = [1,1,2]
        self.pca_colors = config.pca_colors
        for x, y, axes in zip(self.pc_x, self.pc_y, pca_axes):
            axes.set_xlabel(pt.PCA_LABEL % (x, 100, '%'), 
                            color=self.pca_colors[x-1])
            axes.set_ylabel(pt.PCA_LABEL % (y, 100, '%'),
                            color=self.pca_colors[y-1])

    def _plot_pcas(self, trial, figure, trial_id):
        plot_panel = self._plot_panels[trial_id]
        pca_axes = plot_panel.axes['pca']

        results = trial.clustering.results 
        features = results['clustered_pca_rotated_features']
        var = trial.extraction.results['pca_variances']

        pct_var = [tvar/sum(var)*100.0 for tvar in var]


        self.pc_y = [2,3,3] # which pc is associated with what axis.
        self.pc_x = [1,1,2]

        feature_numbers = sorted(features.keys())
        for x, y, axes in zip(self.pc_x, self.pc_y, pca_axes):
            for feature_number in feature_numbers:
                rotated_features = features[feature_number]
                num_features = len(rotated_features)
                if len(rotated_features) < 1:
                    continue # don't try to plot empty clusters.
                trf = numpy.array(rotated_features).T

                color = config.get_color_from_cycle(
                        feature_numbers.index(feature_number))
                axes.plot(trf[x-1], trf[y-1], color=color,
                                          linewidth=0,
                                          marker='o',
                                          markersize=5,
                                          markeredgewidth=0)
                utils.set_axes_ticker(axes, nbins=4, axis='xaxis', prune=None)
                utils.set_axes_ticker(axes, axis='yaxis')

            pca_colors = config.pca_colors
            axes.set_xlabel(pt.PCA_LABEL % (x, pct_var[x-1], '%'), 
                            color=pca_colors[x-1])
            axes.set_ylabel(pt.PCA_LABEL % (y, pct_var[y-1], '%'), 
                            color=pca_colors[y-1])
            plot_panel.draw()


    def _plot_features(self, trial, figure, trial_id):
        plot_panel = self._plot_panels[trial_id]
        axes = plot_panel.axes['feature']

        axes.set_ylabel(pt.FEATURE_AMPLITUDE)
        axes.set_xlabel(pt.FEATURE_INDEX)

        features = trial.clustering.results['clustered_features']

        feature_numbers = sorted(features.keys())
        total_num_features = 0
        for f_num in feature_numbers:
            total_num_features += len(features[f_num])

        pc = config['gui']['plotting']
        cluster_count = 0
        for i, feature_number in enumerate(feature_numbers):
            color = config.get_color_from_cycle(
                    feature_numbers.index(feature_number))
            num_features = len(features[feature_number])
            pct_features = int(num_features/float(total_num_features)*100)
            if num_features < 1:
                continue # don't bother trying to plot empty clusters.
            feature_xs = [a for a in range(len(features[feature_number][0]))]

            utils.plot_limited_num_spikes(axes, feature_xs, 
                                          numpy.array(features[feature_number]),
                                          set_ranking=cluster_count, 
                                          linewidth=pc['std_trace_linewidth'],
                                          color=color, 
                                          alpha=0.2) 
            cluster_count += 1
            if i == 0:
                label = pt.CLUSTER_SIZE
            else:
                label = ''
            label += '%d (%d%s)' % (num_features,pct_features,'%')
            axes.plot([-1, -2], [0, 0], linewidth=pc['bold_linewidth'],
                      color=color, label=label)
            axes.set_xlim(feature_xs[0],feature_xs[-1])
            plot_panel.draw()

        utils.set_axes_ticker(axes, axis='yaxis')
        canvas_size = self._plot_panels[trial_id].GetMinSize()
        legend_offset = config['gui']['plotting']['spacing']['legend_offset']
        utils.add_shadow_legend(legend_offset, legend_offset, axes, canvas_size,
                                ncol=7, loc='lower left')

    def _plot_pros(self, trial, figure, trial_id):
        pc = config['gui']['plotting']
        results = trial.clustering.results
        features = trial.clustering.results['clustered_features']
        cluster_ids = sorted(features.keys())
        # find out how long the features sets are and make the xs for plotting
        efeatures = trial.extraction.results['features'][0]
        feature_xs = [fx for fx in range(len(efeatures))]

        # sort only on overlap.
        projections = sorted(results['projections'], key=lambda x:x[0], 
                             reverse=True) 
        plot_panel = self._plot_panels[trial_id]

        combos = pu.get_projection_combinations(results.keys())
        for k, projection_info in enumerate(projections):
            axes = plot_panel.axes['pro'][k]
            feature_axes = plot_panel.axes['pro_feature'][k]
            overlap, ps, (i, j) = projection_info

            # plot pro features
            cluster_count = 0
            for key in (i, j):
                color = config.get_color_from_cycle(cluster_ids.index(key))
                num_features = len(features[key])
                utils.plot_limited_num_spikes(feature_axes, feature_xs,
                                            numpy.array(features[key]),
                                            set_ranking=cluster_count,
                                            color=color,
                                            linewidth=pc['std_trace_linewidth'],
                                            alpha=0.5)
                cluster_count += 1
                plot_panel.draw()
            feature_axes.set_xlabel(pt.FEATURE_INDEX)
            feature_axes.set_ylabel(pt.FEATURE_AMPLITUDE)
            utils.set_axes_ticker(feature_axes, axis='yaxis')
    
            # check for empty clusters
            if overlap is None:
                empty_clusters = []
                if len(features[i]) == 0:
                    empty_clusters.append(i)
                if len(features[j]) == 0:
                    empty_clusters.append(j)
                axes.set_xlabel(pt.PRO_EMPTY % (i, j, empty_clusters))
                utils.format_y_axis_hist(axes)
                axes.text(0.5, 0.5, pt.CLUSTER_EMPTY,
                          fontsize=16,
                          verticalalignment='center',
                          horizontalalignment='center',
                          transform=axes.transAxes)
                continue

            # plot histograms
            p1, p2 = ps
            bounds = pu.get_bounds(p1, p2)
            h1 = axes.hist(p1, range=bounds, bins=29, 
                          fc=config.get_color_from_cycle(cluster_ids.index(i)),
                          ec='w')
            h2 = axes.hist(p2, range=bounds, bins=29, 
                          fc=config.get_color_from_cycle(cluster_ids.index(j)),
                          ec='w', alpha=0.9)

            # check for clusters of size = 1
            if overlap == -1:
                axes.set_xlabel(pt.PRO_UNKNOWN % (i, j))
                utils.format_y_axis_hist(axes)
                continue

            x, y1, y2 = pu.get_both_gaussians(p1, p2, num_points=300)
            ymax = numpy.max( numpy.hstack([h1[0], h2[0]]) )*1.05

            axes.plot(x, y1*ymax*0.8, color='k', linewidth=2.0)
            axes.plot(x, y2*ymax*0.8, color='k', linewidth=2.0)

            axes.set_xlim(*bounds)
            axes.set_ylim(0, ymax)
            utils.format_y_axis_hist(axes)

            axes.set_ylabel(pt.COUNT_PER_BIN)
            axes.set_xlabel(pt.PRO_OK % (i, j, 100.0*overlap, '%'))
            plot_panel.draw()

