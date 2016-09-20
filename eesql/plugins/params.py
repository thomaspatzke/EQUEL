# Parameter class

class Parameter:
    """Key/Value or single parameter"""
    PARAM_FLAG = 1
    PARAM_KV   = 2
    
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        if value == None:   # Flag parameter
            self.type = self.PARAM_FLAG
        else:
            self.type = self.PARAM_KV

    def toJSON(self, flagdefault=True):
        if self.type == self.PARAM_FLAG:
            return { self.key: flagdefault }
        else:
            return { self.key: self.value }

class ParameterList(list):
    """Collection of parameters"""
    def __init__(self, params):
        """Takes a list of parameter parsing contexts and adds them to collection"""
        self.paramnames = list()
        for param in params:
            self.append(param.param)
            self.paramnames.append(param.param.key)

    def __contains__(self, param):
        return paramname in self.paramnames

    def __getitem__(self, paramname):
        if type(paramname) != str:
            return super().__getitem__(paramname)

        for param in self:
            if param.key == paramname:
                return param.value
        raise KeyError()

    def toJSON(self, flagdefault=True):
        """Generate JSON encoded data structure from parameters stored in collection."""
        res = dict()
        for param in self:
            res.update(param.toJSON(flagdefault))
        return res
