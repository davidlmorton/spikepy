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

background = {True:'black', False:'white'}
foreground = {True:'white', False:'black'}
colors = {True:['cyan', 'magenta', 'yellow'],
          False:['red', 'green', 'blue']}

class RasterVisualization(Visualization):
    name = 'Event Raster(s)'
    requires = ['df_traces', 'df_sampling_freq']
    found_under_tab = 'detection'
    channel_separation_std = ValidFloat(0.1, 100.0, default=8.0,
            description='How far apart the channels are plotted (as a multiple of the standard deviation of the signal).')
    invert_colors = ValidBoolean(default=False)
    raster_position = ValidOption('peak', 'center', default='center')
    raster_size = ValidInteger(1, 1000, default=20, 
            description='Size of raster tick marks in pixels.')
    trace_opacity = ValidFloat(0.0, 1.0, default=0.25, 
            description='How darkly the traces are plotted.')

    def _plot(self, trial, figure, channel_separation_std=8.0, 
            invert_colors=False, 
            raster_position='center', 
            raster_size=20,
            trace_opacity=0.25):
        f_traces = trial.df_traces.data
        f_sf = trial.df_sampling_freq.data
        f_times = create_times_array(f_traces, f_sf)

        if hasattr(trial, 'event_times'):
            event_times = trial.event_times.data
        else:
            event_times = None
        have_event_times = (event_times is not None)

        def as_frac(x=None, y=None):
            f = figure
            canvas_size_in_pixels = (f.get_figwidth()*f.get_dpi(),
                                    f.get_figheight()*f.get_dpi())
            return as_fraction(x=x, y=y, 
                    canvas_size_in_pixels=canvas_size_in_pixels)

        figure.set_facecolor(background[invert_colors])
        figure.set_edgecolor(foreground[invert_colors])
        figure.subplots_adjust(left=as_frac(x=75), 
                right=1.0-as_frac(x=10), 
                bottom=as_frac(y=30), 
                top=1.0-as_frac(y=10))

        channel_separation = numpy.std(f_traces) * channel_separation_std

        axes = figure.add_subplot(111)
        axes.set_axis_bgcolor(background[invert_colors])
        make_into_publication_axes(axes, base_unit_prefix=('', 'm'), 
                scale_bar_origin_frac=as_frac(-25, -5),
                target_size_frac=as_frac(150, 80),
                y_label_rotation='vertical',
                color=foreground[invert_colors])

        # plot traces
        offsets = []
        y_mins = []
        y_maxs = []
        for i, f_trace in enumerate(f_traces):
            offset = -i*channel_separation
            offsets.append(offset)
            y_values = f_trace+offset
            y_mins.append(numpy.min(y_values))
            y_maxs.append(numpy.max(y_values))
            axes.signal_plot(f_times, y_values, color=foreground[invert_colors],
                    alpha=trace_opacity)

        axes.set_ylabel('Channel', color=foreground[invert_colors])
        axes.set_yticks(offsets)
        axes.set_yticklabels([str((i+1)) for i in range(len(offsets))],
                color=foreground[invert_colors])

        y_min = min(y_mins)
        y_max = max(y_maxs)
        y_range = y_max - y_min

        if have_event_times:
            for i, event_sequence in enumerate(event_times):
                color = colors[invert_colors][i%len(colors[invert_colors])]
                e_xs = event_sequence
                if raster_position == 'center':
                    e_ys = [offsets[i] for e in e_xs]
                else:
                    event_indexes = [f_sf * e for e in e_xs]
                    e_ys = [f_traces[i][ei]+offsets[i] for ei in event_indexes]

                axes.plot(e_xs, e_ys, linewidth=0, marker='|', 
                        markersize=raster_size, color=color,
                        markeredgewidth=3)

        axes.set_xlim(f_times[0], f_times[-1])
        axes.set_ylim((y_min - 0.03*y_range, y_max + 0.20*y_range))
