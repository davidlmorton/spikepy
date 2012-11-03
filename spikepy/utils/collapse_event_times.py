
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
            else:
                break
        return numpy.array(collapsed_event_times, dtype=numpy.float64)
            

