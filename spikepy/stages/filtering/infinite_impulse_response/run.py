from .simple_iir import butterworth, bessel

def run(trace_list, sampling_freq,
               function_name=None, 
               critical_freq=None,
               order=None,
               kind=None):
    if (function_name is None or
        critical_freq is None or
        order is None or
        kind is None):
        raise RuntimeError(
            'Keyword arguments to run() are not optional.')

    else:
        if function_name.lower() == 'butterworth':
            filter_function = butterworth
        elif function_name.lower() == 'bessel':
            filter_function = butterworth
        else:
            raise RuntimeError('Function name cannot be:"%s", must be one of "butterworth" or "bessel"' % function_name.lower())
        filtered_trace_list = []
        kind = kind.lower().split()[0]
        for trace in trace_list:
            filtered_trace_list.append(
                filter_function(trace, sampling_freq, critical_freq,
                                order, kind))
        return filtered_trace_list

