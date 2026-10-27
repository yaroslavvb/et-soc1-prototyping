#!/usr/bin/env python3
"""Reduce a pair of SAIFs (measured, base) to a compact gzipped JSON {net: toggles}.

Uses tools/open-flow/txfma/power.py's own read_saif, so the toggle counts are exactly the ones
the published ledger used. Differencing is power.py's: measured - base, keep > 0.
  saif_reduce.py <power.py dir> <saif_o1> <saif_o0> <strip> <out.json.gz>
"""
import gzip, json, sys, importlib.util, os

def load_power(d):
    spec = importlib.util.spec_from_file_location("pwr", os.path.join(d, "power.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

if __name__ == "__main__":
    d, s1, s0, strip, out = sys.argv[1:6]
    pwr = load_power(d)
    tc = pwr.read_saif(s1, strip)
    allnames = sorted(tc)
    if s0 and s0 != "-":
        base = pwr.read_saif(s0, strip)
        tc = {k: v - base.get(k, 0) for k, v in tc.items()}
    tc = {k: v for k, v in tc.items() if v > 0}
    with gzip.open(out, "wt") as fh:
        json.dump({"toggles": tc, "names_measured": allnames}, fh)
    print(f"{out}: {len(tc)} active nets of {len(allnames)} names")
