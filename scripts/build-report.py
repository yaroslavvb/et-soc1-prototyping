#!/usr/bin/env python3
"""Assemble a report from docs/reports/sources/<name>.{body.html,script.js,meta.json} plus a data JSON.

    scripts/build-report.py <name> <data.json> <out.html>

meta.json holds {"title", "description"}. The shared shell and CSS are in report.template.html; the body closes
<main> itself, and the script sees the data as the constant D. The shared chart toolkit, sources/chartkit.js, is
inlined in its own script just before the page script, so the script also sees CK (PLAN2 §2.5 lists its API).

TeX between $$ or \\( \\) is rendered to inline SVG by scripts/tex2svg.js, which needs mathjax-full. package.json
pins it to 3.2.1, the version that built the published pages (3.2.2 gives byte-identical SVGs); install it once, at
the repo root, with
    npm ci
In a git worktree without its own node_modules, set NODE_PATH to a checkout's node_modules.

A page whose script needs a block that a separate step adds to its data refuses to build without it (REQUIRED below:
dvfs-leakage needs `cards`, which tools/ettelem/build_cards_data.py --merge writes into dvfs.json, and `dv2`, which
tools/ettelem/build_dv2_data.py --merge writes)."""
import json
import os
import re
import subprocess
import sys

S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reports", "sources")
name, data_path, out = sys.argv[1:4]
meta = json.load(open(os.path.join(S, name + ".meta.json")))
# Data blocks a page's script cannot run without, and the step that adds each. Without this check the page builds,
# then throws in the reader's browser and leaves whole sections empty.
REQUIRED = {
    "dvfs-leakage": {"cards": "run tools/ettelem/build_cards_data.py ... --merge <dvfs.json> after analyze_dvfs.py "
                              "(the full chain is in the page's Method section and docs/getting-started.md)",
                     "dv2": "run tools/ettelem/build_dv2_data.py --data docs/reports/data/2026-09-28-dvfs2-aifoundry2 "
                            "--merge <dvfs.json> after build_cards_data.py (the page's 'Reproduce this')"},
}
data = json.load(open(data_path))
missing = [f"no '{k}' block: {how}" for k, how in REQUIRED.get(name, {}).items() if k not in data]
if missing:
    raise SystemExit(f"{data_path} is incomplete for {name}:\n  " + "\n  ".join(missing))
tpl = open(os.path.join(S, "report.template.html")).read().replace("</script>\n</main>\n</body>", "</script>\n</body>")
body = open(os.path.join(S, name + ".body.html")).read()
# Math is rendered to standalone SVG here, at build time: the hosts these reports are published to block
# external scripts, so a runtime MathJax from a CDN would leave the equations as raw TeX. Display math is
# $$ ... $$, inline math is \( ... \). Anything inside <pre> or <code> is left alone.
CODE = re.compile(r"<pre\b.*?</pre>|<code\b.*?</code>", re.S)
MATH = re.compile(r"\$\$(.+?)\$\$|\\\((.+?)\\\)", re.S)


def render_math(html):
    """Replace every TeX fragment outside code with the SVG MathJax renders for it."""
    spans, pos, parts = [], 0, []
    for m in CODE.finditer(html):  # split into (text, code, text, code, ...)
        parts.append(("t", html[pos:m.start()]))
        parts.append(("c", m.group(0)))
        pos = m.end()
    parts.append(("t", html[pos:]))
    items = []
    for kind, chunk in parts:
        if kind == "t":
            for m in MATH.finditer(chunk):
                items.append({"tex": (m.group(1) or m.group(2)).strip(), "display": m.group(1) is not None})
    if not items:
        return html, 0
    proc = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex2svg.js")],
                          input=json.dumps({"items": items}), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("tex2svg.js failed (run `npm ci` at the repo root; it installs mathjax-full 3.2.1):\n"
                         + proc.stderr[-2000:])
    svgs = iter(json.loads(proc.stdout)["svg"])
    out = []
    for kind, chunk in parts:
        if kind == "c":
            out.append(chunk)
            continue
        out.append(MATH.sub(lambda m: ('<span class="math-display">%s</span>' if m.group(1) is not None
                                       else '<span class="math-inline">%s</span>') % next(svgs), chunk))
    return "".join(out), len(items)


body, n_math = render_math(body)

