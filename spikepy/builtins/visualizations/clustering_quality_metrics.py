
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
    if percent == 100.0:
        return max(array)
    else:
        return array[numpy.argsort(array)[int((len(array)-1)*(percent/100.0))]]

class ClusterQualityMetricsVisualization(Visualization):
    name = 'Cluster Quality Metrics(s)'
    requires = ['cluster_quality_metrics']
    found_under_tab = 'clustering'

    invert_colors = ValidBoolean(default=True)
    number_of_bins = ValidInteger(min=4, default=70)
    other_clusters = ValidOption('Stacked', 'Flat', default='Stacked')
    alpha = ValidFloat(min=0.0, max=1.0, default=0.85)
    range_percentage = ValidFloat(min=1.0, max=100.0,
            description='Use to eliminate outliers (0-100)', default=95)
    style = ValidOption('Bars', 'Lines', default='Lines')

    def _get_figure_size(self, trial):
        cqm = trial.cluster_quality_metrics.data 
        num_clusters = len(cqm.keys())
        num_rows = (num_clusters+1)/2
        
        width = config['gui']['plotting']['plot_width_inches']
        height = config['gui']['plotting']['plot_height_inches']*num_rows
        size = numpy.array([width, height])
        return size

    def _plot(self, trial, figure, invert_colors=False, 
            number_of_bins=70,
            other_clusters='Stacked',
            alpha=0.85,
            range_percentage=95,
            style='Lines'):

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
                    cqm[i]['mahalanobis_distances_squared'][0], 
                    range_percentage)}
            for j in range(num_clusters):
                ranges[i]['min'] = min(ranges[i]['min'], 
                        min(cqm[i]['mahalanobis_distances_squared'][j]))
                ranges[i]['max'] = max(ranges[i]['max'], 
                        percent_max(
                        cqm[i]['mahalanobis_distances_squared'][j],
                        range_percentage))
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

            color = get_color(i, cqm, invert_colors)
            plot_to_axes(cqm, i, i, style, 1.0, color, number_of_bins, rng, ax)
            for j in [k for k in axes.keys() if k != i]:
                color = get_color(j, cqm, invert_colors)
                counts = plot_to_axes(cqm, i, j, style, alpha, color, 
                        number_of_bins, rng, ax, bottoms=bottoms)
                if other_clusters == 'Stacked':
                    bottoms += counts

def get_color(i, cqm, invert_colors):
    j = i
    sorted_cluster_ids = sorted(cqm.keys())
    e = sorted_cluster_ids.index(j)
    color = cluster_colors[invert_colors][
            e%len(cluster_colors[invert_colors])]
    return color

def plot_to_axes(cqm, i, j, style, alpha, color, number_of_bins, rng, axes, 
        bottoms=0.0):
    counts, bins = numpy.histogram(
            cqm[i]['mahalanobis_distances_squared'][j],
            bins=number_of_bins,
            range=(rng['min'], rng['max']))
    width = bins[1]-bins[0]

    if style == 'Bars':
        axes.bar(bins[:-1], counts, width=width,
                color=color, 
                bottom=bottoms,
                alpha=alpha)
                
    elif style == 'Lines':
        bin_centers = bins[:-1] + width/2.0
        axes.fill_between(bin_centers, bottoms, 
                y2=counts+bottoms, 
                color=color,
                alpha=alpha)
    return counts
    


            


            

            
