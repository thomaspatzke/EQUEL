lexer grammar eesqlLexer ;
//options { language=Python3; }

AS: 'as' ;
AGG: 'agg' ;
POSTPROC: 'postproc' ;
OUTPUT: 'output' ;

Separator: '|' ;
RParS: ')' -> popMode ;
LParLD: '[' -> pushMode(VALUE), pushMode(VALUE), type(LParL) ;
Equals: '=' -> pushMode(VALUE) ;
PrefixChar: [:&<>!#+-] -> pushMode(VALUE) ;
Identifier: [a-zA-Z0-9_.@]+ ;
WS: [ \t\n\r]+ -> skip;

mode VALUE ;
VWS: [ \t\n\r]+ -> skip;
LParS: '(' -> pushMode(DEFAULT_MODE) ;
RParSV: ')' -> popMode, type(RParS) ;
LParL: '[' -> pushMode(VALUE) ;
LSep: ',' -> pushMode(VALUE) ;
RParL: ']' -> popMode ;
SingleQuotedValue: '\'' ~[']+ '\'' -> popMode ;
DoubleQuotedValue: '"' ~["]+ '"' -> popMode ;
UnquotedValue: ~[,([{ )\]}\t\n\r]+ -> popMode ;
// TODO: add quote char escaping (\")
