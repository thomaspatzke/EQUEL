from elasticsearch import Elasticsearch
from .parser import EESQLParser
from eesql.plugins import generic, search, aggregate, output
from .ant.eesqlParser import eesqlParser
from antlr4 import InputStream, FileStream
import json

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
            (PT_AGGREGATE, ["fallback"], generic.GenericPlugin),
            (PT_AGGREGATE, ["shortcut"], aggregate.AggregationShortcutPlugin),
            (PT_AGGREGATE, ["groupby", "add_sum", "add_min", "add_max", "valuecount"], aggregate.AggregationKeywordsPlugin),
            (PT_OUTPUT, ["plain"], output.BaseOutputPlugin),
            (PT_OUTPUT, ["text"], output.TextOutputPlugin),
            ]
    defaultOutput = output.BaseOutputPlugin

    def __init__(self, host="localhost", index=""):
        """Initializes EESQL engine"""
        self.host = host
        self.index = index
        self.plugins = [dict(), dict(), dict(), dict()]
        self.registerDefaultPlugins()

    def parseEESQL(self, eesql, inputclass=InputStream, **kwargs):
        """Parse EESQL expression and return elasticsearch_dsl Search object according to the query expression"""
        inp = inputclass(eesql)
        parser = EESQLParser(self)
        parsetree = parser.parse(inp)
        return EESQLRequest(parsetree, self)

    def parseEESQLFile(self, filename, **kwargs):
        return self.parseEESQL(filename, FileStream, **kwargs)

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

class EESQLRequest:
    def __init__(self, parsetree, engine):
        self.query = parsetree.query
        self.postproc = parsetree.postproc
        self.output = parsetree.output
        if self.output == None:
            self.output = { "default": engine.defaultOutput() }
        self.engine = engine

    def jsonQuery(self, **kwargs):
        return json.dumps(self.query, **kwargs)

    def execute(self, *args, **kwargs):
        """Instantiates base elasticsearch_dsl Search object"""
        es = Elasticsearch(hosts=self.engine.host)
        res = EESQLResult(es.search(index=self.engine.index, body=self.jsonQuery(), *args, **kwargs))
        for outputname in self.output:
            outputplugin = self.output[outputname]
            res.addOutput(outputname, outputplugin.render(res))
        return res

class EESQLResult:
    """Result of an EESQL query"""
    def __init__(self, result):
        """Creates a result object from a result body"""
        self.result = result
        self.outputs = dict()

    def addOutput(self, name, output):
        self.outputs[name] = output

