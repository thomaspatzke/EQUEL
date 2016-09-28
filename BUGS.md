# Known Bugs

* Aggregationi plugins that add aggregations by the AggregationHierarchy instance passed as parameter, like
  AggregationKeywordsPlugin, have no possibility to determine the name passed by user via 'as' keyword. The names are
  therefore currently ignored.
