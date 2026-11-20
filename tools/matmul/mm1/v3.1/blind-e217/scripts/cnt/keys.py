#!/usr/bin/env python3
"""counts-e214: print a spec file's kind keys, comma-joined (for count_e210.py --kinds).   /usr/bin/python3 -I -B keys.py <spec json>"""
import json
import sys

print(','.join(json.load(open(sys.argv[1]))))
