import json

import wx
from wx.lib.pubsub import Publisher as pub

from . import program_text as pt
from .utils import strip_unicode
from .look_and_feel_settings import lfs
from .save_strategy_dialog import SaveStrategyDialog
class StrategyManager(object):
    def __init__(self):
        self.strategies = None # strategies under management
        self.current_strategy = None # may not be under managament yet.

    @property
    def current_strategy(self)
        # always make sure it has most current name.
        self._current_strategy.name = self.get_strategy_name(
                                           self._current_strategy)
        return self._current_strategy

    @current_strategy.setter
    def current_strategy(self, value)
        self._current_strategy = value

    # --- ADD AND REMOVE STRATEGIES ---
    def add_strategy(self, strategy):
        if strategy not in self.strategies:
            self.strategies.append(strategy)
            pub.sendMessage(topic='STRATEGY_ADDED_TO_MANAGER',
                            data=strategy)

    def remove_strategy(self, strategy):
        try:  
            self.strategies.remove(strategy)
        except ValueError:
            raise ValueError('This strategy (%s) is not under management.' %
                             strategy.name)
        self._update_strategy_choices()

    # --- GET STRATEGIES UNDER MANAGEMENT ---
    def get_managed_strategy(self, strategy):
        '''
        If argument 'strategy' is a currently managed strategy, return the
            managed strategy.  Otherwise raise a ValueError.
        '''
        try:
            strategy_index = self.strategies.index[strategy]
            return self.strategies[strategy_index]
        except ValueError:
            raise ValueError('This strategy (%s) is not under management.' %
                             strategy.name)

    def get_strategies_with_same_methods_used(self, strategy):
        return_strategies = []
        for managed_strategy in self.strategies:
            if managed_strategy.methods_used == strategy.methods_used:
                return_strategies.append(managed_strategy)
        return return_strategies

    # --- NAME STRATEGIES ---
    def get_strategy_name(self, strategy):
        '''
        See if this strategy already is under management, if so return 
            its name.  Otherwise give this strategy an appropriate name.
        '''
        if strategy in self.strategies:
            managed_strategy = self.get_managed_strategy(strategy)
            return managed_strategy.name

        cousin_strategies = self.get_strategies_with_same_methods_used(strategy)
        if cousin_strategies:
            return make_strategy_name(cousin_strategies[0].methods_used_name,
                                      pt.CUSTOM_LC)

        return make_strategy_name(pt.CUSTOM_SC, pt.CUSTOM_LC)


