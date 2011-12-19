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
from spikepy.plotting_utils.general import as_fraction 
from spikepy.utils.collapse_event_times import collapse_event_times 
from spikepy.common.valid_types import ValidFloat, ValidBoolean, ValidOption,\
        ValidInteger

background = {True:'black', False:'white'}
foreground = {True:'white', False:'black'}
face_color = {True:'cyan', False:'blue'}

class ISIsVisualization(Visualization):
    name = 'Interspike Interval Histogram'
    requires = ['event_times']
    found_under_tab = 'detection'

    invert_colors = ValidBoolean(default=False)
    large_bin_size = ValidFloat(min=0.1, default=50)
    small_bin_size = ValidFloat(min=0.01, default=1)
    min_num_channels = ValidInteger(min=1, default=3, 
            description='To be considered an event, spikes must be found within "Peak Drift" ms of one another on this many channels.')
    peak_drift = ValidFloat(min=0.0, default=0.3, 
            description='(in ms) Spike peaks across different channels may be identified as originating from a single spike if they are closer in time than this amount.')

    def _plot(self, trial, figure, invert_colors=False, large_bin_size=50, 
            small_bin_size=1, min_num_channels=3, peak_drift=0.3):
        bounds1 = (0.0, 3000.0) # 0 to 3 seconds
        bounds2 = (0.0, 20.0) # first 20 ms

        event_times = trial.event_times.data
        collapsed_event_times = collapse_event_times(event_times, 
                min_num_channels, peak_drift)

        isis = collapsed_event_times[1:] - collapsed_event_times[:-1]
        isis *= 1000.0 # to get it to ms

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
                top=1.0-as_frac(y=25),
                wspace=as_frac(x=80))

        a1 = figure.add_subplot(121)
        a2 = figure.add_subplot(122)

        a1.hist(isis, bins=int((bounds1[1]-bounds1[0])/large_bin_size),
                range=bounds1, fc=face_color[invert_colors], 
                ec=background[invert_colors])

        a2.hist(isis, bins=int((bounds2[1]-bounds2[0])/small_bin_size),
                range=bounds2, fc=face_color[invert_colors], 
                ec=background[invert_colors])

        a1.text(0.98, 0.95, '%d Spike Events Found' 
                % len(collapsed_event_times), 
                color=foreground[invert_colors],
                horizontalalignment='right', 
                verticalalignment='center', 
                transform=a1.transAxes)

        a1.set_ylabel('Count', color=foreground[invert_colors])
        a1.set_xlabel('Interspike Interval (ms)', 
                color=foreground[invert_colors])
        a2.set_xlabel('Interspike Interval (ms)', 
                color=foreground[invert_colors])

        # axes color fixing
        for axes in [a1, a2]:
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

