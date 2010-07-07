import copy

import numpy

from fast_thresh_detect import fast_thresh_detect

def two_threshold_spike_find(input_array, threshold_1, threshold_2=None, 
                             refractory_period=0, max_spike_width=2):
    spikes_1 = find_spike_occurances(input_array, threshold_1, 
                                     refractory_period, max_spike_width)
    if threshold_2 == threshold_1 or threshold_2 is None:
        return spikes_1
    else:
        spikes_2 = find_spike_occurances(input_array, threshold_2, 
                                     refractory_period, max_spike_width)
        all_spikes = copy.deepcopy(spikes_1)
        all_spikes.extend(spikes_2)
        return get_spike_indexes(all_spikes, all_spikes, 
                             max(max_spike_width, refractory_period), 
                             return_loners=True)

def find_spike_occurances(input_array, threshold, refractory_period, 
                          max_spike_width):
    p_crossings, n_crossings = fast_thresh_detect(input_array, threshold, 
                                                  refractory_period)

    n_crossings = numpy.array(n_crossings, dtype=numpy.int64)    
    p_crossings = numpy.array(p_crossings, dtype=numpy.int64)    
    return get_spike_indexes(p_crossings, n_crossings, max_spike_width)


def get_spike_indexes(p_crossings, n_crossings, max_spike_width, return_loners=False):
    spike_occurances = [get_spike_index(p, n_crossings, max_spike_width, return_loners)
                        for p in p_crossings]
    spike_occurances = list_strip(spike_occurances, None)
    return spike_occurances

def get_spike_index(p, ns, max_spike_width, return_loners):
        abs_differences = numpy.abs(ns-p)
        sorted_indexes  = numpy.argsort(abs_differences)
        if return_loners: small_index = 1
        else: small_index = 0
        if abs_differences[sorted_indexes[small_index]] <= max_spike_width:
            n_index = sorted_indexes[small_index]
            spike_occurance = numpy.average([ns[n_index], p])
            return spike_occurance #TODO should spike occurance be an integer?
        if return_loners:
            return p

def list_strip(a_list, item):   
    while True:
        try:
            a_list.remove(item)
        except ValueError:
            break
    return a_list            

