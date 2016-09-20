from elasticsearch_dsl import Search, Q, A
from antlr4 import CommonTokenStream, ParseTreeWalker
from eesql.ant.eesqlLexer import eesqlLexer
from eesql.ant.eesqlParser import eesqlParser
from eesql.ant.eesqlParserListener import eesqlParserListener
from eesql.plugins.params import Parameter, ParameterList
import json

class EESQLParser():
    """Parser builds elasticsearch_dsl Search object from EESQL query expression"""
    def __init__(self, engine, search=Search()):
        """Initialize EESQL parser"""
        self.search = search
        self.engine = engine

    def parse(self, eesql, **kwargs):
        lexer = eesqlLexer(eesql)
        tokenstream = CommonTokenStream(lexer)
        parser = eesqlParser(tokenstream)
        parsetree = parser.eesql()
        walker = ParseTreeWalker()
        listener = EESQLParserListener(self.engine)
        walker.walk(listener, parsetree)
        return json.dumps(parsetree.json, **kwargs)

class EESQLParserListener(eesqlParserListener):
    def __init__(self, engine):
        self.engine = engine
        super().__init__()

    def exitEesql(self, ctx):
        ctx.json = dict()
        for searchExpr in ctx.searchExpr():
            ctx.json.update(searchExpr.json)

    # Expressions
    def exitSearchExpr(self, ctx):
        ctx.json = ctx.genericExpr().json

    def exitGeneric(self, ctx):
        type = self.engine.getPluginTypeForContext(ctx.parentCtx)
        verb = ctx.verb().text
        params = ParameterList(ctx.parameter())
        plugin = self.engine.resolvePlugin(type, verb)
        ctx.json = plugin.apply(verb, params)

    def exitShortcut(self, ctx):
        type = self.engine.getPluginTypeForContext(ctx.parentCtx)
        plugin = self.engine.resolveShortcutPlugin(type)
        prefix = ctx.shortcutExpr().PrefixChar().getText()
        value = ctx.shortcutExpr().value().text
        ctx.json = plugin.apply(prefix, value)

    def exitVerb(self, ctx):
        ctx.text = ctx.Identifier().getText()

    ## Parameters
    def exitKVParam(self, ctx):
        ctx.param = Parameter(ctx.name().Identifier().getText(), ctx.value().text)

    def exitSingleParam(self, ctx):
        ctx.param = Parameter(ctx.Identifier().getText())

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
