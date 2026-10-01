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
    it skips strings, template literals, comments and regular expressions while it counts brackets. Returns
    [(name, line)]."""
    out, n, i, depth, prev, line = [], len(js), 0, 0, ';', 1
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
                    out.append((m.group(1) or m.group(2), line, depth)); i = m.end(); prev = 'a'; continue
                i = m.end(); want = True; inlist = True; d0 = depth
        if want and depth == d0:
            i = skip_ws(i)
            if i < n and js[i] in '{[':
                names, i = pattern(i)
                out.extend((nm, line, d0) for nm in names)
            else:
                mm = ident.match(js, i)
                if mm:
                    out.append((mm.group(0), line, d0)); i = mm.end()
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
            depth += 1
        elif c in ')]}':
            depth -= 1
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
    # the top level: the shallowest depth a declaration at column 0 is at (a page script wrapped in (() => { ... })()
    # declares its names two brackets deep; a closure's own names, deeper, are its own)
    top = min((d for _, _, d in out), default=0)
    return [(nm, ln) for nm, ln, d in out if d == top]


script = includes(open(os.path.join(S, name + ".script.js")).read())
# a name declared twice at the top level: a second const or let stops the page when it loads, and a second function
# silently replaces the first (the includes share the page script's scope, so this guards them; 1 Oct 2026)
if USED:
    seen, dup = {}, []
    for nm, ln in top_names(script):
        if nm in seen:
            dup.append(f"{nm} (lines {seen[nm]} and {ln} of the expanded script)")
        else:
            seen[nm] = ln
    if dup:
        raise SystemExit(f"{name}: a name is declared twice at the top level of the page script and its includes:\n  " + "\n  ".join(dup))
    # the shared ladder's hooks: every one the core names must be declared by the page (ladder-core.js, /*@hooks ...*/)
    HOOKS = re.compile(r"/\*@hooks ([^*]*)\*/")
    need = [h for m in HOOKS.finditer(script) for h in m.group(1).split()]
    miss = [h for h in need if h not in seen]
    if miss:
        raise SystemExit(f"{name}: the page does not define the hooks the shared ladder calls: {', '.join(miss)}")
body = includes(body, ext=('.css',))
html = (tpl.replace("__CHARTKIT__", open(os.path.join(S, "chartkit.js")).read())
        .replace("__TITLE__", meta["title"]).replace("__DESC__", meta["description"])
        .replace("__BODY__", body)
        .replace("__DATA__", json.dumps(data, separators=(",", ":")))
        .replace("__SCRIPT__", script))
open(out, "w").write(html)
print("wrote", out, len(html), "bytes" + (f", {n_math} equations rendered to SVG" if n_math else ""))
