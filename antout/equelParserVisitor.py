# Generated from equelParser.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .equelParser import equelParser
else:
    from equelParser import equelParser

# This class defines a complete generic visitor for a parse tree produced by equelParser.

class equelParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by equelParser#equel.
    def visitEquel(self, ctx:equelParser.EquelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#verb.
    def visitVerb(self, ctx:equelParser.VerbContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#generic.
    def visitGeneric(self, ctx:equelParser.GenericContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#shortcut.
    def visitShortcut(self, ctx:equelParser.ShortcutContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#searchExpr.
    def visitSearchExpr(self, ctx:equelParser.SearchExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#queryString.
    def visitQueryString(self, ctx:equelParser.QueryStringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#firstSearchExpr.
    def visitFirstSearchExpr(self, ctx:equelParser.FirstSearchExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#queryStringExpr.
    def visitQueryStringExpr(self, ctx:equelParser.QueryStringExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#filterExpr.
    def visitFilterExpr(self, ctx:equelParser.FilterExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#aggregationExpr.
    def visitAggregationExpr(self, ctx:equelParser.AggregationExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#postprocExpr.
    def visitPostprocExpr(self, ctx:equelParser.PostprocExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#outputExpr.
    def visitOutputExpr(self, ctx:equelParser.OutputExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#shortcutExpr.
    def visitShortcutExpr(self, ctx:equelParser.ShortcutExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#KVParam.
    def visitKVParam(self, ctx:equelParser.KVParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#UnnamedValue.
    def visitUnnamedValue(self, ctx:equelParser.UnnamedValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#UnnamedList.
    def visitUnnamedList(self, ctx:equelParser.UnnamedListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#SingleParam.
    def visitSingleParam(self, ctx:equelParser.SingleParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#name.
    def visitName(self, ctx:equelParser.NameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#SimpleUQValue.
    def visitSimpleUQValue(self, ctx:equelParser.SimpleUQValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#SimpleSQValue.
    def visitSimpleSQValue(self, ctx:equelParser.SimpleSQValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#SimpleDQValue.
    def visitSimpleDQValue(self, ctx:equelParser.SimpleDQValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#NestedSearch.
    def visitNestedSearch(self, ctx:equelParser.NestedSearchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by equelParser#ValueList.
    def visitValueList(self, ctx:equelParser.ValueListContext):
        return self.visitChildren(ctx)



del equelParser