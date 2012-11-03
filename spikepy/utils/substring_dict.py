

class SubstringDict(dict):
    '''
        A dictionary whose elements can be fetched either by giving the full
    key or a unique subset of the key.  Raises a KeyError if the key provided
    isn't a unique subset of any key.
    '''
    def __getitem__(self, key):
        if key in self.keys():
            return dict.__getitem__(self, key)
        else:
            pkeys = []
            for skey in self.keys():
                if key in skey:
                    pkeys.append(skey)
            if len(pkeys) == 1:
                return dict.__getitem__(self, pkeys[0])
            else:
                raise KeyError("%s is an invalid key." % key)
