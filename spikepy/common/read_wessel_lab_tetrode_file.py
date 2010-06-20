"""
read_file must return 1) a list of voltage traces and 
                      2) a sampling rate.
"""
from .read_wessel_lab_file import read_file as rf

def read_file(filename, time_column=-1, data_columns=[0,1,2,3]):
    return rf(filename, time_column=time_column, data_columns=data_columns)
