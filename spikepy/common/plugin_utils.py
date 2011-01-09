import imp
import os
import uuid
from collections import defaultdict

import wx

from spikepy.developer_tools.registering_class import _class_registry
from spikepy.developer_tools.file_interpreter import FileInterpreter
from spikepy.developer_tools.filtering_method import FilteringMethod
from spikepy.developer_tools.detection_method import DetectionMethod
from spikepy.developer_tools.extraction_method import ExtractionMethod
from spikepy.developer_tools.clustering_method import ClusteringMethod
from spikepy.common.path_utils import get_data_dirs

base_classes = {'detection_filter':  FilteringMethod,
                'detection':         DetectionMethod,
                'extraction_filter': FilteringMethod,
                'extraction':        ExtractionMethod,
                'clustering':        ClusteringMethod}

def get_methods_for_stage(stage_name):
    '''
    Return a list of method objects, given the stage_name.
    '''
    return_methods = []
    base_class = base_classes[stage_name]
    for method_class in _class_registry[base_class]:
        method = method_class()
        return_methods.append(method)
    return return_methods

def get_method(stage_name, method_name):
    '''
    Return a method object, given the stage_name and method_name.
    '''
    for method in get_methods_for_stage(stage_name):
        if method.name == method_name:
            return method
    raise runtimeerror("couldn't find method named '%s' from stage '%s'" %
                        (method_name, stage_name))

def get_all_file_interpreters():
    file_interpreter_classes = _class_registry[FileInterpreter]
    file_interpreters = [f() for f in file_interpreter_classes]
    return file_interpreters

def should_load(fullpath):
    filename = os.path.split(fullpath)[1]
    if filename.startswith('.'):
        return False
    if filename.endswith('.py'):
        return True
    if os.path.isdir(fullpath):
        module_init = os.path.join(fullpath, '__init__.py')
        return os.path.exists(module_init)
    return False

def load_plugins(plugin_dir):
    loaded_modules = {}
    if os.path.exists(plugin_dir):
        entries = os.listdir(plugin_dir)
        for e in entries:
            fullpath_e = os.path.join(plugin_dir, e)
            if should_load(fullpath_e):
                unique_name = 'spikepy_' + (str(uuid.uuid4())).replace('-','_') 
                module_name = os.path.splitext(e)[0]
                fm_results = None
                try:
                    fm_results = imp.find_module(module_name, [plugin_dir]) 
                except ImportError:
                    pass
                if fm_results is not None:
                    loaded_modules[module_name]=imp.load_module(unique_name,
                                                                *fm_results)
                    loaded_modules[module_name+'_name'] = unique_name
    return loaded_modules

def load_all_plugins(data_dirs=None, **kwargs):
    if data_dirs is None:
        data_dirs = get_data_dirs(**kwargs)

    loaded_modules = defaultdict(dict)
    for level in data_dirs.keys():
        for plugin_type in ['file_interpreters', 'methods']:
            plugin_dir = data_dirs[level][plugin_type]
            loaded_modules[level][plugin_type] = load_plugins(plugin_dir)

    return loaded_modules

