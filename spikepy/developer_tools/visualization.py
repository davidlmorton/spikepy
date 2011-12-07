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
from spikepy.common.config_manager import config_manager as config
from spikepy.plotting.plot_panel import PlotPanel

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
    # one of 'detection_filtering', 'detection', 'extraction_filtering',
    #        'extraction', 'clustering', or 'summary' **only used with gui**
    found_under_tab = 'detection_filtering'

    def __init__(self):
        for resource_name in self.requires:
            self._change_ids[resource_name] = None 

    def plot(self, trial, figure, **kwargs):
        '''
            Plot the results from <trial> onto the <figure>.  This is most 
        likely all you'll need to redefine in your subclasses.
        '''
        raise NotImplementedError

    def _draw(self, trial, parent_panel=None):
        # determine if we should replot.
        should_plot = False
        for resource_name, old_change_id in self._change_ids:
            new_change_id = getattr(trial, resource_name).change_info[
                    'change_id']
            if new_change_id != old_change_id:
                should_plot = True
        if not should_plot:
            return

        # are we running within the gui?
        if parent_panel is not None:
            if not hasattr(self, '_plot_panel'):
                self._setup_plot_panel()
            
            self._plot_panel.figure.clear()
            self.plot(trial, self._plot_panel.figure)

            canvas = self._plot_panel.canvas
            canvas.draw()
        else:
            figure = pylab.figure()
            self.plot(trial, figure)
            pylab.show()

    def _setup_plot_panel(self):
        pc = config['gui']['plotting']
        self._plot_panel = PlotPanel(self, figsize=figsize,
                facecolor=pc['face_color'],
                edgecolor=pc['face_color'],
                toolbar_visible=toolbar_visible,
                dpi=pc['dpi'])
        
