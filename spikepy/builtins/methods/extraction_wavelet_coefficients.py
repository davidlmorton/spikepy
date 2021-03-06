#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy
from scipy.stats import kstest
import pywt

from spikepy.developer.methods import ExtractionMethod
from spikepy.common.valid_types import ValidFloat, ValidOption, ValidBoolean,\
        ValidInteger
from spikepy.utils.generate_spike_windows import generate_spike_windows

class ExtractionSpikeWaveletCoefficients(ExtractionMethod):
    name = "Spike Wavelet Coefficients"
    description = "Extract the wavelet coefficients of spike waveforms in a temporal window around the spike event."
    is_stochastic = False
    is_pooling = True
    silent_pooling = False
    provides = ['features', 'feature_times']

    pre_padding = ValidFloat(min=0.0, default=2.0,
            description='Determines the amount of time before the spike (in ms) to include in the windowed spike.')
    post_padding = ValidFloat(min=0.0, default=4.0,
            description='The amount of time after the spike (in ms) to include in the windowed spike.')
    exclude_overlappers = ValidBoolean(default=False,
            description="Throw out all spikes who's windows would overlap with another spike (both overlappers are thrown out.)")
    min_num_channels = ValidInteger(min=1, default=3,
            description="The lowest number of channels on which a spike must have been identified within 'peak drift' milliseconds.")
    peak_drift = ValidFloat(min=0.01, default=0.3,
            description='The greatest amount of time (in ms) between spikes on different channels while they still are considered part of a single spike event.') # ms
    wavelet = ValidOption(*pywt.wavelist(), default='haar')
    num_coefficients_kept = ValidInteger(min=1, max=1000, default=10,
            description='The number of wavelet coefficients that are kept.')
    normalize = ValidBoolean(default=True,
            description='Normalize coefficients after selecting them so that their mean=0.0, and std=1.0')

    def run(self, signal_list, sampling_freq_list, event_times_list, 
            wavelet='haar', num_coefficients_kept=10, normalize=True, **kwargs):
        # features, feature_times for each trial
        features_list = []
        feature_times_list = []
        for signal, sampling_freq, event_times in zip(signal_list, 
                sampling_freq_list, event_times_list):
            features, feature_times, _, _ = generate_spike_windows(signal, 
                    sampling_freq, event_times, **kwargs)
            features_list.append(features)
            feature_times_list.append(feature_times)

        # unify features before getting wavelet_coefficients
        total_len = 0
        for features in features_list:
            total_len += len(features)

        unified_features = numpy.empty((total_len, )+features_list[0].shape[1:])
        begin = 0
        end = 0
        unpacking_index = {}
        for i, features in enumerate(features_list):
            end = begin + len(features)
            unified_features[begin:end] = features
            unpacking_index[i] = [begin, end]
            begin = end

        wavelet_coefficients = get_wavelet_coefficients(unified_features, 
                wavelet, num_coefficients_kept)
        if normalize:
            means = numpy.average(wavelet_coefficients, axis=0)
            stds = numpy.std(wavelet_coefficients, axis=0)
            wavelet_coefficients = (wavelet_coefficients-means)/stds

        # deunify wavelet_coefficients before returning them
        wavelet_coefficients_list = []
        for i in range(len(features_list)):
            begin, end = unpacking_index[i]
            wavelet_coefficients_list.append(wavelet_coefficients[begin:end])

        return [wavelet_coefficients_list, feature_times_list]

def difference_from_normality(observations):
    '''
        The difference from normality as found using the Kolomogorov-Smirnov
    test.
    '''
    std = numpy.std(observations)
    if std != 0.0:
        normalized_observations = (observations-numpy.average(observations))/\
                numpy.std(observations)
        return kstest(normalized_observations, 'norm')[0]
    else:
        return 0.0

def get_columns(array2D, scores, num_columns):
    '''
        Return a new 2D-array with only the columns that had the highest
    scores.
    '''
    sorted_indexes = numpy.argsort(scores)
    return array2D[:, sorted_indexes[-num_columns:][::-1]]

def get_wavelet_coefficients(observations, wavelet='db20', num_coefficients=10):
    '''
        Return the values of the wavelet decomposition which are distributed 
    the most different from the normal distribution.
    '''
    # calculate wavelet coefficients
    coeffs = numpy.hstack(pywt.wavedec(observations[0], wavelet))
    obs_wavelet_coeffs = numpy.empty((len(observations), len(coeffs)), 
            dtype=numpy.float64)
    obs_wavelet_coeffs[0] = coeffs

    for i, obs in enumerate(observations[1:]):
        coeffs = numpy.hstack(pywt.wavedec(obs, wavelet))
        obs_wavelet_coeffs[i+1] = coeffs

    # find difference_from_normality score for each coefficient
    scores = [difference_from_normality(obs_wavelet_coeffs[:,i])
            for i in range(obs_wavelet_coeffs.shape[1])]

    # return only those which had highest scores.
    return get_columns(obs_wavelet_coeffs, scores, num_coefficients)


