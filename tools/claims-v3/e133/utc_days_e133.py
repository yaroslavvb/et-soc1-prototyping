#!/usr/bin/env python3
"""E133: the UTC dates (YYYY-MM-DD) an epoch-second span touches, space-separated (collect_e133.sh's history files are per UTC day)."""
import sys
import time

a, b = int(sys.argv[1]), int(sys.argv[2])
days = sorted({time.strftime("%Y-%m-%d", time.gmtime(t)) for t in range(a, b + 1, 3600)} | {time.strftime("%Y-%m-%d", time.gmtime(b))})
print(" ".join(days))
