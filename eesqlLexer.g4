lexer grammar eesqlLexer ;
//options { language=Python3; }

AS: 'as' ;
FILTER: 'filter' ;
AGG: 'agg' ;
POSTPROC: 'postproc' ;
OUTPUT: 'output' ;

Separator: '|' ;
Equals: '=' -> pushMode(VALUE) ;
Identifier: [a-zA-Z0-9_]+ ;
RPar: ')' -> popMode ;

WS: [ \t\n\r]+ -> skip;

mode VALUE ;
SingleQuotedValue: '\'' ~[']+ '\'' -> popMode ;
DoubleQuotedValue: '"' ~["]+ '"' -> popMode ;
UnquotedValue: ~[ ]+ -> popMode ;
// TODO: add quote char escaping (\")
LParV: '(' -> pushMode(DEFAULT_MODE) ;