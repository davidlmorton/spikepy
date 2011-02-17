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

from .simple_fir import fir_filter

def run(trace_list, sampling_freq, 
               window_name=None, 
               critical_freq=None,
               taps=None,
               kind=None):
    if (window_name is None or
        critical_freq is None or
        taps is None or
        kind is None):
        raise RuntimeError(
            'Keyword arguments to run() are not optional.')

    else:
        filtered_trace_list = []
        kind = kind.lower().split()[0]
        for trace in trace_list:
            filtered_trace_list.append(
                fir_filter(trace, sampling_freq, critical_freq,
                           kernel_window=window_name,
                           taps=taps, 
                           kind=kind))
        return {'std_results':filtered_trace_list,
                'additional_results': None}

