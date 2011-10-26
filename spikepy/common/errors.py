from exceptions import Exception

class SpikepyError(Exception):
    '''
    Base class for exceptions in Spikepy.
    '''
    pass

class NoTasksError(SpikepyError):
    pass

class ImpossibleTaskError(SpikepyError):
    pass

class TaskCreationError(SpikepyError):
    pass

class CannotMarkTrialError(SpikepyError):
    pass

class FileInterpretationError(SpikepyError):
    pass

class ConfigError(SpikepyError):
    pass

class ResourceLockedError(SpikepyError):
    pass

class ResourceNotLockedError(SpikepyError):
    pass

class InvalidLockingKeyError(SpikepyError):
    pass

class AddResourceError(SpikepyError):
    pass

class MissingTrialError(SpikepyError):
    pass

class InvalidOptionError(SpikepyError):
    pass

class UnknownStageError(SpikepyError):
    pass

class MissingPluginError(SpikepyError):
    pass

class PluginDefinitionError(SpikepyError):
    pass

class UnknownCategoryError(SpikepyError):
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
