

import numpy
import scipy.signal as scisig

def resample(signal, prev_sample_rate, new_sample_rate):
    if prev_sample_rate == new_sample_rate:
        return signal

    rate_factor = new_sample_rate/float(prev_sample_rate)
    num_samples = int(len(signal.T)*rate_factor)
    if signal.ndim == 2:
        result = numpy.empty((len(signal), num_samples), dtype=signal.dtype)
        for si, s in enumerate(signal):
            result[si] = scisig.resample(s, num_samples)
        return result
    else:
        return scisig.resample(signal, num_samples)    
