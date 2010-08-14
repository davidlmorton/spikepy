import os

from wx.lib.pubsub import Publisher as pub

from .trial import Trial

# import all read_* modules
#XXX look in other places too?
files = os.listdir(os.path.split(__file__)[0])
file_readers = {}
for file in files:
    if file.startswith('read_') and file.endswith(os.path.extsep+'py'):
        module_name = os.path.splitext(file)[0]
        exec('from . import %s' % module_name)
        if module_name.endswith('_file'):
            name = module_name[5:-5]
        else:
            name = module_name[5:]
        pub.sendMessage(topic=("REGISTERED_'%s'_TYPE" % name).upper(), 
                        data=name)
        file_readers[name] = eval('%s.read_file' % module_name)

def open_data_file(fullpath, data_format='guess', **kwargs):
    """
    Open a datafile given the filename and return a Trial object.
    """
    if data_format == 'guess':
        data_format = guess_data_format(fullpath)
    read_in_file = file_readers[data_format]

    voltage_traces, sampling_freq = read_in_file(fullpath, **kwargs)
    trial = Trial(sampling_freq=sampling_freq,
                  raw_traces=voltage_traces,
                  fullpath=fullpath)
    return trial

    
def guess_data_format(filename):
    """
    Guess the name of the data format, given its filename.
    """
    if filename.endswith('tet'): return 'wessel_lab_tetrode'
    return 'wessel_lab' #XXX obviously flesh this out.
