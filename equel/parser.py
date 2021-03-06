from elasticsearch_dsl import Search, Q, A
from antlr4 import CommonTokenStream, ParseTreeWalker
from equel.ant.equelLexer import equelLexer
from equel.ant.equelParser import equelParser
from equel.ant.equelParserListener import equelParserListener
from equel.plugins.params import Parameter, ParameterList

class EQUELParser():
    """Parser builds elasticsearch_dsl Search object from EQUEL query expression"""
    def __init__(self, engine):
        """Initialize EQUEL parser"""
        self.engine = engine

    def parse(self, equel):
        lexer = equelLexer(equel)
        tokenstream = CommonTokenStream(lexer)
        parser = equelParser(tokenstream)
        parsetree = parser.equel()
        walker = ParseTreeWalker()
        listener = EQUELParserListener(self.engine)
        walker.walk(listener, parsetree)
        return parsetree

class EQUELParserListener(equelParserListener):
    def __init__(self, engine):
        self.engine = engine
        self.query = dict()
        self.aggs = AggregationHierarchy()  # aggregation symbol table that contains all aggregation names with aggregation references
        self.postproc = PostprocessingChain()
        self.output = Outputs()
        super().__init__()

    # Main rule
    def exitEquel(self, ctx):
        ctx.query = self.query
        ctx.query.update(self.aggs.getJSON())
        ctx.postproc = self.postproc
        ctx.output = self.output

    # Expressions
    def exitSearchExpr(self, ctx):
        json = ctx.genericExpr().json
        if ctx.genericExpr().plugin.filterable and not isinstance(ctx.parentCtx, equelParser.FirstSearchExprContext):
            try:    # append to filter list in existing query structure
                self.query["query"]["bool"]["filter"].append(json)
            except KeyError:    # expected query structure doesn't exist, create it
                self.query["query"] = {
                        "bool": {
                            "must": self.query["query"],
                            "filter": [ json ]
                        }
                    }
        elif ctx.genericExpr().plugin.filterable and isinstance(ctx.parentCtx, equelParser.FirstSearchExprContext):
                self.query["query"] = json
        else:
            self.query.update(json)

    def exitQueryStringExpr(self, ctx):
        plugin = self.engine.resolveQueryStringPlugin()
        self.query = plugin.apply(None, ctx.queryString().query, self, ctx)

    def exitQueryString(self, ctx):
        ctx.query = "".join([qsc.getText() for qsc in ctx.QueryStringChar()])

    def exitAggregationExpr(self, ctx):
        try:
            aggId = ctx.aggId.text
        except:
            aggId = None

        try:
            targetId = ctx.targetId.text
        except:
            targetId = None

        if ctx.genericExpr().json:
            self.aggs.add(aggId, ctx.genericExpr().json, targetId)

    def exitPostprocExpr(self, ctx):
        pp = ctx.genericExpr().json
        self.postproc.append(pp)

    def exitOutputExpr(self, ctx):
        try:
            outId = ctx.outId.text
        except:
            outId = None
        out = ctx.genericExpr().json
        self.output.add(out, outId)

    def exitGeneric(self, ctx):
        type = self.engine.getPluginTypeForContext(ctx.parentCtx)
        verb = ctx.verb().text
        params = ParameterList(ctx.parameter())
        ctx.plugin = self.engine.resolvePlugin(type, verb)
        ctx.json = ctx.plugin.apply(verb, params, self, ctx)    # TODO: name 'json' does not match, as it contains dicts or output plugin objects

    def exitShortcut(self, ctx):
        type = self.engine.getPluginTypeForContext(ctx.parentCtx)
        ctx.plugin = self.engine.resolveShortcutPlugin(type)
        prefix = ctx.shortcutExpr().PrefixChar().getText()
        value = ctx.shortcutExpr().value().text
        ctx.json = ctx.plugin.apply(prefix, value, self, ctx)

    def exitVerb(self, ctx):
        ctx.text = ctx.Identifier().getText()

    ## Parameters
    def exitKVParam(self, ctx):
        ctx.param = Parameter(ctx.name().Identifier().getText(), ctx.value().text)

    def exitUnnamedValue(self, ctx):
        ctx.param = Parameter(None, ctx.value().text)

    def exitUnnamedList(self, ctx):
        ctx.param = Parameter(None, list(map(lambda c: c.text, ctx.value())))

    def exitSingleParam(self, ctx):
        ctx.param = Parameter(ctx.Identifier().getText(), True)

    ### Values
    def exitSimpleUQValue(self, ctx):
        ctx.text = ctx.UnquotedValue().getText()

    def unquoteValue(self, s):
        return s[1:-1]

    def exitSimpleSQValue(self, ctx):
        ctx.text = self.unquoteValue(ctx.SingleQuotedValue().getText())

    def exitSimpleDQValue(self, ctx):
        ctx.text = self.unquoteValue(ctx.DoubleQuotedValue().getText())

    def exitValueList(self, ctx):
        ctx.text = list()
        for value in ctx.value():
            ctx.text.append(value.text)

