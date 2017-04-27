# Aggregation Plugins
from .generic import BasePlugin, GenericPlugin, BaseShortcutPlugin, EQUELPluginException

class GenericAggregationPlugin(GenericPlugin):
    """Extends generic EQUEL to JSON conversion by aggregation-specific aspects"""
    name = "Generic Aggregation Plugin"
    description = "Generic EQUEL aggregation to JSON conversion"

    def apply(self, verb, *args, **kwargs):
         res = super().apply(verb, *args, **kwargs)
         try:       # convert order parameter into ES order JSON
             order = res[verb]["order"]
             direction = "asc"
             if order[-1] == "-":
                 order = order[:-1]
                 direction = "desc"
             elif order[-1] == "+":
                 order = order[:-1]
                 direction = "asc"
             res[verb]["order"] = { order: direction }
         except KeyError:   # no order given
             pass
         return res

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
            "~": ("cardinality", "field"),
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

class FilterAggregationPlugin(GenericAggregationPlugin):
    """Filter aggregation with support for simple queries"""
    name = "Filter Aggregation Plugin"
    description = "Parameter 'querytype' defines query type (default: query_string)"

    def apply(self, verb, *args, **kwargs):
        res = super().apply(verb, *args, **kwargs)
        try:
            querytype = res["filter"]["querytype"]
            del res["filter"]["querytype"]
        except KeyError:
            querytype = "query_string"

        res["filter"] = { querytype: res["filter"] }
        return res
