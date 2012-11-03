
import types
import traceback
import imp
import os
import uuid
from collections import defaultdict

from spikepy.developer.visualization import Visualization
from spikepy.developer.file_interpreter import FileInterpreter
from spikepy.developer.data_interpreter import DataInterpreter
from spikepy.developer.methods import FilteringMethod, \
        DetectionMethod, ExtractionMethod, \
        ClusteringMethod, AuxiliaryMethod

from spikepy.common.path_utils import get_data_dirs
from spikepy.utils.substring_dict import SubstringDict 
from spikepy.common.errors import *
from spikepy.common.warnings import warn

base_class_index = {'data_interpreter':  DataInterpreter,
                    'file_interpreter':  FileInterpreter,
                    'visualization':     Visualization,
                    'auxiliary':         AuxiliaryMethod,
                    'filtering':         FilteringMethod,
                    'detection':         DetectionMethod,
                    'extraction':        ExtractionMethod,
                    'clustering':        ClusteringMethod}

# --- UTILITY FUNCTIONS ---
def get_plugin_category(plugin):
    '''Return the base_class's category name given the class.'''
    for name, base_class in base_class_index.items():
        if issubclass(plugin.__class__, base_class):
            return name
    raise UnknownCategoryError("Couldn't find the category for %s" % 
            plugin.name)

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

def load_plugins_from_dir(plugin_dir, module_suffix):
    ''' Load all the plugins in the given <plugin_dir>.'''
    loaded_plugins = []
    if os.path.exists(plugin_dir):
        entries = os.listdir(plugin_dir)
        for e in entries:
            fullpath_e = os.path.join(plugin_dir, e)
            if should_load(fullpath_e):
                module_name = os.path.splitext(e)[0]
                unique_name = 'spikepy_plugin_%s_%s' % (module_name, 
                        module_suffix)

                # load the module
                fm_results = None
                try:
                    fm_results = imp.find_module(module_name, [plugin_dir]) 
                except ImportError:
                    pass
                if fm_results is not None:
                    try:
                        module=imp.load_module(unique_name, *fm_results)
                        loaded_plugins.extend(get_plugins_from_module(module, 
                                class_list=base_class_index.values()))
                    except:
                        print "Failed to load plugin '%s':" % module_name
                        traceback.print_exc()
    return loaded_plugins

def get_plugins_from_module(module, class_list=[]):
    '''
        Return the plugins defined in the <module> which inherit from
    any of the classes in <class_list>.
    Returns: A list of plugins
    '''
    results = []
    for name in dir(module):
        thing = getattr(module, name)
        is_class = isinstance(thing, types.TypeType)
        if is_class:
            is_subclass = issubclass(thing, tuple(class_list))
            if is_subclass and (thing not in class_list):
                try: 
                    plugin = thing()
                except TypeError:
                    raise PluginDefinitionError('Spikepy plugins must be instantiable with no arguments. %s violates this requirement.' % thing.name)
                results.append(plugin)
    return results
    
def load_all_plugins(data_dirs=None, module_suffix=None, **kwargs):
    '''Load file_interpreters and methods from all levels.'''
    if data_dirs is None:
        data_dirs = get_data_dirs(**kwargs)
    if module_suffix is None:
        module_suffix = str(uuid.uuid4()).replace('-','_')

    plugin_levels = {}
    loaded_plugins = defaultdict(SubstringDict)
    for level in ['builtins', 'application', 'user']:
        for plugin_type in ['file_interpreters', 'methods', 
                'data_interpreters', 'visualizations']:
            plugin_dir = data_dirs[level][plugin_type]
            plugins = load_plugins_from_dir(plugin_dir, module_suffix)
            for plugin in plugins:
                plugin_levels[plugin] = level
                category = get_plugin_category(plugin)
                if plugin.name in loaded_plugins[category].keys():
                    # already loaded this plugin.
                    existing_plugin = loaded_plugins[category][plugin.name]
                    existing_level = plugin_levels[existing_plugin]
                    warn('plugin "%s" loaded from "%s level" is replacing one loaded from "%s level".' % (plugin.name, level, existing_level))

                loaded_plugins[category][plugin.name] = plugin
    return loaded_plugins

