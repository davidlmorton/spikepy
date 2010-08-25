from spikepy.developer_tools.registering_class import RegisteringClass

class FileInterpreter(object):
    __metaclass__ = RegisteringClass
    _skips_registration = True
    _is_base_class = True

