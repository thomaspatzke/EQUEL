from elasticsearch_dsl import Search
from .parser import EESQLParser
from eesql.plugins import generic, search
from .ant.eesqlParser import eesqlParser

class EESQLEngine:
    """Main class for EESQL usage"""

    # Plugin Types
    PT_SEARCH    = 0
    PT_AGGREGATE = 1
    PT_POSTPROC  = 2
    PT_OUTPUT    = 3

    # Default Plugins
    defaultPlugins = [
            (PT_SEARCH, ["fallback"], search.GenericSearchPlugin),
            (PT_SEARCH, ["shortcut"], search.SearchShortcutPlugin),
            (PT_SEARCH, ["sort"], search.SortPlugin),
            (PT_SEARCH, ["fields"], search.FieldFilterPlugin),
            ]

    def __init__(self, host="localhost", index="*"):
        """Initializes EESQL engine"""
        self.host = host
        self.index = index
        self.plugins = [dict(), dict(), dict(), dict()]
        self.registerDefaultPlugins()

    def initSearch(self):
        """Instantiates base elasticsearch_dsl Search object"""
        return Search(using=self.host).index(self.index)

    def parseEESQL(self, eesql, **kwargs):
        """Parse EESQL expression and return elasticsearch_dsl Search object according to the query expression"""
        parser = EESQLParser(self, search=self.initSearch())
        return parser.parse(eesql, **kwargs)

    def registerPlugin(self, plugintype, verbs, cls):
        """
        Register plugin class of given type for one or multiple verbsr.
        Default plugin (: prefixed) is verb 'default'.
        Fallback plugin that is chosen if no matching plugin was found is defined with 'fallback'.
        """
        if type(verbs) == str:
            self.plugins[plugintype][verb] = cls
        elif type(verbs) == list:
            for verb in verbs:
                self.plugins[plugintype][verb] = cls

    def registerDefaultPlugins(self):
        for plugin in self.defaultPlugins:
            self.registerPlugin(*plugin)

    def listPlugins(self):
        res = list()
        for plugintype in self.plugins:
            for pluginverb in plugintype:
                res.append(plugintype[pluginverb].name)
        return res

    class PluginNotFound(Exception):
        pass

    def resolvePlugin(self, type, verb):
        try:
            exprTypePlugins = self.plugins[type]
        except IndexError:
            raise ValueError("No plugins registered for given plugin type %d" % (type))

        try:
            plugin = exprTypePlugins[verb]
        except KeyError:
            try: 
                plugin = exprTypePlugins["fallback"]
            except KeyError:
                raise self.PluginNotFound("Request for plugin of type %d, verb '%s' can't be resolved" % (type, verb))
        return plugin()

    def resolveShortcutPlugin(self, type):
        try:
            exprTypePlugins = self.plugins[type]
        except IndexError:
            raise ValueError("No plugins registered for given plugin type %d" % (type))

        try:
            return exprTypePlugins["shortcut"]()
        except KeyError:
            raise self.PluginNotFound("No shortcut plugin of type %d registered" % (type))

    def getPluginTypeForContext(self, ctx):
        if type(ctx) in [eesqlParser.SearchExprContext, eesqlParser.FilterExprContext]:
            return self.PT_SEARCH
        elif type(ctx) == eesqlParser.AggregationExprContext:
            return self.PT_AGGREGATE
        elif type(ctx) == eesqlParser.PostprocExprContext:
            return self.PT_POSTPROC
        elif type(ctx) == eesqlParser.OutputExprContext:
            return self.PT_OUTPUT
        else:
            raise TypeError("Expression context type expected!")
