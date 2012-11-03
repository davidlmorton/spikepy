
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

    

