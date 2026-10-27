#!/usr/bin/env python3
"""An event-driven gate-level simulator for the open TensorFMA32, with SDF delays.

    gsim.py --netlist txfma_routed.v --models <stdcell/*.v> \
            --seq-model DFFHQx4_ASAP7_75t_R=dff --seq-model DLLx1_ASAP7_75t_R=latch \
            --vectors randn.vec [--sdf txfma_routed.sdf] --out toggles.json

Why this exists. The glitch question needs a simulator with a delay model that can take an SDF.
Verilator has none; Icarus 14.0 has one but aborts on this SDF (`ERROR: NULL handle passed to
vpi_scan`) for every file containing an `(INTERCONNECT ...)` entry, and annotates nothing at all
unless `$sdf_annotate` is handed the DUT scope explicitly. What is left is to write the engine,
which is small because this whole library is four Verilog primitives (`and`, `or`, `not`, `buf`)
plus one flip-flop and one latch, and the netlist after routing is flat.

How it is kept honest. ONE engine runs both passes; `--sdf` is the only difference between them.
With no SDF every delay is zero and the per-net toggle counts must reproduce Icarus's own
zero-delay VCD **exactly**, net by net (`glitch.py --validate`). Only then is the timed count
worth anything.

Semantics, stated because they are choices:

* **Three-valued** nets (0, 1, X). A toggle is 0->1 or 1->0; X is neither, as in `vcd_toggles.py`.
* **Pin values, not net values, drive the cells.** An SDF `(INTERCONNECT src inst/pin d)` entry is
  a delay on that one load pin, so two loads of one net see it at different times. That skew is a
  large part of what makes a glitch on a routed design, and it is the half Icarus cannot annotate.
* **Module-path delays**, as a `specify` block would: the output is scheduled at
  `t + IOPATH(changed input -> output)`, rise or fall by the direction the output takes. When
  several inputs have just changed, the shortest path wins.
* **Inertial delay** at every scheduled point, load pin and cell output alike: a transition still
  pending when the driving condition reverses is cancelled, so a pulse shorter than the delay it
  would have travelled through is swallowed. For a glitch count that is the conservative choice -
  a transport-delay model reports more.
* **Time is integer femtoseconds**; the SDF's ps values are used as written. (Icarus would round
  every delay to the 10 ps precision of the bench's `timescale`, which smears exactly the path
  imbalances this measures.)
* `(COND ...)` state-dependent IOPATHs are honoured by default; `--no-cond` falls back to the
  unconditional entry, which is what Icarus's `ifnone` would use.

Two counts come out of one run:
  * `settled` - every net's value at the end of each 1 ns vector step against the step before.
    That is what a zero-delay VCD records, and it is the glitch-free denominator.
  * `transitions` - every physical edge, whenever it happens. The numerator.
"""
import argparse
import heapq
import json
import os
import re
import sys
from collections import defaultdict

X = 2
OP_AND, OP_OR, OP_NOT, OP_BUF = 0, 1, 2, 3
_PRIM = {"and": OP_AND, "or": OP_OR, "not": OP_NOT, "buf": OP_BUF}


class CellType:
    __slots__ = ("name", "ins", "out", "nloc", "ops", "kind", "oslot", "islots", "scratch",
                 "dpos", "cpos")


