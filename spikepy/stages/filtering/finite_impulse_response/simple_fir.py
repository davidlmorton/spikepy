import numpy
import scipy.signal as scisig

def spectral_inversion(kernel):
    kernel = -kernel
    kernel[len(kernel)/2] += 1.0
    return kernel

def fir_filter(signal, sampling_freq, critical_freq, kernel_window='hamming',
               taps=101, kind='high', **kwargs):
    """
    Build a filter kernel of type <kind> and apply it to the signal.  
    Returns the filtered signal.

    Inputs:
        signal          : an n element sequence
        sampling_freq   : rate at which data were collected (Hz)
        critical_freq   : frequency for low-pass/high-pass cutoff (Hz)
                          -- for band-pass this is a 2-element sequence
        kernel_window   : a string from the following list:
                           - boxcar, triang, blackman, hamming, hanning,
                           - bartlett, parzen, bohman, blackmanharris, 
                           - nuttall, barthann
        taps            : the number of taps in the kernel (an integer)
        kind            : the kind of pass filtering to perform 
                          -- ('high', 'low', 'band')
        **kwargs        : keyword arguments passed on to scipy.firwin or
                          the scipy.convolve functions.
    Returns:
        filtered_signal     : an n element sequence
    """

    nyquist_freq = sampling_freq/2
    critical_freq = numpy.array(critical_freq, dtype=numpy.float64)
    normalized_critical_freq = critical_freq / nyquist_freq

    if not taps % 2: # ensure taps is odd
        taps += 1

    if kind.lower() in ['low', 'low pass', 'low_pass']:
        kernel = scisig.firwin(taps, normalized_critical_freq, 
                               window=kernel_window, **kwargs)
    elif kind.lower() in ['high', 'high pass', 'high_pass']:
        lp_kernel = scisig.firwin(taps, normalized_critical_freq, 
                                  window=kernel_window, **kwargs)
        kernel = spectral_inversion(lp_kernel)
        
    elif kind.lower() in ['band', 'band pass', 'band_pass']:
        lp_kernel = scisig.firwin(taps, normalized_critical_freq[0], 
                                  window=kernel_window, **kwargs)
        hp_kernel = scisig.firwin(taps, normalized_critical_freq[1], 
                                   window=kernel_window, **kwargs)
        hp_kernel = spectral_inversion(hp_kernel)

        bp_kernel = spectral_inversion(lp_kernel + hp_kernel)
        kernel = bp_kernel

    return numpy.roll(scisig.lfilter(kernel, [1], signal, **kwargs), -taps/2+1)

