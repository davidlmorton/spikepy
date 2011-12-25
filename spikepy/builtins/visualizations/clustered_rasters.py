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
from spikepy.plotting_utils.general import create_times_array, as_fraction 
from spikepy.plotting_utils.make_into_publication_axes import \
        make_into_publication_axes, update_scalebars 
from spikepy.common.valid_types import ValidFloat, ValidBoolean, ValidOption,\
        ValidInteger
from spikepy.plotting_utils.make_into_raster_axes import make_into_raster_axes

background = {True:'black', False:'white'}
foreground = {True:'white', False:'black'}
cluster_colors = {True:['cyan', 'magenta', 'yellow', 'blue', 'red', 'green',
        'orange', 'white'],
        False:['blue', 'red', 'green', 'cyan', 'majenta', 'orange',
        'black', 'purple']}

class ClusteredEventRasterVisualization(Visualization):
    name = 'Clustered Event Raster(s)'
    requires = ['clusters']
    found_under_tab = 'clustering'
    channel_separation_std = ValidFloat(0.1, 100.0, default=8.0,
            description='How far apart the channels are plotted (as a multiple of the standard deviation of the signal).')
    invert_colors = ValidBoolean(default=True)
    raster_size = ValidInteger(1, 1000, default=20, 
            description='Size of raster tick marks in pixels.')
    trace_opacity = ValidFloat(0.0, 1.0, default=0.25, 
            description='How darkly the traces are plotted.')
    traces_shown = ValidOption('Unfiltered', 'Detection Filtered', 
            'Extraction Filtered', 'None', default='Extraction Filtered',
            description='Which traces are drawn in the background.')

    def _plot(self, trial, figure, channel_separation_std=8.0, 
            invert_colors=False, 
            raster_size=20,
            trace_opacity=0.25,
            traces_shown='Extraction Filtered'):

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
                bottom=as_frac(y=30), 
                top=1.0-as_frac(y=10))

        if traces_shown != 'None':
            tn = {
                    'Detection Filtered':('df_traces', 'df_sampling_freq'),
                    'Extraction Filtered':('ef_traces', 'ef_sampling_freq'),
                    'Unfiltered':('pf_traces', 'pf_sampling_freq')}
            # check to see if we can proceed.
            missing_requirements = []
            for attr in tn[traces_shown]:
                if not (hasattr(trial, attr) and 
                    getattr(trial, attr).data is not None):
                    missing_requirements.append(attr)

            if missing_requirements:
                figure.text(0.5, 0.5, 'This visualization cannot be completed due to unmet requirements:\n\n%s' % '\n'.join(missing_requirements))
                return
            else:
                traces = getattr(trial, tn[traces_shown][0]).data
                sf = getattr(trial, tn[traces_shown][1]).data

            axes = figure.add_subplot(111)
            axes.set_axis_bgcolor(background[invert_colors])
            make_into_publication_axes(axes, base_unit_prefix=('', 'm'), 
                    scale_bar_origin_frac=as_frac(-25, -5),
                    target_size_frac=as_frac(150, 80),
                    y_label_rotation='vertical',
                    color=foreground[invert_colors])
            axes.lock_axes()

            # plot traces
            offsets = []
            y_mins = []
            y_maxs = []
            times = create_times_array(traces, sf)
            channel_separation = numpy.std(traces[0]) * channel_separation_std
            for i, trace in enumerate(traces):
                offset = -i*channel_separation
                offsets.append(offset)
                y_values = trace+offset
                y_mins.append(numpy.min(y_values))
                y_maxs.append(numpy.max(y_values))
                axes.signal_plot(times, y_values, 
                        color=foreground[invert_colors],
                        alpha=trace_opacity)

            axes.set_ylabel('Channel', color=foreground[invert_colors])
            axes.set_yticks(offsets)
            axes.set_yticklabels([str((i+1)) for i in range(len(offsets))],
                    color=foreground[invert_colors])

            axes.unlock_axes()

            y_min = min(y_mins)
            y_max = max(y_maxs)
            y_range = y_max - y_min

            axes.set_xlim(times[0], times[-1])
            axes.set_ylim((y_min - 0.03*y_range, y_max + 0.20*y_range))
            axes.get_yaxis().set_ticks_position('left')

        # plot rasters
        if traces_shown != 'None':
            ra = figure.add_axes(axes.get_position(), frameon=False)
            xlims = (times[0], times[-1])
        else:
            ra = figure.add_subplot(111, frameon=False)
            xlims = None
        ra.text(1+as_frac(28), 0.5, 'Cluster', 
                color=foreground[invert_colors],
                clip_on=False,
                verticalalignment='center',
                horizontalalignment='center',
                rotation='vertical',
                transform=ra.transAxes)

        ymin, ymax = (0.0, 1.0)
        yrange = ymax - ymin
        cft = trial.clustered_feature_times
        minx = 1e30
        maxx = -1e30
        poss = []
        for i, cluster_name in enumerate(sorted(cft.keys())):
            color = cluster_colors[invert_colors][
                    i%len(cluster_colors[invert_colors])]
            e_xs = cft[cluster_name]
            pos = ymax - i/float(len(cft.keys())-1)*yrange
            poss.append(pos)
            if len(e_xs) > 0:
                minx = min(minx, min(e_xs))
                maxx = max(maxx, max(e_xs))
                ra.plot(numpy.array(e_xs), 
                        numpy.ones(len(e_xs))*pos,
                        linewidth=0, 
                        marker='|', 
                        markersize=raster_size, 
                        color=color,
                        markeredgewidth=2)

        if xlims is not None:
            ra.set_xlim(xlims)
        ra.set_ylim(ymin-0.1*yrange, ymax+0.1*yrange)

        ra.get_yaxis().set_ticks_position('right')
        ra.set_yticks(poss)
        ra.set_yticklabels(sorted(cft.keys()))
        ra.set_xticks([])
        ra.set_xticklabels([''], visible=False)
        make_into_raster_axes(ra)

        # fix colors
        lines = ra.get_xticklines()
        lines.extend(axes.get_yticklines())
        for line in lines:
            line.set_color(foreground[invert_colors])
        labels = ra.get_xticklabels()
        labels.extend(ra.get_yticklabels())
        for label in labels:
            label.set_color(foreground[invert_colors])