def parse_models(paths, seq_kinds):
    """{cellname: CellType} from ASAP7's own Verilog models (gate primitives only)."""
    src = []
    for p in paths:
        with open(p, errors="replace") as fh:
            src.append(fh.read())
    src = "\n".join(src)
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    src = re.sub(r"\bspecify\b.*?\bendspecify\b", "", src, flags=re.S)
    out = {}
    for m in re.finditer(r"\bmodule\s+(\w+)\s*\(.*?\);(.*?)\bendmodule", src, re.S):
        name, body = m.group(1), m.group(2)
        ct = CellType()
        ct.name, ct.ins, ct.out, ct.ops, ct.kind = name, [], None, [], "comb"
        loc = {}

        def slot(nm):
            if nm not in loc:
                loc[nm] = len(loc)
            return loc[nm]

        for d in re.finditer(r"\b(input|output|wire|reg)\b([^;]*);", body):
            kind = d.group(1)
            for nm in re.findall(r"[A-Za-z_]\w*", d.group(2)):
                slot(nm)
                if kind == "input" and nm not in ct.ins:
                    ct.ins.append(nm)
                elif kind == "output":
                    ct.out = nm
        for p in re.finditer(r"\b(and|or|not|buf)\s*\(([^)]*)\)\s*;", body):
            args = [x.strip() for x in p.group(2).split(",")]
            ins = []
            for x in args[1:]:
                if x in ("1'b1", "1"):
                    ins.append((1, 1))
                elif x in ("1'b0", "0"):
                    ins.append((1, 0))
                else:
                    ins.append((0, slot(x)))
            ct.ops.append((_PRIM[p.group(1)], slot(args[0]), tuple(ins)))
        ct.nloc = len(loc)
        ct.dpos = ct.cpos = -1
        if name in seq_kinds:
            ct.kind = seq_kinds[name]
            ct.ops = []
            if ct.out is None or "D" not in ct.ins or "CLK" not in ct.ins:
                continue
            ct.oslot = -1
            ct.dpos, ct.cpos = ct.ins.index("D"), ct.ins.index("CLK")
        else:
            if not ct.ops or ct.out is None or ct.out not in loc:
                continue
            ct.oslot = loc[ct.out]
            _order(ct)
        # the local slot of each input, in pin order: slots follow the model's declaration
        # order, which puts `output Y` first, so input k is NOT slot k.
        ct.islots = tuple(loc[nm] for nm in ct.ins)
        ct.scratch = [X] * ct.nloc
        out[name] = ct
    return out


def _order(ct):
    """Topologically order a cell's primitives so one left-to-right pass evaluates it."""
    producer = {o: k for k, (_, o, _) in enumerate(ct.ops)}
    done, order, pending = set(), [], list(range(len(ct.ops)))
    while pending:
        nxt = []
        for k in pending:
            _, _, ins = ct.ops[k]
            if all(c or v not in producer or producer[v] in done for c, v in ins):
                order.append(k)
                done.add(k)
            else:
                nxt.append(k)
        if len(nxt) == len(pending):
            raise SystemExit(f"cell {ct.name}: primitives do not order (combinational loop?)")
        pending = nxt
    ct.ops = [ct.ops[k] for k in order]


def eval_cell(ops, loc):
    for op, o, ins in ops:
        if op == OP_AND:
            r = 1
            for c, v in ins:
                a = v if c else loc[v]
                if a == 0:
                    r = 0
                    break
                if a == X:
                    r = X
            loc[o] = r
        elif op == OP_OR:
            r = 0
            for c, v in ins:
                a = v if c else loc[v]
                if a == 1:
                    r = 1
                    break
                if a == X:
                    r = X
            loc[o] = r
        elif op == OP_NOT:
            c, v = ins[0]
            a = v if c else loc[v]
            loc[o] = X if a == X else 1 - a
        else:
            c, v = ins[0]
            loc[o] = v if c else loc[v]


# ---------------------------------------------------------------- netlist

_DECL = re.compile(r"^\s*(input|output|wire)\s*(?:\[\s*(\d+)\s*:\s*(\d+)\s*\])?\s*"
                   r"(\\\S+|[A-Za-z_][\w$]*)\s*$")
_INST = re.compile(r"^\s*([A-Za-z][\w$]*)\s+(\\\S+|[A-Za-z_][\w$]*)\s*\((.*)\)\s*$", re.S)
_CONN = re.compile(r"\.\s*(\w+)\s*\(\s*([^()]*?)\s*\)")
_REF = re.compile(r"^(\\\S+|[A-Za-z_][\w$]*)\s*(?:\[\s*(\d+)\s*\])?$")


