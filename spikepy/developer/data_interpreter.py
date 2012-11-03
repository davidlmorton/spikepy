
        return_dict = {}
        for trial in trials:
            filename = '%s__%s' % (trial.display_name, 
                    self.name.replace(' ', '_'))
            return_dict[trial.trial_id] = os.path.join(base_path, filename)
        return return_dict

    def is_available(self, trials):
        ''' 
            Return True if the trials supplied have all the requirements to 
        allow this data-interpreter to run.
        '''
        try:
            self._check_requirements(trials)
            return True
        except DataUnavailableError:
            return False

    def _check_requirements(self, trials):
        '''
            Raises DataUnavailableError if requirements are not met for this
        data_interpreter.  Returns None.
        '''
        for trial in trials:
            for req in self.requires:
                if not hasattr(trial, req):
                    raise DataUnavailableError(
                            "Trial '%s' does not have resource '%s'." % 
                            (trial.display_name, req))
                else:
                    resource = getattr(trial, req)
                    if resource.data is None:
                        raise DataUnavailableError(
                                "Trial '%s' has not yet set resource '%s'." % 
                                (trial.display_name, req))
                        

