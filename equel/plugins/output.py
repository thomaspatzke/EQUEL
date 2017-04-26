# Output Plugins
from .generic import EQUELPluginException
from equel import engine
import json
import re

reRemoveIndices = re.compile('\[\d+\]')

class BaseOutputPlugin:
    """Base class for output plugins"""
    _expectedParams = ()    # list of expected params as (name, default_value) tuples for storage of params dict
    def apply(self, verb, params, parser, ctx):
        """
        The following parameters are passed to this method:

        * the verb from the EQUEL expression as string
        * the parameters from the EQUEL expression as dict (name->value)

        All parameters are stored in params dict. If parameter from expected params is missing, it is stored with the given default value
        """
        self.params = dict()
        for name, value in self._expectedParams:
            if name not in params:
                self.params[name] = value
            else:
                self.params[name] = params[name]
        return self
    
    def render(self, result):
        """
        Output plugins usually return strings that are shown to users, but may return specific objects for e.g. web application frameworks.
        The result object is passed to this method.
        
        """
        out = engine.EQUELOutput(engine.EQUELOutput.TYPE_TEXT)
        out.append(json.dumps(result.result, indent=2))
        return out

class FieldSelectionMixin():
    """
    Default functions for selection of fields for output plugins. They must define two parameters: fields and exclude.
    """

    def apply(self, verb, params, parser, ctx):
        """Parameter postprocessing"""
        super().apply(verb, params, parser, ctx)
        if type(self.params['fields']) == str:
            self.params['fields'] = [self.params['fields']]
        if type(self.params['exclude']) == str:
            self.params['exclude'] = [self.params['exclude']]
        return self

    def check_field_output(self, key):
        """
        Check if field should be output:

        * if whitelist is defined, field must be contained here and not contained on blacklist
        * if no whitelist is defined, field must not be contained on blacklist

        List indices are stripped from field name.
        """
        cprefixni = reRemoveIndices.sub("", key)
        fields = self.params['fields']
        excludefields = self.params['exclude']
        return (len(fields) > 0 and cprefixni in fields and cprefixni not in excludefields) or (len(fields) <= 0 and cprefixni not in excludefields)

