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

def collapse_event_times(event_times, 
        min_num_channels, peak_drift):
    assert peak_drift >= 0.0
    all_times = numpy.hstack(event_times)
    channels = numpy.hstack([[i for d in event_times[i]] 
            for i in range(len(event_times))])
    sorted_indexes = all_times.argsort()
    sorted_times = all_times[sorted_indexes]
    if len(event_times) < min_num_channels:
        return sorted_times
    else:
        if min_num_channels == 1:
            return sorted_times
        # Think of a worm moving through the times, if it can stretch to
        # cover <min_num_channels> then we have a single event across multiple
        # channels.  The event time will be the event_time of the 
        # lowest numbered channel that participated in the event.
        h = 0 # head
        t = 0 # tail
        collapsed_event_times = []
        while h < len(sorted_times):
            # stretch head up as far as can go.
            while h+1 < len(sorted_times) and \
                    sorted_times[h+1] - sorted_times[t] < peak_drift:
                h += 1

            # detect event
            if ((h - t) + 1 >= min_num_channels and
                    len(set(channels[sorted_indexes][t:h+1])) >= 
                    min_num_channels):
                event_time = all_times[min(sorted_indexes[t:h+1])]
                collapsed_event_times.append(event_time)
                h += 1
                t = h
            elif h+1 < len(sorted_times):
                h += 1
                # possibly move up t
                while sorted_times[h] - sorted_times[t] > peak_drift:
                    t += 1
        return numpy.array(collapsed_event_times, dtype=numpy.float64)
            

