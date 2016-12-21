# Generated from eesqlParser.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .eesqlParser import eesqlParser
else:
    from eesqlParser import eesqlParser

# This class defines a complete generic visitor for a parse tree produced by eesqlParser.

class eesqlParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by eesqlParser#eesql.
    def visitEesql(self, ctx:eesqlParser.EesqlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#verb.
    def visitVerb(self, ctx:eesqlParser.VerbContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#generic.
    def visitGeneric(self, ctx:eesqlParser.GenericContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#shortcut.
    def visitShortcut(self, ctx:eesqlParser.ShortcutContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#searchExpr.
    def visitSearchExpr(self, ctx:eesqlParser.SearchExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#queryString.
    def visitQueryString(self, ctx:eesqlParser.QueryStringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#firstSearchExpr.
    def visitFirstSearchExpr(self, ctx:eesqlParser.FirstSearchExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#queryStringExpr.
    def visitQueryStringExpr(self, ctx:eesqlParser.QueryStringExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#filterExpr.
    def visitFilterExpr(self, ctx:eesqlParser.FilterExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#aggregationExpr.
    def visitAggregationExpr(self, ctx:eesqlParser.AggregationExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#postprocExpr.
    def visitPostprocExpr(self, ctx:eesqlParser.PostprocExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#outputExpr.
    def visitOutputExpr(self, ctx:eesqlParser.OutputExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#shortcutExpr.
    def visitShortcutExpr(self, ctx:eesqlParser.ShortcutExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#KVParam.
    def visitKVParam(self, ctx:eesqlParser.KVParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#UnnamedList.
    def visitUnnamedList(self, ctx:eesqlParser.UnnamedListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#SingleParam.
    def visitSingleParam(self, ctx:eesqlParser.SingleParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#name.
    def visitName(self, ctx:eesqlParser.NameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#SimpleUQValue.
    def visitSimpleUQValue(self, ctx:eesqlParser.SimpleUQValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#SimpleSQValue.
    def visitSimpleSQValue(self, ctx:eesqlParser.SimpleSQValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#SimpleDQValue.
    def visitSimpleDQValue(self, ctx:eesqlParser.SimpleDQValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#NestedSearch.
    def visitNestedSearch(self, ctx:eesqlParser.NestedSearchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by eesqlParser#ValueList.
    def visitValueList(self, ctx:eesqlParser.ValueListContext):
        return self.visitChildren(ctx)



del eesqlParser