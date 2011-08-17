"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
from spikepy.developer_tools.supplemental_method import SupplementalMethod
from spikepy.common.path_utils import get_data_dirs

base_classes = {'file_interpreter':  FileInterpreter,
                'supplemental':      SupplementalMethod,
                'detection_filter':  FilteringMethod,
                'detection':         DetectionMethod,
                'extraction_filter': FilteringMethod,
                'extraction':        ExtractionMethod,
                'clustering':        ClusteringMethod}

# --- UTILITY FUNCTIONS ---
def get_methods_with_base(base_name):
    '''
        Return a list of method objects and a list of method classes, 
    given the base_name.
    '''
    return_methods = []
    return_classes = []
    base_class = base_classes[base_name]
    for method_class in _class_registry[base_class]:
        method = method_class()
        return_methods.append(method)
        return_classes.append(method_class)
    return (return_methods, return_classes)


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

class PluginManager(object):
    def __init__(self):
        self._loaded_modules = None

    def load(self):
        _class_registry = {} # reset class registry before loading new classes
        self._loaded_modules = load_all_plugins()

    def get_method(self, base_name, method_name, instantiate=False):
        '''
        Return a method object (or class), given the base_name and method_name.
        '''
        for method, method_class in zip(*get_methods_with_base(base_name)):
            if method.name == method_name:
                if instantiate:
                    return method
                else:
                    return method_class
        raise RuntimeError("couldn't find method named '%s' with base '%s'" %
                            (method_name, base_name))

    def get_methods(self, base_name, instantiate=False):
        if instantiate:
            index = 0
        else:
            index = 1
        return get_methods_with_base(base_name)[index]

    @property
    def file_interpreters(self):
        return get_methods_with_base('file_interpreter')[0]

    @property
    def loaded_modules(self):
        return self._loaded_modules

    @property
    def class_registry(self):
        return _class_registry
