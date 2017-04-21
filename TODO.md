## Future Plans

So many ideas, so little time...

Feel free to pick up an idea and implement it, but lets coordinate this to prevent of duplicate usage of resources on
the same task.

### Post-processing modules

* Mapping of values from documents returned by Elasticsearch to values from a database or mapping file, e.g. Windows EventIDs to
  descriptions, IPs to hostnames.
* Aggregation of separate start/stop events into one event that combines both attributes.
* Find similar events around a specified event class (e.g. similar attacker activity around characteristic login events
  or command line invocations)
* Temporal correlation of events. Search the temporal context of each search hit for hits to another query.
  Include additional hits of such searches or drop original hit if secondary search fails to find anything.

### Output modules

* Interactive HTML
* Graphical diagrams with Graphviz/vis.js/Neo4j
    * Relationsip diagrams, e.g. communication between hosts, process dependencies.

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

## Known Bugs

* Further aggregations at root level not possible

* Aggregationi plugins that add aggregations by the AggregationHierarchy instance passed as parameter, like
  AggregationKeywordsPlugin, have no possibility to determine the name passed by user via 'as' keyword. The names are
  therefore currently ignored.
