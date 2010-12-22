import os

from wx.lib.pubsub import Publisher as pub

from .trial import Trial
from spikepy.developer_tools.registering_class import _class_registry
from spikepy.developer_tools.file_interpreter import FileInterpreter
from spikepy.builtins import file_interpreters

def get_all_file_interpreters():
    file_interpreter_classes = _class_registry[FileInterpreter]
    file_interpreters = [f() for f in file_interpreter_classes]
    return file_interpreters

def open_data_file(fullpath, file_interpreter_name=None):
    """
    Open a datafile given the filename and return a Trial object.
    """
    if file_interpreter_name is None:
        file_interpreter = guess_file_interpreter(fullpath)

    return file_interpreter.read_data_file(fullpath)

    
def guess_file_interpreter(fullpath):
    """
    Guess the file_interpreter, given a data file's fullpath.
    """
    filename = os.path.split(fullpath)[-1]
    extention = filename.split(os.path.extsep)[-1]
    file_interpreters = get_all_file_interpreters()
    for fi in  file_interpreters:
        if fi.extention == extention:
            return fi
    return file_interpreters[0]
