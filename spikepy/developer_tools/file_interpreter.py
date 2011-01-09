from spikepy.developer_tools.registering_class import RegisteringClass
from spikepy.common.trial import Trial

class FileInterpreter(object):
    '''
    This class should be subclassed in order for developers to add a new file
interpreter to spikepy.  
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods AVAILABLE to subclasses:
    - make_trial_object(sampling_freq, raw_traces, fullpath)
        -- This method returns a new Trial object.  A list of Trial objects
           is the expected return value of the read_data_file method.
Methods that subclasses are REQUIRED to implement:
    - read_data_file(fullpath)
        -- This method recieves only a string representation of the
           fullpath to the data file.  It is required to return a list of 
           Trial objects, even if only one was created.  You should use the
           method make_trial_object to create these Trial objects.
    '''
    __metaclass__ = RegisteringClass
    _skips_registration = True
    _is_base_class = True

    def make_trial_object(self, sampling_freq, raw_traces, fullpath):
        return Trial(sampling_freq=sampling_freq, raw_traces=raw_traces,
                     fullpath=fullpath)

