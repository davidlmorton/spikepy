from collections import defaultdict

import numpy

from .window_spikes import window_spikes

def run(trace_list, sampling_freq=None,
                    spike_list=None,
                    pre_padding=None,
                    post_padding=None,
                    exclude_overlappers=None):
    if (sampling_freq       is None or
        spike_list          is None or
        pre_padding         is None or
        post_padding        is None or
        exclude_overlappers is None):
        raise RuntimeError(
            'Keyword arguments to run() are not optional.')

    else:
        pre_padding_percent = pre_padding/float(pre_padding+post_padding)
        # from sampling frequency (in Hz) and pre/post_padding (in ms) determine
        #     window_size (in samples)
        window_duration = (pre_padding + post_padding) / 1000.0 # now in secs
        # +1 to account for the sample itself.
        window_size = int(window_duration * sampling_freq) + 1 

        waveforms          = defaultdict(list)
        excluded_waveforms = defaultdict(list)
        print pre_padding_percent, window_duration, window_size
        for trace in trace_list:
            results = window_spikes(trace, spike_list,
                    window_size=window_size,
                    pre_padding=pre_padding_percent,
                    exclude_overlappers=exclude_overlappers)
            spike_windows    = results[0]
            spike_indexes    = results[1]
            excluded_windows = results[2]
            excluded_indexes = results[3]
            print spike_windows
            print spike_indexes
            print excluded_windows
            print excluded_indexes

            # collect waveforms from (potentially) multiple traces.
            for si, sw in zip(spike_indexes, spike_windows):
                waveforms[si].append(
                        numpy.array(sw, dtype=numpy.float64))
            for ei, ew in zip(excluded_indexes, excluded_windows):
                excluded_waveforms[ei].append(
                        numpy.array(ew, dtype=numpy.float64))
        # concatenate collected waveforms from the same spike.
        for key in waveforms.keys():
            waveforms[key] = numpy.hstack(waveforms[key])
        for key in excluded_waveforms.keys():
            excluded_waveforms[key] = numpy.hstack(excluded_waveforms[key])
             
        return {'features':waveforms, 'excluded_features':excluded_waveforms}
