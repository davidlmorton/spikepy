
import datetime
import copy
import uuid

import numpy

from spikepy.common.scheduler import Scheduler, Operation

class TaskManager(object):
    '''
        Manages a number of Tasks and allows you to get the ones
    ready to be run.
    '''
    def __init__(self):
        self._scheduler = Scheduler()
        self._task_to_operation_index = {}
        self._operation_name_to_task_index = {}

    @property
    def tasks(self):
        return self._task_to_operation_index.keys()

    @property
    def num_tasks(self):
        return len(self.tasks)

    def remove_all_tasks(self):
        self._task_to_operation_index = {}
        self._operation_name_to_task_index = {}

    def remove_task(self, task):
        if task in self._task_to_operation_index.keys():
            operation = self._task_to_operation_index[task]
            del self._operation_name_to_task_index[operation.name]
            del self._task_to_operation_index[task]
        else:
            raise TaskError('Tried to remove a task that is not under management.')

    def add_root_task(self, root_task):
        removed_ops = self._scheduler.set_root_outputs(root_task.provided_ids)
        removed_tasks = [self._operation_name_to_task_index[op.name]
                for op in removed_ops]
        for task in removed_tasks:
            self.remove_task(task)
        return removed_tasks

    def add_task(self, new_task):
        # 1. make operation
        # 2. add operation into scheduler
        # 3. add task and operation to indecies

        # find a unique name for this operation.
        operation_name = new_task.plugin.name[:1] # TODO make shorter 
        if operation_name in self._operation_name_to_task_index.keys():
            operation_name += '_2'
        while operation_name in self._operation_name_to_task_index.keys():
            num = int(operation_name.split('_')[-1])
            operation_name = operation_name.replace('_%d' % num, '_%d' % (num+1))
            
        operation = Operation(new_task.required_ids, new_task.provided_ids,
                name=operation_name)
        self._scheduler.add_operation(operation)

        self._task_to_operation_index[new_task] = operation
        self._operation_name_to_task_index[operation_name] = new_task
    
    def get_ready_tasks(self):
        '''
            Return a list of runnable tasks. 
        '''
        potentials = self._scheduler.get_ready_operations()

        ready_tasks = []
        for op in potentials:
            task = self._operation_name_to_task_index[op.name]
            if task.is_ready:
                ready_tasks.append(task)

        return ready_tasks 

    def get_plot_dict(self):
        return self._scheduler.get_plot_dict()

    def checkout_task(self, task):
        if task not in self.tasks:
            raise TaskError('Task not under management: %s' % 
                    str(task))
        else:
            operation = self._task_to_operation_index[task]
            self._scheduler.start_operation(operation)
            return task.checkout()

    def complete_task(self, task, result=None):
        if task not in self.tasks:
            raise TaskError('Task not under management: %s' % 
                    str(task))
        else:
            operation = self._task_to_operation_index[task]
            self._scheduler.finish_operation(operation)
            self.remove_task(task)
            if result is not None:
                return task.complete(result)
            else:
                return task.skip()

    def __str__(self):
        str_list = ['TaskManager:']
        for task in self.tasks:
            str_list.append('    %s' % str(task))
        return '\n'.join(str_list)

class StageRootTask(object):
    def __init__(self, trials, plugins):
        self.trials = trials
        self.plugins = plugins
        self.provides = self._calculate_provides()

    def _calculate_provides(self):
        '''
            This should return the list of resources that are required by
        self.plugins but are not originated by them.
        '''
        # find the name of the resources that are required but not originated.
        originated_by_plugins = set()
        required_by_plugins = set()
        for p in self.plugins:
            originated_by_plugins.update(set(p.provides)-set(p.requires))
            required_by_plugins.update(set(p.requires))
        originated_by_root = required_by_plugins - originated_by_plugins

        provides = []
        unmet_requirements = []
        for trial in self.trials:
            for plugin in self.plugins:
                for requirement_name in originated_by_root:
                    if hasattr(trial, requirement_name) and\
                            getattr(trial, requirement_name) is not None:
                        provides.append(getattr(trial, requirement_name))
                    else:
                        unmet_requirements.append((requirement_name, 
                                trial.display_name))
        if unmet_requirements:
            raise UnmetRequirementsError(unmet_requirements)
        else:
            return provides

    @property
    def provided_ids(self):
        return [r.id for r in self.provides]


