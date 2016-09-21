parser grammar eesqlParser ;
//options { tokenVocab=eesqlLexer; language=Python3; }
options { tokenVocab=eesqlLexer; }

eesql:
    searchExpr ( Separator searchExpr )* ( Separator AGG aggregationExpr ( Separator AGG? aggregationExpr )* )? ( Separator POSTPROC postprocExpr ( Separator postprocExpr )* )? ( Separator OUTPUT outputExpr ( Separator outputExpr )* )? ;

verb: Identifier ;

genericExpr:
    verb ( parameter )* # generic |
    shortcutExpr # shortcut;

searchExpr:
    genericExpr ;

/*
orSearchExpr:
    andSearchExpr ( '||' andSearchExpr )*;

andSearchExpr:
    notSearchExpr ( '&&' notSearchExpr )* ;

notSearchExpr:
    '!'? searchExpr ;
    */

filterExpr:
    searchExpr ;

aggregationExpr:
    genericExpr ( AS Identifier )? ;

postprocExpr:
    genericExpr ;

outputExpr:
    genericExpr ;

shortcutExpr:
    PrefixChar value ;

parameter:
    name Equals value # KVParam |
    LParL value ( LSep value )* RParL # UnnamedList |
    Identifier # SingleParam;

name:
    Identifier ;

value:
    UnquotedValue # SimpleUQValue |
    SingleQuotedValue # SimpleSQValue |
    DoubleQuotedValue # SimpleDQValue |
    LParS searchExpr RParS # NestedSearch |
    LParL value ( LSep value )* RParL # ValueList;
