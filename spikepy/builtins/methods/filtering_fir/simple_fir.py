"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy
import scipy.signal as scisig

def spectral_inversion(kernel):
    kernel = -kernel
    kernel[len(kernel)/2] += 1.0
    return kernel

def make_fir_filter(sampling_freq, critical_freq, kernel_window, order, kind, 
                    **kwargs):
    """
    Create a finite impulse response filter kernel.
    Inputs:
        sampling_freq    : the sampling frequency in hz of the signal that the
                           filter will be used on
        critical_freq    : a single number frequency for high or low pass 
                           filters, or a tuple of two frequencies for bandpass 
                           filters
        kernel_window    : the name of the windowing function to use
        order            : the number of sample points to use for filtering 
                           (this is sometimes called the taps)
        kind             : the kind of passband to use (i.e. 'high', 'low', or 
                           'band')
    Returns:
        kernel           : the filter kernel
    """
    nyquist_freq = sampling_freq/2
    critical_freq = numpy.array(critical_freq, dtype=numpy.float64)
    normalized_critical_freq = critical_freq / nyquist_freq

    taps = order+1
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
        low = numpy.min(normalized_critical_freq)
        high = numpy.max(normalized_critical_freq)
        lp_kernel = scisig.firwin(taps, low, 
                                  window=kernel_window, **kwargs)
        hp_kernel = scisig.firwin(taps, high, 
                                   window=kernel_window, **kwargs)
        hp_kernel = spectral_inversion(hp_kernel)

        bp_kernel = spectral_inversion(lp_kernel + hp_kernel)
        kernel = bp_kernel

    return kernel

def fir_filter(signal, sampling_freq, critical_freq, kernel_window='hamming',
               order=101, kind='high', **kwargs):
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
                          -- ('high', 'low', 'band', 'stop')
        **kwargs        : keyword arguments passed on to scipy.signal.firwin.
    Returns:
        filtered_signal     : an n element sequence
    """
    print kind.lower()
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
