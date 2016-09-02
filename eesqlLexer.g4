lexer grammar eesqlLexer ;
//options { language=Python3; }

AS: 'as' ;
FILTER: 'filter' ;
AGG: 'agg' ;
POSTPROC: 'postproc' ;
OUTPUT: 'output' ;

Separator: '|' ;
RPar: ')' -> popMode ;
Equals: '=' -> pushMode(VALUE) ;
Colon: ':' -> pushMode(VALUE) ;
Identifier: [a-zA-Z0-9_]+ ;

WS: [ \t\n\r]+ -> skip;

mode VALUE ;
VWS: [ \t\n\r]+ -> skip;
LParV: '(' -> pushMode(DEFAULT_MODE) ;
SingleQuotedValue: '\'' ~[']+ '\'' -> popMode ;
DoubleQuotedValue: '"' ~["]+ '"' -> popMode ;
UnquotedValue: ~[(]~[ )\t\n\r]* -> popMode ;
// TODO: add quote char escaping (\")