class TextOutputPlugin(BaseOutputPlugin, FieldSelectionMixin):
    """
    Returns text in the following format:

    mainvalue
    param1=value1 [...]

    mainvalue is the value of a dedicated field, e.g. raw log message.

    Parameters:
    * nocolor (flag): don't Colorize output. Colorization highlights captions and main value with terminal escape sequences.
    * mainfield: Name of the main field where the main value is pulled from. If not given, no mainvalue is shown.
    * fields: List of fields to display. If not given, all fields are displayed.
    * exclude: List of fields not to display.
    * maxmainlen: Maximum length of main value.
    * maxvallen: Maximum value length.
    * entryspace: number of empty lines between entries.
    * condensed: do not start a new line for each field.
    """
    _expectedParams = (
                ("nocolor", False),
                ("mainfield", None),
                ("fields", list()),
                ("exclude", list()),
                ("maxmainlen", 120),
                ("maxvallen", 80),
                ("docsep", 1),
                ("condensed", False),
            )

    def apply(self, verb, params, parser, ctx):
        """Parameter postprocessing"""
        super().apply(verb, params, parser, ctx)
        if type(self.params['fields']) == str:
            self.params['fields'] = [self.params['fields']]
        if type(self.params['exclude']) == str:
            self.params['exclude'] = [self.params['exclude']]
        return self

    def colorize(self, text, *args, **kwargs):
        """Output colorized if configured"""
        if not self.params['nocolor']:
            from termcolor import colored
            return colored(text, *args, **kwargs)
        else:
            return text
            
    def check_field_output(self, key):
        """
        Check if field should be output:

        * if whitelist is defined, field must be contained here and not contained on blacklist
        * if no whitelist is defined, field must not be contained on blacklist

        List indices are stripped from field name.
        """
        cprefixni = reRemoveIndices.sub("", key)
        fields = self.params['fields']
        excludefields = self.params['exclude']
        return (len(fields) > 0 and cprefixni in fields and cprefixni not in excludefields) or (len(fields) <= 0 and cprefixni not in excludefields)

    def render_fields(self, docpart, prefix="", namecolor="green"):
        """
        Renders fields of a part of a document recursively. Parameters:

        * docpart: part of the document to render
        * prefix: prefix of field names for the processed docpart
        """
        suffix = "\n"
        if self.params['condensed']:
            suffix = " "
        result = ""
        maxlen = int(self.params['maxvallen'])
        if type(docpart) == dict:
            for key in docpart:
                if prefix == "":
                    cprefix = key
                else:
                    cprefix = prefix + "." + key

                if type(docpart[key]) in (dict, list):
                    result += self.render_fields(docpart[key], cprefix, namecolor)
                else:
                    if self.check_field_output(cprefix):
                        origval = str(docpart[key])
                        val = origval[:maxlen]
                        if len(origval) > len(val):
                            val += self.colorize("[...]", attrs=["dark"])
                        result += "%s%s%s%s" % (self.colorize(cprefix, namecolor), self.colorize("=", "blue"), val, suffix)
        elif type(docpart) == list:
            for i in range(0, len(docpart)):
                cprefix = prefix + "[%d]" % (i + 1)

                if type(docpart[i]) in (dict, list):
                    result += self.render_fields(docpart[i], cprefix, namecolor)
                else:
                    if self.check_field_output(cprefix):
                        origval = str(docpart[i])
                        val = origval[:maxlen]
                        if len(origval) > len(val):
                            val += self.colorize("[...]", attrs=["dark"])
                        result += "%s%s%s%s" % (self.colorize(cprefix, namecolor), self.colorize("=", "blue"), val, suffix)
        else:
            result += str(docpart) + suffix

        return result

    def render_aggregation(self, output, agg, prefix=""):
        if "buckets" in agg:     # Bucket Aggregation
            numBuckets = len(agg['buckets'])
            i = 0
            for bucket in agg['buckets']:   # iterate over buckets and print key and document count
                i += 1
                lastBucket = i == numBuckets
                output.append(prefix)
                bucketPrefix = "  "
                if lastBucket:
                    output.append("└")
                else:
                    output.append("├")
                    bucketPrefix = "│ "
                output.appendLine((" %s " + self.colorize("(%d)", "red")) % (bucket['key'], bucket['doc_count']))

                subaggNames = set(bucket.keys()).difference(('key', 'doc_count'))
                numSubaggs = len(subaggNames)
                j = 0
                for subaggName in subaggNames:    # iterate over sub aggregations
                    j += 1
                    lastSubagg = j == numSubaggs
                    subagg = bucket[subaggName]
                    if type(subagg) == dict:
                        output.append(prefix + bucketPrefix)
                        subaggPrefix = "  "
                        if lastSubagg:
                            output.append("└")
                        else:
                            output.append("├")
                            subaggPrefix = "│ "
                        output.appendLine(self.colorize(" Aggregation: ", "yellow") + subaggName)
                        self.render_aggregation(output, subagg, prefix + bucketPrefix + subaggPrefix)
        else:   # metrics aggregation
            numMetrics = len(agg)
            i = 0
            for metric in agg:
                i += 1
                output.append(prefix)
                if i < numMetrics:
                    output.append("├")
                else:
                    output.append("└")
                if metric == "hits":
                    output.appendLine(" %s %s total hits=%d max score=%f" % (self.colorize(metric, "green"), self.colorize(":", "blue"), agg[metric]["total"], agg[metric]["max_score"]))
                    j = 0
                    numDocs = len(agg[metric]["hits"])
                    for doc in agg[metric]["hits"]:
                        j += 1
                        if j < numDocs:
                            output.appendLine("%s  ├ index=%s id=%s score=%f" % (prefix, doc["_index"], doc["_id"], doc["_score"]))
                            output.append(self.render_fields(doc["_source"], prefix + "  │  ", "white"))
                        else:
                            output.appendLine("%s  └ index=%s id=%s score=%f" % (prefix, doc["_index"], doc["_id"], doc["_score"]))
                            output.append(self.render_fields(doc["_source"], prefix + "     ", "white"))
                else:
                    output.appendLine(" %s %s %s" % (self.colorize(metric, "green"), self.colorize("=", "blue"), agg[metric]))

    def render(self, result):
        output = engine.EQUELOutput(engine.EQUELOutput.TYPE_TEXT, ["search", "aggregations"])

        # Search hits
        for doc in result.result["hits"]["hits"]:  # iterate over all documents from result
            if 'mainfield' in self.params:
                try:
                    mainfieldpath = self.params['mainfield'].split(".")
                    docpart = doc['_source']
                    for key in mainfieldpath:
                        docpart = docpart[key]
                    origval = str(docpart)
                    val = origval[:int(self.params['maxmainlen'])]
                    output.append(self.colorize(val, "yellow", "on_blue", ["bold"]))
                    if len(origval) > len(val):
                        output.append(self.colorize("[...]", "yellow", "on_blue"))
                    output.append("\n")
                except:
                    output.append("-\n")
            output.append(self.render_fields(doc['_source']))
            output.append(self.params['docsep'] * "\n")

        # Aggregations
        if 'aggregations' in result.result:
            output.selectStream("aggregations")
            aggs = result.result['aggregations']
            i = 0
            for aggName in aggs:
                i += 1
                output.appendLine(self.colorize("Aggregation: ", "yellow") + aggName)
                self.render_aggregation(output, aggs[aggName], "  ")

        return output

