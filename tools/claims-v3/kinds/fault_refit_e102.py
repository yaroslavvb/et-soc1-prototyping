#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""POST HOC, exploratory, no rule of E102's depends on it. E92's post-hoc fit (posthoc_fit_e92.py, whose "four prices + flops" per type is E103-R3's null) refitted on the same tiles and the same D, with one thing changed: where its C read, result bus,
store and adder-flop counts start from. Run from the repo's root, once per start:

    fault_refit_e102.py fl   <e92 reduction json> <out json> <out txt>     # C = fl((n-1) S), through fault_fl_ns_e102.counts: the control, which should read as E92's own fit does
    fault_refit_e102.py real <e92 reduction json> <out json> <out txt>     # the sum accum.c reaches

Everything else is posthoc_fit_e92.main, unchanged: its tile list, its D per tile, its fit, its leave-one-out and its held-out E86 tiles. Live, operand bus and products do not depend on C and come from its own calls. Four op indices over make_e92's launch of 542,000,
as its flop count has, where its result-bus count has 16: the control shows what that alone does. FAULT_SAMPLES changes the four (the robustness arm is 16), FAULT_WORKERS sets the pool."""
import glob
import hashlib
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "tools", "claims-v3", "rpath"), os.path.join(ROOT, "tools", "claims-v3", "hlp")]
import fault_fl_ns_e102 as ff      # noqa: E402
import make_e102 as m102           # noqa: E402
import make_e88 as me              # noqa: E402
import make_e92 as m92             # noqa: E402
import posthoc_fit_e92 as pf       # noqa: E402


def one(a):
    path, ty, start, accum = a
    raw = open(path, "rb").read()
    aw, bw = me.words_from_tile(raw)
    sim = me.simulate(ty, aw, bw, launch_ops=m92.LAUNCH_OPS)
    bus, _, _ = me.bus_bits(ty, aw, bw)
    c = ff.counts(ty, raw, start, accum, launch=m92.LAUNCH_OPS, samples=int(os.environ.get("FAULT_SAMPLES", m92.FLOP_SAMPLES)))
    return f"{ty}:" + hashlib.sha256(raw).hexdigest(), {"live": sim["live_frac"], "bus": bus, "prod": sim["prod"], "res": c["res"], "alt": c["alt"], "flops": c["flops"], "other_frac": c["other_frac"]}


def main():
    start, e92, out, txt = sys.argv[1:5]
    accum = m102.accum_binary()
    paths = []
    for ty in ("fp32", "fp16"):
        for folder in ("tiles", "e90/tiles", "e92/tiles", "real/tiles"):
            paths += [(p, ty, start, accum) for p in sorted(glob.glob(os.path.join(HERE, folder, ty, "*.bin")))]
    with ProcessPoolExecutor(int(os.environ.get("FAULT_WORKERS", "3"))) as ex:
        cache = dict(ex.map(one, paths))
    cachef = out + ".counts"
    json.dump(cache, open(cachef, "w"))
    sys.argv = ["posthoc_fit_e92", e92, out, "--txt", txt, "--cache", cachef]
    pf.counts_of = lambda ty, raw: (_ for _ in ()).throw(RuntimeError("a tile outside the cache"))
    pf.main()
    os.remove(cachef)


if __name__ == "__main__":
    main()
