# Parameter class

class Parameter:
    """Key/Value, single parameter or unnamed list"""
    PARAM_FLAG = 1
    PARAM_KV   = 2
    PARAM_LIST = 3
    
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        if value == None:   # Flag parameter
            self.type = self.PARAM_FLAG
        elif key == None and type(value) == str:
            self.type = self.PARAM_KV
            self.key = "unnamed"
        elif key == None and type(value) == list:
            self.type = self.PARAM_LIST
            self.key = "unnamed_list"
        else:
            self.type = self.PARAM_KV

    def __str__(self):
        return "(%s: %s)" % (self.key, self.value)

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
        self.flags = list()
        for param in params:
            self.append(param.param)
            self.paramnames.append(param.param.key)

    def append(self, param):
        super().append(param)
        if param.type == param.PARAM_FLAG:
            self.flags.append(param.key)

    def __contains__(self, param):
        return param in self.paramnames

    def __getitem__(self, paramname):
        if type(paramname) != str:
            return super().__getitem__(paramname)

        lists = list()
        for param in self:      # first collect all occurrences of a parameter key
            if param.key == paramname:
                    lists.append(param.value)

        if len(lists) == 0:     # none found? exception!
            raise KeyError()
        elif len(lists) == 1:   # one found? return its value
            return lists[0]
        else:                   # else return all values as list
            return lists

    def __str__(self):
        res = ""
        for param in self:
            res += str(param) + ", "
        return res[:-2]

    def toJSON(self, flagdefault=True):
        """Generate JSON encoded data structure from parameters stored in collection."""
        res = dict()
        for param in self:
            res.update(param.toJSON(flagdefault))
        return res
