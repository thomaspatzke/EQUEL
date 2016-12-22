parser grammar equelParser ;
options { tokenVocab=equelLexer; }

equel:
    firstExpr ( Separator searchExpr )* ( Separator AGG aggregationExpr ( Separator aggregationExpr )* )? ( Separator POSTPROC postprocExpr ( Separator postprocExpr )* )? ( Separator OUTPUT outputExpr ( Separator outputExpr )* )? ;

verb: Identifier ;

genericExpr:
    verb ( parameter )* # generic |
    shortcutExpr # shortcut;

searchExpr:
    genericExpr ;

queryString:
    QueryStringChar+ ;

firstExpr:
    searchExpr # firstSearchExpr |
    queryString # queryStringExpr ;

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
    (AGG targetId=Identifier)? genericExpr ( AS aggId=Identifier )? ;

postprocExpr:
    genericExpr ;

outputExpr:
    genericExpr ( AS outId=Identifier )? ;

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
