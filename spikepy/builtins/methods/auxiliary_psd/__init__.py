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

from spikepy.developer.methods import AuxiliaryMethod
from spikepy.common.valid_types import ValidFloat
from spikepy.utils.frequency_analysis import psd

class PSDPF(AuxiliaryMethod):
    group = 'PSD'
    name = 'Power Spectral Density (Pre-Filtering)'
    description = 'Spectral Density of the pre-filtered signal.'
    runs_with_stage = 'detection_filter'
    requires = ['pf_traces', 'pf_sampling_freq']
    provides = ['pf_psd', 'pf_freqs']
    is_stochastic = False

    frequency_resolution = ValidFloat(min=0.1, default=10,
            description="The minimal acceptable frequency resolution.  The actual frequency resolution may be better than this (but won't be worse).")

    def run(self, signal, sampling_freq, **kwargs):
        return psd(signal.flatten(), sampling_freq, 
                kwargs['frequency_resolution'])

class PSDDF(PSDPF):
    group = 'PSD'
    name = 'Power Spectral Density (Post-Detection-Filtering)'
    description = 'Spectral Density of the detection-filtered signal.'
    runs_with_stage = 'detection_filter'
    requires = ['df_traces', 'df_sampling_freq']
    provides = ['df_psd', 'df_freqs']

class PSDEF(PSDPF):
    group = 'PSD'
    name = 'Power Spectral Density (Post-Extraction-Filtering)'
    description = 'Spectral Density of the extraction-filtered signal.'
    runs_with_stage = 'extraction_filter'
    requires = ['ef_traces', 'ef_sampling_freq']
    provides = ['ef_psd', 'ef_freqs']
    