def parse_netlist(path):
    with open(path, errors="replace") as fh:
        src = fh.read()
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    body = src[src.index(");") + 2:src.rindex("endmodule")]
    nets, nidx, dirs, insts = [], {}, {}, []

    def add(nm):
        i = nidx.get(nm)
        if i is None:
            i = nidx[nm] = len(nets)
            nets.append(nm)
        return i

    for stmt in body.split(";"):
        if not stmt.strip():
            continue
        d = _DECL.match(stmt)
        if d:
            kind, hi, lo, nm = d.group(1), d.group(2), d.group(3), d.group(4)
            nm = nm[1:] if nm.startswith("\\") else nm
            if hi is None:
                add(nm)
                if kind != "wire":
                    dirs[nm] = kind
            else:
                for b in range(min(int(hi), int(lo)), max(int(hi), int(lo)) + 1):
                    add(f"{nm}[{b}]")
                if kind != "wire":
                    dirs[nm] = kind
            continue
        i = _INST.match(stmt)
        if not i:
            raise SystemExit(f"unparsed statement: {stmt.strip()[:140]!r}")
        iname = i.group(2)
        pins = []
        for c in _CONN.finditer(i.group(3)):
            r = _REF.match(c.group(2).strip())
            if not r:
                raise SystemExit(f"cannot parse net reference {c.group(2)!r} in {iname}")
            nm = r.group(1)
            nm = nm[1:] if nm.startswith("\\") else nm
            if r.group(2) is not None:
                nm = f"{nm}[{r.group(2)}]"
            pins.append((c.group(1), add(nm)))
        insts.append((i.group(1), iname[1:] if iname.startswith("\\") else iname, pins))
    return nets, nidx, dirs, insts


# ---------------------------------------------------------------- SDF

def _typ(s):
    """typ field of a (min:typ:max) triple, in fs; an empty field falls back to a neighbour."""
    p = s.split(":")
    for k in (1, 0, 2):
        if k < len(p) and p[k].strip():
            return int(round(float(p[k]) * 1000.0))
    return 0


def _unesc(s):
    """OpenSTA escapes '.' and '/' inside a name with a backslash: strip those."""
    return s.replace("\\", "")


def _split_pin(tok):
    """'inst/pin' split on the last UNESCAPED '/'.

    The flat routed netlist has instance names that themselves contain '/' and '.' - the kept
    multiplier blocks' cells are `txfmafrac0_top.txfma0_f1.wallace1/_1234_` - and the SDF writes
    them escaped. Splitting on the last '/' without honouring the escapes silently loses the
    delay of every cell in the multiplier, which is the part this measurement is about.
    """
    k, last = 0, None
    while k < len(tok):
        if tok[k] == "\\":
            k += 2
            continue
        if tok[k] == "/":
            last = k
        k += 1
    if last is None:
        return "", _unesc(tok)
    return _unesc(tok[:last]), _unesc(tok[last + 1:])


_INSTANCE = re.compile(r"^\(INSTANCE\s*([^)\s]*)\s*\)$")
_IOPATH = re.compile(r"\(IOPATH\s+(?:\((?:posedge|negedge)\s+)?([\w\[\]]+)\)?\s+"
                     r"(\([\w]+[+-]:[\w]+\)|[\w\[\]]+)\s*\(([^)]*)\)\s*\(([^)]*)\)")
_IC = re.compile(r"\(INTERCONNECT\s+(\S+)\s+(\S+)\s+\(([^)]*)\)(?:\s*\(([^)]*)\))?")
_COND = re.compile(r"^\(COND\s+\(?(.*?)\)?$")


