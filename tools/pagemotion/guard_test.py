#!/usr/bin/env python3
"""guard_test.py: build-report.py's include guard (DESIGN §5.4 T16, since 1 Oct 2026): it refuses a name declared twice in
one scope and a page that lacks a hook the shared core calls, and accepts the same name in two scopes (the memory
levels' own scope and the shared ladder's beside it). Prints PASS or FAIL lines; the exit code is the number of failures."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '..', '..', 'scripts', 'build-report.py')).read()
ns = {'re': re, 'os': os}
exec(src[src.index('def top_names'):src.index('script = includes(open(')], ns)
guard = ns['guard']
fails = 0


def ok(c, what, extra=''):
    global fails
    fails += 0 if c else 1
    print(('PASS ' if c else 'FAIL ') + what + ('  ' + str(extra) if extra else ''))


core = "/*@hooks pageExits pageBusy*/\nconst Z = {};\nfunction goTo() {}\n"
page = "(function () {\n'use strict';\n" + core + "function pageExits() {}\nfunction pageBusy() {}\n})();\n"
ok(guard(page) == [], 'one scope with the core and its hooks: accepted', guard(page))
ok(any('declared twice' in p and 'goTo' in p for p in guard(page.replace("function pageBusy() {}", "function pageBusy() {}\nfunction goTo() {}"))),
   'a function declared twice in one scope: refused')
ok(any('declared twice' in p and ' Z ' in p for p in guard(page.replace("function pageBusy() {}", "function pageBusy() {}\nconst Z = 1;"))),
   'a const declared twice in one scope: refused')
ok(any('hooks' in p and 'pageBusy' in p for p in guard(page.replace("function pageBusy() {}\n", ""))), 'a missing hook: refused')
two = "let MLB = null, MLH = null;\n(function () {\n'use strict';\nconst Z = {lv: 'l1'};\nfunction goTo() {}\n})();\nMLH = (function (DM) {\n'use strict';\n" + core + "function pageExits() {}\nfunction pageBusy() {}\nreturn {};\n})(D);\n"
ok(guard(two) == [], 'the same names in two scopes (the memory levels\' and the ladder\'s): accepted', guard(two))
ok(any('hooks' in p for p in guard(two.replace("function pageExits() {}\nfunction pageBusy() {}\nreturn {};", "return {};").replace("const Z = {lv: 'l1'};", "const Z = {lv: 'l1'};\nfunction pageExits() {}\nfunction pageBusy() {}"))),
   'hooks declared in another scope than the core\'s: refused')
print(f'{fails} failed')
sys.exit(fails)
