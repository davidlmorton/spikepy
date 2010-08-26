from file_interpreter import FileInterpreter
from registering_class import _class_registry as class_registry

file_interpreters = class_registry[FileInterpreter]

del class_registry

