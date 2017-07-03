from elasticsearch import Elasticsearch
from .parser import EQUELParser
from equel.plugins import generic, search, aggregate, output
from .ant.equelParser import equelParser
from antlr4 import InputStream, FileStream
import arrow
import json
import re

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
            (PT_SEARCH, ["timerange"], search.TimeRangePlugin),
            (PT_AGGREGATE, ["fallback"], aggregate.GenericAggregationPlugin),
            (PT_AGGREGATE, ["shortcut"], aggregate.AggregationShortcutPlugin),
            (PT_AGGREGATE, ["groupby", "add_sum", "add_min", "add_max", "valuecount"], aggregate.AggregationKeywordsPlugin),
            (PT_AGGREGATE, ["filter"], aggregate.FilterAggregationPlugin),
            (PT_OUTPUT, ["plain"], output.BaseOutputPlugin),
            (PT_OUTPUT, ["text"], output.TextOutputPlugin),
            (PT_OUTPUT, ["csv"], output.CSVOutputPlugin),
            ]
    defaultOutput = output.BaseOutputPlugin

    def __init__(self, host="localhost", index="*", timeout=60, timerange=None):
        """Initializes EQUEL engine"""
        self.host = host
        self.index = index
        self.timeout = timeout
        self.plugins = [dict(), dict(), dict(), dict(), dict()]
        self.registerDefaultPlugins()
        self.setDefaultTimeRange(timerange)

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

    def setDefaultTimeRange(self, t):
        """Set default time range. All requests are restrcited to the time frame and field given in t."""
        if isinstance(t, (EQUELTimeRange, type(None))):
            self.timerange = t
        else:
            raise TypeError("Expected EQUELTimeRange")

class EQUELRequest:
    def __init__(self, parsetree, engine):
        self.query = parsetree.query
        self.postproc = parsetree.postproc
        self.output = parsetree.output
        if self.output == {}:
            self.output = { "default": engine.defaultOutput() }
        self.engine = engine

    def jsonQuery(self, **kwargs):
        if self.engine.timerange:
            return json.dumps(self.engine.timerange.wrapQuery(self.query), **kwargs)
        else:
            return json.dumps(self.query, **kwargs)

    def execute(self, *args, **kwargs):
        """Instantiates base elasticsearch_dsl Search object"""
        es = Elasticsearch(hosts=self.engine.host, timeout=self.engine.timeout)
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

    def write(self, content):
        """Alias for .append() to make it compatible to functions that expect this method."""
        self.append(content)

    def appendLine(self, content, stream=None):
        self.append(content + "\n", stream)

    def __getitem__(self, key):
        return self.streams[key]

    def __iter__(self):
        return iter(self.streamlist)

class EQUELTimeRange:
    """Time range used to restrict queries"""
    import arrow
    RELOP_NEGATIVE_OFFSET = "-"
    RELOP_AROUND = "~"
    units = {
            "s": "seconds",
            "m": "minutes",
            "h": "hours",
            "d": "days",
            "w": "weeks",
            "mon": "months",
            "y": "years"
            }

    def __init__(self, tfrom, tto=None, tz=None, estz=None, field="@timestamp"):
        """
        Initialize time range object with:

        * tfrom: start date/time as string that gets parsed. This can also be:
            * a relative time value like -7d. In this case, format is ignored and it is calculated relative to the end time. Supported time units
              are: (s)econds, (min)utes, (h)ours, (d)ay, (w)eeks, (m)onths and (y)ears.
            * an "around" expression like ~5m.

        Optional:
        * tto: end date/time. Current if not given. May be a relative expression like +15min similar to tfrom relative time values
        * tz: timezone as string, local timezone if not given.
        * estz: target timezone as string. All times are converted into this time zone. No conversion if not given.
        * field: ES field name, by default @timestamp.
        """
        
        lt = arrow.now(tz)
        tz = lt.tzinfo
        relto_parsed = False

        # end time
        if tto:
            relto_parsed = re.match("^\\+(\d+)([shdwmy]|mon)$", tto)
            if not relto_parsed:    # if relative expression is given, postpone until from time is parsed
                self.tto = arrow.get(tto).replace(tzinfo=tz)
            else:
                self.tto = arrow.get(tto).replace(tzinfo=tz)
        else:   # if not given, take current time
            self.tto = lt

        # start time
        relfrom_parsed = re.match("^([~-])(\d+)([shdwmy]|mon)$", tfrom)
        if relfrom_parsed:
            if relto_parsed:    # raise exception if from and to time are relative
                raise ValueError("Only one time from a range may be relative")

            op = relfrom_parsed.group(1)
            num = int(relfrom_parsed.group(2))
            unit = relfrom_parsed.group(3)
            if op == self.RELOP_NEGATIVE_OFFSET:    # negative offset
                unitparam = self.units[unit]
                self.tfrom = self.tto.shift(**{ unitparam: -num })
            elif op == self.RELOP_AROUND:           # around expression: [ to - offset : to + offset ]
                unitparam = self.units[unit]
                self.tfrom = self.tto.shift(**{ unitparam: -num })
                self.tto = self.tto.shift(**{ unitparam: +num })
        else:
            self.tfrom = arrow.get(tfrom).replace(tzinfo=tz)

        # postponed end time processing in case on a relative time
        if relto_parsed:
            num = int(relto_parsed.group(1))
            unit = relto_parsed.group(2)
            unitparam = self.units[unit]
            self.tto = self.tfrom.shift(**{ unitparam: num })

        # Conversion to ES target timezone
        if estz:
            self.tfrom = self.tfrom.tto(estz)
            self.tto = self.tto.to(estz)

        self.field = field

    def getRangeQuery(self):
        """Return time frame as ES DSL range query"""
        return { "range": { self.field: { "gte": self.tfrom.timestamp * 1000, "lte": self.tto.timestamp * 1000, "format": "epoch_millis" } } }

    def wrapQuery(self, query):
        """Wrap existing query into query restricted to time range"""
        return { "query": { "bool": { "must": [ query["query"], self.getRangeQuery() ] } } }

    def __str__(self):
        return "[ %s..%s ]" % (str(self.tfrom), str(self.tto))