# A page's script may pull in another file of sources/ with a line /*@include name.js*/ (the chip diagram's deep zoom,
# 30 Sep 2026: its outside levels and the circuit kit copied from the memory levels); the file is inserted in place,
# so it shares the page script's scope. A missing file stops the build. Since 1 Oct 2026 (the shared ladder of the chip
# diagram and the memory levels) an included file may include others (at most 4 deep, never itself), and a page's body
# may pull in a stylesheet the same way, /*@include name.css*/ on a line of its own inside a <style>.
INCLUDE = re.compile(r"^[ \t]*/\*@include ([\w.\-]+)\*/[ \t]*$", re.M)
USED = []


def includes(text, stack=(), ext=('.js',)):
    def one(m):
        fn = m.group(1)
        where = stack[-1] if stack else name
        if not fn.endswith(ext):
            raise SystemExit(f"{where} includes {fn}: only {' or '.join(ext)} files may be included there")
        if fn in stack:
            raise SystemExit(f"{name}: the includes form a cycle: {' -> '.join(stack + (fn,))}")
        if len(stack) >= 4:
            raise SystemExit(f"{name}: includes nested more than 4 deep: {' -> '.join(stack + (fn,))}")
        f = os.path.join(S, fn)
        if not os.path.exists(f):
            raise SystemExit(f"{where} includes {fn}, which is not in docs/reports/sources/")
        USED.append(fn)
        return includes(open(f).read(), stack + (fn,), ext)
    return INCLUDE.sub(one, text)


def top_names(js):
    """The names a script declares at its top level: function, class, const, let and var declarations at column 0 at
    the shallowest bracket depth any has, with every declarator of a const/let/var list and the names in a destructuring pattern. A light scanner:
    it skips strings, template literals, comments and regular expressions while it counts brackets. Since 1 Oct 2026
    (the memory levels host the shared ladder in a scope of its own beside their own) each name comes with its scope,
    the position of the innermost bracket around it (-1: none), and the scopes of the /*@hooks ...*/ comments are
    returned too. Returns ([(name, line, scope)], {hooks comment position: scope})."""
    out, n, i, depth, prev, line = [], len(js), 0, 0, ';', 1
    opens = []      # the positions of the brackets open at i
    hooks = {}      # a /*@hooks ...*/ comment's position: its scope
    decl = re.compile(r'(?:async[ \t]+)?function\*?[ \t]+([A-Za-z_$][\w$]*)|class[ \t]+([A-Za-z_$][\w$]*)|(?:const|let|var)[ \t]+')
    ident = re.compile(r'[A-Za-z_$][\w$]*')
    want = False   # in a const/let/var list: the next declarator's name follows
    inlist = False  # in a const/let/var statement (a comma at its depth starts the next declarator)
    d0 = 0          # the depth of that statement

    def pattern(i):
        """the names of a destructuring pattern starting at js[i] ({ or [); returns (names, end)"""
        j, d = i, 0
        while j < n:
            if js[j] in '{[':
                d += 1
            elif js[j] in '}]':
                d -= 1
                if d == 0:
                    break
            j += 1
        names = []
        for part in re.sub(r'\.\.\.', '', js[i + 1:j]).split(','):
            nm = part.split(':')[-1].split('=')[0].strip()
            if re.match(r'^[A-Za-z_$][\w$]*$', nm):
                names.append(nm)
        return names, j + 1

    def skip_ws(i):
        nonlocal line
        while i < n and js[i] in ' \t\n\r':
            if js[i] == '\n':
                line += 1
            i += 1
        return i

    while i < n:
        c = js[i]
        if i == 0 or js[i - 1] == '\n':
            m = decl.match(js, i)
            if m:
                if m.group(1) or m.group(2):
                    out.append((m.group(1) or m.group(2), line, depth, opens[-1] if opens else -1)); i = m.end(); prev = 'a'; continue
                i = m.end(); want = True; inlist = True; d0 = depth
        if want and depth == d0:
            i = skip_ws(i)
            if i < n and js[i] in '{[':
                names, i = pattern(i)
                out.extend((nm, line, d0, opens[-1] if opens else -1) for nm in names)
            else:
                mm = ident.match(js, i)
                if mm:
                    out.append((mm.group(0), line, d0, opens[-1] if opens else -1)); i = mm.end()
            want = False; prev = 'a'; continue
        if c == '\n':
            line += 1
            # a new statement at column 0 ends a list that had no semicolon
            if depth == d0 and inlist and i + 1 < n and js[i + 1] not in ' \t\n.?:+-*/&|,)]}=<>':
                inlist = False
        if c in '\'"`':
            q = c; i += 1
            while i < n and js[i] != q:
                if js[i] == '\\':
                    i += 1
                elif js[i] == '\n':
                    line += 1
                elif q == '`' and js[i] == '$' and i + 1 < n and js[i + 1] == '{':
                    d2 = 1; i += 2
                    while i < n and d2:
                        ch = js[i]
                        if ch == '{':
                            d2 += 1
                        elif ch == '}':
                            d2 -= 1
                        elif ch == '\n':
                            line += 1
                        elif ch in '\'"`':
                            q2 = ch; i += 1
                            while i < n and js[i] != q2:
                                if js[i] == '\n':
                                    line += 1
                                i += 2 if js[i] == '\\' else 1
                        i += 1
                    continue
                i += 1
            i += 1; prev = 'a'; continue
        if c == '/' and i + 1 < n and js[i + 1] == '/':
            j = js.find('\n', i); i = n if j < 0 else j; continue
        if c == '/' and i + 1 < n and js[i + 1] == '*':
            if js.startswith('/*@hooks ', i):
                hooks[i] = opens[-1] if opens else -1
            j = js.find('*/', i + 2); line += js.count('\n', i, n if j < 0 else j); i = n if j < 0 else j + 2; continue
        if c == '/' and prev in '(,=:[!&|?{};+-*%<>~^':
            i += 1; cls = False
            while i < n and (js[i] != '/' or cls):
                if js[i] == '\\':
                    i += 1
                elif js[i] == '[':
                    cls = True
                elif js[i] == ']':
                    cls = False
                i += 1
            i += 1; prev = 'a'; continue
        if c in '([{':
            depth += 1; opens.append(i)
        elif c in ')]}':
            depth -= 1
            if opens:
                opens.pop()
        elif c == ',' and depth == d0 and inlist:
            want = True
        elif c == ';' and depth == d0:
            inlist = False
        if not c.isspace():
            if c.isalnum() or c in '_$':
                mm = ident.match(js, i)
                w = mm.group(0) if mm else c
                prev = '(' if w in ('return', 'typeof', 'case', 'in', 'of', 'new', 'delete', 'void', 'throw', 'else') else 'a'
                i += len(w); continue
            prev = c
        i += 1
    # each scope's names apart: a page script wrapped in (() => { ... })() declares its names two brackets deep, a
    # closure's own names (circuitkit's), deeper, are its own, and the memory levels' two scopes (their own and the
    # ladder's, 1 Oct 2026) each theirs
    return [(nm, ln, sc) for nm, ln, d, sc in out], hooks