class RootTask(object):
    def __init__(self, trials):
        self.trials = trials

    @property
    def provides(self):
        result = []
        for trial in self.trials:
            for resource in trial.originates:
                result.append(resource)
        return result

    @property
    def provided_ids(self):
        return [r.id for r in self.provides]


class Task(object):
    '''
        Task objects combine a list of trials with a plugin and
    the kwargs that the plugin needs to run.
    '''
    def __init__(self, trials, plugin, plugin_category, plugin_kwargs={}):
        self.trials = trials
        trial_ids = [t.trial_id for t in trials]
        self.task_id = uuid.uuid4()
        self.plugin = plugin
        self.plugin_category = plugin_category
        self.plugin_kwargs = plugin_kwargs
        self.locking_keys = {}
        self._prepare_trials_for_task()
        self.trial_packing_index = {}

    def __str__(self):
        str_list = ['Task: plugin="%s"' % self.plugin.name]
        for trial in self.trials:
            str_list.append('        trial="%s"' % trial.display_name)
        return '\n'.join(str_list)

    @property
    def provides(self):
        '''Return the Resource(s) this task provides after running.'''
        result = []
        for trial in self.trials:
            for resource_name in self.plugin.provides:
                result.append(getattr(trial, resource_name))
        return result

    @property
    def provided_ids(self):
        return [r.id for r in self.provides]
        
    @property
    def requires(self):
        '''Return the Resource(s) this task requires to run.'''
        result = []
        for trial in self.trials:
            for resource_name in self.plugin.requires:
                result.append(getattr(trial, resource_name))
        return result

    @property
    def required_ids(self):
        return [r.id for r in self.requires]

    def _prepare_trials_for_task(self):
        '''
            If the trials do not have any of the Resources that the plugin
        provides, create it.
        '''
        for trial in self.trials:
            for resource_name in self.plugin.provides:
                if not hasattr(trial, resource_name):
                    trial.add_resource(Resource(resource_name))
                elif not isinstance(getattr(trial, resource_name), Resource):
                    raise TaskError('This plugin provides %s, but that is a read-only attribute on trial %s.' % (resource_name, trial.trial_id))

    @property
    def would_generate_unique_results(self):
        '''
        Return whether or not running this task would generate new
        results.
        '''
        if self.plugin.is_stochastic:
            return True
        else:
            old_results = self.provides
            new_change_info = self.change_info
            for old_result in old_results:
                for old_change_info in old_result.change_info:
                    checks = [change_info_matches(oci, new_change_info) 
                            for oci in old_result.change_info]
                    if True not in checks:
                        return True
        return False

    @property
    def change_info(self):
        return_dict = {}
        return_dict['by'] = self.plugin.name
        return_dict['with'] = self.plugin_kwargs
        u = []
        for rname in self.plugin.requires:
            pu = [(trial.trial_id, rname) for trial in self.trials]
            u.append(pu)
        return_dict['using'] = u
        return return_dict

    @property
    def is_ready(self):
        '''
            Return True if this task's requirements and resources it provides
        are all unlocked.
        '''
        items = self.requires + self.provides
        for item in items:
            if (hasattr(item, 'is_locked') and item.is_locked):
                return False
        return True

    def skip(self):
        for pname in self.plugin.provides:
            for trial in self.trials:
                item = getattr(trial, pname)
                key = self.locking_keys[item]
                item.checkin(key=key)

    def complete(self, result):
        '''
        Complete the task with the given result.  Put the proper data into the 
        appropriate resources as well as update the data-provenance.
        '''
        change_info = self.change_info
        for pname, presult in zip(self.plugin.provides, result):
            # unpack/unpool the results (if needed)
            if self.plugin.is_pooling: 
                if self.plugin.silent_pooling:
                    if self.plugin.unpool_as is None:
                        presult = [presult for t in self.trials]
                    else:
                        unpool_as = self.plugin.unpool_as[
                                self.plugin.provides.index(pname)]
                        if unpool_as is not None:
                            presult = self._unpack_pooled_resource(unpool_as, 
                                    presult)
            else:
                presult = [presult for t in self.trials]

            # update the data provenance
            for trial, tresult in zip(self.trials, presult):
                item = getattr(trial, pname)
                key = self.locking_keys[item]
                preserve_provenance = pname in self.plugin.requires and\
                                      pname in self.plugin.provides
                data_dict = {'data':tresult,
                             'change_info':change_info}
                item.checkin(data_dict, key=key, 
                        preserve_provenance=preserve_provenance) 

    def checkout(self):
        '''
        Return a dictionary with the stuff needed to run.
        '''
        run_info = {}
        run_info['task_id'] = self.task_id
        run_info['plugin_info'] = {'stage':self.plugin_category, 
                'name':self.plugin.name}
        run_info['args'] = self._get_args()
        run_info['kwargs'] = self.plugin_kwargs

        # check out and keep track of locking keys for what task provides.
        for item in self.provides:
            co = item.checkout()
            self.locking_keys[item] = co['locking_key']
        return run_info

    def _get_args(self):
        '''Return the data we require as arguments to run.'''
        arg_list = []
        for requirement_name in self.plugin.requires:
            if self.plugin.is_pooling:
                arg_list.append(self._pack_pooled_resource(requirement_name))
            else:
                trial = self.trials[0]
                requirement = getattr(trial, requirement_name).data
                arg_list.append(requirement)
        return arg_list
        
    def _pack_pooled_resource(self, resource_name): 
        '''
        Pack the resources from all of self.trials into a single numpy array.
        '''
        if not self.plugin.silent_pooling:
            result = []
            for trial in self.trials:
                resource = getattr(trial, resource_name).data
                result.append(resource)
            return result
            
        # count total length
        ndim_set = set()
        total_len = 0
        for trial in self.trials:
            resource = getattr(trial, resource_name).data
            if hasattr(resource, 'ndim'):
                ndim = resource.ndim
            else:
                ndim = 0
            ndim_set.add(ndim)
            if hasattr(resource, '__len__'):
                total_len += len(resource)
            else:
                total_len += 1
        if len(ndim_set) != 1:
            raise TaskError('The dimensionality of the %s of different trials do not match.  Instead of all being a single dimensionality your trials have %s with dimensionality as follows.  %s' % 
                (resource_name, resource_name, 
                str(list(num_feature_dimensionalities))))

        # figure out begin and end for later packing/unpacking.
        begin = 0
        end = 0
        self.trial_packing_index = {}
        for trial in self.trials:
            resource = getattr(trial, resource_name).data
            if hasattr(resource, '__len__'):
                end = begin + len(resource)
            else:
                end = begin + 1
            self.trial_packing_index[str(trial.trial_id)+
                    resource_name] = [begin, end]
            begin = end

        # pack it up
        if ndim == 0:
            pooled_resource = [getattr(trial, resource_name).data 
                    for trial in self.trials]
            try:
                pooled_resource = numpy.array(pooled_resource)
            except ValueError: #can't be made into an array.
                raise ValueError('Cannot perform silent_pooling on "%s" because it cannot be made into a numpy array' % resource_name)
        elif ndim == 1:
            pooled_resource = numpy.empty(total_len, dtype=resource.dtype)
            for trial in self.trials:
                resource = getattr(trial, resource_name).data
                begin, end = self.trial_packing_index[
                        str(trial.trial_id)+resource_name]
                pooled_resource[begin:end] = resource
        elif ndim >= 2:
            pooled_shape = (total_len, ) + resource.shape[1:]
            pooled_resource = numpy.empty(pooled_shape, 
                    dtype=resource.dtype)
            for trial in self.trials:
                resource = getattr(trial, resource_name).data
                begin, end = self.trial_packing_index[
                        str(trial.trial_id)+resource_name]
                pooled_resource[begin:end] = resource
        return pooled_resource
            
    def _unpack_pooled_resource(self, resource_name, pooled_resource):
        results = []
        for trial in self.trials:
            begin, end = self.trial_packing_index[
                    str(trial.trial_id)+resource_name]
            results.append(pooled_resource[begin:end])
        return results


