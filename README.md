# EESQL - the Extended ElasticSearch Query Language

The projects was motivated by usage of [ElasticSearch](https://www.elastic.co/products/elasticsearch) and
[Kibana](https://www.elastic.co/products/kibana) for log analysis in incident response and as tool in [web application
security testing](https://github.com/thomaspatzke/WASE). Both are great tools for this purpose, but Kibana exposes
only a fraction of the power of ElasticSearch and is missing some features that would make log analysis much easier.

This project aims to create a query language for ElasticSearch with the following goals:

* Easy to understand and to write for humans (compared to Query DSL JSON expressions)
* Exposure of a big amount of ElasticSearch capabilities (compared to Kibana)
* Extensible by plugin architecture
* Extension of ElasticSearch capabilities by post processing modules
* "Everything fits in one line of an EESQL expression"
* Easy integrated in own projects

## EESQL Expressions

### Overview

ElasticSearch DSL queries and aggregations are expressed in one EESQL expression. Furthermore, post-processing and
output formats can be added to such an expression.

Generally, EESQL expressions are built as follows:

search | filter_1 | ... | aggregation_1 | ... | postprocessing_1 | ... | output_1 | ...

Each part in an EESQL expression is called subexpression. ALl EESQL expression begin with exactly one search
subexpression that aquires the data on which the further subexpressions operate. The search is followed by an arbitrary
number of filters, aggregations, post-processing instructions and outputs. Searches, filters and aggregations are
handled completely by ElasticSearch, postprocessing and output is EESQL functionality. The output of the last search,
aggregation or post-processing module is fanned out to an arbitrary number of output modules that can be stored/shown
parallel.

### General Subexpression Syntax

Subexpressions are built as follows:

type verb switch_1 ... parameter_1=value_1 ...

The type defines the type of the rule: filter, agg, postproc and output. The first subexpression from a new type must be
prepended with this keyword for disambiguation reasons. A verb refers to a plugin, which is a piece of code that follows
some interface conventions. 

Parameter values may be quoted with single (') or double (") quotes. Unquoted values end at the next token separator
character (spaces and newlines). Some parameter support nested subexpressions, which are placed in parenthesis.
Examples:

```
query_string query=foo
query_string query="foo bar"
query_string query='foo bar'
nested path=nested.field query=(:"nested.field.foo:bar AND foobar")
```

The list is another possible value type and can contain values or nested search expressions. Lists are enclosed in
square brackets \[ and \]. Search expressions inside the list must additionally be enclosed in parenthesis.

Examples

```
multi_match query=foobar fields=[foo, bar, bla, blubb]
filter terms field=[value, "multiple words", '"double quoted value"']
nested path=response.header query=(match response.header.name=content-security-policy)
```

### Sub Expression Types

#### Search Expression

The verbs match to the query clauses from [ElasticSearch Query
DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html). Some shortcuts and syntactic
elements were added for simplification of EESQL expressions, these are:

* Boolean operators &, | and ! to build *bool* compound queries.
* Grouping operator ( and )
* Starting a search expression with a colon causes that it is treated as ElasticSearch query string. `:"some query"` is
  equivalent to `query_string query="some query"`.

#### Filter Expression

Filter rules are the same as search rules prefixed with the word *filter*.

#### Aggregation Expression

Multiple aggregation expressions are applied to each other in order of their appearance. An aggregation expression
follows the syntax stated above and can end with a name assignment by:

```
... | agg ... as name | ...
```

This name can be used to refer to a particular aggregation from postprocessing and output plugins.

#### Postprocessing and Output Expressions

These expressions simply follow the syntax stated above.

## Implementation Architecture

### Plugins

EESQL is implemented in a plugin architecture. Plugins can register for a verb which is then used in EESQL expressions
to address the plugin. The following plugin types are specified according to the expression syntax and semantics defined
above:

* search/filter plugin: generates a query DSL expression
* aggregation plugin: adds/nests an aggregation expression to a ElasticSearch Query DSL query.
* postprocessing plugin: gets an ElasticSearch result tree, changes it and passes it to the next postprocessing module or to
  all following output modules.
* output plugin: gets an ElasticSearch result tree and outputs it

Parameters are passed as set (switches) and associative arrays (maps) to the plugin.

## API

### Usage

### Extension

## Future Plans

So many ideas, so little time...

Feel free to pick up an idea and implement it, but lets coordinate this to prevent of duplicate usage of resources on
the same task.

### Post-processing modules

* Aggregation of separate start/stop events into one event that combines both attributes.
* Find similar events around a specified event class (e.g. similar attacker activity around characteristic login events)

### Output modules

* Interactive HTML
* Graphical diagrams
* Textual tables
* Textual documentation

### Search Reusing Previous Results

Search expressions in a later position that use results from previous EESQL subexpressions.

Example: search for spawning command line interpreters from uncommon processes and use session identifier to display
actions performed in the spawned shells.

### Relaxation of Strict Subexpression Type Order

Example: output subexpression for intermediate results.

### Remove Subexpression Type Declarations

Remove agg, postproc and output keywords from first subexpression with a new type by assignment of verbs to types.

### Complex Aggregation Structures

ElasticSearch supports more complex tree structures of aggregations while EESQL currently supports only linear
aggregations. The plan is to make such complex aggregation structures accessible via EESQL by intoduction of a grouping
operator, e.g.:

... | (agg_1.1 | agg_1.2 | (agg_1.2.1 | agg_1.2.2)) | agg_2 | ...

### Web Frontend

A web application as fronted for EESQL that displays results and offers graphical visualization capabilities by
additional output plugins.
