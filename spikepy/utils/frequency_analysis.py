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

from matplotlib import mlab

from spikepy.utils.resample import resample


def find_NFFT(frequency_resolution, sampling_frequency, 
              force_power_of_two=False):
    #This function returns the NFFT
    NFFT = (sampling_frequency*1.0)/frequency_resolution-2
    if force_power_of_two:
        pow_of_two = 1
        pot_nfft = 2**pow_of_two
        while pot_nfft < NFFT:
            pow_of_two += 1
            pot_nfft = 2**pow_of_two
        return pot_nfft
    else:
        return NFFT


def find_frequency_resolution(NFFT, sampling_frequency):
    return (sampling_frequency*1.0)/(NFFT + 2)


def find_NFFT_and_noverlap(frequency_resolution, sampling_frequency,
                           time_resolution):
    NFFT =  find_NFFT(frequency_resolution, sampling_frequency)
    
    # finds the power of two which is just greater than NFFT
    pow_of_two = 1
    pot_nfft = 2**pow_of_two
    noverlap = pot_nfft-sampling_frequency*time_resolution
    while pot_nfft < NFFT or noverlap < 0:
        pow_of_two += 1
        pot_nfft = 2**pow_of_two
        noverlap = pot_nfft-sampling_frequency*time_resolution

    pot_frequency_resolution = find_frequency_resolution(pot_nfft, 
                                                         sampling_frequency)
    
    return {'NFFT':int(NFFT), 'power_of_two_NFFT':int(pot_nfft), 
            'noverlap':int(noverlap), 
            'power_of_two_frequency_resolution':pot_frequency_resolution} 


def psd(signal, sampling_frequency, frequency_resolution,
        high_frequency_cutoff=None,  axes=None, **kwargs):
    """
    This function wraps matplotlib.mlab.psd to provide a more intuitive 
        interface.
    Inputs:
        signal                  : the input signal (a one dimensional array)
        sampling_frequency      : the sampling frequency of signal
        frequency_resolution    : the desired frequency resolution of the 
                                    specgram.  this is the guaranteed worst
                                    frequency resolution.
        --keyword arguments--
        axes=None               : If an Axes instance is passed then it will
                                  plot to that.
        **kwargs                : Arguments passed on to 
                                   matplotlib.mlab.specgram
    Returns:
        Pxx
        freqs
    """
    if (high_frequency_cutoff is not None 
        and high_frequency_cutoff < sampling_frequency):
        resampled_signal = resample_signal(signal, sampling_frequency, 
                                                    high_frequency_cutoff)
    else:
        high_frequency_cutoff = sampling_frequency
        resampled_signal = signal
    NFFT= find_NFFT(frequency_resolution, high_frequency_cutoff, 
                    force_power_of_two=True) 
    if axes is not None:
        return axes.psd(resampled_signal, NFFT=NFFT, 
                             Fs=high_frequency_cutoff, 
                             noverlap=0, **kwargs)
    else:
        return mlab.psd(resampled_signal, NFFT=NFFT, 
                Fs=high_frequency_cutoff, noverlap=0, **kwargs)

