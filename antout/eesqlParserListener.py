# Generated from eesqlParser.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .eesqlParser import eesqlParser
else:
    from eesqlParser import eesqlParser

# This class defines a complete listener for a parse tree produced by eesqlParser.
class eesqlParserListener(ParseTreeListener):

    # Enter a parse tree produced by eesqlParser#eesql.
    def enterEesql(self, ctx:eesqlParser.EesqlContext):
        pass

    # Exit a parse tree produced by eesqlParser#eesql.
    def exitEesql(self, ctx:eesqlParser.EesqlContext):
        pass


    # Enter a parse tree produced by eesqlParser#verb.
    def enterVerb(self, ctx:eesqlParser.VerbContext):
        pass

    # Exit a parse tree produced by eesqlParser#verb.
    def exitVerb(self, ctx:eesqlParser.VerbContext):
        pass


    # Enter a parse tree produced by eesqlParser#generic.
    def enterGeneric(self, ctx:eesqlParser.GenericContext):
        pass

    # Exit a parse tree produced by eesqlParser#generic.
    def exitGeneric(self, ctx:eesqlParser.GenericContext):
        pass


    # Enter a parse tree produced by eesqlParser#shortcut.
    def enterShortcut(self, ctx:eesqlParser.ShortcutContext):
        pass

    # Exit a parse tree produced by eesqlParser#shortcut.
    def exitShortcut(self, ctx:eesqlParser.ShortcutContext):
        pass


    # Enter a parse tree produced by eesqlParser#searchExpr.
    def enterSearchExpr(self, ctx:eesqlParser.SearchExprContext):
        pass

    # Exit a parse tree produced by eesqlParser#searchExpr.
    def exitSearchExpr(self, ctx:eesqlParser.SearchExprContext):
        pass


    # Enter a parse tree produced by eesqlParser#filterExpr.
    def enterFilterExpr(self, ctx:eesqlParser.FilterExprContext):
        pass

    # Exit a parse tree produced by eesqlParser#filterExpr.
    def exitFilterExpr(self, ctx:eesqlParser.FilterExprContext):
        pass


    # Enter a parse tree produced by eesqlParser#aggregationExpr.
    def enterAggregationExpr(self, ctx:eesqlParser.AggregationExprContext):
        pass

    # Exit a parse tree produced by eesqlParser#aggregationExpr.
    def exitAggregationExpr(self, ctx:eesqlParser.AggregationExprContext):
        pass


    # Enter a parse tree produced by eesqlParser#postprocExpr.
    def enterPostprocExpr(self, ctx:eesqlParser.PostprocExprContext):
        pass

    # Exit a parse tree produced by eesqlParser#postprocExpr.
    def exitPostprocExpr(self, ctx:eesqlParser.PostprocExprContext):
        pass


    # Enter a parse tree produced by eesqlParser#outputExpr.
    def enterOutputExpr(self, ctx:eesqlParser.OutputExprContext):
        pass

    # Exit a parse tree produced by eesqlParser#outputExpr.
    def exitOutputExpr(self, ctx:eesqlParser.OutputExprContext):
        pass


    # Enter a parse tree produced by eesqlParser#shortcutExpr.
    def enterShortcutExpr(self, ctx:eesqlParser.ShortcutExprContext):
        pass

    # Exit a parse tree produced by eesqlParser#shortcutExpr.
    def exitShortcutExpr(self, ctx:eesqlParser.ShortcutExprContext):
        pass


    # Enter a parse tree produced by eesqlParser#KVParam.
    def enterKVParam(self, ctx:eesqlParser.KVParamContext):
        pass

    # Exit a parse tree produced by eesqlParser#KVParam.
    def exitKVParam(self, ctx:eesqlParser.KVParamContext):
        pass


    # Enter a parse tree produced by eesqlParser#UnnamedList.
    def enterUnnamedList(self, ctx:eesqlParser.UnnamedListContext):
        pass

    # Exit a parse tree produced by eesqlParser#UnnamedList.
    def exitUnnamedList(self, ctx:eesqlParser.UnnamedListContext):
        pass


    # Enter a parse tree produced by eesqlParser#SingleParam.
    def enterSingleParam(self, ctx:eesqlParser.SingleParamContext):
        pass

    # Exit a parse tree produced by eesqlParser#SingleParam.
    def exitSingleParam(self, ctx:eesqlParser.SingleParamContext):
        pass


    # Enter a parse tree produced by eesqlParser#name.
    def enterName(self, ctx:eesqlParser.NameContext):
        pass

    # Exit a parse tree produced by eesqlParser#name.
    def exitName(self, ctx:eesqlParser.NameContext):
        pass


    # Enter a parse tree produced by eesqlParser#SimpleUQValue.
    def enterSimpleUQValue(self, ctx:eesqlParser.SimpleUQValueContext):
        pass

    # Exit a parse tree produced by eesqlParser#SimpleUQValue.
    def exitSimpleUQValue(self, ctx:eesqlParser.SimpleUQValueContext):
        pass


    # Enter a parse tree produced by eesqlParser#SimpleSQValue.
    def enterSimpleSQValue(self, ctx:eesqlParser.SimpleSQValueContext):
        pass

    # Exit a parse tree produced by eesqlParser#SimpleSQValue.
    def exitSimpleSQValue(self, ctx:eesqlParser.SimpleSQValueContext):
        pass


    # Enter a parse tree produced by eesqlParser#SimpleDQValue.
    def enterSimpleDQValue(self, ctx:eesqlParser.SimpleDQValueContext):
        pass

    # Exit a parse tree produced by eesqlParser#SimpleDQValue.
    def exitSimpleDQValue(self, ctx:eesqlParser.SimpleDQValueContext):
        pass


    # Enter a parse tree produced by eesqlParser#NestedSearch.
    def enterNestedSearch(self, ctx:eesqlParser.NestedSearchContext):
        pass

    # Exit a parse tree produced by eesqlParser#NestedSearch.
    def exitNestedSearch(self, ctx:eesqlParser.NestedSearchContext):
        pass


    # Enter a parse tree produced by eesqlParser#ValueList.
    def enterValueList(self, ctx:eesqlParser.ValueListContext):
        pass

    # Exit a parse tree produced by eesqlParser#ValueList.
    def exitValueList(self, ctx:eesqlParser.ValueListContext):
        pass


