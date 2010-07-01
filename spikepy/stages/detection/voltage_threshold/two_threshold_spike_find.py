import numpy

from fast_thresh_detect import fast_thresh_detect

def two_threshold_spike_find(input_array, threshold_1, threshold_2=0.0, 
                             refractory_period=0, max_spike_width=2):
    spikes_1 = find_spike_occurances(input_array, threshold_1, 
                                     refractory_period, max_spike_width)
    spikes_2 = find_spike_occurances(input_array, threshold_2, 
                                     refractory_period, max_spike_width)
    print spikes_1, spikes_2
    return get_spike_indexes(spikes_1, spikes_2, max_spike_width)



def find_spike_occurances(input_array, threshold, refractory_period, 
                          max_spike_width):
    p_crossings, n_crossings = fast_thresh_detect(input_array, threshold, 
                                                  refractory_period)

    n_crossings = numpy.array(n_crossings)    
    return get_spike_indexes(p_crossings, n_crossings, max_spike_width)


def get_spike_indexes(p_crossings, n_crossings, max_spike_width):
    spike_occurances = [get_spike_index(p, n_crossings, max_spike_width)
                        for p in p_crossings]
    spike_occurances = list_strip(spike_occurances, None)
    return spike_occurances

def get_spike_index(p, ns, max_spike_width):
        abs_differences = numpy.abs(ns-p)
        sorted_indexes  = numpy.argsort(abs_differences)
        if abs_differences[sorted_indexes[0]] <= max_spike_width:
            n_index = sorted_indexes[0]
            spike_occurance = numpy.average([ns[n_index], p])
            return spike_occurance #TODO should spike occurance be an integer?

def list_strip(a_list, item):   
    while True:
        try:
            a_list.remove(item)
        except ValueError:
            break
    return a_list            

