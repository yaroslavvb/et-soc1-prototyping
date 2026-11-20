#!/usr/bin/env python3
"""decl-e217: parse each named Python file (syntax only; nothing runs).   /usr/bin/python3 -I -B w00_syntax.py <file> ..."""
import ast
import sys

for f in sys.argv[1:]:
    ast.parse(open(f).read(), f)
    print('syntax ok', f.rsplit('/', 1)[-1])
