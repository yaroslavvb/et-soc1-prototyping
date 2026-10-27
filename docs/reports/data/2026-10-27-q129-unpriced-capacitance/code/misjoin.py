#!/usr/bin/env python3
"""Why the published join and the post-CTS re-simulation disagree on the nets they BOTH name.

Q129, corrected 27 Oct 2026. The first version of this directory called that residual
(-0.0077 pJ per multiply-add at `randn`) "the scatter between two simulations of logically
identical netlists". It is not scatter: it is a SECOND error in the published join, on the very
vectors whose high bits the join was already missing.

Verilator renumbers a vector whose declared LSB is not 0 from 0 in its SAIF. A wire declared
`[63:12]` is `bus[12]..bus[63]` to the extractor and `bus[0]..bus[51]` to the SAIF, so

  * `bus[52]..bus[63]`  have no SAIF name at all  -> never priced (the `bitshift` row of the
                                                     decomposition: 598 nets, 1,875.9 fF)
  * `bus[12]..bus[51]`  exist in BOTH namespaces and denote DIFFERENT physical bits -> power.py
                        matched them by name and charged each wire the activity of the bit
                        `lsb` places up.

The test is that the shift PREDICTS the published value: for a disagreeing net `bus[i]` the
pre-route SAIF's count equals the post-CTS count of `bus[i+lsb]`. This script classifies every
disagreeing net that way, per pattern, and dumps the per-net evidence for `randn`.

Layout: run it from the working tree the rest of this directory's code ran in, i.e. with
`in/net_cap_keep.txt`, `in/txfma_syn_keep.v` and `in/red/{syn,pnr}_<pattern>.json.gz` beside it
(`code/saif_reduce.py` makes the reductions). Pass that root as argv[1]; it defaults to the
script's own directory.

  python3 code/misjoin.py [<root>] [<outdir>]

Writes `<outdir>/misjoin_per_pattern.json` and `<outdir>/misjoin_randn-nets.json`.
"""
import collections
import gzip
import json
import os
import re
import sys

ROOT = (sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))) + "/"
OUT = (sys.argv[2] if len(sys.argv) > 2 else ROOT + "res") + "/"
VDD = 0.517
V2 = VDD * VDD
MA = 512.0
PATTERNS = ["randn", "zeros", "ones",
            "lb_h0", "lb_h1", "lb_h2", "lb_h4", "lb_h8",
            "lq_h0", "lq_h1", "lq_h2", "lq_h4", "lq_h8"]
BASE = re.compile(r"^(.*)\[(\d+)\]$")
# `wire [63:12] \name ;` in the pre-route hierarchical netlist, which is where a vector's
# declared LSB survives (the flat post-CTS netlist has already renamed everything).
DECL = re.compile(r"^\s*(?:wire|reg|input|output|inout)\s*\[\s*(\d+)\s*:\s*(\d+)\s*\]\s*"
                  r"\\?([A-Za-z_][A-Za-z0-9_$\\]*)\s*[;,]", re.M)

cap = {}
for line in open(ROOT + "in/net_cap_keep.txt"):
    if line.startswith("#"):
        continue
    p = line.split()
    if len(p) >= 3:
        cap[p[0]] = (float(p[1]) + float(p[2])) * 1e15      # F -> fF

decl = {}
for msb, lsb, name in DECL.findall(open(ROOT + "in/txfma_syn_keep.v", errors="replace").read()):
    decl.setdefault(name.replace("\\", ""), (int(msb), int(lsb)))


def declared_lsb(net):
    """(match, declared LSB) of the vector this extracted net is a bit of."""
    m = BASE.match(net)
    if not m:
        return None, 0
    v = decl.get(m.group(1).split("/")[-1])
    return m, (v[1] if v else 0)


def load(path):
    d = json.load(gzip.open(path))
    return ({k.replace("\\", ""): v for k, v in d["toggles"].items()},
            set(n.replace("\\", "") for n in d.get("names_measured", [])))


def energy(net, dtog):
    """pJ per multiply-add of a toggle-count difference on this net."""
    return 0.5 * cap[net] * 1e-15 * V2 * dtog * 1e12 / MA


