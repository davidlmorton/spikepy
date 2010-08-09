import traceback
import sys

from scipy.signal import resample

def pool_process(pool, function, args=tuple(), kwargs=dict()):
    if pool is not None:
        try:
            pool_result = pool.apply_async(function, args=args, kwds=kwargs)
            result = pool_result.get()
        except:
            traceback.print_exc()
            sys.exit(1)
    else:
        result = function(*args, **kwargs)
    return result

def upsample_trace_list(trace_list, prev_sample_rate, desired_sample_rate):
    rate_factor = desired_sample_rate/float(prev_sample_rate)
    return [resample(trace, len(trace)*rate_factor, window='hamming')
            for trace in trace_list]


