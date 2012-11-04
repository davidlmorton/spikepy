#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy

from spikepy.developer.visualization import Visualization
from spikepy.plotting_utils.general import create_times_array, as_fraction 
from spikepy.plotting_utils.make_into_publication_axes import \
        make_into_publication_axes, update_scalebars 
from spikepy.common.valid_types import ValidFloat, ValidBoolean

background = {True:'black', False:'white'}
foreground = {True:'white', False:'black'}
colors = {True:['cyan', 'magenta', 'yellow'],
          False:['red', 'green', 'blue']}

class DetectionTraceVisualization(Visualization):
    name = 'Detection Filtered Data Trace(s)'
    requires = ['pf_traces', 'pf_sampling_freq']
    found_under_tab = 'detection_filter'
    channel_separation_std = ValidFloat(0.1, 100.0, default=8.0,
            description='How far apart the channels are plotted (as a multiple of the standard deviation of the signal).')
    invert_colors = ValidBoolean(default=False)

    def _get_auxiliary_results(self, trial):
        return trial.df_traces.data, trial.df_sampling_freq.data

    def _plot(self, trial, figure, channel_separation_std=8.0, 
            invert_colors=False):
        pf_traces = getattr(trial, self.requires[0]).data
        pf_sf = getattr(trial, self.requires[1]).data

        f_traces, f_sf = self._get_auxiliary_results(trial)
        have_filtered_results = (f_traces is not None)

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

        pf_times = create_times_array(pf_traces, pf_sf)
        if have_filtered_results:
            f_times = create_times_array(f_traces, f_sf)
            channel_separation = (numpy.std(pf_traces[0]) + 
                    numpy.std(f_traces[0]))*(channel_separation_std/2.0)
        else:
            channel_separation = (numpy.std(pf_traces[0]))*channel_separation_std

        axes = figure.add_subplot(111)
        axes.set_axis_bgcolor(background[invert_colors])
        make_into_publication_axes(axes, base_unit_prefix=('', 'm'), 
                scale_bar_origin_frac=as_frac(-25, -5),
                target_size_frac=as_frac(150, 80),
                y_label_rotation='vertical',
                color=foreground[invert_colors])
        axes.lock_axes()

        offsets = []
        y_mins = []
        y_maxs = []
        for i, pf_trace in enumerate(pf_traces):
            offset = -i*channel_separation
            offsets.append(offset)
            y_values = pf_trace+offset
            y_mins.append(numpy.min(y_values))
            y_maxs.append(numpy.max(y_values))
            axes.signal_plot(pf_times, pf_trace+offset, 
                    color=foreground[invert_colors],
                    alpha=0.5,
                    label='Pre-Filtered')

        if have_filtered_results:
            for i, f_trace in enumerate(f_traces):
                color = colors[invert_colors][i%len(colors[invert_colors])]
                offset = offsets[i]
                y_values = f_trace+offset
                y_mins.append(numpy.min(y_values))
                y_maxs.append(numpy.max(y_values))
                axes.signal_plot(f_times, y_values, color=color, 
                        label='Filtered')

        axes.set_ylabel('Channel', color=foreground[invert_colors])
        axes.set_yticks(offsets)
        axes.set_yticklabels([str((i+1)) for i in range(len(offsets))],
                color=foreground[invert_colors])

        y_min = min(y_mins)
        y_max = max(y_maxs)
        y_range = y_max - y_min

        axes.unlock_axes()
        axes.set_xlim(pf_times[0], pf_times[-1])
        axes.set_ylim((y_min - 0.03*y_range, y_max + 0.20*y_range))


class ExtractionTraceVisualization(DetectionTraceVisualization):
    name = 'Extraction Filtered Data Trace(s)'
    requires = ['pf_traces', 'pf_sampling_freq']
    found_under_tab = 'extraction_filter'

    def _get_auxiliary_results(self, trial):
        return trial.ef_traces.data, trial.ef_sampling_freq.data


