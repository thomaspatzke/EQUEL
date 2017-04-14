#!/usr/bin/env python3
# Command line interface to compile ElasticSearch queries from EQUEL expressions and perform queries against an ES instance.

import argparse

# change default decoding error behaviour to less strict 'replace', globally
import codecs
codecs.register_error('strict', codecs.replace_errors)

from elasticsearch import Elasticsearch
from equel.engine import EQUELEngine
import json
import sys

argparser = argparse.ArgumentParser(description="EQUEL Command Line Interface")
argparser.add_argument("--server", "-s", action="append", default="localhost", help="ElasticSearch server")
argparser.add_argument("--index", "-i", default="*", help="ElasticSearch index pattern to query")
argparser.add_argument("--max-results", "-m", type=int, default=1000, help="Maximum returned documents")
argparser.add_argument("--timeout", "-t", type=int, default=60, help="Request timeout")
argparser.add_argument("--outputs", "-O", help="Select output streams as comma separated list: output1.stream1,output2.stream2,[...]")
argparser.add_argument("--compileonly", "-c", action="store_true", help="Only compile EQUEL to ES query - don't perform any requests")
argparser.add_argument("--indent", "-I", type=int, default=2, help="Indent request with given width")
argparser.add_argument("--file", "-f", action="store_true", help="Treat expression as file that contains an EQUEL expression")
argparser.add_argument("expression", help="Expression or file name")
args = argparser.parse_args()

# parse outputs (-O) parameter
selected_outputs = dict()
if args.outputs:
    outputs = args.outputs.split(",")
    for output in outputs:
        try:
            out, stream = output.split(".")
            try:
                selected_outputs[out].add(stream)
            except KeyError:
                selected_outputs[out] = { stream }
        except ValueError:
            print("Output selection must have format output.stream", file=sys.stderr)
            sys.exit(10)
else:
    selected_outputs = None

e = EQUELEngine(args.server, args.index)
if args.file:
    request = e.parseEQUELFile(args.expression)
else:
    request = e.parseEQUEL(args.expression)

if args.compileonly:
    print(request.jsonQuery(indent=args.indent))
    sys.exit(0)

res = request.execute(size=args.max_results)
for name in res.outputs:
    if selected_outputs and name not in selected_outputs:
        continue
    output = res.outputs[name]
    print("===== Output: %s =====" % (name))
    if output:
        for stream in output:
            if selected_outputs and stream not in selected_outputs[name]:
                continue
            print("========== Output Stream '%s':" % (stream))
            print(output[stream])
