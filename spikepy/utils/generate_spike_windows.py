
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
        if bi > 0 and ei < signal_len-1:
            # test for begining overlapping with end of last spike
            if i > 0 and bi < (spike_index_list[i-1] + post_i):
                excluded_spike_index_set.add(si)
            else:
                # doesn't overlap and isn't too close to ends of signal
                good_spike_index_set.add(si)
        else: 
            # spike too close to start of signal or end of signal 
            truncated_spike_index_set.add(si)

    gsil = list(good_spike_index_set)
    esil = list(excluded_spike_index_set)
    tsil = list(truncated_spike_index_set)
    return (gsil, esil, tsil)
