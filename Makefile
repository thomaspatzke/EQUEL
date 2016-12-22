all:
	antlr4 -o antout -visitor -Dlanguage=Python3 equelLexer.g4 equelParser.g4
