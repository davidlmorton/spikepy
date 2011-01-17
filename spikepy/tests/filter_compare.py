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

"""
Compare the output of various kinds of filtering.
"""
import os
import sys

import pylab
import numpy

from spikepy.common.open_data_file import open_data_file
from spikepy.filtering.simple_iir import bessel, butterworth
from spikepy.filtering.simple_fir import fir_filter

def compare_filters(f1_settings, f2_settings, data_filename):
    """
    filter the data in data_filename with these two settings and
    plot the results.
    """
    t = open_data_file(data_filename, data_format='wessel_lab')
    tt = t.traces[0]
    tf1 = f1_settings['filter_func'](tt, t.sampling_freq,
                                     *f1_settings['args'])
    tf2 = f2_settings['filter_func'](tt, t.sampling_freq,
                                     *f2_settings['args'])

    tt -= numpy.average(tt) # zero mean the data before plotting it
    pylab.plot(tt, linewidth=2.5, color='black', label='Raw Data')
    pylab.plot(tf1, linewidth=1.5, color='red', label=f1_settings['label'])
    pylab.plot(tf2, linewidth=1.5, color='blue', label=f2_settings['label'])
    pylab.xlabel("Time (samples) sampling_frequency = %d Hz" %
                 t.sampling_freq)
    pylab.ylabel("Voltage (mV)")
    pylab.title(str(t))
    pylab.legend()
    pylab.show()


# Butterworth 4th order vs. 101 tap hamming
f1_settings = {'filter_func':butterworth, 'args':[300, 3, 'high'], 
               'label':'3th order Butterworth > 300 Hz'}
f2_settings = {'filter_func':fir_filter, 'args':[300, 'hamming', 101, 'high'],
               'label':'101 taps hamming > 300 Hz'}
pylab.figure(1)
compare_filters(f1_settings, f2_settings, '../sample_data/287-Turtle_NI_Cortex_II-data')

"""
# Butterworth 4th vs. 8th order
f1_settings = {'filter_func':butterworth, 'args':[300, 4, 'high'], 
               'label':'4th order Butterworth > 300 Hz'}
f2_settings = {'filter_func':butterworth, 'args':[300, 8, 'high'],
               'label':'8th order Butterworth > 300 Hz'}
pylab.figure(1)
compare_filters(f1_settings, f2_settings, '../sample_data/287-Turtle_NI_Cortex_II-data')


# Bessel 4th vs. 8th order
f1_settings = {'filter_func':bessel, 'args':[300, 4, 'high'], 
               'label':'4th order bessel > 300 Hz'}
f2_settings = {'filter_func':bessel, 'args':[300, 8, 'high'],
               'label':'8th order bessel > 300 Hz'}
pylab.figure(2)
compare_filters(f1_settings, f2_settings, '../sample_data/287-Turtle_NI_Cortex_II-data')

# Butterworth 4th order 100Hz vs 300Hz
f1_settings = {'filter_func':butterworth, 'args':[100, 4, 'high'], 
               'label':'4th order Butterworth > 100 Hz'}
f2_settings = {'filter_func':butterworth, 'args':[300, 4, 'high'],
               'label':'4th order Butterworth > 300 Hz'}
pylab.figure(3)
compare_filters(f1_settings, f2_settings, '../sample_data/287-Turtle_NI_Cortex_II-data')

# Butterworth vs. bessel 4th order 100Hz
f1_settings = {'filter_func':butterworth, 'args':[100, 4, 'high'], 
               'label':'4th order Butterworth > 100 Hz'}
f2_settings = {'filter_func':bessel, 'args':[100, 4, 'high'],
               'label':'4th order bessel > 100 Hz'}
pylab.figure(4)
compare_filters(f1_settings, f2_settings, '../sample_data/287-Turtle_NI_Cortex_II-data')
"""

