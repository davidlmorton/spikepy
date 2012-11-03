
    if kind.lower()[-4:] == 'stop':
        low = numpy.min(critical_freq)
        high = numpy.max(critical_freq)
        result = fir_filter(signal, sampling_freq, low, 
                kernel_window=kernel_window, order=order, kind='low', **kwargs)
        result += fir_filter(signal, sampling_freq, high, 
                kernel_window=kernel_window, order=order, kind='high', **kwargs)
        return result

    kernel = make_fir_filter(sampling_freq, critical_freq, kernel_window, order,
            kind, **kwargs)

    taps = order+1

    if not taps % 2: # ensure taps is odd
        taps += 1

    if signal.ndim == 2:
        result = numpy.empty(signal.shape, dtype=signal.dtype)
        for i in range(len(signal)):
            zero_padded_signal = numpy.hstack([signal[i], 
                    numpy.zeros(taps, dtype=signal.dtype)])
            result[i] = numpy.roll(scisig.lfilter(kernel, [1], zero_padded_signal), 
                    -taps/2+1)[:len(signal[i])]
    else:
        zero_padded_signal = numpy.hstack([signal, 
                numpy.zeros(taps, dtype=signal.dtype)])
        result = numpy.roll(scisig.lfilter(kernel, [1], signal), -taps/2+1)[:len(signal)]
    return result
