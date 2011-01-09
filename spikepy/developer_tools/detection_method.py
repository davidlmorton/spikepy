from spikepy.developer_tools.registering_class import RegisteringClass

class DetectionMethod(object):
    '''
    This class should be subclassed in order for developers to add a new 
spike detection method to spikepy.
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods that subclasses are REQUIRED to implement:
    - make_control_panel(parent, **kwargs)
        -- This method returns a wx.Panel object (or a subclass) that acts as 
           the control panel for the new method.  kwargs should be 
           passed to the wx.Panel constructor.
    - run(signal_list, sampling_freq, **kwargs)
        -- This method returns the list of spike times (in seconds).  kwargs 
           are all the arguments to the new method's code.
    '''
    __metaclass__ = RegisteringClass
    _skips_registration = True
    _is_base_class = True
