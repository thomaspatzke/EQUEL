# Aggregation Plugins
from .generic import BasePlugin, GenericPlugin, BaseShortcutPlugin, EESQLPluginException

class AggregationShortcutPlugin(BaseShortcutPlugin):
    """
    Shortcuts to commonly used aggregations.
    """
    name = "Aggregation shortcut plugin"
    description = "Shortcuts to commonly used aggregations"
    translation = {     # translation table: prefix -> (aggregation, parametername)
            ":": ("terms", "field"),
            "+": ("sum", "field"),
            "<": ("min", "field"),
            ">": ("max", "field"),
            "#": ("value_count", "field"),
            }

    def apply(self, prefix, value):
        return { self.translation[prefix][0]: { self.translation[prefix][1]: value } }
