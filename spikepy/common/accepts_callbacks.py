from types import MethodType, FunctionType
from functools import wraps
from collections import defaultdict
import uuid

class accepts_callbacks(object):
    def __init__(self, f):
        self.f = f
        self._pre_callbacks = defaultdict(list)
        self._post_callbacks = defaultdict(list)
        self._callback_functions = {} 
        self._callback_use_target_status = {}
        self._callback_take_target_status = {}
        self._attached_object = None

    def __get__(self, obj, obj_type=None):
        self._attached_object = obj
        return MethodType(self, obj, obj_type)

    def register_pre(self, callback, priority=0, take_target=True, label=None):
        '''
        Registers the callback to be called before the target.
        Inputs:
            callback: The callback function that will be called before
                the target function is run.
            take_target: If true the callback function will accept the arguments
                that are supplied to the target function.  If False the 
                callback function will accept no arguments.
            priority: Higher priority callbacks are run first, ties are in 
                registration order.
                arguments provided to target.
            label: A name to call this callback, must be unique
                or none, if non-unique it will raise a RuntimeError.
                If None, a unique label will be automatically generated.
                NOTE: Callbacks can be unregistered using their label.
        Returns:
            label
        '''
        label = self._register(callback, priority, label, True)
        self._callback_take_target_status[label] = take_target
        return label

    def _register(self, callback, priority, label, pre):
        try:
            priority = int(priority)
        except:
            raise RuntimeError('Priority could not be cast into an integer.')

        if label is None:
            label = uuid.uuid4()

        if label in self._callback_functions.keys():
            raise RuntimeError('Callback with label="%s" already registered.' 
                    % label)
        else:
            self._callback_functions[label] = callback

        if pre:
            self._pre_callbacks[priority].append(label)
        else:
            self._post_callbacks[priority].append(label)
        return label

    def register_post(self, callback, priority=0, use_target=False, label=None):
        '''
        Registers the callback to be called after the target.
        Inputs:
            callback: The callback function that will be called before
                the target function is run.
            priority: Higher priority callbacks are run first,
                ties are in registration order.
            use_target: Use the results from the target function as inputs
                instead of the inputs to the target function.
            label: A name to call this callback, must be unique (and hashable)
                or None, if non-unique it will raise a RuntimeError.
                If None, a unique label will be automatically generated.
                NOTE: Callbacks can be unregistered using their label.
        Returns:
            label
        '''
        label = self._register(callback, priority, label, False)
        self._callback_use_target_status[label] = use_target
        return label

    def __call__(self, *args, **kwargs):
        if self._attached_object is not None:
            cb_args = args[1:] # skip over 'self' arg
        else:
            cb_args = args

        for priority in reversed(sorted(self._pre_callbacks.keys())):
            for label in self._pre_callbacks[priority]:
                if self._callback_take_target_status[label]:
                    self._callback_functions[label](*cb_args, **kwargs)
                else:
                    if self._attached_object:
                        self._callback_functions[label](args[0])
                    else:
                        self._callback_functions[label]()

        target_result = self.f(*args, **kwargs)

        for priority in reversed(sorted(self._post_callbacks.keys())):
            for label in self._post_callbacks[priority]:
                if self._callback_use_target_status[label]:
                    self._callback_functions[label](target_result)
                else:
                    self._callback_functions[label](*cb_args, **kwargs)

        return target_result
