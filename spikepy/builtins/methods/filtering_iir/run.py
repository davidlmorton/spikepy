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

from .simple_iir import butterworth, bessel

def run(trace_list, sampling_freq,
               function_name=None, 
               acausal=None,
               critical_freq=None,
               order=None,
               kind=None):
    if (function_name is None or
        acausal is None or
        critical_freq is None or
        order is None or
        kind is None):
        raise RuntimeError(
            'Keyword arguments to run() are not optional.')

    else:
        if function_name.lower() == 'butterworth':
            filter_function = butterworth
        elif function_name.lower() == 'bessel':
            filter_function = bessel
        else:
            raise RuntimeError('Function name cannot be:"%s", must be one of "butterworth" or "bessel"' % function_name.lower())
        filtered_trace_list = []
        kind = kind.lower().split()[0]
        for trace in trace_list:
            filtered_trace_list.append(
                filter_function(trace, sampling_freq, critical_freq,
                                order, kind, acausal=acausal))
        return {'std_results':filtered_trace_list,
                'additional_results':None}