def guard(script):
    """The include guard (1 Oct 2026): a name declared twice in one scope of the expanded script (a second const or let
    stops the page when it loads, and a second function silently replaces the first: the includes share the scope they
    are included in), and the shared ladder's hooks (ladder-core.js, /*@hooks ...*/) not declared in the scope the core
    is included in. Returns the problems, [] when there are none (tools/pagemotion/guard_test.py plants both)."""
    names, hscope = top_names(script)
    seen, dup = {}, []
    for nm, ln, sc in names:
        if (sc, nm) in seen:
            dup.append(f"a name is declared twice at the top level of the page script and its includes: {nm} (lines {seen[(sc, nm)]} and {ln} of the expanded script)")
        else:
            seen[(sc, nm)] = ln
    HOOKS = re.compile(r"/\*@hooks ([^*]*)\*/")
    need = [(h, hscope.get(m.start(), -1)) for m in HOOKS.finditer(script) for h in m.group(1).split()]
    miss = [h for h, sc in need if (sc, h) not in seen]
    if miss:
        dup.append(f"the page does not define the hooks the shared ladder calls: {', '.join(miss)}")
    return dup


# ---- the built page's comments (1 Oct 2026, the code review of the shared ladder: comments were 14-15% of the two
# interactive pages' scripts, which sat at 95-97% of their size budgets): a page whose meta.json has "strip_comments"
# ships its script without the comments that take whole lines (the sources keep them). A lexer of strings, template
# literals with nested ${...}, regular expressions and comments finds them; a comment after code on its line stays.