class CSVOutputPlugin(BaseOutputPlugin, FieldSelectionMixin):
    """
    Returns search result and aggregations in CSV format.

    Parameters:
    * fields: List of fields to display. If not given, all fields are displayed.
    * exclude: List of fields not to display.
    * dialect: Passed as dialect parameter to csv.DictWriter
    * header: output header as first line
    * nestedcolfield: name of a field which values are used as column name prefix in case of a multivalud nested documents
    * nestedvalfield: name of field of nested documents that contains value that is used in CSV 
    * listsep: Multivalued fields are joined in one CSV field separated by this string
    """

    _expectedParams = (
                ("fields", list()),
                ("exclude", list()),
                ("dialect", "excel"),
                ("header", True),
                ("nestedcolfield", None),
                ("nestedvalfield", None),
                ("listsep", ", "),
            )

    def columnNames(self, doc, prefix=""):
        """
        Recursively determine all column names for CSV generation as follows:

        * Use field name as column name for plain fields
        * For fields with subdocuments: use fieldname as prefix and create for each subdocument field a column fieldname.subfieldname. May be nested.
        * For multivalued fields with nested documents: if nested document has a field which name was configured in nestedcolfield, use the values of
          this field as column name part.

          Example:
          {"nested": [{"name": "foo", ...}, {"name": "bar", ...}]}

          is derived to following field names: nested.foo, nested.bar. The parameter nestedvalfield defines the field of the nested document that is
          used as value.

          For obvious reasons, the selected field shouldn't have too many distinct values.
        """
        columns = list()
        excluded = self.params['exclude']
        if type(doc) != dict:
            raise ValueError("Expected dict")

        for field, value in doc.items():
            if prefix + field in excluded:
                continue
            if type(value) == dict:  # field contains subfields - recurse and create field.subfield columns
                columns.extend(self.columnNames(value, prefix + field + "."))
            elif type(value) == list:  # multivalued field: contains values or nested docs?
                if type(value[0]) == dict and self.params['nestedcolfield'] != None:     # nested field
                    nestedcolfield = self.params['nestedcolfield']
                    nestedvalfield = self.params['nestedvalfield']
                    for subdoc in value:
                        try:
                            nestedcol = subdoc[nestedcolfield]
                            colname = prefix + field + "." + nestedcol
                            if colname in excluded:
                                continue
                            columns.append(colname)
                            if type(subdoc[nestedvalfield]) == dict:
                                columns.extend(self.columnNames(value[nestedvalfield], prefix + field + "." + nestedcol))
                        except KeyError:            # ignore if nested document doesn't contains field with column name
                            pass
            else:                               # value - use field name as column
                columns.append(prefix + field)

        return columns

    def extractFieldsFromDoc(self, doc, prefix=""):
        """Extract field values defined in self.columns from document into a dict required for csv.DictWriter."""
        res = dict()
        for field, value in doc.items():
            if type(value) == dict:             # subdocument
                res.update(self.extractFieldsFromDoc(value, prefix + field + "."))
            elif type(value) == list:
                if type(value[0]) == dict:      # multiple nested documents
                    nestedcolfield = self.params['nestedcolfield']
                    nestedvalfield = self.params['nestedvalfield']
                    if nestedcolfield != None and nestedvalfield != None:
                        for subdoc in value:
                            try:
                                nestedcol = prefix + field + "." + subdoc[nestedcolfield]
                                if nestedcol in self.columns:
                                    res[nestedcol] = subdoc[nestedvalfield]
                            except KeyError:    # nested document doesn't contains column name or value field
                                pass
                else:                           # multivalued field
                    if prefix + field in self.columns:
                        res[prefix + field] = self.params["listsep"].join(value)
            else:                               # simple value
                if prefix + field in self.columns:
                    res[prefix + field] = value
        return res

    def render(self, result):
        output = engine.EQUELOutput(engine.EQUELOutput.TYPE_TEXT, ["search"])

        self.columns = list()
        # First step: determine all columns that should appear in result of search result CSV
        if len(self.params['fields']) > 0:    # if field whitelist is given, take this
            self.columns = self.params['fields']
        else:
            for doc in result.result["hits"]["hits"]:  # iterate over all documents from result and pull columns from there
                doccolumns = self.columnNames(doc["_source"])
                for column in doccolumns:
                    if column not in self.columns:
                        self.columns.append(column)

        import csv
        csvwriter = csv.DictWriter(output, self.columns, dialect=self.params['dialect'])
        if self.params['header']:
            csvwriter.writeheader()

        # Next: Iterate over documents and fill CSV with data
        for doc in result.result["hits"]["hits"]:
            extracted = self.extractFieldsFromDoc(doc["_source"])
            csvwriter.writerow(extracted)

        return output
