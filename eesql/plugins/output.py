# Output Plugins
from .generic import EESQLPluginException
import json
import re

reRemoveIndices = re.compile('\[\d+\]')

class BaseOutputPlugin:
    """Base class for output plugins"""
    _expectedParams = ()    # list of expected params as (name, default_value) tuples for storage of params dict
    def apply(self, verb, params, _):
        """
        The following parameters are passed to this method:

        * the verb from the EESQL expression as string
        * the parameters from the EESQL expression as dict (name->value)

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
        return json.dumps(result.result, indent=2)

class TextOutputPlugin(BaseOutputPlugin):
    """
    Returns text in the following format:

    mainvalue
    param1=value1 [...]

    mainvalue is the value of a dedicated field, e.g. raw log message.

    Parameters:
    * color (flag): Colorize output, highlight captions and main value with terminal escape sequences.
    * mainfield: Name of the main field where the main value is pulled from. If not given, no mainvalue is shown.
    * fields: List of fields to display. If not given, all fields are displayed.
    * exclude: List of fields not to display.
    * maxmainlen: Maximum length of main value.
    * maxvallen: Maximum value length.
    * entryspace: number of empty lines between entries.
    * condensed: do not start a new line for each field.
    """
    _expectedParams = (
                ("color", True),
                ("mainfield", None),
                ("fields", list()),
                ("exclude", list()),
                ("maxmainlen", 120),
                ("maxvallen", 80),
                ("docsep", 1),
                ("condensed", False),
            )

    def apply(self, verb, params, _):
        """Parameter postprocessing"""
        print(params)
        super().apply(verb, params, _)
        if type(self.params['fields']) == str:
            self.params['fields'] = [self.params['fields']]
        if type(self.params['exclude']) == str:
            self.params['exclude'] = [self.params['exclude']]
        return self

    def colorize(self, text, *args, **kwargs):
        """Output colorized if configured"""
        if self.params['color']:
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

    def render_fields(self, docpart, prefix=""):
        """
        Renders fields of a part of a document recursively. Parameters:

        * docpart: part of the document to render
        * prefix: prefix of field names for the processed docpart
        """
        suffix = "\n"
        if self.params['condensed']:
            suffix = " "
        result = ""
        maxlen = self.params['maxvallen']
        if type(docpart) == dict:
            for key in docpart:
                if prefix == "":
                    cprefix = key
                else:
                    cprefix = prefix + "." + key

                if type(docpart[key]) in (dict, list):
                    result += self.render_fields(docpart[key], cprefix)
                else:
                    if self.check_field_output(cprefix):
                        origval = str(docpart[key])
                        val = origval[:maxlen]
                        if len(origval) > len(val):
                            val += self.colorize("[...]", attrs=["dark"])
                        result += "%s%s%s%s" % (self.colorize(cprefix, "green"), self.colorize("=", "yellow"), val, suffix)
        elif type(docpart) == list:
            for i in range(0, len(docpart)):
                cprefix = prefix + "[%d]" % (i + 1)

                if type(docpart[i]) in (dict, list):
                    result += self.render_fields(docpart[i], cprefix)
                else:
                    if self.check_field_output(cprefix):
                        origval = str(docpart[i])
                        val = origval[:maxlen]
                        if len(origval) > len(val):
                            val += self.colorize("[...]", attrs=["dark"])
                        result += "%s%s%s%s" % (self.colorize(cprefix, "green"), self.colorize("=", "yellow"), val, suffix)
        else:
            result += str(docpart) + suffix

        return result

    def render(self, result):
        output = ""
        for doc in result.result["hits"]["hits"]:  # iterate over all documents from result
            if 'mainfield' in self.params:
                try:
                    mainfieldpath = self.params['mainfield'].split(".")
                    docpart = doc['_source']
                    for key in mainfieldpath:
                        docpart = docpart[key]
                    origval = str(docpart)
                    val = origval[:self.params['maxmainlen']]
                    output += self.colorize(val, "yellow", "on_blue", ["bold"])
                    if len(origval) > len(val):
                        output += self.colorize("[...]", "yellow", "on_blue")
                    output += "\n"
                except:
                    output += "-\n"
            output += self.render_fields(doc['_source'])
            output += self.params['docsep'] * "\n"
        return output
