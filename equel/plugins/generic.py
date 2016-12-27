# Generic plugins

class EQUELPluginException(ValueError):
    """This exception is raised when a plugin fails in processing of an expression"""
    pass

class BasePlugin:
    """Main interfaces shared across all plugin types"""
    name = "Base Plugin"
    description = "Plugin base class"

    def __init__(self):
        """Constructor"""
        pass

    def apply(self, verb, params, parser, ctx):
        """
        Called every time the plugin is used and should return the expected return a dict that is merged into the request for search and aggregation plugins.
        The following parameters are passed:
        * the verb from the EQUEL expression
        * a dict of parameters
        * the current parser object
        * the parsing context of the parse tree node that triggered plugin invocation
        """
        pass

class BaseShortcutPlugin:
    """Main interfaces for shortcut plugins shared across all plugin types"""
    name = "Base Shortcut Plugin"
    description = "Shortcut plugin base class"

    def __init__(self):
        """Constructor"""
        pass

    def apply(verb, prefix, value, parser, ctx):
        """Called every time the plugin is used and should return a dict"""
        pass

class GenericPlugin(BasePlugin):
    """Generic EQUEL to JSON conversion, e.g. verb p1=v1 p2=v2 -> {"verb": {"p1": "v1", "p2": "v2" }}"""
    name = "Generic Plugin"
    description = "Generic EQUEL to JSON conversion"

    def apply(self, verb, params, parser, ctx):
        return { verb: params.toJSON() }
