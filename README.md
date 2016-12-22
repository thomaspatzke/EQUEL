# EQUEL - an **E**lasticsearch **QUE**ry **L**anguage

The projects was motivated by usage of [Elasticsearch](https://www.elastic.co/products/elasticsearch) and
[Kibana](https://www.elastic.co/products/kibana) for log analysis in incident response and as tool in [web application
security testing](https://github.com/thomaspatzke/WASE). Both are great tools for this purpose, but Kibana exposes
only a fraction of the power of Elasticsearch and is missing some features that would make log analysis much easier.

This project aims to create a query language for Elasticsearch with the following goals:

* Easy to understand and to write for humans (compared to Query DSL JSON expressions)
* Exposure of a big amount of Elasticsearch capabilities (compared to the usual Query String expressions)
* Extensible by plugin architecture
* Extension of Elasticsearch capabilities by post processing plugins
* Easy addition of own output formats and visualizations with output plugins
* Linear query structure instead of nesting
* "Everything fits in one line of an EQUEL expression" - especially aggregations
* Easy integration in projects that already use Elasticsearch

Note: EQUEL is neither Splunk SPL nor SQL. It's not the idea to "emulate" one of both.

## Requirements

EQUEL was developed with Python 3. It depends on the following packages:

* elasticsearch (5.0.1)
* elasticsearch\_dsl (5.0.0)
* antlr4-python3-runtime (4.6)
* termcolor (1.1.0) - output plugin *text*

Tested versions are given in parentheses. Other versions may work, too. All these 
modules are installable via pip.

## EQUEL Expressions

### Overview

Elasticsearch DSL queries and aggregations are expressed in one EQUEL expression. Furthermore, post-processing and
output formats can be added to such an expression.

Generally, EQUEL expressions are built as follows:

search | searchmodifier\_1 |  ... | aggregation\_1 | ... | postprocessing\_1 | ... | output\_1 | ...

Each part in an EQUEL expression is called subexpression. All EQUEL expression begin with exactly one search
subexpression that may be an Elasticsearch query string. The search is followed by an arbitrary number of search
modifiers (e.g. sorting, field filtering), aggregations, post-processing instructions and outputs.  Searches, search
modifiers and aggregations are handled completely by Elasticsearch, postprocessing and output is EQUEL functionality.
The output of the last search, aggregation or post-processing module is fanned out to an arbitrary number of output
modules that can be stored/shown parallel.

### General Subexpression Syntax

Subexpressions are built as follows:

type verb switch\_1 ... parameter\_1=value\_1 ...

The type defines the type of the rule: filter, agg, postproc and output. The first subexpression from a new type must be
prepended with this keyword for disambiguation reasons. A verb refers to a plugin, which is a piece of code that follows
some interface conventions. The first subexpression is recognized as Elasticsearch query string if it doesn't starts
with a whitelisted verb or shortcut character (+ and - are not whitelisted, see below).

A subexpression can be expressed as a shortcut. Each rule type class can define a plugin that handles such shortcut
expressions. A shortcut expression is prefixed with one of these characters: `:&<>!#+-` (default should be the colon)
and contains a single quoted or unqouted value. The prefix is passed to the plugin and can be used as behavior modifier.
Currently, shortcuts are defined as follows:

* Searches: equivalent to a *query\_string* with the value passed to its *query* parameter. The prefix *&* changes the
  default operator to *AND*.
* Aggregations:
  * *:*: equivalent to the *terms* aggregation with the value passed to the *field* parameter.
  * *#*: equivalent to the *value\_count* aggregation with the value passed to the *field* parameter.
  * *+*: equivalent to the *sum* aggregation with the value passed to the *field* parameter.
  * *<* and *>*: equivalent to the *min* and *max* aggregation with the value passed to the *field* parameter.

Shortcut example:
```
&"EventID:4624 LogonType:3" | agg :ComputerName | :TargetUserName
```

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

Unnamed lists are also supported:

```
:"EventID:4625" | sort [ComputerName,TargetDomainName,TargetUserName]
```

### Sub Expression Types

#### Search Expression

The verbs match to the query clauses from [Elasticsearch Query
DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html). Some shortcuts and syntactic
elements were added for simplification of EQUEL expressions, these are:

* Automatic recognition of search as Elasticsearch query string if first word is not a whitelisted EQUEL verb.
* Starting a search expression with a colon causes that it is treated as Elasticsearch query string. `:"some query"` is
  equivalent to `query_string query="some query"`.

#### Aggregation Expression

Multiple aggregation expressions are applied to each other in order of their appearance. An aggregation expression
follows the syntax stated above and can be prefixed with a nesting specification and end with a name assignment:

```
... | [agg <target>] ... [as <name>] | ...
```

The target name can be used to refer to a particular aggregation as nesting target from other aggregations or from
postprocessing and output expressions. Further aggregations are nested into the previous aggregation. If the agg keyword
is used in a later aggregation after the first one, it must be followed by an already defined aggregation name. The new
aggregation is then nested into the specified aggregation instead of the default behavior.

An aggregation is named agg*i* if no name is specified. *i* is an incrementing counter starting with 1.

#### Postprocessing and Output Expressions

These expressions simply follow the syntax stated above.

## Implementation Architecture

### Plugins

EQUEL is implemented in a plugin architecture. Plugins can register for a verb which is then used in EQUEL expressions
to address the plugin. The following plugin types are specified according to the expression syntax and semantics defined
above:

* search/search modifier plugin: generates a query DSL expression
* aggregation plugin: adds/nests an aggregation expression to a Elasticsearch Query DSL query.
* postprocessing plugin: gets an Elasticsearch result tree, modifies it and passes it to the next postprocessing module or to
  all following output modules.
* output plugin: gets an Elasticsearch result tree and outputs it

Parameters are passed as follows to the plugin:

* *param=value*: as dict element with *param* as key name. If a parameter name appears multiple times, all values are
  passed as list in the dict element.
* *flag*: as dict element with a default value (usually True, but can be specified otherwise by plugins)
* *param=\[value,...\]*: as above, but with a list as value. Multiple occurrences are passed as list inside of the list.
* *\[value,...\]*: as dict element with the key *unnamed_list*. Multiple unnamed lists are passed as list of lists.

There are two special cases for plugin names:

* *fallback*: if no plugin matches to the verb, this plugin is ivnoked. For searches and aggregations a plugin is
  invoked that performs a generic transormation.
* *shortcut*: A specialized shortcut plugin is invoked.

Generally a plugin object is instantiated on usage and the apply method is called as follows for the two known plugin
types:

* *Normal plugin*: plugin.apply(verb, params)
* *Shortcut plugin*: plugin.apply(prefix, value)

## API

### Usage

### Extension

## Future Plans

So many ideas, so little time...

Feel free to pick up an idea and implement it, but lets coordinate this to prevent of duplicate usage of resources on
the same task.

### Post-processing modules

* Aggregation of separate start/stop events into one event that combines both attributes.
* Mapping of values from documents returned by Elasticsearch to values from a database, e.g. Windows EventIDs to
  descriptions, IPs to hostnames.
* Find similar events around a specified event class (e.g. similar attacker activity around characteristic login events
  or command line invocations)

### Output modules

* Interactive HTML
* Graphical diagrams
    * Relationsip diagrams, e.g. communication between hosts, process dependencies.
* Textual tables
* Textual documentation

### Search Reusing Previous Results

Search expressions in a later position that use results from previous EQUEL subexpressions.

Example: search for spawning command line interpreters from uncommon processes and use session identifier to display
actions performed in the spawned shells.

### Relaxation of Strict Subexpression Type Order

Example: output subexpression for intermediate results.

### Adding Useful Operators to Searches

At the end of a search:

* groupby

Connecting searches:

* and
* or
* not

### Remove Subexpression Type Declarations

Remove agg, postproc and output keywords from first subexpression with a new type by assignment of verbs to types.

### Web Frontend

A web application as fronted for EQUEL that displays results and offers graphical visualization capabilities by
additional output plugins. Should be a separate project.

## Credits

* Florian Roth ([@Cyb3rOps](https://twitter.com/Cyb3rOps)) for
    * Many valuable suggestions and feedback
    * The fancy logo
* Ralf Glauberman for giving it the *EQUEL* name
