
        if hasattr(self, '_run_thread'):
            self._run_thread.join()

    @property
    def is_running(self):
        if hasattr(self, '_run_thread'):
            return self._run_thread.is_alive()
        else:
            return False

    def run(self, stage_name=None, strategy=None,  
            message_queue=multiprocessing.Queue(),
            async=False):
        '''
            Run the given strategy (defaults to current_strategy), or a stage 
        from that strategy.  Results are placed into the appropriate 
        trial's resources.
        Inputs:
            strategy: A Strategy object.  If not passed, 
                    session.current_strategy will be used.
            stage_name: If passed, only that stage will be run.
            message_queue: If passed, will be populated with run messages.
            async: If True, processing will run in a separate thread.  This 
                    thread can be joined with session.join_run()
        '''
        if strategy is None or not isinstance(strategy, Strategy):
            strategy = self.current_strategy 

        # if still none, then abort run.
        if strategy is None:
            raise NoCurrentStrategyError("You must supply a strategy or set the session's current strategy.")
            
        self.process_manager.prepare_to_run_strategy(strategy, 
                stage_name=stage_name)

        self._run_thread = threading.Thread(
                target=self.process_manager.run_tasks,
                kwargs={'message_queue':message_queue})
        self._run_thread.start()
        if not async:
            self._run_thread.join()

    def get_default_strategy(self):
        methods_used = {}
        settings = {}
        for stage_name in stages.stages:
            plugin = self.plugin_manager.get_default_plugin(stage_name)
            methods_used[stage_name] = plugin.name
            settings[stage_name] = plugin.get_parameter_defaults()

        # add auxiliary stages
        auxiliary_stages = {}
        auxiliary_stages['Detection Spike Window'] = \
                {'pre_padding':5.0,
                 'post_padding':5.0,
                 'exclude_overlappers':False,
                 'min_num_channels':3,
                 'peak_drift':0.3}
        auxiliary_stages['Extraction Spike Window'] = \
                {'pre_padding':3.0,
                 'post_padding':6.0,
                 'exclude_overlappers':False,
                 'min_num_channels':3,
                 'peak_drift':0.3}
        auxiliary_stages['Resample after Detection Filter'] = \
                {'new_sampling_frequency':25000}
        auxiliary_stages['Resample after Extraction Filter'] = \
                {'new_sampling_frequency':25000}
        auxiliary_stages['Power Spectral Density (Pre-Filtering)'] =\
                {'frequency_resolution':5.0}
        auxiliary_stages['Power Spectral Density (Post-Detection-Filtering)'] =\
                {'frequency_resolution':5.0}
        auxiliary_stages['Power Spectral Density (Post-Extraction-Filtering)'] \
                = {'frequency_resolution':5.0}
        default_strategy = Strategy(methods_used=methods_used, 
                settings=settings, auxiliary_stages=auxiliary_stages)
        return default_strategy 

    # PRIVATE FNS
    def _files_opened(self, results):
        # Called after process_manager opens a file
        trials = []
        for result in results:
            if isinstance(result, Trial):
                trials.append(result)
            elif isinstance(result, Strategy):
                try:
                    self.strategy_manager.add_strategy(result)
                except: # may be a name conflict or something.
                    pass
                self.current_strategy = result
        self.trial_manager.add_trials(trials)


            





    