class AggregationHierarchy:
    """Class used for building an aggregation hierarchy"""
    def __init__(self):
        self.aggId = 0          # Initial value of counter for automatic aggregation naming - 1
        self.prev = None        # pointer to the previous aggregation where next one is nested into when not specified differently with 'agg <id>' statement
        self.aggs = dict()      # the aggregation hierarchy is built into this. For technical reasons (references to aggregations) each agg located at root level is added as list element and the list is merged finally.
        self.aggNames = dict()  # symbol table: name -> aggregation object (JSON/dict)

    def add(self, name, baseagg, target=None):
        """
        Add aggregation to hierarchy with specified name and nested into given target aggregation.

        If name is not specified, a default name 'agg<count>' is generated.
        If target is not specified, the aggregation is nested into the last aggregation or as first root aggregation.
        The trget name 'root' has a special meaning and adds aggregation to the top level of the hierarchy.
        """
        if not name:                # automatically generate name with counter if 'as' statement is missing
            name = "agg%d" % (self.nextAggId())
        agg = { name: baseagg }
        self.addName(name, baseagg)

        if self.prev == None or type(target) == str and target == "root":    # first aggregation expression or explicit specification of root level in hierarchy
            self.aggs.update(agg)
        else:
            if type(target) == str:           # target is given
                self.prev = self.getAgg(target)
            if "aggs" not in self.prev:         # add subaggregation key if not present
                self.prev["aggs"] = dict()
            self.prev["aggs"].update(agg)       # as for the root tag the subaggregations are added as list elements to keep the reference from the symbol table alive
        self.prev = baseagg

    def getJSON(self):
        """Finalize aggregation hierarchy and return dict that can be merged into a query and converted into JSON."""
        if len(self.aggs) > 0:
            return { "aggs": self.aggs }
        else:
            return {}

    def nextAggId(self):
        self.aggId += 1
        return self.aggId

    def addName(self, name, agg):
        """Add aggregation name to symbol table"""
        if name in self.aggNames:
            raise self.AlreadyExistsError(name)
        self.aggNames[name] = agg

    def getAgg(self, name):
        """Retrieve aggregation from symbol table"""
        try:
            return self.aggNames[name]
        except KeyError:
            raise self.NotFoundException(name)

    class AlreadyExistsError(ValueError):
        """Is raised when name that already exists should be added"""
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return "Name '%s' already exists" % (self.name)

    class NotFoundException(ValueError):
        """Is raised when name is not found in symbol table"""
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return "Name '%s' not found" % (self.name)

class PostprocessingChain(list):
    pass

class Outputs(dict):
    def __init__(self):
        self.autocount = 1

    def add(self, output, name=None):
        if name == None:
            name = "output_%d" % (self.autocount)
            self.autocount += 1
        self[name] = output
