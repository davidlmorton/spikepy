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
from collections import defaultdict

from spikepy.developer_tools.file_interpreter import FileInterpreter
from spikepy.developer_tools.filtering_method import FilteringMethod
from spikepy.developer_tools.detection_method import DetectionMethod
from spikepy.developer_tools.extraction_method import ExtractionMethod
from spikepy.developer_tools.clustering_method import ClusteringMethod
from spikepy.developer_tools.supplemental_method import SupplementalMethod
from spikepy.common.path_utils import get_data_dirs

base_classes = {'file_interpreter':  FileInterpreter,
                'supplemental':      SupplementalMethod,
                'filtering':         FilteringMethod,
                'detection':         DetectionMethod,
                'extraction':        ExtractionMethod,
                'clustering':        ClusteringMethod}

# --- UTILITY FUNCTIONS ---
def get_base_class_name(base_class):
    '''Return the base_class's simple name given the class.'''
    for name, class_ in base_classes.items():
        if base_class is class_:
            return name
    raise RuntimeError("Couldn't fine the name for %s" % base_class)

def should_load(fullpath):
    '''Return True if we should load fullpath as a plugin.'''
    filename = os.path.split(fullpath)[1]
    if filename.startswith('.'):
        return False
    if filename.endswith('.py'):
        if filename.startswith('__init__'):
            return False
        else:
            return True
    if os.path.isdir(fullpath):
        module_init = os.path.join(fullpath, '__init__.py')
        return os.path.exists(module_init)
    return False

def load_plugins(plugin_dir):
    ''' Load all the plugins in the given <plugin_dir>.'''
    loaded_plugins = []
    if os.path.exists(plugin_dir):
        entries = os.listdir(plugin_dir)
        for e in entries:
            fullpath_e = os.path.join(plugin_dir, e)
            if should_load(fullpath_e):
                module_name = os.path.splitext(e)[0]
                unique_name = 'spikepy_plugin_%s' % (module_name)

                # load the module
                fm_results = None
                try:
                    fm_results = imp.find_module(module_name, [plugin_dir]) 
                except ImportError:
                    pass
                if fm_results is not None:
                    module=imp.load_module(unique_name, *fm_results)
                    loaded_plugins.extend(get_classes_from_module(module, 
                            base_classes.values()))
    return loaded_plugins

def get_classes_from_module(module, class_list):
    '''
        Return the classes defined in the <module> which inherit from
    any of the classes in <class_list>.
    Returns: A list of tuples...
        [(new_class, class_it_inherited_from), ...]
    '''
    CLASS_TYPE = type(class_list[0])
    classes = []
    for name in dir(module):
        thing = getattr(module, name)
        if isinstance(thing, CLASS_TYPE) and thing not in class_list:
            #   thing should instantiate with no arguments, if not, it isn't
            # what we're looking for.
            try: 
                instance = thing()
            except TypeError:
                continue
            classes.extend([(thing(), cl) for cl in class_list if 
                    isinstance(thing(), cl)])
    return classes
    
def load_all_plugins(data_dirs=None, **kwargs):
    '''Load file_interpreters and methods from all levels.'''
    if data_dirs is None:
        data_dirs = get_data_dirs(**kwargs)

    loaded_plugins = defaultdict(lambda :defaultdict(list))
    for level in data_dirs.keys():
        for plugin_type in ['file_interpreters', 'methods']:
            plugin_dir = data_dirs[level][plugin_type]
            plugins = load_plugins(plugin_dir)
            for new_class, base_class in plugins:
                loaded_plugins[get_base_class_name(base_class)][level].append(
                        new_class)
    return loaded_plugins

class PluginManager(object):
    '''PluginManager is used to load and access spikepy plugins.'''
    def __init__(self, config_manager):
        self.config_manager = config_manager 
        self._loaded_plugins = None
        self.load()

    def load(self, **kwargs):
        '''Load or reload all plugins.'''
        self._loaded_plugins = load_all_plugins(**kwargs)

    @property
    def file_interpreters(self):
        '''All file_interpreters, regardles of level.'''
        result = []
        for level, plugins in self.loaded_plugins['file_interpreter'].items():
            result.extend(plugins)
        return result

    @property
    def detection_filters(self):
        """Plugins stored in a dict by level 'builtins'/'application'/'user'"""
        return self._get_filters_of_type('df')

    @property
    def extraction_filters(self):
        """Plugins stored in a dict by level 'builtins'/'application'/'user'"""
        return self._get_filters_of_type('ef')

    def _get_filters_of_type(self, provides_prefix):
        typed_filters = defaultdict(list)
        for category, filters in self.loaded_plugins['filtering'].items():
            for filter_ in filters:
                typed_filter = filter_.__class__()
                new_items = [item.replace('<stage_name>', provides_prefix)
                        for item in typed_filter.provides]
                typed_filter.provides = new_items
                typed_filters[category].append(typed_filter)
        return typed_filters

    @property
    def detectors(self):
        """Plugins stored in a dict by level 'builtins'/'application'/'user'"""
        return self.loaded_plugins['detection']

    @property
    def extractors(self):
        """Plugins stored in a dict by level 'builtins'/'application'/'user'"""
        return self.loaded_plugins['extraction']

    @property
    def clusterers(self):
        """Plugins stored in a dict by level 'builtins'/'application'/'user'"""
        return self.loaded_plugins['clustering']

    @property
    def supplementors(self):
        """Plugins stored in a dict by level 'builtins'/'application'/'user'"""
        return self.loaded_plugins['supplemental']

    @property
    def loaded_plugins(self):
        '''All loaded plugins, stored in a dict by type then level'''
        return self._loaded_plugins

