#  Copyright (C) 2013  David Morton
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

from spikepy.developer.methods import FilteringMethod
from spikepy.common.valid_types import ValidInteger

# import any libraries that you need here
from signal_filters import butterworth

class FilteringIIR(FilteringMethod):
    '''
    This class implements an Butterworth filter.
    '''
    # the name that will show up in the pull-down selector
    name = 'Butterworth'
    description = 'Just a simple Butterworth filter.'
    # Does this method's run function return different results when given the
    # exact same inputs?  This information is used by Spikepy to determine if
    # the plugin needs to be run again or if the results of a previous run can
    # be reused.
    is_stochastic = False

    # Definition of the filter's options.  The default value will be in the
    # initial value in the gui and the restrictions (such as max and
    # min) will be enforced in the gui as well.
    low_cutoff_frequency = ValidInteger(min=10, default=300)
    high_cutoff_frequency = ValidInteger(min=50, max=20000, default=3000)
    order = ValidInteger(2, 8, default=3)

    def run(self, signal, sampling_freq,
            low_cutoff_frequency, high_cutoff_frequency, order):
        """
        This function will actually do the filtering and return the filtered_signal
        as well as the new (possibly different) sampling_frequency (in Hz).

        The first two arguments are always:
           1) the signal: an N element sequence of voltage readings.
           2) the signal's sampling frequency in Hertz.

        The rest of the arguments are the values of the options and will be passed
        in by Spikepy as keyword arguments.
        """
        filtered_signal = butterworth(signal, sampling_freq,
                low=low_cutoff_frequency, high=high_cutoff_frequency,
                order=order)
        return [filtered_signal, sampling_freq]
