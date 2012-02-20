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

from spikepy.developer.visualization import Visualization
from spikepy.plotting_utils.general import as_fraction 
from spikepy.common.valid_types import ValidFloat, ValidBoolean, ValidOption,\
        ValidInteger

background = {True:'black', False:'white'}
foreground = {True:'white', False:'black'}
line_color = {True:'yellow', False:'green'}
cluster_colors = {True:['cyan', 'magenta', 'yellow', 'blue', 'red', 'green',
        'orange', 'white'],
        False:['blue', 'red', 'green', 'cyan', 'magenta', 'orange',
        'black', 'purple']}

class FeaturesVisualization(Visualization):
    name = 'Features'
    requires = ['features']
    found_under_tab = 'extraction'

    invert_colors = ValidBoolean(default=False)
    line_width = ValidInteger(min=0, default=1)
    max_drawn = ValidInteger(min=1, default=250,
        description='Maximum number of features drawn, to speed up plotting')
    opacity = ValidFloat(min=0.0, max=1.0, default=0.25)
    point_size = ValidInteger(min=0, default=2)

    def _plot(self, trial, figure, invert_colors=False, line_width=1, 
            max_drawn=250, opacity=0.25, point_size=2):
        features = trial.features.data

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
                bottom=as_frac(y=40), 
                top=1.0-as_frac(y=25))

        axes = figure.add_subplot(111)

        
        for feature in features[:max_drawn]:
            if point_size > 0:
                marker = 'o'
            else:
                marker = ''
            axes.plot(feature, color=line_color[invert_colors],
                alpha=opacity, 
                linewidth=line_width, 
                marker=marker,
                markeredgecolor=line_color[invert_colors],
                markerfacecolor=foreground[invert_colors],
                markersize=point_size)

        axes.text(0.98, 0.95, '%d drawn' % min(max_drawn, len(features)), 
                color=foreground[invert_colors],
                horizontalalignment='right', 
                verticalalignment='center', 
                transform=axes.transAxes)

        axes.set_ylabel('Feature Amplitude', color=foreground[invert_colors])
        axes.set_xlabel('Feature Index (found features for %d events)' % len(features), 
                color=foreground[invert_colors])

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

class ClusteredFeaturesVisualization(Visualization):
    name = 'Clustered Features'
    requires = ['clusters']
    found_under_tab = 'clustering'

    invert_colors = ValidBoolean(default=True)
    line_width = ValidInteger(min=0, default=1)
    max_drawn = ValidInteger(min=1, default=250,
        description='Maximum number of features drawn (per cluster), to speed up plotting')
    opacity = ValidFloat(min=0.0, max=1.0, default=0.25)
    point_size = ValidInteger(min=0, default=2)
    legend = ValidBoolean(default=False, 
            description='Display a legend showing the number of features in each cluster and the cluster names.')

    def _plot(self, trial, figure, invert_colors=False, line_width=1, 
            max_drawn=250, opacity=0.25, point_size=2, legend=False):
        features = trial.features.data

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
                bottom=as_frac(y=40), 
                top=1.0-as_frac(y=25))

        axes = figure.add_subplot(111)

        cfs = trial.clustered_features
        for i, cluster_name in enumerate(sorted(cfs.keys())):
            features = cfs[cluster_name]
            num_drawn = min(max_drawn, len(features))
            color=cluster_colors[invert_colors][
                    i%len(cluster_colors[invert_colors])]
            for j, feature in enumerate(features[:max_drawn]):
                if point_size > 0:
                    marker = 'o'
                else:
                    marker = ''
                if j == 0:
                    label = '%s: %d of %d drawn' % (cluster_name, 
                            num_drawn, len(features))
                    alpha = 1.0
                else:
                    label = None
                    alpha = opacity

                axes.plot(feature, 
                    color=color,
                    alpha=alpha, 
                    linewidth=line_width, 
                    marker=marker,
                    markeredgecolor=foreground[invert_colors],
                    markerfacecolor=color,
                    markersize=point_size,
                    label=label)

        axes.set_ylabel('Feature Amplitude', color=foreground[invert_colors])
        axes.set_xlabel('Feature Index', 
                color=foreground[invert_colors])

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

        # setup legend
        if legend:
            l = axes.legend(loc='upper right')
            frame = l.get_frame()
            frame.set_facecolor(background[invert_colors])
            frame.set_edgecolor(foreground[invert_colors])
            for text in l.texts:
                text.set_color(foreground[invert_colors])