class Resource(object):
    """
        The Resource class handles locking(checkout) and unlocking(checkin)
    allowing only one process to access the data at a time.  Additionally,
    resources store metadata about how and when they were last changed and 
    by whom.
    """
    def __init__(self, name, data=None):
        self.name = name
        self._id = uuid.uuid4()
        self._locked = False
        self._locking_key = None
        self.manually_set_data(data)

    @property
    def id(self):
        return self._id

    def manually_set_data(self, data=None):
        '''
        Sets the data for this resource, bypassing the checkout-checkin system.
        '''
        if self._locked:
            raise ResourceError(pt.RESOURCE_LOCKED % self.name)
        self._change_info = {'by':'Manually', 'at':datetime.datetime.now(), 
                'with':None, 'using':None, 'change_id':uuid.uuid4()}
        self._data = data

    @classmethod
    def from_dict(cls, info_dict):
        name = info_dict['name']
        data = info_dict['data']
        change_info = info_dict['change_info']
        new_resource = cls(name, data=data)
        new_resource._change_info = change_info
        return new_resource

    @property
    def as_dict(self):
        info_dict = {'name':self.name}
        info_dict['data'] = self.data
        info_dict['change_info'] = self.change_info
        return info_dict

    def checkout(self):
        '''
            Check out this resource, locking it so that noone else can check it
        out until you've checked it in via <checkin>.
        '''
        if self.is_locked:
            raise ResourceError(pt.RESOURCE_LOCKED % self.name)
        else:
            self._locking_key = uuid.uuid4()
            self._locked = True
            return {'name':self.name, 
                    'data':self._data, 
                    'locking_key':self._locking_key}

    def checkin(self, data_dict=None, key=None, preserve_provenance=False):
        '''
            Check in resource so others may use it.  If <data_dict> is
        supplied it should be a dictionary with:
            'data': the data 
            'change_info': see docstring on self.change_info
                           NOTE: This function adds 'at' and 'change_id' to
                                 'change_info' automatically, so those can
                                 be left out of the 'change_info' dictionary.
        '''
        if not self.is_locked:
            raise ResourceNotError(pt.RESOURCE_NOT_LOCKED % self.name)
        else:
            if key == self._locking_key:
                if data_dict is not None:
                    self._commit_change_info(data_dict['change_info'], 
                            preserve_provenance)
                    self._data = data_dict['data']
                self._locking_key = None
                self._locked = False
            else:
                raise ResourceError(pt.RESOURCE_KEY_INVALID % 
                        (str(key), self.name))

    def _commit_change_info(self, change_info, preserve_provenance):
        assert "by" in change_info.keys()
        assert isinstance(change_info['with'], dict)
        assert isinstance(change_info['using'], list)

        # so doesn't point back to strategy's settings dict.
        change_info['with'] = copy.copy(change_info['with']) 

        change_info['at'] = datetime.datetime.now()
        change_info['change_id'] = uuid.uuid4()

        if preserve_provenance:
            if isinstance(self._change_info, list):
                self._change_info.append(change_info)
            else:
                self._change_info = [self._change_info, change_info]
        else:
            self._change_info = [change_info]

    @property
    def is_locked(self):
        return self._locked

    @property
    def data(self):
        return self._data

    @property
    def change_info(self):
        '''
            Information describing how this resource was changed. This is a 
        listof dicts (one for each change).
        Keys:
            by : string, name of the plugin function that changed this resource.
            at : datetime, the date/time of the last change to this resource.
            with : dict, a dictionary of keyword args for the <by> function.
            using : list, a list of (trial_id, resource_name) that 
                    were used as arguments to the <by> function.
            change_id : a uuid generated when this resource was last changed.
        '''
        return self._change_info

    

