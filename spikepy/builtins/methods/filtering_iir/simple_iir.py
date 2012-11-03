
    if signal.ndim == 2:
        result = numpy.empty(signal.shape, dtype=signal.dtype)
        for i in range(len(signal)):
            result[i] = iir_filter(signal[i], sampling_freq, critical_freq,
                    scisig.bessel, order, kind, **kwargs)
    else:
        result = iir_filter(signal, sampling_freq, critical_freq,
                      scisig.bessel, order, kind, **kwargs)
    return result

bessel.__doc__ += '\n--iir_filter docstring--\n%s' % iir_filter.__doc__
