#!/usr/bin/env python3
"""reg-e224 probe (desk, no forecast frozen, nothing scored): which (format, data kind) MM1-v3.2 prices in energy (a committed switch count and
a phi), by its own tables (energy_v31's merged tables plus counts-e214), at KB = 1 (fp32 S1) and KB >= 2 (fp32 S2); and the E212 and E217 tile
kinds. Reads only the landed model code at the scratch clone's HEAD. /usr/bin/python3 -I -B, single-threaded."""
import json
import os
import sys

LAB = sys.argv[1]
V32 = os.path.join(LAB, "tools", "matmul", "mm1", "v3.2")
sys.path.insert(0, V32)
import mm1_v32  # noqa: E402
import energy_v32 as EV2  # noqa: E402
EV = EV2.EV
P = json.load(open(os.path.join(V32, "out", "mm1_v32_params.json")))
M = mm1_v32.Model(P)
out = {"fp32_S1": sorted(EV.E210C31["S1"].keys()), "fp32_S2": sorted(EV.E210C31["S2"].keys()),
       "swt": sorted(EV.SWT31.keys())}
e212 = {}
for fmt in ("fp32", "fp16", "int8"):
    d = os.path.join(LAB, "tools", "matmul", "mm1", "v3.1", "inputs", "e212tiles", fmt)
    e212[fmt] = sorted(f[:-4] for f in os.listdir(d)) if os.path.isdir(d) else []
out["e212tiles"] = e212
# MM1-v3.2's energy verdict per (fmt, kind) at a small full-mask shape, KB 1 and KB 4
probe = []
kinds = {"fp32": ["random", "zeros", "ones"] + ["pattern:" + k for k in e212["fp32"]],
         "fp16": ["random", "zeros", "ones"] + ["pattern:" + k for k in e212["fp16"]],
         "int8": ["random", "zeros", "ones"] + ["pattern:" + k for k in e212["int8"]]}
specs = []
for fmt, ks in kinds.items():
    for k in ks:
        for arm in ("gemmL1x1x1", "gemmL2x2x4"):
            specs.append({"card": "aifoundry1 card 1", "arm": arm, "fmt": fmt, "kind": k, "mask": "0xffffffff", "f": 600.0, "kernel": "rgm136"})
res = M.predict_many(specs)
for s, r in zip(specs, res):
    probe.append({"fmt": s["fmt"], "kind": s["kind"], "arm": s["arm"], "W_over_idle": r.get("W_over_idle"),
                  "energy": (None if "W_over_idle" in r else r.get("energy")),
                  "phi": r.get("phi"), "switches_keys": sorted((r.get("switches") or {}).keys())[:6]})
out["probe"] = probe
json.dump(out, open(sys.argv[2], "w"), indent=1)
for q in probe:
    print(q["fmt"], q["kind"], q["arm"], "W" if q["W_over_idle"] is not None else "NOT FORECAST",
          None if q["W_over_idle"] is None else round(q["W_over_idle"], 3))
print("fp32 S1 keys", len(out["fp32_S1"]), "S2 keys", len(out["fp32_S2"]), "swt", len(out["swt"]))
print("e212tiles", {k: len(v) for k, v in e212.items()})
