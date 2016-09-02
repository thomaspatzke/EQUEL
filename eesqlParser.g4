parser grammar eesqlParser ;
//options { tokenVocab=eesqlLexer; language=Python3; }
options { tokenVocab=eesqlLexer; }

eesql:
    searchExpr ( Separator FILTER filterExpr ( Separator filterExpr )* )? ( Separator AGG aggregationExpr ( Separator aggregationExpr )* )? ( Separator POSTPROC postprocExpr ( Separator postprocExpr )* )? ( Separator OUTPUT outputExpr ( Separator outputExpr )* )? ;

verb: Identifier ;

genericExpr:
    verb ( parameter )* ;

searchExpr:
//    orSearchExpr |
    genericExpr |
    searchShortcut;

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

searchShortcut:
    Colon SingleQuotedValue |
    Colon DoubleQuotedValue |
    Colon UnquotedValue
    ;

parameter:
    name Equals value |
    Identifier;

name:
    Identifier ;

value:
    UnquotedValue |
    SingleQuotedValue |
    DoubleQuotedValue |
    LParV searchExpr RPar;
