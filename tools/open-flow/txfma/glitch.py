#!/usr/bin/env python3
"""Count a VCD's net toggles, validate gsim against Icarus, and price the glitch factor.

    glitch.py vcd   <dump.vcd> --from-ns 1105 --to-ns 2210 --out counts.json
    glitch.py check --gsim zero.json --vcd zero_counts.json
    glitch.py price --zero zero.json --timed timed.json \
                    --netcap net_caps_spef_mixed.txt.gz --muladds 512 --vdd 0.517 \
                    --out glitch.json

`vcd` expands every bus into one entry per bit, named the way the netlist and the SPEF
capacitance table name it (`E1A_FF.Q[33]`), so the three can be joined without guessing.

`check` is the validation gate: with no SDF, gsim's settled count must equal Icarus's own
zero-delay VCD count for every net. Anything else and the timed numbers mean nothing.

`price` reports, for each scope, the glitch factor in toggles (timed transitions / zero-delay
settled transitions) and in energy (the same ratio weighted by each net's capacitance), at
Miller factors 0, 1 and 2.
"""
import argparse
import gzip
import json
import re
import sys
from collections import defaultdict

# The two netlists spell the hierarchy differently - `mixed` keeps only the four multiplier
# boundaries and names their nets `txfmafrac0_top.txfma0_f1.wallace1/_1234_`, while `keep` keeps
# all 182 and names them `txfmafrac0_top/txfma0_f1/wallace1/_1234_` - so both spellings are
# listed and the block test accepts either separator after the prefix.
def _both(path):
    return [path.replace("|", "."), path.replace("|", "/")]


BLOCKS = {
    "ppg": _both("txfmafrac0_top|txfma0_f1|ppg"),
    "wallace1": _both("txfmafrac0_top|txfma0_f1|wallace1"),
    "wallace2": _both("txfmafrac0_top|txfma0_f2|wallace2"),
    "prod_adder_64b": _both("txfmafrac0_top|txfma0_f2|prod_adder_64b"),
}
SCOPES = {
    "wallace_tree": ["wallace1", "wallace2"],
    "multiplier": ["ppg", "wallace1", "wallace2", "prod_adder_64b"],
}


def in_block(name, pref):
    for p in pref:
        if name == p or name.startswith(p + "/") or name.startswith(p + "."):
            return True
    return False


# ---------------------------------------------------------------- VCD

_VAR = re.compile(r"^\$var\s+\S+\s+(\d+)\s+(\S+)\s+(.*?)\s*\$end")
_RANGE = re.compile(r"^\[(\d+)(?::(\d+))?\]$")


def count_vcd(path, t0, t1, strip):
    """{net_or_bit_name: toggles} between t0 and t1 inclusive, 0<->1 transitions only."""
    ids = {}
    scope = []
    last = {}
    tog = defaultdict(int)
    t = 0
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("$scope"):
                scope.append(s.split()[2])
                continue
            if s.startswith("$upscope"):
                if scope:
                    scope.pop()
                continue
            if s.startswith("$var"):
                m = _VAR.match(s)
                if not m:
                    continue
                w, sid, rest = int(m.group(1)), m.group(2), m.group(3)
                parts = rest.split()
                nm = parts[0]
                hi = lo = None
                if len(parts) > 1:
                    r = _RANGE.match(parts[-1])
                    if r:
                        hi = int(r.group(1))
                        lo = int(r.group(2)) if r.group(2) is not None else hi
                nm = nm[1:] if nm.startswith("\\") else nm
                # Only the DUT's OWN nets. $dumpvars(0, tbt) also dumps every cell instance's
                # pins one scope deeper, and a net name here can itself contain '/', so the
                # filter has to be on the scope path, not on the name.
                if strip and "/".join(scope) != strip:
                    continue
                if sid not in ids:
                    ids[sid] = (nm, w, hi, lo)
                continue
            if s.startswith("$enddefinitions"):
                break
    with opener(path, "rt", errors="replace") as fh:
        indefs = True
        for line in fh:
            s = line.strip()
            if indefs:
                if s.startswith("$enddefinitions"):
                    indefs = False
                continue
            if not s:
                continue
            c = s[0]
            if c == "#":
                try:
                    t = int(s[1:])
                except ValueError:
                    pass
                continue
            if c in "bB":
                p = s.split()
                if len(p) < 2:
                    continue
                val, sid = p[0][1:], p[1]
            elif c in "01xzXZ":
                val, sid = c, s[1:]
            else:
                continue
            e = ids.get(sid)
            if e is None:
                continue
            prev = last.get(sid)
            last[sid] = val
            if prev is None or not (t0 <= t <= t1):
                continue
            full, w, hi, lo = e
            if w == 1:
                # a `wire [0:0] x` is one bit but the netlist names it x[0], and the VCD
                # declares it `x [0]`; keep the index so the two tables join
                if hi is not None:
                    full = f"{full}[{hi}]"
                if prev != val and prev in "01" and val in "01":
                    tog[full] += 1
                continue
            pad = prev[0] if prev[0] in "xzXZ" else "0"
            p = prev.rjust(w, pad)[-w:]
            pad = val[0] if val[0] in "xzXZ" else "0"
            v = val.rjust(w, pad)[-w:]
            if hi is None:
                hi, lo = w - 1, 0
            step = -1 if hi >= lo else 1
            for j in range(w):
                if p[j] != v[j] and p[j] in "01" and v[j] in "01":
                    tog[f"{full}[{hi + step * j}]"] += 1
    return dict(tog)