class PluginManager(object):
    '''PluginManager is used to load and access spikepy plugins.'''
    def __init__(self, **kwargs):
        self._loaded_plugins = None
        self.load_plugins(**kwargs)

    def validate_strategy(self, strategy):
        '''
            Check to make sure all methods are valid plugins and that all
        settings are valid for those plugins.  Returns None if successful, 
        raises error if strategy is invalid.
        '''
        for stage_name, method_name in strategy.methods_used.items():
            plugin = self.find_plugin(stage_name, method_name)
            settings = strategy.settings[stage_name]
            plugin.validate_parameters(settings)

        for method_name, settings in strategy.auxiliary_stages.items():
            plugin = self.find_plugin('auxiliary', method_name)
            plugin.validate_parameters(settings)

    def load_plugins(self, **kwargs):
        '''Load or reload all plugins.'''
        self._loaded_plugins = load_all_plugins(**kwargs)

    @property
    def visualizations(self):
        return self.loaded_plugins['visualization']

    @property
    def file_interpreters(self):
        return self.loaded_plugins['file_interpreter']

    @property
    def data_interpreters(self):
        return self.loaded_plugins['data_interpreter']

    @property
    def detection_filters(self):
        return self._get_filters_of_type('df')

    @property
    def extraction_filters(self):
        return self._get_filters_of_type('ef')

    def _get_filters_of_type(self, provides_prefix):
        typed_filters = {}
        for filter_ in self.loaded_plugins['filtering'].values():
            typed_filter = filter_.__class__() # new instance
            new_items = [item.replace('<stage_name>', provides_prefix)
                    for item in typed_filter.provides]
            typed_filter.provides = new_items
            is_correct_type = False
            for pname in typed_filter.provides:
                if provides_prefix in pname:
                    is_correct_type = True
            if is_correct_type:
                typed_filters[typed_filter.name] = typed_filter
        return typed_filters

    @property
    def detectors(self):
        return self.loaded_plugins['detection']

    @property
    def extractors(self):
        return self.loaded_plugins['extraction']

    @property
    def clusterers(self):
        return self.loaded_plugins['clustering']

    @property
    def auxiliary_plugins(self):
        return self.loaded_plugins['auxiliary']

    @property
    def loaded_plugins(self):
        '''
        All loaded plugins, stored in a nested dict by category then name.
        '''
        return self._loaded_plugins

    def get_default_plugin(self, stage_name):
        defaults = {'detection_filter':'Infinite Impulse Response',
                        'detection':'Threshold',
                        'extraction_filter':'Copy Detection Filtering',
                        'extraction':'Spike Window',
                        'clustering':'K-means'}
        return self.find_plugin(stage_name, defaults[stage_name])

    def get_plugins_by_stage(self, stage_name):
        ''' Return a list of plugins from the stage with <stage_name>.  '''
        lsn = stage_name.lower().replace(' ', '_')
        lookup_index = {'detection_filter':self.detection_filters,
                        'detection':self.detectors,
                        'extraction_filter':self.extraction_filters,
                        'extraction':self.extractors,
                        'clustering':self.clusterers,
                        'auxiliary':self.auxiliary_plugins}
        if lsn not in lookup_index.keys():
            raise UnknownStageError(
                    'There is no stage "%s" (parsed from "%s").' % 
                    (lsn, stage_name))
        return lookup_index[lsn]

    def find_plugin(self, stage_name, plugin_name):
        stage_plugins = self.get_plugins_by_stage(stage_name)
        try:
            return stage_plugins[plugin_name]
        except KeyError:
            raise MissingPluginError(
                    'No plugin named "%s" could be found in stage "%s"'%
                    (plugin_name, stage_name))

    def get_data_interpreter(self, name):
        try:
            return self.data_interpreters[name]
        except KeyError:
            raise MissingPluginError(
                    'No data_interpreter named "%s" could be found'% stage_name)


plugin_manager = PluginManager()
        
        
        

