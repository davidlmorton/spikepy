"""
read_file must return 1) a list of voltage traces and 
                      2) a sampling rate.
"""
import numpy

def read_file(filename, time_column=-1, data_columns=[0]):
    data = numpy.loadtxt(filename)
    voltage_traces = data.T[data_columns]
    times = data.T[time_column]
    sample_rate = int(len(times)/times[-1]*1000) # 1000 because times in ms.

    return voltage_traces, sample_rate
