# Generic plugins

class EESQLPluginException(ValueError):
    """This exception is raised when a plugin fails in processing of an expression"""
    pass

class BasePlugin:
    """Main interfaces shared across all plugin types"""
    name = "Base Plugin"
    description = "Plugin base class"

    def __init__(self):
        """Constructor"""
        pass

    def apply(verb, params):
        """Called every time the plugin is used and should return a dict"""
        pass

class BaseShortcutPlugin:
    """Main interfaces for shortcut plugins shared across all plugin types"""
    name = "Base Shortcut Plugin"
    description = "Shortcut plugin base class"

    def __init__(self):
        """Constructor"""
        pass

    def apply(verb, prefix, value):
        """Called every time the plugin is used and should return a dict"""
        pass

class GenericPlugin(BasePlugin):
    """Generic EESQL to JSON conversion, e.g. verb p1=v1 p2=v2 -> {"verb": {"p1": "v1", "p2": "v2" }}"""
    name = "Generic Plugin"
    description = "Generic EESQL to JSON conversion"

    def apply(self, verb, params):
        return { verb: params.toJSON() }
