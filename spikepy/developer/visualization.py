
    # The name of the visualization
    name = ''

    # The resources that this visualization requires to generate results.
    requires = []

    # One of 'detection_filter', 'detection', 'extraction_filter',
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

    def _get_figure_size(self, trial):
        width = config['gui']['plotting']['plot_width_inches']
        height = config['gui']['plotting']['plot_height_inches']
        size = numpy.array([width, height])
        return size

    @property
    def pylab(self):
        if hasattr(self, '_pylab'):
            return self._pylab
        else:
            import pylab
            self._pylab = pylab
            return pylab

    @pylab.setter
    def pylab(self, value):
        self._pylab = value

    def _get_unmet_requirements(self, trial):
        '''
            Return a list of the resource names that this visualization
        requirs but the given trial does not have available.
        '''
        unmet_requirements = []
        for req_name in self.requires:
            if (hasattr(trial, req_name) and 
                    getattr(trial, req_name).data is not None):
                pass
            else:
                unmet_requirements.append(req_name)
        return unmet_requirements

    def _handle_unmet_requirements(self, parent_panel, unmet_requirements):
        '''
            Print onto the figure the list of unmet requirements.
        '''
        if parent_panel is not None:
            figure = parent_panel.plot_panel.figure
            figure.set_facecolor('white')
            figure.set_edgecolor('black')
            figure.clear()
        else:
            figsize = config.get_size('figure')
            figure = self.pylab.figure(figsize=figsize)
            figure.set_facecolor('white')
            figure.set_edgecolor('black')
            figure.canvas.set_window_title(self.name)

        msg = pt.CANNOT_CREATE_VISUALIZATION % \
                '\n'.join(unmet_requirements)
        figure.text(0.5, 0.5, msg, verticalalignment='center',
                horizontalalignment='center')
            
        if parent_panel is not None:
            figure.canvas.draw()
        else:
            self.pylab.show()

    def _handle_cannot_plot(self, parent_panel):
        '''
            Print onto the figure a message stating that the visualization
        couldn't be completed
        '''
        figure = parent_panel.plot_panel.figure
        figure.set_facecolor('white')
        figure.set_edgecolor('black')
        figure.clear()

        msg = pt.CANNOT_COMPLETE_VISUALIZATION
        figure.text(0.5, 0.5, msg, verticalalignment='center',
                horizontalalignment='center')
            
        figure.canvas.draw()

    def _handle_no_trial_passed(self, parent_panel):
        '''
            Print onto the figure a message stating that the visualization
        couldn't be completed because no trial was passed in.
        '''
        if parent_panel is not None:
            figure = parent_panel.plot_panel.figure
            figure.set_facecolor('white')
            figure.set_edgecolor('black')
            figure.clear()
        else:
            figsize = config.get_size('figure')
            figure = self.pylab.figure(figsize=figsize)
            figure.set_facecolor('white')
            figure.set_edgecolor('black')
            figure.canvas.set_window_title(self.name)

        msg = pt.NO_TRIAL_SELECTED 
        figure.text(0.5, 0.5, msg, verticalalignment='center',
                horizontalalignment='center')
            
        if parent_panel is not None:
            figure.canvas.draw()
        else:
            self.pylab.show()

    def draw(self, trial=None, parent_panel=None, **kwargs):
        '''
            Draw the visualization using the user-defined self._plot fn.
        '''
        if trial is None:
            self._handle_no_trial_passed(parent_panel)
            return

        unmet_requirements = self._get_unmet_requirements(trial)
        if unmet_requirements: 
            self._handle_unmet_requirements(parent_panel, unmet_requirements)
            return

        # are we running within the gui?
        fig_size = self._get_figure_size(trial)
        if parent_panel is not None:
            if trial.trial_id == self._last_drawn_trial_id:
                preserve_history = True
                parent_panel.plot_panel._save_history()
            else:
                self._last_drawn_trial_id = trial.trial_id
                preserve_history = False

            parent_panel.plot_panel.set_minsize(*fig_size)
            parent_panel.plot_panel.figure.set_figwidth(fig_size[0])
            parent_panel.plot_panel.figure.set_figheight(fig_size[1])
            utils.recursive_layout(parent_panel)
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
            parent_panel.plot_panel.set_minsize(*fig_size)
            figure = self.pylab.figure(figsize=figsize)
            figure.set_figwidth(fig_size[0])
            figure.set_figheight(fig_size[1])
            figure.canvas.set_window_title(self.name)
            self._plot(trial, figure, **kwargs)
            self.pylab.show()
            # reset change_ids so the visualization is forced to plot again
            #  next time.
            for resource_name in self.requires:
                self._change_ids[resource_name] = None 
