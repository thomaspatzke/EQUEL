all:
	antlr4 -o antout -visitor -Dlanguage=Python3 eesqlLexer.g4 eesqlParser.g4
