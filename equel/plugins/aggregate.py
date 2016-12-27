# Aggregation Plugins
from .generic import BasePlugin, GenericPlugin, BaseShortcutPlugin, EQUELPluginException

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

    def apply(self, prefix, value, parser, ctx):
        return { self.translation[prefix][0]: { self.translation[prefix][1]: value } }

class AggregationKeywordsPlugin(BasePlugin):
    """
    Short keywords for commonly used aggregations. Currently only one parameter is accepted.
    """
    name = "Aggregation keywords plugin"
    description = "Short keywords for commonly used aggregations"
    translation = {     # translation table: keyword -> (aggregation, parametername)
            "groupby": ("terms", "field"),
            "add_sum": ("sum", "field"),
            "add_min": ("min", "field"),
            "add_max": ("max", "field"),
            "valuecount": ("value_count", "field"),
            }

    def apply(self, verb, params, parser, ctx):
        for field in params.flags:
            parser.aggs.add(None, { self.translation[verb][0]: { self.translation[verb][1]: field } })
