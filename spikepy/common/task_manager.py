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
import uuid

class TaskManager(object):
    '''
        Manages a number of Tasks and allows you to get the ones
    ready to be run.
    '''
    def __init__(self):
        self._modifying_tasks = []
        self._non_modifying_tasks = []

    @property
    def num_tasks(self):
        return len(self._modifying_tasks) + len(self._non_modifying_tasks)

    @property
    def tasks(self):
        return self._modifying_tasks + self._non_modifying_tasks

    def __str__(self):
        str_list = ['TaskManager:']
        for task in self.tasks:
            str_list.append('    %s' % str(task))
        return '\n'.join(str_list)

    def remove_tasks(self):
        self._modifying_tasks = []
        self._non_modifying_tasks = []

    def pull_runnable_tasks(self):
        '''
            Return a list of (task, task_info) tuples for each runnable task 
        and remove those tasks from the organizer.
        '''
        results = []

        task_list = [task for task in self._stationary_tasks.values()]
        task_list += [task for task in self._non_stationary_tasks.values()]
        skipped_tasks = []
        impossible_tasks = []
        for task in task_list:
            all_provided_items = []
            for ttask in self._non_stationary_tasks.values():
                all_provided_items.extend(ttask.provides)
            can_run = True

            # do you require something that someone here will later provide?
            for req in task.requires:
                if req in all_provided_items:
                    can_run = False
                    break

            # do you require or provide something that is locked?
            if not task.is_ready:
                can_run = False

            # do you require something never set?
            if can_run:
                (co_task, co_task_info) = self.checkout_task(task)
                impossible = False
                for item in co_task.requires:
                    if item.data is None:
                        impossible = True

                if impossible:
                    co_task.skip()
                    impossible_tasks.append(co_task)
                elif co_task.would_generate_unique_results:
                    results.append((co_task, co_task_info))
                else:
                    co_task.skip()
                    skipped_tasks.append(co_task)
                
        return results, skipped_tasks, impossible_tasks 

    def checkout_task(self, task):
        task_found = False
        if task in self._modifying_tasks:
            self._modifying_tasks.remove(task)
            task_found = True
        elif task in self._non_modifying_tasks:
            self._non_modifying_tasks.remove(task)
            task_found = True

        if not task_found:
            raise TaskNotManagedError('Task not under management: %s' % 
                    str(task))

        return task.checkout()

    def add_task(self, new_task):
        ''' Add a task to the Manager. '''
        if new_task.modifies:
            self._modifying_tasks.append(new_task)
        else:
            self._non_modifying_tasks.append(new_task)

def change_info_matches(reference, sample):
    '''
    Return True if the sample change_info matches the reference.
    Only compares the following keys:
        'using'
        'with'
        'by'
    '''
    if not isinstance(reference, dict) or\
            not isinstance(sample, dict):
        return False
    for key in ['by','using','with']:
        if reference[key] != sample[key]:
            return False
    return True


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
    def modifies(self):
        '''
            Return the list of Resources that this task both requires and
        provides.
        '''
        return list(set(self.provides).intersection(set(self.requires))]

    @property
    def originates(self):
        '''
            Return the list of Resources that this task originates.  That is
        the list of Resources that this task provides but does not require.
        '''
        return list(set(self.provides) - set(self.requires))

    @property
    def provides(self):
        '''Return the Resource(s) this task provides after running.'''
        result = []
        for trial in self.trials:
            for resource_name in self.plugin.provides:
                result.append(getattr(trial, resource_name))
        return result

    @property
    def requires(self):
        '''Return the Resource(s) this task requires to run.'''
        result = []
        for trial in self.trials:
            for resource_name in self.plugin.requires:
                result.append(getattr(trial, resource_name))
        return result

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
                    raise TaskCreationError('This plugin provides %s, but that is a read-only attribute on trial %s.' % (resource_name, trial.trial_id))

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

    def get_run_info(self):
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
            raise DimensionalityError('The dimensionality of the %s of different trials do not match.  Instead of all being a single dimensionality your trials have %s with dimensionality as follows.  %s' % 
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

    def manually_set_data(self, data=None):
        '''
        Sets the data for this resource, bypassing the checkout-checkin system.
        '''
        if self._locked:
            raise ResourceLockedError(pt.RESOURCE_LOCKED % self.name)
        self._change_info = {'by':'Manually', 'at':datetime.datetime.now(), 
                'with':None, 'using':None, 'change_id':uuid.uuid4()}
        self._data = data

    def __hash__(self):
        return hash(self._id)

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
            raise ResourceLockedError(pt.RESOURCE_LOCKED % self.name)
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
            raise ResourceNotLockedError(pt.RESOURCE_NOT_LOCKED % self.name)
        else:
            if key == self._locking_key:
                if data_dict is not None:
                    self._commit_change_info(data_dict['change_info'], 
                            preserve_provenance)
                    self._data = data_dict['data']
                self._locking_key = None
                self._locked = False
            else:
                raise InvalidLockingKeyError(pt.RESOURCE_KEY_INVALID % 
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

    

