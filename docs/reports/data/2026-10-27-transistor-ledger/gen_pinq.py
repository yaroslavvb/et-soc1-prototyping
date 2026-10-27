#!/usr/bin/env python3
"""Q128(d): the charge one DRIVEN GATE PIN takes, measured on the cells this
design actually drives, not on three chosen ones.

For each cell type, for each of its input pins, drive that pin 0 -> VDD through
an ammeter and integrate; hold the other inputs at 0 in one deck and at VDD in
another, because the Miller term depends on whether the output moves.  Divide
by the fins that pin gates (read from the CDL) to get charge per fin.

Runs on aifoundry2, in the directory that holds 7nm_TT_osdi.pm, cells_ng.cdl
and bsimcmg.osdi.

  gen_pinq.py <cdl> <libdir> <cells.txt> <outdir> [vdd ...]
"""
import os
import re
import sys

CELL_RE = re.compile(r'^\s*cell\s*\(\s*"?([^")]+)"?\s*\)')
PIN_RE = re.compile(r'^\s*pin\s*\(\s*"?([^")]+)"?\s*\)')
DIR_RE = re.compile(r'^\s*direction\s*:\s*([a-z]+)\s*;')
CAP_RE = re.compile(r'^\s*capacitance\s*:\s*([-0-9.eE+]+)\s*;')


def read_liberty(libdir):
    out = {}
    for fn in sorted(os.listdir(libdir)):
        if not (fn.startswith("asap7sc7p5t_") and fn.endswith(".lib")):
            continue
        cell = pin = None
        dc = dp = None
        depth = 0
        for line in open(os.path.join(libdir, fn), errors="replace"):
            m = CELL_RE.match(line)
            if m and "{" in line:
                cell, dc = m.group(1), depth
                out.setdefault(cell, {})
            elif cell is not None:
                m = PIN_RE.match(line)
                if m and "{" in line:
                    pin, dp = m.group(1), depth
                    out[cell].setdefault(pin, ["", None])
                elif pin is not None:
                    m = DIR_RE.match(line)
                    if m:
                        out[cell][pin][0] = m.group(1)
                    else:
                        m = CAP_RE.match(line)
                        if m and out[cell][pin][1] is None:
                            out[cell][pin][1] = float(m.group(1))
            depth += line.count("{") - line.count("}")
            if dp is not None and depth <= dp:
                pin, dp = None, None
            if dc is not None and depth <= dc:
                cell, dc = None, None
    return out


def read_cdl(cdl):
    """{cell: (ports, {gate_port: fins}, total_fins)}"""
    out = {}
    cur, ports, byg, tot = None, [], {}, 0
    for line in open(cdl, errors="replace"):
        s = line.strip()
        if s.upper().startswith(".SUBCKT "):
            p = s.split()
            cur, ports, byg, tot = p[1], p[2:], {}, 0
        elif s.upper().startswith(".ENDS"):
            if cur:
                out[cur] = (ports, byg, tot)
            cur = None
        elif cur and (s.startswith("N") or s.startswith("M")):
            p = s.split()
            if len(p) < 6:
                continue
            m = re.search(r'nfin\s*=\s*(\d+)', s)
            k = int(m.group(1)) if m else 1
            tot += k
            if p[2] in ports:
                byg[p[2]] = byg.get(p[2], 0) + k
    return out


def main():
    cdl, libdir, cellsf, outdir = sys.argv[1:5]
    vdds = [float(x) for x in sys.argv[5:]] or [0.517]
    lib = read_liberty(libdir)
    cdls = read_cdl(cdl)
    want = [l.strip() for l in open(cellsf) if l.strip()]
    os.makedirs(outdir, exist_ok=True)
    names, meta = [], {}
    for cell in want:
        if cell not in cdls or cell not in lib:
            print("skip (no cdl or lib):", cell)
            continue
        ports, byg, tot = cdls[cell]
        ins = [p for p in ports if lib[cell].get(p, ["", None])[0] == "input"]
        outs = [p for p in ports if lib[cell].get(p, ["", None])[0] == "output"]
        if not ins or not outs:
            print("skip (no in/out):", cell)
            continue
        for tgt in ins:
            if byg.get(tgt, 0) == 0:
                continue        # the pin gates nothing in the schematic
            for hold, hv in (("lo", "0"), ("hi", "vdd")):
                for vdd in vdds:
                    vn = ("%.3f" % vdd).replace(".", "p")
                    nodes = []
                    for p in ports:
                        if p == tgt:
                            nodes.append("ng")
                        elif p in ins:
                            nodes.append(hv)
                        elif p in outs:
                            nodes.append("o_" + p)
                        elif p.upper() in ("VDD", "VPB", "VPWR"):
                            nodes.append("vd")
                        elif p.upper() in ("VSS", "VNB", "VGND"):
                            nodes.append("vs")
                        else:
                            nodes.append("x_" + p)
                    oload = "".join(f"C{i} o_{p} 0 0.5f\n" for i, p in enumerate(outs))
                    fn = f"pq_{cell}_{tgt}_{hold}_{vn}.sp"
                    open(os.path.join(outdir, fn), "w").write(f"""* Q128(d) pin charge: {cell} pin {tgt}, other inputs {hold}, VDD={vdd} V
.include 7nm_TT_osdi.pm
.include cells_ng.cdl
.temp 25
Vin  nin 0 PULSE(0 {vdd} 1n 5p 5p 2n 4n)
Vinm nin ng 0
Vdd  vdd 0 {vdd}
Vdut vdd vd 0
Vssm vs  0  0
X1 {' '.join(nodes)} {cell}
{oload}Fi 0 nqi Vinm 1
Cqi nqi 0 1
.ic v(nqi)=0
.control
pre_osdi bsimcmg.osdi
tran 0.02p 5n
meas tran qi_lo FIND v(nqi) AT=0.95n
meas tran qi_hi FIND v(nqi) AT=2.95n
meas tran qi_end FIND v(nqi) AT=4.95n
.endc
.end
""")
                    names.append(fn)
                    meta[fn] = {"cell": cell, "pin": tgt, "hold": hold, "vdd": vdd,
                                "fins_gated_by_this_pin": byg[tgt],
                                "fins_in_the_cell": tot,
                                "liberty_pin_fF": lib[cell][tgt][1]}
    import json
    json.dump(meta, open(os.path.join(outdir, "meta.json"), "w"), indent=1, sort_keys=True)
    print(f"{len(names)} decks in {outdir}")


if __name__ == "__main__":
    main()
