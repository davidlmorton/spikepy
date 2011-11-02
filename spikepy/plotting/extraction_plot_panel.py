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

from wx.lib.pubsub import Publisher as pub
import wx
import numpy

from spikepy.plotting.spikepy_plot_panel import SpikepyPlotPanel
from spikepy.plotting import utils
from spikepy.common import program_text as pt
from spikepy.common.config_manager import config_manager as config

class ExtractionPlotPanel(SpikepyPlotPanel):
    def __init__(self, parent, session, name):
        SpikepyPlotPanel.__init__(self, parent, session, name)


    def _basic_setup(self, trial_id):
        plot_panel = self._plot_panels[trial_id]
        plot_panel.clear()

        # set the size of the plot properly.
        num_rows = 2
        self._resize_canvas(num_rows, trial_id)

        # set up feature axes and pca axes
        figure = plot_panel.figure
        plot_panel.axes['feature'] = fa = figure.add_subplot(num_rows, 1, 1)
        plot_panel.axes['pc'] = figure.add_subplot(num_rows*2, 1, 3, sharex=fa)
        plot_panel.axes['pca'] = []
        for i in xrange(3):
            axes = figure.add_subplot(num_rows, 3, i+4)
            plot_panel.axes['pca'].append(axes)

        canvas_size = plot_panel.GetMinSize()
        # adjust subplots to spikepy uniform standard
        config.default_adjust_subplots(figure, canvas_size)

        # adjust axes into place.
        e = 1/8.0
        utils.adjust_axes_edges(fa, (1.0, 1.0), bottom=-e)
        utils.adjust_axes_edges(plot_panel.axes['pc'], (1.0, 1.0),
                                bottom=-e, top=e)
        for pca_axes in plot_panel.axes['pca']:
            utils.adjust_axes_edges(pca_axes, (1.0, 1.0), top=-e)

        # tweek psd axes and trace axes
        top = -config['gui']['plotting']['spacing']['title_vspace']
        nl_bottom = config['gui']['plotting']['spacing']['no_label_axes_bottom']
        bottom = config['gui']['plotting']['spacing']['axes_bottom']
        utils.adjust_axes_edges(plot_panel.axes['feature'], canvas_size,
                                bottom=nl_bottom, top=top)
        utils.adjust_axes_edges(plot_panel.axes['pc'], canvas_size,
                                bottom=bottom)

        left = config['gui']['plotting']['spacing']['axes_left']
        outter = (2.0*left)/3.0
        inner = left/3.0
        pca_axes = plot_panel.axes['pca']
        utils.adjust_axes_edges(pca_axes[0], canvas_size, right=outter)
        utils.adjust_axes_edges(pca_axes[1], canvas_size, right=inner, 
                                left=inner)
        utils.adjust_axes_edges(pca_axes[2], canvas_size, left=outter)

        # label axes
        plot_panel.axes['feature'].set_xticklabels([''], visible=False)
        plot_panel.axes['feature'].set_ylabel(pt.FEATURE_AMPLITUDE)
        plot_panel.axes['pc'].set_xlabel(pt.FEATURE_INDEX)
        plot_panel.axes['pc'].set_ylabel(pt.PC_AMPLITUDE,
                                         multialignment='center')

        self.pc_y = [2,3,3] # which pc is associated with what axis.
        self.pc_x = [1,1,2]
        self.pca_colors = config.pca_colors
        for x, y, axes in zip(self.pc_x, self.pc_y, pca_axes):
            axes.set_xlabel(pt.PCA_LABEL % (x, 100, '%'), 
                            color=self.pca_colors[x-1])
            axes.set_ylabel(pt.PCA_LABEL % (y, 100, '%'),
                            color=self.pca_colors[y-1])

    def _pre_run(self, trial_id):
        pass

    def _post_run(self, trial_id):
        # clear all the axes
        plot_panel = self._plot_panels[trial_id]
        feature_axes = plot_panel.axes['feature']
        pc_axes = plot_panel.axes['pc']
        utils.clear_axes(feature_axes)
        utils.clear_axes(pc_axes)
        pca_axes = plot_panel.axes['pca']
        for axes in pca_axes:
            utils.clear_axes(axes)

        trial = self._trials[trial_id]
        results = trial.extraction.results
        features = results['features']
        rotated_features = results['pca_rotated_features']
        pc = results['pca_basis_vectors']
        var = results['pca_variances']
        pct_var = [tvar/sum(var)*100.0 for tvar in var]
        trf = rotated_features.T

        # plot the features
        pconfig = config['gui']['plotting']['extraction']
        trial = self._trials[trial_id]
        features = trial.extraction.results['features']
        feature_xs = [i for i in range(len(features[0]))]

        utils.plot_limited_num_spikes(feature_axes, feature_xs, features, 
                              info_anchor=(0.03, 1.03),
                              info_ha='left',
                              linewidth=pconfig['feature_trace_linewidth'],
                              color='k', 
                              alpha=pconfig['feature_trace_alpha'])
        utils.set_axes_ticker(feature_axes, axis='yaxis')
        feature_axes.set_xlim(feature_xs[0],feature_xs[-1])
        plot_panel.draw()

        # plot the pc vector components.
        for i, pc_vector in reversed([i for i in enumerate(pc[:3])]):
            pc_axes.fill_between(feature_xs, pc_vector, 
                                 color=self.pca_colors[i],
                                 alpha=0.8)
        utils.set_axes_ticker(pc_axes, axis='yaxis', prune=None)
        plot_panel.draw()

        # plot the pca projections
        for x, y, axes in zip(self.pc_x, self.pc_y, pca_axes):
            axes.set_xlabel(pt.PCA_LABEL % (x, pct_var[x-1], '%'),
                            color=self.pca_colors[x-1])
            axes.set_ylabel(pt.PCA_LABEL % (y, pct_var[y-1], '%'),
                            color=self.pca_colors[y-1])
            axes.plot(trf[x-1], trf[y-1], color='black', 
                                          linewidth=0, 
                                          marker='o',
                                          markersize=4,
                                          markeredgewidth=0)
            utils.set_axes_ticker(axes, nbins=4, axis='xaxis', prune=None)
            utils.set_axes_ticker(axes, axis='yaxis')
            plot_panel.draw()


