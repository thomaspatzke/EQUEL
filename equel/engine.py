from elasticsearch import Elasticsearch
from .parser import EQUELParser
from equel.plugins import generic, search, aggregate, output
from .ant.equelParser import equelParser
from antlr4 import InputStream, FileStream
import json

class EQUELEngine:
    """Main class for EQUEL usage"""

    # Plugin Types
    PT_QUERYSTRING = 0
    PT_SEARCH      = 1
    PT_AGGREGATE   = 2
    PT_POSTPROC    = 3
    PT_OUTPUT      = 4

    # Default Plugins
    defaultPlugins = [
            (PT_QUERYSTRING, ["fallback"], search.ESQueryStringPlugin),
            (PT_SEARCH, ["fallback"], search.GenericSearchPlugin),
            (PT_SEARCH, ["shortcut"], search.SearchShortcutPlugin),
            (PT_SEARCH, ["sort"], search.SortPlugin),
            (PT_SEARCH, ["fields"], search.FieldFilterPlugin),
            (PT_SEARCH, ["nest"], search.NestQueryPlugin),
            (PT_SEARCH, ["script"], search.ScriptQueryPlugin),
            (PT_SEARCH, ["scriptfield"], search.ScriptFieldPlugin),
            (PT_AGGREGATE, ["fallback"], generic.GenericPlugin),
            (PT_AGGREGATE, ["shortcut"], aggregate.AggregationShortcutPlugin),
            (PT_AGGREGATE, ["groupby", "add_sum", "add_min", "add_max", "valuecount"], aggregate.AggregationKeywordsPlugin),
            (PT_OUTPUT, ["plain"], output.BaseOutputPlugin),
            (PT_OUTPUT, ["text"], output.TextOutputPlugin),
            ]
    defaultOutput = output.BaseOutputPlugin

    def __init__(self, host="localhost", index=""):
        """Initializes EQUEL engine"""
        self.host = host
        self.index = index
        self.plugins = [dict(), dict(), dict(), dict(), dict()]
        self.registerDefaultPlugins()

    def parseEQUEL(self, equel, inputclass=InputStream, **kwargs):
        """Parse EQUEL expression and return elasticsearch_dsl Search object according to the query expression"""
        inp = inputclass(equel)
        parser = EQUELParser(self)
        parsetree = parser.parse(inp)
        return EQUELRequest(parsetree, self)

    def parseEQUELFile(self, filename, **kwargs):
        return self.parseEQUEL(filename, FileStream, **kwargs)

    def registerPlugin(self, plugintype, verbs, cls):
        """
        Register plugin class of given type for one or multiple verbsr.
        Default plugin (: prefixed) is verb 'default'.
        Fallback plugin that is chosen if no matching plugin was found is defined with 'fallback'.
        """
        if verbs == None:
            self.plugins[plugintype] = cls
        elif type(verbs) == str:
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

    def resolveQueryStringPlugin(self):
        return self.plugins[self.PT_QUERYSTRING]["fallback"]()

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
        if type(ctx) in [equelParser.SearchExprContext, equelParser.FilterExprContext]:
            return self.PT_SEARCH
        elif type(ctx) == equelParser.AggregationExprContext:
            return self.PT_AGGREGATE
        elif type(ctx) == equelParser.PostprocExprContext:
            return self.PT_POSTPROC
        elif type(ctx) == equelParser.OutputExprContext:
            return self.PT_OUTPUT
        else:
            raise TypeError("Expression context type expected!")

class EQUELRequest:
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
        result = EQUELResult(es.search(index=self.engine.index, body=self.jsonQuery(), *args, **kwargs))
        for outputname in self.output:
            outputplugin = self.output[outputname]
            result.addOutput(outputname, outputplugin)
        return result

class EQUELResult:
    """Result of an EQUEL query"""
    def __init__(self, result):
        """Creates a result object from a result body"""
        self.result = result
        self.outputs = dict()

    def addOutput(self, name, outputPlugin):
        self.outputs[name] = outputPlugin.render(self)

class EQUELOutput:
    """Result from an output plugin."""
    TYPE_TEXT = 1
    TYPE_HTML = 2
    TYPE_IMAGE = 3

    textTypes = { TYPE_TEXT, TYPE_HTML }
    binaryTypes = { TYPE_IMAGE }

    def __init__(self, type, initStreams=['default']):
        """Inititalize output object with type."""
        self.type = type
        if type in self.textTypes:
            self.initContent = ''
        else:
            self.initContent = b''
        self.streams = dict()
        self.streamlist = list()
        for s in initStreams:
            self.initStream(s)
        if len(initStreams) > 0:
            self.currentStream = initStreams[0]
        else:
            self.currentStream = None

    def initStream(self, name):
        """Initialize output stream with default initial content for this type."""
        self.streams[name] = self.initContent
        self.streamlist.append(name)
        self.selectStream(name)

    def selectStream(self, name):
        self.currentStream = name

    def append(self, content, stream=None):
        """Append content to current or named output stream."""
        if stream == None:
            stream = self.currentStream
        self.streams[stream] += content

    def appendLine(self, content, stream=None):
        self.append(content + "\n", stream)

    def __getitem__(self, key):
        return self.streams[key]

    def __iter__(self):
        return iter(self.streamlist)
