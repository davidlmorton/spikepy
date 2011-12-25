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
import numpy

from spikepy.developer_tools.visualization import Visualization
from spikepy.plotting_utils.general import as_fraction, set_axes_ticker 
from spikepy.utils.pca import pca
from spikepy.common.valid_types import ValidFloat, ValidBoolean, ValidOption,\
        ValidInteger

background = {True:'black', False:'white'}
foreground = {True:'white', False:'black'}
projection_color = {True:['cyan', 'magenta', 'yellow'], 
        False:['blue', 'red', 'green']}
cluster_colors = {True:['cyan', 'magenta', 'yellow', 'blue', 'red', 'green',
        'orange', 'white'],
        False:['blue', 'red', 'green', 'cyan', 'majenta', 'orange',
        'black', 'purple']}

class ClusteredFeaturePCAVisualization(Visualization):
    name = 'Principal Component Projections (clustered features)'
    requires = ['features', 'clusters']
    found_under_tab = 'clustering'

    invert_colors = ValidBoolean(default=True)
    dot_size = ValidInteger(min=1, default=3)

    def _plot(self, trial, figure, dot_size=3, invert_colors=False):
        features = trial.features.data
        if features.shape[1] < 3:
            msg = 'Features must have three or more dimensions for PCA Visualization.'
            figure.text(0.5, 0.5, msg, verticalalignment='center',
                    horizontalalignment='center')
            return

        rotated_features, pc_vectors, variances = pca(features)
        pct_var = [tvar/sum(variances)*100.0 for tvar in variances]
        trf = rotated_features.T

        def as_frac(x=None, y=None):
            f = figure
            canvas_size_in_pixels = (f.get_figwidth()*f.get_dpi(),
                                    f.get_figheight()*f.get_dpi())
            return as_fraction(x=x, y=y, 
                    canvas_size_in_pixels=canvas_size_in_pixels)

        figure.set_facecolor(background[invert_colors])
        figure.set_edgecolor(foreground[invert_colors])
        figure.subplots_adjust(left=as_frac(x=80), 
                right=1.0-as_frac(x=35), 
                bottom=as_frac(y=50), 
                wspace=as_frac(x=97)*3.0, # wspace is based on axes not figure
                top=1.0-as_frac(y=40))

        a1 = figure.add_subplot(131)
        a2 = figure.add_subplot(132)
        a3 = figure.add_subplot(133)
        pca_axes = [a1, a2, a3]

        PCA_LABEL = 'Principal Component %d (%3.1f%s)'
        pc_x = [2, 3, 3]
        pc_y = [1, 1, 2]

        # cluster the rotated features
        clustered_trf = []
        for i in [0, 1, 2]:
            clustered_trf.append(trial.cluster_data(trf[i]))

        for x, y, axes in zip(pc_x, pc_y, pca_axes):
            axes.set_xlabel(PCA_LABEL % (x, pct_var[x-1], '%'),
                            color=projection_color[invert_colors][x-1])
            axes.set_ylabel(PCA_LABEL % (y, pct_var[y-1], '%'),
                            color=projection_color[invert_colors][y-1])
            set_axes_ticker(axes, nbins=4, axis='xaxis', prune=None)
            set_axes_ticker(axes, axis='yaxis')
            for i, key in enumerate(sorted(clustered_trf[0].keys())):
                axes.plot(clustered_trf[x-1][key], 
                        clustered_trf[y-1][key], 
                        color=cluster_colors[invert_colors][
                                i%len(cluster_colors[invert_colors])], 
                        linewidth=0, 
                        marker='o', 
                        markersize=dot_size, 
                        markeredgewidth=0)
            
            # axes color fixing
            frame = axes.patch
            frame.set_facecolor(background[invert_colors])
            frame.set_edgecolor(foreground[invert_colors])
            for spine in axes.spines.values():
                spine.set_color(foreground[invert_colors])
            lines = axes.get_xticklines()
            lines.extend(axes.get_yticklines())
            for line in lines:
                line.set_color(foreground[invert_colors])
            labels = axes.get_xticklabels()
            labels.extend(axes.get_yticklabels())
            for label in labels:
                label.set_color(foreground[invert_colors])

class FeaturePCAVisualization(Visualization):
    name = 'Principal Component Projections (unclustered features)'
    requires = ['features']
    found_under_tab = 'extraction'

    invert_colors = ValidBoolean(default=False)
    dot_size = ValidInteger(min=1, default=3)

    def _plot(self, trial, figure, dot_size=3, invert_colors=False):
        features = trial.features.data
        if features.shape[1] < 3:
            msg = 'Features must have three or more dimensions for PCA Visualization.'
            figure.text(0.5, 0.5, msg, verticalalignment='center',
                    horizontalalignment='center')
            return

        rotated_features, pc_vectors, variances = pca(features)
        pct_var = [tvar/sum(variances)*100.0 for tvar in variances]
        trf = rotated_features.T

        def as_frac(x=None, y=None):
            f = figure
            canvas_size_in_pixels = (f.get_figwidth()*f.get_dpi(),
                                    f.get_figheight()*f.get_dpi())
            return as_fraction(x=x, y=y, 
                    canvas_size_in_pixels=canvas_size_in_pixels)

        figure.set_facecolor(background[invert_colors])
        figure.set_edgecolor(foreground[invert_colors])
        figure.subplots_adjust(left=as_frac(x=80), 
                right=1.0-as_frac(x=35), 
                bottom=as_frac(y=50), 
                wspace=as_frac(x=97)*3.0, # wspace is based on axes not figure
                top=1.0-as_frac(y=40))

        a1 = figure.add_subplot(131)
        a2 = figure.add_subplot(132)
        a3 = figure.add_subplot(133)
        pca_axes = [a1, a2, a3]

        PCA_LABEL = 'Principal Component %d (%3.1f%s)'
        pc_x = [2, 3, 3]
        pc_y = [1, 1, 2]
        for x, y, axes in zip(pc_x, pc_y, pca_axes):
            axes.set_xlabel(PCA_LABEL % (x, pct_var[x-1], '%'),
                            color=projection_color[invert_colors][x-1])
            axes.set_ylabel(PCA_LABEL % (y, pct_var[y-1], '%'),
                            color=projection_color[invert_colors][y-1])
            set_axes_ticker(axes, nbins=4, axis='xaxis', prune=None)
            set_axes_ticker(axes, axis='yaxis')
            axes.plot(trf[x-1], 
                    trf[y-1], 
                    color=foreground[invert_colors], 
                    linewidth=0, 
                    marker='o', 
                    markersize=dot_size, 
                    markeredgewidth=0)
            
            # axes color fixing
            frame = axes.patch
            frame.set_facecolor(background[invert_colors])
            frame.set_edgecolor(foreground[invert_colors])
            for spine in axes.spines.values():
                spine.set_color(foreground[invert_colors])
            lines = axes.get_xticklines()
            lines.extend(axes.get_yticklines())
            for line in lines:
                line.set_color(foreground[invert_colors])
            labels = axes.get_xticklabels()
            labels.extend(axes.get_yticklabels())
            for label in labels:
                label.set_color(foreground[invert_colors])


