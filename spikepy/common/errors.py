from exceptions import Exception

class SpikepyError(Exception):
    '''
    Base class for exceptions in Spikepy.
    '''
    pass

class DuplicateStrategyError(SpikepyError):
    pass

class MissingStrategyError(SpikepyError):
    pass

class ArgumentTypeError(SpikepyError):
    pass

class InconsistentNameError(SpikepyError):
    pass

class NameForbiddenError(SpikepyError):
    pass

class SettingsNameForbiddenError(NameForbiddenError):
    pass


class MethodsUsedNameForbiddenError(NameForbiddenError):
    pass
