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
import traceback
import sys

from spikepy.common.config_manager import config_manager as config
from spikepy.common import program_text as pt
from spikepy.common.valid_types import ValidType

class Visualization(object):
    """
    This class should be subclassed in order for developers to add a new
visualization to spikepy (non-interactive plots and graphs and such).
There is no need ot instantiate (create an object from) the subclass,
spikepy will handle that internally.  Therefore it is important to have an
__init__ method that requires no arguments.
    """
    name = ''
    requires = []
    # one of 'detection_filter', 'detection', 'extraction_filter',
    #        'extraction', 'clustering', or 'summary' **only used with gui**
    found_under_tab = 'detection_filter'

    def __init__(self):
        self._change_ids = {}
        for resource_name in self.requires:
            self._change_ids[resource_name] = None 
        self._last_drawn_trial_id = None

    def _plot(self, trial, figure, **kwargs):
        '''
            Plot the results from <trial> onto the <figure>.  This is most 
        likely all you'll need to redefine in your subclasses.
        '''
        raise NotImplementedError

    def _get_unmet_requirements(self, trial):
        unmet_requirements = []
        for req_name in self.requires:
            if (hasattr(trial, req_name) and 
                    getattr(trial, req_name).data is not None):
                pass
            else:
                unmet_requirements.append(req_name)
        return unmet_requirements

    def _handle_unmet_requirements(self, parent_panel, unmet_requirements):
        if parent_panel is not None:
            figure = parent_panel.plot_panel.figure
            figure.clear()
        else:
            import pylab
            figsize = config.get_size('figure')
            figure = pylab.figure(figsize=figsize)
            figure.canvas.set_window_title(self.name)

        msg = pt.CANNOT_CREATE_VISUALIZATION % \
                '\n'.join(unmet_requirements)
        figure.text(0.5, 0.5, msg, verticalalignment='center',
                horizontalalignment='center')
            
        if parent_panel is not None:
            figure.canvas.draw()
        else:
            pylab.show()

    def _handle_cannot_plot(self, parent_panel):
        figure = parent_panel.plot_panel.figure
        figure.clear()

        msg = pt.CANNOT_COMPLETE_VISUALIZATION
        figure.text(0.5, 0.5, msg, verticalalignment='center',
                horizontalalignment='center')
            
        figure.canvas.draw()

    def _handle_no_trial_passed(self, parent_panel):
        if parent_panel is not None:
            figure = parent_panel.plot_panel.figure
            figure.clear()
        else:
            import pylab
            figsize = config.get_size('figure')
            figure = pylab.figure(figsize=figsize)
            figure.canvas.set_window_title(self.name)

        msg = pt.NO_TRIAL_SELECTED 
        figure.text(0.5, 0.5, msg, verticalalignment='center',
                horizontalalignment='center')
            
        if parent_panel is not None:
            figure.canvas.draw()
        else:
            pylab.show()

    def draw(self, trial=None, parent_panel=None, **kwargs):
        if trial is None:
            self._handle_no_trial_passed(parent_panel)
            return

        unmet_requirements = self._get_unmet_requirements(trial)
        if unmet_requirements: 
            self._handle_unmet_requirements(parent_panel, unmet_requirements)
            return

        # are we running within the gui?
        if parent_panel is not None:
            if trial.trial_id == self._last_drawn_trial_id:
                preserve_history = True
                parent_panel.plot_panel._save_history()
            else:
                self._last_drawn_trial_id = trial.trial_id
                preserve_history = False

            parent_panel.plot_panel.clear()
            try:
                self._plot(trial, parent_panel.plot_panel.figure, **kwargs)
                canvas = parent_panel.plot_panel.canvas

                if preserve_history:
                    parent_panel.plot_panel._restore_history()
                canvas.draw()
            except:
                exc_info = sys.exc_info()
                traceback.print_exception(exc_info[0], exc_info[1],
                        exc_info[2], 100)
                self._handle_cannot_plot(parent_panel)
        else:
            import pylab
            figsize = config.get_size('figure')
            figure = pylab.figure(figsize=figsize)
            figure.canvas.set_window_title(self.name)
            self._plot(trial, figure, **kwargs)
            pylab.show()
            # reset change_ids so the visualization is forced to plot again
            #  next time.
            for resource_name in self.requires:
                self._change_ids[resource_name] = None 

    def get_parameter_attributes(self):
        ''' Return a dictionary of ValidType attributes. '''
        attrs = {}
        attribute_names = dir(self)
        for name in attribute_names:
            value = getattr(self, name)
            if isinstance(value, ValidType):
                attrs[name] = value
        return attrs
    
    def get_parameter_defaults(self):
        ''' Return a dictionary containing the default parameter values.  '''
        kwargs = {}
        for attr_name, attr in self.get_parameter_attributes().items():
            kwargs[attr_name] = attr()
        return kwargs

    def validate_parameters(self, parameter_dict):
        '''
            Attempts to validate parameters in a dictionary.  If parameters are 
        invalid an exception is raised.  If parameters are valid, None is 
        returned.
        '''
        for key, value in parameter_dict.items():
            getattr(self, key)(value)
        
