#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
from exceptions import Exception

class SpikepyError(Exception):
    '''
    Base class for exceptions in Spikepy.
    '''
    pass

class FeatureDimensionalityError(SpikepyError):
    pass

class DataUnavailableError(SpikepyError):
    pass

class NoClustersError(SpikepyError):
    pass

class NoCurrentStrategyError(SpikepyError):
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

class MissingResourceError(SpikepyError):
    pass

class InvalidValueError(SpikepyError):
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
