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
from spikepy.plotting_utils.general import create_times_array  
from spikepy.plotting_utils.make_into_publication_axes import \
        make_into_publication_axes, update_scalebars 

class DetectionTraceVisualization(Visualization):
    name = 'Detection Filtered Data Trace(s)'
    requires = ['pf_traces', 'pf_sampling_freq', 
            'df_traces', 'df_sampling_freq']
    found_under_tab = 'detection_filtering'

    def plot(self, trial, figure, **kwargs):
        pf_traces = getattr(trial, self.requires[0]).data
        pf_sf = getattr(trial, self.requires[1]).data

        f_traces = getattr(trial, self.requires[2]).data
        f_sf = getattr(trial, self.requires[3]).data
        have_filtered_results = (f_traces is not None)

        figure.set_facecolor('black')
        figure.set_edgecolor('white')

        pf_times = create_times_array(pf_traces, pf_sf)
        if have_filtered_results:
            f_times = create_times_array(f_traces, f_sf)
            channel_separation = (numpy.std(pf_traces) + 
                    numpy.std(f_traces))*3.0
        else:
            channel_separation = (numpy.std(pf_traces))*6.0

        axes = figure.add_subplot(111)
        axes.set_axis_bgcolor('black')
        make_into_publication_axes(axes, base_unit_prefix=('', 'm'), 
                color='white')

        offsets = []
        y_mins = []
        y_maxs = []
        for i, pf_trace in enumerate(pf_traces):
            offset = -i*channel_separation
            offsets.append(offset)
            y_values = pf_trace+offset
            y_mins.append(numpy.min(y_values))
            y_maxs.append(numpy.max(y_values))
            axes.signal_plot(pf_times, pf_trace+offset, color='white',
                    label='Pre-Filtered')

        if have_filtered_results:
            colors = ['blue', 'green', 'red']
            for i, f_trace in enumerate(f_traces):
                color = colors[i%len(colors)]
                offset = offsets[i]
                y_values = f_trace+offset
                y_mins.append(numpy.min(y_values))
                y_maxs.append(numpy.max(y_values))
                axes.signal_plot(f_times, y_values, color=color, 
                        label='Filtered')

        y_min = min(y_mins)
        y_max = max(y_maxs)
        y_range = y_max - y_min

        axes.set_xlim(pf_times[0], pf_times[-1])
        axes.set_ylim((y_min - 0.03*y_range, y_max + 0.20*y_range))

            
            

        

