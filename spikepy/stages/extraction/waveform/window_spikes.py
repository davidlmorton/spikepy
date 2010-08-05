import numpy

def window_spikes(signal, spike_index_list, window_size=40, 
                                            pre_padding=0.50, 
                                            exclude_overlappers=True):
    '''
    Returns shapshots of each spike in the spike_index_list.  The snapshot 
        is of size window_size and has the spike index at 
        pre_padding x 100 percent.  Windows which would overlap are excluded 
        and their indexes are returned.
    Inputs:
        signal              : a one dimensional numpy array of values
        spike_index_list    : a one dimensional list or array of integers
        window_size         : the total size of the spike snapshot
        pre_padding         : the normalized relative position of the peak
    Returns:
        spike_windows             : a list of one dimensional numpy arrays
        good_spike_index_list     : the indexes which go along with 
                                        spike_windows
        excluded_windows          : a list of one dimensional numpy arrays
        excluded_spike_index_list : the indexes which go along with 
                                        excluded_windows

    example:
        window_size = 30
        pre_padding = 0.30

                 -
                / \
             /-/   \
        ----/       \-----------------  
        ..............................
        |        |         |         |
        0        10        20        30
    '''
    pre_i = int(window_size * pre_padding)
    post_i = window_size - pre_i

    classified_spike_index_lists = determine_excluded_spikes(signal, 
                                                             spike_index_list, 
                                                             window_size,
                                                             pre_padding,
                                                             pre_i,
                                                             post_i)
    good_spike_index_list      = classified_spike_index_lists[0]
    excluded_spike_index_list  = classified_spike_index_lists[1]
    truncated_spike_index_list = classified_spike_index_lists[2]
    if not exclude_overlappers: 
        good_spike_index_list.extend(excluded_spike_index_list)

    # ------------------------------------------------------------------------
    # -- make the spike windows from the good_spike_index_list
    # ------------------------------------------------------------------------
    spike_windows = numpy.empty( 
            (len(good_spike_index_list),window_size), dtype=numpy.float64)
    excluded_windows = numpy.empty( 
            (len(excluded_spike_index_list),window_size), dtype=numpy.float64)
    for i, si in enumerate(good_spike_index_list):
        spike_windows[i] = signal[si-pre_i:si+post_i]
    for i, si in enumerate(excluded_spike_index_list):
        excluded_windows[i] = signal[si-pre_i:si+post_i]
    
    return (spike_windows, good_spike_index_list,
            excluded_windows, excluded_spike_index_list)

def determine_excluded_spikes(signal, spike_index_list, window_size, 
                              pre_padding, pre_i, post_i):
    """
    determine which (if any) indexes will be excluded due to overlapping
    """
    print spike_index_list
    good_spike_index_set      = set()
    excluded_spike_index_set  = set()
    truncated_spike_index_set = set()
    for i in xrange(len(spike_index_list)):
        # assume spike is good unless it overlaps with edge of another 
        #   spike window
        si = spike_index_list[i]
        
        bi = si - pre_i   # proposed begining index
        ei = si + post_i  # proposed ending index
        # test for spike too close to begining or end of signal
        if bi > 0 and ei < len(signal)-1:
            # test for begining overlapping with end of last spike
            if i > 0 and bi < (spike_index_list[i-1] + post_i):
                excluded_spike_index_set.add(si)
                excluded_spike_index_set.add(si)
            else:
                # doesn't overlap and isn't too close to ends of signal
                good_spike_index_set.add(si)
        else: 
            # spike too close to start of signal or end of signal 
            truncated_spike_index_set.add(si)

    gsil = sorted(list(good_spike_index_set))
    esil = sorted(list(excluded_spike_index_set))
    tsil = sorted(list(truncated_spike_index_set))
    return (gsil, esil, tsil)
