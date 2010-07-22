from .simple_fir import fir_filter

def run(trace_list, window_name=None, 
               sampling_freq=None,
               critical_freq=None,
               taps=None,
               kind=None):
    if (window_name is None or
        sampling_freq is None or
        critical_freq is None or
        taps is None or
        kind is None):
        raise RuntimeError(
            'Keyword arguments to run() are not optional.')

    else:
        filtered_trace_list = []
        kind = kind.lower().split()[0]
        for trace in trace_list:
            filtered_trace_list.append(
                fir_filter(trace, sampling_freq, critical_freq,
                           kernel_window=window_name,
                           taps=taps, 
                           kind=kind))
        return filtered_trace_list