# ---------------------------------------------------------------- pricing

def read_netcap(path):
    out = {}
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            f = line.split()
            if len(f) < 4:
                continue
            out[f[0]] = (float(f[1]), float(f[2]), float(f[3]))
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("vcd")
    v.add_argument("vcd")
    v.add_argument("--from-ns", type=float, default=1105.0)
    v.add_argument("--to-ns", type=float, default=2210.0)
    v.add_argument("--tick-ps", type=float, default=10.0, help="the VCD's own time unit")
    v.add_argument("--strip", default="tbt/dut")
    v.add_argument("--out", required=True)

    c = sub.add_parser("check")
    c.add_argument("--gsim", required=True)
    c.add_argument("--field", default="settled")
    c.add_argument("--vcd", required=True)
    c.add_argument("--out")

    p = sub.add_parser("price")
    p.add_argument("--zero", required=True)
    p.add_argument("--timed", required=True)
    p.add_argument("--zero-field", default="settled")
    p.add_argument("--timed-field", default="transitions")
    p.add_argument("--netcap", required=True)
    p.add_argument("--muladds", type=float, default=512.0)
    p.add_argument("--vdd", type=float, default=0.517)
    p.add_argument("--label", default="")
    p.add_argument("--clock-re", default=r"(^|/)(clock|clk|CLK)(\[|$|/)|clknet|clkbuf",
                   help="nets counted as clock (power.py's own default)")
    p.add_argument("--out", required=True)

    a = ap.parse_args()

    if a.cmd == "vcd":
        t0 = int(round(a.from_ns * 1000.0 / a.tick_ps))
        t1 = int(round(a.to_ns * 1000.0 / a.tick_ps))
        tog = count_vcd(a.vcd, t0, t1, a.strip)
        res = {"vcd": a.vcd, "window_ticks": [t0, t1], "tick_ps": a.tick_ps,
               "nets_with_toggles": len(tog), "total": sum(tog.values()), "toggles": tog}
        with open(a.out, "w") as fh:
            json.dump(res, fh)
        print(json.dumps({k: res[k] for k in ("window_ticks", "nets_with_toggles", "total")},
                         indent=1))
        return

    if a.cmd == "check":
        g = json.load(open(a.gsim))[a.field]
        w = json.load(open(a.vcd))["toggles"]
        # a net declared `wire [0:0] x` is x[0] in the netlist; iverilog may dump it as a
        # plain scalar x. Reconcile that one spelling before comparing.
        renamed = []
        for k in [k for k in g if k.endswith("[0]") and k not in w]:
            if k[:-3] in w:
                g[k[:-3]] = g.pop(k)
                renamed.append(k)
        gk, wk = set(g), set(w)
        only_g = sorted(gk - wk)
        only_v = sorted(wk - gk)
        diff = {k: (g[k], w[k]) for k in (gk & wk) if g[k] != w[k]}
        tg, tv = sum(g.values()), sum(w.values())
        res = {"gsim_total": tg, "vcd_total": tv, "gsim_nets": len(gk), "vcd_nets": len(wk),
               "only_in_gsim": len(only_g), "only_in_vcd": len(only_v),
               "nets_differing": len(diff),
               "scalar_spelling_reconciled": renamed,
               "exact": not only_g and not only_v and not diff,
               "sample_only_gsim": only_g[:20], "sample_only_vcd": only_v[:20],
               "sample_diff": dict(list(diff.items())[:20]),
               "abs_diff_total": sum(abs(x - y) for x, y in diff.values())
                                 + sum(g[k] for k in only_g) + sum(w[k] for k in only_v)}
        if a.out:
            with open(a.out, "w") as fh:
                json.dump(res, fh, indent=1)
        print(json.dumps({k: res[k] for k in res if not k.startswith("sample")}, indent=1))
        if res["sample_diff"]:
            print("sample differences (gsim, vcd):", json.dumps(res["sample_diff"], indent=1))
        if res["sample_only_gsim"]:
            print("only in gsim:", res["sample_only_gsim"])
        if res["sample_only_vcd"]:
            print("only in vcd:", res["sample_only_vcd"])
        return

    # ---- price
    z = json.load(open(a.zero))
    tm = json.load(open(a.timed))
    zc = z[a.zero_field]
    tc = tm[a.timed_field]
    cap = read_netcap(a.netcap)
    half = 0.5 * a.vdd * a.vdd

    def capf(n, k):
        g, co, pin = cap.get(n, (0.0, 0.0, 0.0))
        return g + k * co + pin

    known = set(z.get("all_nets") or ()) | set(zc) | set(tc)
    cap_all = {0: 0.0, 1: 0.0, 2: 0.0}
    cap_known = {0: 0.0, 1: 0.0, 2: 0.0}
    for n, (g, co, pin) in cap.items():
        for k in (0, 1, 2):
            c = g + k * co + pin
            cap_all[k] += c
            if n in known:
                cap_known[k] += c
    allnets = set(zc) | set(tc)
    # the same clock-net test power.py uses, so the two files split the tree the same way
    clk = re.compile(a.clock_re)
    scope_nets = {"unit": allnets,
                  "clock": {n for n in allnets if clk.search(n)},
                  "signal": {n for n in allnets if not clk.search(n)}}
    for b, pref in BLOCKS.items():
        scope_nets[b] = {n for n in allnets if in_block(n, pref)}
    for s, bs in SCOPES.items():
        scope_nets[s] = set().union(*(scope_nets[b] for b in bs))

    out = {"label": a.label, "zero": z.get("sdf"), "timed": tm.get("sdf"),
           "timed_interconnect": tm.get("interconnect"), "timed_cond": tm.get("cond"),
           "muladds": a.muladds, "vdd": a.vdd,
           "netcap_nets": len(cap), "netlist_nets": len(known),
           "coverage": {f"k{k}": {"cap_all_fF": cap_all[k] * 1e15,
                                  "cap_named_by_sim_fF": cap_known[k] * 1e15,
                                  "cap_fraction_priced": (cap_known[k] / cap_all[k])
                                  if cap_all[k] else None} for k in (0, 1, 2)},
           "scopes": {}}
    for s, ns in scope_nets.items():
        zt = sum(zc.get(n, 0) for n in ns)
        tt = sum(tc.get(n, 0) for n in ns)
        row = {"nets": len(ns),
               "nets_priced": sum(1 for n in ns if n in cap),
               "zero_toggles": zt, "timed_toggles": tt,
               "zero_toggles_per_muladd": zt / a.muladds,
               "timed_toggles_per_muladd": tt / a.muladds,
               "glitch_toggle_ratio": (tt / zt) if zt else None,
               "nets_with_glitches": sum(1 for n in ns if tc.get(n, 0) > zc.get(n, 0)),
               "nets_quieter": sum(1 for n in ns if tc.get(n, 0) < zc.get(n, 0))}
        for k in (0, 1, 2):
            ez = sum(zc.get(n, 0) * capf(n, k) for n in ns) * half
            et = sum(tc.get(n, 0) * capf(n, k) for n in ns) * half
            row[f"k{k}"] = {
                "zero_pJ_per_muladd": ez / a.muladds * 1e12,
                "timed_pJ_per_muladd": et / a.muladds * 1e12,
                "glitch_energy_ratio": (et / ez) if ez else None,
                "extra_pJ_per_muladd": (et - ez) / a.muladds * 1e12,
                "cap_priced_fF": sum(capf(n, k) for n in ns) * 1e15}
        out["scopes"][s] = row

    # the biggest glitchers, for the report
    extra = sorted(((tc.get(n, 0) - zc.get(n, 0)) * capf(n, 1), n) for n in allnets)
    out["top_glitch_nets"] = [{"net": n, "zero": zc.get(n, 0), "timed": tc.get(n, 0),
                               "extra_fJ": e * half * 1e15 / a.muladds}
                              for e, n in reversed(extra[-25:])]
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    for s in ("unit", "signal", "clock", "multiplier", "wallace_tree", "ppg",
              "wallace1", "wallace2", "prod_adder_64b"):
        r = out["scopes"][s]
        print(f"{s:16s} toggles/MAC {r['zero_toggles_per_muladd']:9.1f} -> "
              f"{r['timed_toggles_per_muladd']:9.1f}  x{(r['glitch_toggle_ratio'] or 0):.3f}   "
              f"pJ/MAC(k=1) {r['k1']['zero_pJ_per_muladd']:.4f} -> "
              f"{r['k1']['timed_pJ_per_muladd']:.4f}  "
              f"x{(r['k1']['glitch_energy_ratio'] or 0):.3f}")


if __name__ == "__main__":
    main()
