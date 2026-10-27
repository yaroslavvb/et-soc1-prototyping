"""Minimal Liberty (.lib) reader: group tree with attributes. Reads ASAP7 NLDM files."""
import re

NUM = re.compile(r'^-?[\d.]+(e-?\d+)?$', re.I)


class Group:
    __slots__ = ('gtype', 'name', 'attrs', 'groups')

    def __init__(self, gtype, name):
        self.gtype, self.name = gtype, name
        self.attrs = {}          # simple  key : value;
        self.groups = []         # child Groups

    def find(self, gtype, name=None):
        return [g for g in self.groups
                if g.gtype == gtype and (name is None or g.name == name)]

    def one(self, gtype, name=None):
        r = self.find(gtype, name)
        return r[0] if r else None


def _clean(v):
    v = v.strip().rstrip(';').strip()
    # strip the quotes of a single quoted string only -- a multi-row
    # `values ("r1", "r2", ...)` list also starts and ends with a quote.
    if v.startswith('"') and v.endswith('"') and v.count('"') == 2:
        v = v[1:-1]
    return v


def parse(path):
    # join continuation lines, strip /* */ comments
    txt = open(path, 'r', errors='replace').read()
    txt = re.sub(r'/\*.*?\*/', '', txt, flags=re.S)
    txt = txt.replace('\\\n', ' ')
    root = Group('root', '')
    stack = [root]
    for raw in txt.split('\n'):
        line = raw.strip()
        if not line:
            continue
        while line:
            # group open:  name (args) {
            m = re.match(r'^([A-Za-z_][\w]*)\s*\(([^)]*)\)\s*\{', line)
            if m:
                g = Group(m.group(1), _clean(m.group(2)))
                stack[-1].groups.append(g)
                stack.append(g)
                line = line[m.end():].strip()
                continue
            if line.startswith('}'):
                if len(stack) > 1:
                    stack.pop()
                line = line[1:].strip()
                continue
            # complex attr: name (v1, v2, ...);
            m = re.match(r'^([A-Za-z_][\w]*)\s*\(([^;]*)\)\s*;', line)
            if m:
                stack[-1].attrs.setdefault(m.group(1), []).append(_clean(m.group(2)))
                line = line[m.end():].strip()
                continue
            # simple attr: name : value;
            m = re.match(r'^([A-Za-z_][\w]*)\s*:\s*([^;]*);', line)
            if m:
                stack[-1].attrs.setdefault(m.group(1), []).append(_clean(m.group(2)))
                line = line[m.end():].strip()
                continue
            # simple attr with no trailing ';' (ASAP7 writes `area : 0.04374`)
            m = re.match(r'^([A-Za-z_][\w]*)\s*:\s*(\S.*)$', line)
            if m and '{' not in m.group(2):
                stack[-1].attrs.setdefault(m.group(1), []).append(_clean(m.group(2)))
                break
            break   # unparsed remainder (shouldn't happen in these files)
    return root


def attr1(g, key, cast=None):
    v = g.attrs.get(key)
    if not v:
        return None
    v = v[0]
    if cast:
        try:
            return cast(v)
        except ValueError:
            return None
    return v


def table(g):
    """A LUT group (cell_rise / rise_power / ...) -> (idx1, idx2, values[][])."""
    def nums(s):
        return [float(x) for x in re.split(r'[,\s"]+', s.strip()) if x]
    i1 = g.attrs.get('index_1')
    i2 = g.attrs.get('index_2')
    i1 = nums(i1[0]) if i1 else None
    i2 = nums(i2[0]) if i2 else None
    vals = g.attrs.get('values')
    if not vals:
        return i1, i2, None
    # rows are quoted strings separated by commas: "a, b, c", "d, e, f"
    rowstrs = re.findall(r'"([^"]*)"', vals[0])
    rows = [nums(r) for r in rowstrs] if rowstrs else [nums(vals[0])]
    if len(rows) == 1 and i1 and i2 and len(rows[0]) == len(i1) * len(i2):
        rows = [rows[0][k * len(i2):(k + 1) * len(i2)] for k in range(len(i1))]
    return i1, i2, rows


def interp(i1, i2, rows, x1, x2=None):
    """Bilinear (or linear) interpolation, clamped at the table edges."""
    if rows is None:
        return None
    if i1 is None:                       # scalar
        return rows[0][0]
    def lin(xs, x):
        if len(xs) == 1:
            return 0, 0, 0.0
        if x <= xs[0]:
            return 0, 1, 0.0
        if x >= xs[-1]:
            return len(xs) - 2, len(xs) - 1, 1.0
        for k in range(len(xs) - 1):
            if xs[k] <= x <= xs[k + 1]:
                return k, k + 1, (x - xs[k]) / (xs[k + 1] - xs[k])
        return len(xs) - 2, len(xs) - 1, 1.0
    a, b, fa = lin(i1, x1)
    if i2 is None or x2 is None:
        row = rows[0] if len(rows) == 1 else None
        if row is not None and len(row) == len(i1):      # 7x1 laid out as one row
            return row[a] * (1 - fa) + row[b] * fa
        return rows[a][0] * (1 - fa) + rows[b][0] * fa
    c, d, fc = lin(i2, x2)
    v = (rows[a][c] * (1 - fa) * (1 - fc) + rows[b][c] * fa * (1 - fc)
         + rows[a][d] * (1 - fa) * fc + rows[b][d] * fa * fc)
    return v
