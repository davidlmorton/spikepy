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
    def __init__(self, parent, name):
        SpikepyPlotPanel.__init__(self, parent, name)


    def _basic_setup(self, trial_id):
        plot_panel = self._plot_panels[trial_id]
        plot_panel.clear()

        # set the size of the plot properly.
        num_rows = 3
        figheight = self._figsize[1] * (num_rows - 1)
        figwidth  = self._figsize[0]
        plot_panel.set_minsize(figwidth, figheight)
        self._trial_renamed(trial_id=trial_id)

        # set up feature axes and pca axes
        figure = plot_panel.figure
        plot_panel.axes['feature'] = fa = figure.add_subplot(num_rows, 1, 1)
        plot_panel.axes['pc'] = figure.add_subplot(num_rows, 1, 2, sharex=fa)
        plot_panel.axes['pca'] = []
        for i in xrange(3):
            axes = figure.add_subplot(num_rows, 3, i+7)
            plot_panel.axes['pca'].append(axes)

        canvas_size = plot_panel.GetMinSize()
        # adjust subplots to spikepy uniform standard
        config.default_adjust_subplots(figure, canvas_size)

        # tweek psd axes and trace axes
        top = -config['gui']['plotting']['spacing']['title_vspace']
        bottom = config['gui']['plotting']['spacing']['axes_bottom']
        nl_bottom = config['gui']['plotting']['spacing']['no_label_axes_bottom']
        utils.adjust_axes_edges(plot_panel.axes['feature'], canvas_size,
                                bottom=-nl_bottom, top=top)
        utils.adjust_axes_edges(plot_panel.axes['pc'], canvas_size,
                                bottom=3*bottom/4, top=2*nl_bottom)

        left = config['gui']['plotting']['spacing']['axes_left']
        outter = (2.0*left)/3.0
        inner = left/3.0
        pca_axes = plot_panel.axes['pca']
        utils.adjust_axes_edges(pca_axes[0], canvas_size, right=outter,
                                top=bottom/4)
        utils.adjust_axes_edges(pca_axes[1], canvas_size, right=inner, 
                                left=inner,
                                top=bottom/4)
        utils.adjust_axes_edges(pca_axes[2], canvas_size, left=outter,
                                top=bottom/4)

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

        # plot the pca projections
        trial = self._trials[trial_id]
        rotated_features, pc, var = trial.get_pca_rotated_features()
        pct_var = [tvar/sum(var)*100.0 for tvar in var]
        trf = rotated_features.T

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

        # plot the pc vector components.
        feature_xs = [i for i in range(len(pc[0]))]
        for i, pc_vector in reversed([i for i in enumerate(pc[:3])]):
            pc_axes.fill_between(feature_xs, pc_vector, 
                                 color=self.pca_colors[i],
                                 alpha=0.8)
        utils.set_axes_ticker(pc_axes, axis='yaxis', prune=None)

        # plot the features
        pc = config['gui']['plotting']['extraction']
        trial = self._trials[trial_id]
        features = trial.extraction.results['features']

        for feature in features:
            feature_axes.plot(feature_xs, feature, 
                              linewidth=pc['feature_trace_linewidth'],
                              color='k', 
                              alpha=pc['feature_trace_alpha'])
        utils.set_axes_ticker(feature_axes, axis='yaxis')
        feature_axes.set_xlim(feature_xs[0],feature_xs[-1])

