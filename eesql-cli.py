#!/usr/bin/env python3
# Command line interface to compile ElasticSearch queries from EESQL expressions and perform queries against an ES instance.

import argparse
from elasticsearch import Elasticsearch
from eesql.engine import EESQLEngine
import json
import sys

argparser = argparse.ArgumentParser(description="EESQL Command Line Interface")
argparser.add_argument("--server", "-s", action="append", default="localhost", help="ElasticSearch server")
argparser.add_argument("--index", "-i", default="*", help="ElasticSearch index pattern to query")
argparser.add_argument("--max-results", "-m", type=int, default=1000, help="Maximum returned documents")
argparser.add_argument("--compileonly", "-c", action="store_true", help="Only compile EESQL to ES query - don't perform any requests")
argparser.add_argument("--indent", "-I", type=int, default=2, help="Indent request with given width")
argparser.add_argument("--file", "-f", action="store_true", help="Treat expression as file that contains an EESQL expression")
argparser.add_argument("expression", help="Expression or file name")
args = argparser.parse_args()

e = EESQLEngine(args.server, args.index)
if args.file:
    request = e.parseEESQLFile(args.expression)
else:
    request = e.parseEESQL(args.expression)

if args.compileonly:
    print(request.jsonQuery(indent=args.indent))
    sys.exit(0)

res = request.execute(size=args.max_results)
for name in res.outputs:
    print("===== Output: %s =====" % (name))
    print(res.outputs[name])
