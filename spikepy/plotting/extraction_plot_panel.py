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
        num_rows = 2
        figheight = self._figsize[1] * num_rows
        figwidth  = self._figsize[0]
        plot_panel.set_minsize(figwidth, figheight)
        self._trial_renamed(trial_id=trial_id)

        # set up feature axes and pca axes
        figure = plot_panel.figure
        plot_panel.axes['feature'] = figure.add_subplot(num_rows, 1, 1)
        plot_panel.axes['pca'] = []
        for i in xrange(3):
            axes = figure.add_subplot(num_rows, 3, i+4)
            plot_panel.axes['pca'].append(axes)

        canvas_size = plot_panel.GetMinSize()
        # adjust subplots to spikepy uniform standard
        config.default_adjust_subplots(figure, canvas_size)

        # tweek psd axes and trace axes
        top = -config['gui']['plotting']['spacing']['title_vspace']
        bottom = config['gui']['plotting']['spacing']['axes_bottom']
        utils.adjust_axes_edges(plot_panel.axes['feature'], canvas_size,
                                bottom=bottom, top=top)

        left = config['gui']['plotting']['spacing']['axes_left']
        outter = (2.0*left)/3.0
        inner = left/3.0
        pca_axes = plot_panel.axes['pca']
        utils.adjust_axes_edges(pca_axes[0], canvas_size, right=outter)
        utils.adjust_axes_edges(pca_axes[1], canvas_size, right=inner, 
                                                          left=inner)
        utils.adjust_axes_edges(pca_axes[2], canvas_size, left=outter)

        # label axes
        plot_panel.axes['feature'].set_xlabel(pt.FEATURE_INDEX)
        plot_panel.axes['feature'].set_ylabel(pt.FEATURE_AMPLITUDE)

        self.pc_y = [2,3,3] # which pc is associated with what axis.
        self.pc_x = [1,1,2]
        self.pca_colors = ['r', 'g', 'b']
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
        utils.clear_axes(plot_panel.axes['feature'])
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
                                          marker='.')
            utils.set_axes_ticker(axes, nbins=4, axis='xaxis', prune=None)
            utils.set_axes_ticker(axes, axis='yaxis')

        # plot the features
        pc = config['gui']['plotting']['extraction']
        trial = self._trials[trial_id]
        features = trial.extraction.results['features']
        feature_axes = plot_panel.axes['feature']

        for feature in features:
            feature_axes.plot(feature, 
                              linewidth=pc['feature_trace_linewidth'],
                              color=pc['feature_trace_color'], 
                              alpha=pc['feature_trace_alpha'])
        utils.set_axes_ticker(feature_axes, axis='yaxis')
        feature_axes.set_xlim((0,len(features[0])-1))