def lex_comments(js):
    """yield (start, end, kind) of every comment, kind '//' or '/*'"""
    n, i = len(js), 0
    stack = []          # template nesting: each entry the brace depth at which a ${ opened
    depth = 0
    prev = ''           # the previous significant token, for regex detection
    KW = {'return', 'typeof', 'case', 'in', 'of', 'new', 'delete', 'void', 'throw', 'else', 'do', 'instanceof', 'yield', 'await'}
    out = []
    def regex_ok():
        if prev == '':
            return True
        if prev in KW:
            return True
        if re.match(r'^[A-Za-z_$0-9]', prev) or prev in (')', ']', '}'):
            return prev == '}'  # after a block's } a regex may start a statement; ) ] identifiers numbers: division
        return True
    while i < n:
        c = js[i]
        if c in ' \t\r\n':
            i += 1; continue
        if c == '/' and i + 1 < n and js[i + 1] == '/':
            j = js.find('\n', i); j = n if j < 0 else j
            out.append((i, j, '//')); i = j; continue
        if c == '/' and i + 1 < n and js[i + 1] == '*':
            j = js.find('*/', i + 2); j = n if j < 0 else j + 2
            out.append((i, j, '/*')); i = j; continue
        if c in '\'"':
            q = c; i += 1
            while i < n and js[i] != q:
                if js[i] == '\\':
                    i += 1
                elif js[i] == '\n':
                    raise ValueError(f'newline in a string at {i}: {js[i-60:i+10]!r}')
                i += 1
            i += 1; prev = 'str'; continue
        if c == '`':
            i += 1
            while True:
                if i >= n:
                    raise ValueError('unterminated template')
                ch = js[i]
                if ch == '\\':
                    i += 2; continue
                if ch == '`':
                    i += 1; break
                if ch == '$' and i + 1 < n and js[i + 1] == '{':
                    # code inside ${...}: lex recursively until the matching }
                    i = lex_code_until_brace(js, i + 2, out)
                    continue
                i += 1
            prev = 'str'; continue
        if c == '/' and regex_ok():
            i += 1; cls = False
            while i < n and (js[i] != '/' or cls):
                if js[i] == '\\':
                    i += 1
                elif js[i] == '[':
                    cls = True
                elif js[i] == ']':
                    cls = False
                elif js[i] == '\n':
                    raise ValueError(f'newline in a regex at {i}: {js[i-80:i+5]!r}')
                i += 1
            i += 1
            while i < n and js[i].isalpha():
                i += 1
            prev = 'regex'; continue
        m = re.compile(r'[A-Za-z_$][\w$]*|\d[\w.]*').match(js, i)
        if m:
            prev = m.group(0); i = m.end(); continue
        prev = c; i += 1
    return out

def lex_code_until_brace(js, i, out):
    """lex code from i until the } that closes a ${ (comments inside are not stripped: they are recorded only)"""
    n, d, prev = len(js), 0, '('
    while i < n:
        c = js[i]
        if c == '}' and d == 0:
            return i + 1
        if c == '{':
            d += 1
        elif c == '}':
            d -= 1
        if c in '\'"':
            q = c; i += 1
            while i < n and js[i] != q:
                if js[i] == '\\':
                    i += 1
                i += 1
            i += 1; continue
        if c == '`':
            i += 1
            while i < n and js[i] != '`':
                if js[i] == '\\':
                    i += 2; continue
                if js[i] == '$' and i + 1 < n and js[i + 1] == '{':
                    i = lex_code_until_brace(js, i + 2, out); continue
                i += 1
            i += 1; continue
        if c == '/' and i + 1 < n and js[i + 1] == '*':
            j = js.find('*/', i + 2); i = j + 2; continue
        i += 1
    raise ValueError('unterminated ${')

def strip(js):
    cm = lex_comments(js)
    keep, last, removed = [], 0, 0
    for s, e, k in cm:
        ls = js.rfind('\n', 0, s) + 1
        if js[ls:s].strip():
            continue                     # after code on its line: stays
        le = js.find('\n', e); le = len(js) if le < 0 else le
        if js[e:le].strip():
            continue                     # code after the comment on its last line: stays
        keep.append(js[last:ls]); last = le + 1 if le < len(js) else le
        removed += js.count('\n', ls, le) + 1
    keep.append(js[last:])
    return ''.join(keep), removed


def strip_comments(js):
    s, _ = strip(js)
    return s


script = includes(open(os.path.join(S, name + ".script.js")).read())
if USED:
    problems = guard(script)
    if problems:
        raise SystemExit(f"{name}: " + "\n  ".join(problems))
if meta.get("strip_comments"):
    script = strip_comments(script)
body = includes(body, ext=('.css',))
html = (tpl.replace("__CHARTKIT__", open(os.path.join(S, "chartkit.js")).read())
        .replace("__TITLE__", meta["title"]).replace("__DESC__", meta["description"])
        .replace("__BODY__", body)
        .replace("__DATA__", json.dumps(data, separators=(",", ":")))
        .replace("__SCRIPT__", script))
open(out, "w").write(html)
print("wrote", out, len(html), "bytes" + (f", {n_math} equations rendered to SVG" if n_math else ""))
