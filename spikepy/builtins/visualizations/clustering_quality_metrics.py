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
from spikepy.plotting_utils.general import create_times_array, as_fraction 
from spikepy.common.valid_types import ValidBoolean, ValidOption, ValidInteger,\
        ValidFloat
from spikepy.common.config_manager import config_manager as config

background = {True:'black', False:'white'}
foreground = {True:'white', False:'black'}
cluster_colors = {True:['cyan', 'magenta', 'yellow', 'blue', 'red', 'green',
        'orange', 'white'],
        False:['blue', 'red', 'green', 'cyan', 'magenta', 'orange',
        'black', 'purple']}

def percent_max(array, percent):
    return array[numpy.argsort(array)[int(len(array)*(percent/100.0))]]

class ClusterQualityMetricsVisualization(Visualization):
    name = 'Cluster Quality Metrics(s)'
    requires = ['cluster_quality_metrics']
    found_under_tab = 'clustering'

    invert_colors = ValidBoolean(default=True)
    number_of_bins = ValidInteger(min=4, default=25)
    other_clusters = ValidOption('Stacked', 'Flat', default='Stacked')
    alpha = ValidFloat(min=0.0, max=1.0, default=0.85)
    style = ValidOption('Bars', 'Lines', default='Bars')

    def _get_figure_size(self, trial):
        cqm = trial.cluster_quality_metrics.data 
        num_clusters = len(cqm.keys())
        num_rows = (num_clusters+1)/2
        
        width = config['gui']['plotting']['plot_width_inches']
        height = config['gui']['plotting']['plot_height_inches']*num_rows
        size = numpy.array([width, height])
        return size

    def _plot(self, trial, figure, invert_colors=False, 
            number_of_bins=25,
            other_clusters='Stacked',
            alpha=0.85,
            style='Bars'):

        cqm = trial.cluster_quality_metrics.data 
        num_clusters = len(cqm.keys())
        num_rows = (num_clusters+1)/2

        def as_frac(x=None, y=None):
            f = figure
            canvas_size_in_pixels = (f.get_figwidth()*f.get_dpi(),
                                    f.get_figheight()*f.get_dpi())
            return as_fraction(x=x, y=y, 
                    canvas_size_in_pixels=canvas_size_in_pixels)

        figure.set_facecolor(background[invert_colors])
        figure.set_edgecolor(foreground[invert_colors])
        figure.subplots_adjust(left=as_frac(x=75), 
                right=1.0-as_frac(x=40), 
                bottom=as_frac(y=45), 
                top=1.0-as_frac(y=10),
                hspace=0.25)
        
        # create axes
        axes = {}
        ranges = {}
        count = 0
        for i in [k for k in cqm.keys() if k != 'Rejected']:
            axes[i] = figure.add_subplot(num_rows, 2, count+1)
            axes[i].set_axis_bgcolor(background[invert_colors])

            ranges[i] = {'min':0.0, 
                    'max':percent_max(
                    cqm[i]['mahalanobis_distances_squared'][0], 97)}
            for j in range(num_clusters):
                ranges[i]['min'] = min(ranges[i]['min'], 
                        min(cqm[i]['mahalanobis_distances_squared'][j]))
                ranges[i]['max'] = max(ranges[i]['max'], 
                        percent_max(
                        cqm[i]['mahalanobis_distances_squared'][j], 97))
            axes[i].set_xlabel(r'$D^2$ from Cluster ' + str(i), 
                    color=foreground[invert_colors])
            if count == 0:
                axes[i].set_ylabel('Number of Spikes', 
                        color=foreground[invert_colors])
            count += 1

            # axes color fixing
            frame = axes[i].patch
            frame.set_facecolor(background[invert_colors])
            frame.set_edgecolor(foreground[invert_colors])
            for spine in axes[i].spines.values():
                spine.set_color(foreground[invert_colors])
            lines = axes[i].get_xticklines()
            lines.extend(axes[i].get_yticklines())
            for line in lines:
                line.set_color(foreground[invert_colors])
            labels = axes[i].get_xticklabels()
            labels.extend(axes[i].get_yticklabels())
            for label in labels:
                label.set_color(foreground[invert_colors])
            axes[i].text(0.5, 0.98, 
r'''$L_{ratio}$=%2.2e  $L_{value}$=%2.2e 
Isolation Distance=%2.4f'''%
                    (cqm[i]['l_ratio'], cqm[i]['l_value'], 
                    cqm[i]['isolation_distance']),
                    horizontalalignment='center',
                    verticalalignment='top',
                    multialignment='center',
                    transform=axes[i].transAxes,
                    color=foreground[invert_colors])

        # plot histograms
        for i in axes.keys():
            ax = axes[i]
            rng = ranges[i]
            bottoms = numpy.zeros(number_of_bins, dtype=numpy.int32)
            for e, j in enumerate(sorted(axes.keys())):
                counts, bins = numpy.histogram(
                        cqm[i]['mahalanobis_distances_squared'][j],
                        bins=number_of_bins,
                        range=(rng['min'], rng['max']))
                width = bins[1]-bins[0]
                color = cluster_colors[invert_colors][
                        e%len(cluster_colors[invert_colors])]

                if style == 'Bars':
                    bottom = 0.0
                    if other_clusters == 'Stacked':
                        if i == j:
                            bottom = 0.0
                        else:
                            bottom = bottoms
                    ax.bar(bins[:-1], counts, width=width,
                            color=color, 
                            bottom=bottom,
                            alpha=alpha,
                            edgecolor=foreground[invert_colors])
                        
                elif style == 'Lines':
                    bin_centers = bins[:-1] + width/2.0
                    if i == j:
                        ax.fill_between(bin_centers, counts, color=color,
                                alpha=alpha)
                    else:
                        if other_clusters == 'Stacked':
                            ax.fill_between(bin_centers, bottoms, 
                                    y2=counts+bottoms, 
                                    color=color,
                                    alpha=alpha)
                        elif other_clusters == 'Flat':
                            ax.fill_between(bin_centers, counts, 
                                    color=color, alpha=alpha)

                if i != j:
                    bottoms += counts


            


            

            
