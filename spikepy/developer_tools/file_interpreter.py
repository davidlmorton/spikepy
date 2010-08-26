from spikepy.developer_tools.registering_class import RegisteringClass

class FileInterpreter(object):
    __metaclass__ = RegisteringClass
    _skips_registration = True
    _is_base_class = True

    def make_trial_object(sampling_freq, raw_traces, fullpath):
        return Trial(sampling_freq=sampling_freq, raw_traces=raw_traces,
                     fullpath=fullpath)

