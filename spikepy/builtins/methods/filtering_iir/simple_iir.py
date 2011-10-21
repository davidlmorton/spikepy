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

from .filtfilt import filtfilt


def iir_filter(signal, sampling_freq, critical_freq, filter_func,
                order, kind, acausal=False, **kwargs):
    """
    Build a filter_func of type <kind> and apply it to the signal.  
    Returns the filtered signal.

    Inputs:
        signal              : an n element sequence
        sampling_freq   : rate at which data were collected (Hz)
        critical_freq   : frequency for low-pass/high-pass cutoff (Hz)
                          -- for band-pass this is a 2-element sequence
        filter_func     : a function from the following list:
                           - scipy.signal.bessel
                           - scipy.signal.butter    (Butterworth)
        order           : the order of the filter (an integer)
        kind            : the kind of pass filtering to perform 
                          -- ('high', 'low', 'band')
        **kwargs        : keyword arguments passed on to scipy.signal functions.
    Returns:
        filtered_signal     : an n element sequence
    """
    nyquist_freq = sampling_freq/2
    critical_freq = numpy.array(critical_freq, dtype=numpy.float64)
    normalized_critical_freq = critical_freq / nyquist_freq

    b, a = filter_func(order, normalized_critical_freq, 
                       btype=kind, output='ba', **kwargs)
    if acausal:
        return filtfilt(b, a, signal)
    else:
        return scisig.lfilter(b, a, signal, **kwargs)


def butterworth(signal, sampling_freq, critical_freq,
                order=4, kind='high', acausal=False, **kwargs):
    """
    This calls iir_filter with filter_func = scipy.signal.butter.
    """
    if signal.ndim == 2:
        result = numpy.empty(signal.shape, dtype=signal.dtype)
        for i in range(len(signal)):
            result[i] = iir_filter(signal[i], sampling_freq, critical_freq,
                    scisig.butter, order, kind, **kwargs)
    else:
        result = iir_filter(signal, sampling_freq, critical_freq,
                      scisig.butter, order, kind, **kwargs)
    return result

butterworth.__doc__ += '\n--iir_filter docstring--\n%s' % iir_filter.__doc__

def bessel(signal, sampling_freq, critical_freq,
                order=4, kind='high', acausal=False, **kwargs):
    """
    This calls iir_filter with filter_func = scipy.signal.butter.
    """
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