per_pattern = {}
rows_randn = []
for pat in PATTERNS:
    syn, _ = load(ROOT + f"in/red/syn_{pat}.json.gz")
    pnr, pnr_names = load(ROOT + f"in/red/pnr_{pat}.json.gz")
    agg = collections.defaultdict(float)
    cnt = collections.Counter()
    for net in cap:
        if net not in syn:
            continue                                  # not a net the published join matched
        d = pnr.get(net, 0) - syn[net]
        if d == 0:
            continue
        e = energy(net, d)
        m, lsb = declared_lsb(net)
        shifted = f"{m.group(1)}[{int(m.group(2)) + lsb}]" if (m and lsb) else None
        if shifted and shifted in pnr and abs(syn[net] - pnr[shifted]) < 1e-9:
            kind = "misjoin_shift_predicted_exactly"
        elif lsb:
            kind = "misjoin_same_vector_not_exact"
        elif net not in pnr_names:
            kind = "net_the_post_cts_sim_does_not_name"
        else:
            kind = "unexplained"
        cnt[kind] += 1
        agg[kind] += e
        if pat == "randn":
            rows_randn.append({
                "net": net, "cap_fF": cap[net], "declared_lsb": lsb,
                "published_join_toggles": syn[net], "post_cts_toggles": pnr.get(net, 0),
                "shift_predicted_net": shifted,
                "shift_predicted_toggles": pnr.get(shifted) if shifted else None,
                "pJ_per_muladd": e, "kind": kind,
            })
    tot = sum(agg.values())
    mis = agg["misjoin_shift_predicted_exactly"] + agg["misjoin_same_vector_not_exact"]
    per_pattern[pat] = {
        "nets_disagreeing": sum(cnt.values()),
        "residual_pJ_per_muladd": tot,
        "misjoin_pJ_per_muladd": mis,
        "misjoin_share_of_the_residual": (mis / tot) if tot else 0.0,
        "net_the_post_cts_sim_does_not_name_pJ_per_muladd":
            agg["net_the_post_cts_sim_does_not_name"],
        "unexplained_pJ_per_muladd": agg["unexplained"],
        "nets": dict(cnt),
    }
    print(f"{pat:8s} residual {tot:+.7f} pJ  mis-join {mis:+.7f} "
          f"({(mis / tot * 100) if tot else 0:6.2f}%)  "
          f"dropped {agg['net_the_post_cts_sim_does_not_name']:+.7f}  "
          f"unexplained {agg['unexplained']:+.7f}  nets {sum(cnt.values())}")

bases = collections.Counter(BASE.match(r["net"]).group(1) for r in rows_randn
                            if r["declared_lsb"] and BASE.match(r["net"]))
out = {
    "question": "Q129",
    "date": "2026-10-27",
    "what": "the residual between the published join (pre-route SAIF) and the direct post-CTS "
            "simulation, on the nets they both name, decomposed. It is the published join "
            "pricing the wrong physical bit on vectors whose declared LSB is not 0, not "
            "inter-simulation scatter.",
    "mechanism": "Verilator renumbers a vector declared [msb:lsb] from 0 in its SAIF. The "
                 "extractor's bus[i] for lsb <= i <= msb-lsb exists in both namespaces and means "
                 "a different physical bit in each, so power.py's name join charges that wire the "
                 "activity of bus[i+lsb]. The test: the pre-route value of bus[i] equals the "
                 "post-CTS value of bus[i+lsb].",
    "vector_bases_affected": dict(sorted(bases.items())),
    "per_pattern": per_pattern,
}
os.makedirs(OUT, exist_ok=True)
json.dump(out, open(OUT + "misjoin_per_pattern.json", "w"), indent=1)
rows_randn.sort(key=lambda r: -abs(r["pJ_per_muladd"]))
json.dump(rows_randn, open(OUT + "misjoin_randn-nets.json", "w"), indent=1)
print(f"\nwrote {OUT}misjoin_per_pattern.json and {OUT}misjoin_randn-nets.json "
      f"({len(rows_randn)} nets, {len(bases)} renumbered vector bases)")