def parse_sdf(path):
    iopath = defaultdict(dict)
    cond = defaultdict(list)
    ic = {}
    inst, pend = None, None
    with open(path, errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            if s.startswith("(CELL"):
                inst, pend = None, None
                continue
            m = _INSTANCE.match(s)
            if m:
                inst = _unesc(m.group(1))
                continue
            if s.startswith("(COND"):
                c = _COND.match(s)
                pend = c.group(1).strip() if c else None
                continue
            if "(IOPATH" in s:
                m = _IOPATH.search(s)
                if m:
                    ip, op = m.group(1), m.group(2)
                    om = re.match(r"\((\w+)[+-]:(\w+)\)", op)
                    if om:
                        op = om.group(1)
                    d = (_typ(m.group(3)), _typ(m.group(4)))
                    if pend:
                        terms, bad = [], False
                        for t in pend.split("&"):
                            t = t.strip()
                            neg = t[:1] in "~!"
                            nm = t.lstrip("~!").strip()
                            if not re.match(r"^\w+$", nm):
                                bad = True
                                break
                            terms.append((nm, 0 if neg else 1))
                        if not bad and terms:
                            cond[inst].append((ip, op, tuple(terms), d))
                    else:
                        iopath[inst][(ip, op)] = d
                pend = None
                continue
            if "(INTERCONNECT" in s:
                m = _IC.search(s)
                if m:
                    d1 = _typ(m.group(3))
                    d2 = _typ(m.group(4)) if m.group(4) else d1
                    # keyed on the DESTINATION pin alone: a load pin has one driver, and the
                    # source is spelled as a driver pin for a cell and as a net for a port.
                    ic[_split_pin(m.group(2))] = (d1, d2)
                continue
    return iopath, cond, ic


# ---------------------------------------------------------------- the machine

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--netlist", required=True)
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--seq-model", action="append", default=[], help="CELL=dff|latch")
    ap.add_argument("--vectors", required=True)
    ap.add_argument("--sdf")
    ap.add_argument("--cond", dest="cond", action="store_true", default=True)
    ap.add_argument("--no-cond", dest="cond", action="store_false")
    ap.add_argument("--no-interconnect", action="store_true",
                    help="drop the SDF's INTERCONNECT delays (what Icarus is limited to)")
    ap.add_argument("--step-ps", type=float, default=1000.0)
    ap.add_argument("--from-ns", type=float, default=1105.0)
    ap.add_argument("--to-ns", type=float, default=2210.0)
    ap.add_argument("--max-events", type=int, default=800_000_000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    seq = dict(s.split("=") for s in a.seq_model)
    models = parse_models(a.models, seq)
    nets, nidx, dirs, insts = parse_netlist(a.netlist)
    nn, ncell = len(nets), len(insts)
    print(f"netlist: {nn} nets, {ncell} instances, {len(models)} cell models", file=sys.stderr)

    cell_ct = [None] * ncell
    cell_out = [-1] * ncell
    cell_pins = [None] * ncell
    cell_kind = bytearray(ncell)            # 0 comb, 1 dff, 2 latch
    pin_cell, pin_pos, pin_net, pin_inst = [], [], [], []
    dangling, sourceless = [], []
    DANGLE = "\x00dangling/"

    def add_net(nm):
        i = nidx.get(nm)
        if i is None:
            i = nidx[nm] = len(nets)
            nets.append(nm)
        return i

    for ci, (ctype, iname, pins) in enumerate(insts):
        ct = models.get(ctype)
        if ct is None:
            raise SystemExit(f"no usable model for cell type {ctype}")
        cell_ct[ci] = ct
        cell_kind[ci] = {"comb": 0, "dff": 1, "latch": 2}[ct.kind]
        byname = dict(pins)
        if ct.out not in byname:
            # CTS's `clkload*` dummies connect A only: their output drives nothing, so give it
            # a net of its own, marked so it is left out of the toggle tables.
            byname[ct.out] = add_net(f"{DANGLE}{iname}/{ct.out}")
            dangling.append(ci)
        cell_out[ci] = byname[ct.out]
        pl = []
        for k, ip in enumerate(ct.ins):
            pl.append(len(pin_net))
            pin_net.append(byname[ip])
            pin_cell.append(ci)
            pin_pos.append(k)
            pin_inst.append(iname)
        cell_pins[ci] = pl
        if not pl:
            sourceless.append(ci)           # TIEHIx1 / TIELOx1: a constant, no input pin
    nn = len(nets)
    npin = len(pin_net)
    loads = [[] for _ in range(nn)]
    for p in range(npin):
        loads[pin_net[p]].append(p)
    loads = [tuple(v) for v in loads]

    pin_ic = [(0, 0)] * npin
    cell_dly = [None] * ncell
    cell_cond = [None] * ncell
    bind = {"iopath": 0, "iopath_missing": 0, "interconnect": 0,
            "interconnect_missing": 0, "cond_paths": 0}
    if a.sdf:
        iopath, cond, ic = parse_sdf(a.sdf)
        print(f"sdf: {len(iopath)} cells with IOPATH, {len(ic)} interconnect entries",
              file=sys.stderr)
        bind["iopath_from_cond"] = 0
        for ci, (ctype, iname, pins) in enumerate(insts):
            ct = cell_ct[ci]
            tab = iopath.get(iname, {})
            cnd = cond.get(iname, ())
            d = []
            for ip in ct.ins:
                v = tab.get((ip, ct.out)) or tab.get((ip, "Q")) or tab.get((ip, "Y"))
                if v is None:
                    # XOR2x2 and XNOR2x2 carry no `ifnone` path, so OpenSTA writes their
                    # delays only inside (COND ...). Default such a pin to the shortest of
                    # its conditional entries, the same rule the path picker uses.
                    cands = [dd for cip, _, _, dd in cnd if cip == ip]
                    if cands:
                        v = (min(x[0] for x in cands), min(x[1] for x in cands))
                        bind["iopath_from_cond"] += 1
                if v is None:
                    d.append((0, 0))
                    bind["iopath_missing"] += 1
                else:
                    d.append(v)
                    bind["iopath"] += 1
            cell_dly[ci] = tuple(d)
            if a.cond and cnd:
                cl = []
                for ip, op, terms, dd in cnd:
                    if ip not in ct.ins or any(nm not in ct.ins for nm, _ in terms):
                        continue
                    cl.append((ct.ins.index(ip),
                               tuple((ct.ins.index(nm), v) for nm, v in terms), dd))
                if cl:
                    cell_cond[ci] = tuple(cl)
                    bind["cond_paths"] += len(cl)
        if not a.no_interconnect:
            for p in range(npin):
                ct = cell_ct[pin_cell[p]]
                v = ic.get((pin_inst[p], ct.ins[pin_pos[p]]))
                if v is None:
                    bind["interconnect_missing"] += 1
                else:
                    pin_ic[p] = v
                    bind["interconnect"] += 1
        print("sdf bind: " + json.dumps(bind), file=sys.stderr)
    else:
        for ci in range(ncell):
            cell_dly[ci] = tuple((0, 0) for _ in cell_ct[ci].ins)

    # --- stimulus: the bench drives dut.clock from clk_g, and ties trans_coefficients to 0
    pi_clock, pi_reset, pi_valid = nidx["clock"], nidx["reset"], nidx["in_valid"]
    in_data = [nidx[f"in_data[{b}]"] for b in range(167)]
    trans = [nidx[f"trans_coefficients[{b}]"] for b in range(58)]
    vec = []
    with open(a.vectors) as fh:
        for line in fh:
            f = line.split()
            if len(f) == 5:
                vec.append((int(f[1]), int(f[2]), int(f[3]), int(f[4], 16)))
    print(f"vectors: {len(vec)} steps", file=sys.stderr)

    netv = bytearray([X]) * nn
    pinv = bytearray([X]) * npin
    out_tgt = bytearray([X]) * ncell
    pin_tgt = bytearray([X]) * npin
    live_out = [0] * ncell
    live_pin = [0] * npin
    trans_cnt = [0] * nn
    settle_cnt = [0] * nn
    snap = bytearray([X]) * nn
    touched = []

    future = []
    delta = []
    nba_q = []
    push, pop = heapq.heappush, heapq.heappop
    state = {"stamp": 0, "nev": 0}
    lo, hi = int(a.from_ns * 1e6), int(a.to_ns * 1e6)

    def drive(ni, val, now):
        if netv[ni] == val:
            return
        old = netv[ni]
        if old != X and val != X and lo <= now <= hi:
            trans_cnt[ni] += 1
        netv[ni] = val
        touched.append(ni)
        st = state["stamp"]
        for p in loads[ni]:
            if pin_tgt[p] == val:
                continue
            pin_tgt[p] = val
            if pinv[p] == val:
                live_pin[p] = 0
                continue
            st += 1
            live_pin[p] = st
            d = pin_ic[p][0 if val == 1 else 1]
            if d:
                push(future, (now + d, st, 1, p))
            else:
                delta.append((st, 1, p))
        state["stamp"] = st

    def sched_out(ci, nv, now, dly, nba=False):
        out_tgt[ci] = nv
        if netv[cell_out[ci]] == nv:
            live_out[ci] = 0
            return
        st = state["stamp"] = state["stamp"] + 1
        live_out[ci] = st
        if dly:
            push(future, (now + dly, st, 0, ci))
        elif nba:
            # A flip-flop with no CLK->Q delay is Verilog's `Q <= D`: it samples now and
            # applies after every other event at this instant, so two flip-flops in series
            # cannot race through a zero-delay clock tree of unequal depth.
            nba_q.append((st, 0, ci))
        else:
            delta.append((st, 0, ci))

    def path_delay(ci, nv):
        """Shortest IOPATH from an input that has just arrived, honouring (COND ...)."""
        pl = cell_pins[ci]
        dl = cell_dly[ci]
        cc = cell_cond[ci]
        k0 = 0 if nv == 1 else 1
        best = None
        for k, p in enumerate(pl):
            if pinv[p] != pin_tgt[p]:
                continue
            d = dl[k][k0]
            if cc:
                for cpos, terms, cdd in cc:
                    if cpos == k and all(pinv[pl[q]] == v for q, v in terms):
                        d = cdd[k0]
                        break
            if best is None or d < best:
                best = d
        return 0 if best is None else best

    def on_pin(p, now):
        pinv[p] = pin_tgt[p]
        ci = pin_cell[p]
        k = cell_kind[ci]
        pl = cell_pins[ci]
        ct = cell_ct[ci]
        if k == 0:
            loc = ct.scratch
            isl = ct.islots
            for j, q in enumerate(pl):
                loc[isl[j]] = pinv[q]
            eval_cell(ct.ops, loc)
            nv = loc[ct.oslot]
            if out_tgt[ci] == nv:
                return
            sched_out(ci, nv, now, path_delay(ci, nv))
            return
        if k == 1:                                   # rising-edge flip-flop
            if pin_pos[p] != ct.cpos or pinv[p] != 1:
                return
            nv = pinv[pl[ct.dpos]]
        else:                                        # latch, transparent while CLK is low
            nv = pinv[pl[ct.dpos]] if pinv[pl[ct.cpos]] == 0 else out_tgt[ci]
        if out_tgt[ci] == nv:
            return
        sched_out(ci, nv, now, cell_dly[ci][pin_pos[p]][0 if nv == 1 else 1], k == 1)

    def run_delta(now):
        while True:
            i = 0
            while i < len(delta):
                st, kind, idx = delta[i]
                i += 1
                state["nev"] += 1
                if kind:
                    if live_pin[idx] == st:
                        live_pin[idx] = 0
                        on_pin(idx, now)
                else:
                    if live_out[idx] == st:
                        live_out[idx] = 0
                        drive(cell_out[idx], out_tgt[idx], now)
            del delta[:]
            if not nba_q:
                return
            delta.extend(nba_q)
            del nba_q[:]

    def advance(tgt, now0):
        run_delta(now0)
        while future and future[0][0] <= tgt:
            now = future[0][0]
            while future and future[0][0] == now:
                _, st, kind, idx = pop(future)
                state["nev"] += 1
                if kind:
                    if live_pin[idx] == st:
                        live_pin[idx] = 0
                        on_pin(idx, now)
                else:
                    if live_out[idx] == st:
                        live_out[idx] = 0
                        drive(cell_out[idx], out_tgt[idx], now)
            run_delta(now)
            if state["nev"] > a.max_events:
                raise SystemExit("event budget exhausted")

    # t = 0: the bench's initial register values, the flip-flops' initial 0, the tie cells
    for ci in range(ncell):
        if cell_kind[ci]:
            out_tgt[ci] = 0
            drive(cell_out[ci], 0, 0)
    for ci in sourceless:
        ct = cell_ct[ci]
        loc = ct.scratch
        eval_cell(ct.ops, loc)
        out_tgt[ci] = loc[ct.oslot]
        drive(cell_out[ci], loc[ct.oslot], 0)
    drive(pi_clock, 0, 0)
    drive(pi_reset, 1, 0)
    drive(pi_valid, 0, 0)
    for b in in_data:
        drive(b, 0, 0)
    for b in trans:
        drive(b, 0, 0)
    advance(0, 0)
    snap[:] = netv
    del touched[:]

    step = int(a.step_ps * 1000.0)
    t = 0
    for k, (cg, r, v, d) in enumerate(vec, start=1):
        t = k * step
        advance(t - 1, t - 1)
        drive(pi_clock, cg, t)
        drive(pi_reset, r, t)
        drive(pi_valid, v, t)
        for b in range(167):
            drive(in_data[b], (d >> b) & 1, t)
        advance(t, t)
        if lo <= t <= hi:
            for ni in set(touched):
                o, w = snap[ni], netv[ni]
                if o != w:
                    if o != X and w != X:
                        settle_cnt[ni] += 1
                    snap[ni] = w
        else:
            for ni in set(touched):
                snap[ni] = netv[ni]
        del touched[:]
        if k % 500 == 0:
            print(f"  step {k}/{len(vec)}  events {state['nev']:,}", file=sys.stderr, flush=True)
    advance(t + 2 * step, t)

    res = {"netlist": os.path.basename(a.netlist),
           "sdf": os.path.basename(a.sdf) if a.sdf else None,
           "cond": bool(a.sdf) and a.cond,
           "interconnect": bool(a.sdf) and not a.no_interconnect,
           "nets": nn, "instances": ncell, "pins": npin, "events": state["nev"],
           "dangling_outputs": len(dangling), "tie_cells": len(sourceless),
           "window_ns": [a.from_ns, a.to_ns],
           "total_transitions": sum(trans_cnt[i] for i in range(nn)
                                    if not nets[i].startswith(DANGLE)),
           "total_settled": sum(settle_cnt[i] for i in range(nn)
                                if not nets[i].startswith(DANGLE)),
           "transitions_dangling": sum(trans_cnt[i] for i in range(nn)
                                       if nets[i].startswith(DANGLE)),
           "sdf_bind": bind if a.sdf else None,
           "all_nets": [nets[i] for i in range(nn) if not nets[i].startswith(DANGLE)],
           "transitions": {nets[i]: trans_cnt[i] for i in range(nn)
                           if trans_cnt[i] and not nets[i].startswith(DANGLE)},
           "settled": {nets[i]: settle_cnt[i] for i in range(nn)
                       if settle_cnt[i] and not nets[i].startswith(DANGLE)}}
    with open(a.out, "w") as fh:
        json.dump(res, fh)
    print(json.dumps({k: res[k] for k in ("nets", "instances", "pins", "events",
                                          "total_transitions", "total_settled", "sdf_bind")},
                     indent=1))


if __name__ == "__main__":
    main()
