

from spikepy.common.trial_manager import Trial
from spikepy.common.strategy import Strategy

class FileInterpreter(object):
    '''
    This class should be subclassed in order for developers to add a new file
interpreter to spikepy.  
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods that subclasses are REQUIRED to implement:
    - read_data_file(fullpath)
        -- This method recieves only a string representation of the
           fullpath to the data file.  It is required to return a list of 
           Trial and or Strategy objects, even if only one was created.
    '''
    # A list of one or more file extentions this interpreter can open.
    extentions = [] 
    #     Higher priority means that this FileInterpreter will be tried first
    # if spikepy tries more than one FileInterpreter.
    priority = 10

    def read_data_file(self, fullpath):
        raise NotImplementedError


