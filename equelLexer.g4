lexer grammar equelLexer ;
//options { language=Python3; }

// Initial mode tries to detect EQUEL expression by whitelisted prefix character or verb keyword.
// ESQueryString token is passed to parser if no EQUEL is detected which triggers handling of query string syntax.
// In all cases, the lexer is put into EQUEL mode after first recognized token. Normally, it shouldn't return into
// the initial mode.

FirstPrefixChar: [:&<>#] -> pushMode(EQUEL), pushMode(VALUE), type(PrefixChar) ;
FirstIdentifier: ( 'match_all' | 'match' | 'match_phrase' | 'match_phrase_prefix' | 'multi_match' | 'common_terms' | 'query_string' | 'simple_query_string' | 'term' | 'terms' | 'range' | 'exists' | 'prefix' | 'wildcard' | 'regexp' | 'fuzzy' | 'type' | 'ids' | 'script' | 'span_term' | 'span_multi' | 'span_first' | 'span_near' | 'span_or' | 'span_not' | 'span_containing' | 'span_within' | 'field_masking_span' ) -> pushMode(EQUEL), type(Identifier) ;
QueryStringFirstChar: ~[|] -> pushMode(QUERY), type(QueryStringChar) ;

mode QUERY ;
QueryStringChar: ~[|] ;
QueryStringEnd: [ \t\n\r]*[|] -> mode(EQUEL), type(Separator) ;

mode EQUEL ;
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
UnnamedSingleQuotedValue: '\'' ~[']+ '\'' -> type(SingleQuotedValue) ;
UnnamedDoubleQuotedValue: '"' ~["]+ '"' -> type(DoubleQuotedValue) ;
WS: [ \t\n\r]+ -> skip;

mode VALUE ;
VWS: [ \t\n\r]+ -> skip;
LParS: '(' -> pushMode(EQUEL) ;
RParSV: ')' -> popMode, type(RParS) ;
LParL: '[' -> pushMode(VALUE) ;
LSep: ',' -> pushMode(VALUE) ;
RParL: ']' -> popMode ;
SingleQuotedValue: '\'' ~[']+ '\'' -> popMode ;
DoubleQuotedValue: '"' ~["]+ '"' -> popMode ;
UnquotedValue: ~[,([{ )\]}\t\n\r]+ -> popMode ;
// TODO: add quote char escaping (\")
