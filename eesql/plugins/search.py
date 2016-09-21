# Search Plugins
from .generic import BasePlugin, GenericPlugin, BaseShortcutPlugin, EESQLPluginException

class GenericSearchPlugin(GenericPlugin):
    """Convert EESQL into JSON and wrap into query attribute"""
    name = "Generic Search Plugin"
    description = "Generic EESQL to JSON conversion with wrapping into query attribute"

    def apply(self, verb, params):
        return { "query": super().apply(verb, params) }

class SearchShortcutPlugin(BaseShortcutPlugin):
    """
    Converts given value into a query_string query. Prefixes:
    ':': Use ES default as default operator (currently OR)
    '&': AND as default operator
    """
    name = "Search shortcut plugin"
    description = "Convert value into query_string query"

    def apply(self, prefix, value):
        res = { "query_string": { "query": value } }
        if prefix == "&":
            res["query_string"]["default_operator"] = "AND"
        return { "query": res }

class SortPlugin(BasePlugin):
    """
    Sort entries by addition of a 'sort' query option. Parameter s contains one or multiple field names.
    If suffixed with + or - the sort order is added explicitely (asc/desc).
    """
    name = "Search result sort plugin"
    description = "Sort search results"

    def __init__(self):
        super().__init__()
        self.sortfields = list()

    def appendField(self, field):
        if field.endswith("+"):
            self.sortfields.append({ field[:-1] : { "order": "asc" } })
        if field.endswith("-"):
            self.sortfields.append({ field[:-1] : { "order": "desc" } })
        else:
            self.sortfields.append(field)

    def apply(self, verb, params):
        try:
            fields = params["unnamed_list"]
        except KeyError:
            raise EESQLPluginException("Expression 'sort' requires list of fields")

        if len(fields) == 0:
            raise EESQLPluginException("List of fields of sort expression must not be empty")
        elif type(fields[0]) == list:
            raise EESQLPluginException("Only one list of fields in sort expression is allowed")

        for field in fields:
            self.appendField(field)

        return { "sort": self.sortfields }

class FieldFilterPlugin(BasePlugin):
    """Filter fields from search result"""
    name = "Filter fields from search result plugin"
    description = "Filters fields from search result documents"

    def apply(self, verb, params):
        try:
            fields = params["unnamed_list"]
        except KeyError:
            raise EESQLPluginException("Expression 'filter' requires list of fields")

        if len(fields) == 0:
            raise EESQLPluginException("List of fields of sort expression must not be empty")
        elif type(fields[0]) == list:
            raise EESQLPluginException("Only one list of fields in sort expression is allowed")

        return { "_source": fields }
