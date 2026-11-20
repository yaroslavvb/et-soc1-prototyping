#!/usr/bin/env python3
"""counts-e214: exit 0 only when a check file's top-level "pass" is true.   /usr/bin/python3 -I -B passcheck.py <json>"""
import json
import sys

sys.exit(0 if json.load(open(sys.argv[1])).get('pass') is True else 1)
