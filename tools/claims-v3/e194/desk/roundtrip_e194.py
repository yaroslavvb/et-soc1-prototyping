#!/usr/bin/env python3
"""E194's desk check A, the round trip (E194.md section 15): forecast_e194.py with its card set back to E191's
(aifoundry1-c1, key c1) or E189's (aifoundry3, key a3), its clock back to 600 MHz and its die band back to E189's 52-60 C
must reproduce every number of E191's and E189's frozen forecast files, in their configurations and their counters
arms, exactly (at their 6 significant digits). Strings (notes and how-texts) are not compared; keys E194 adds are not in
the old files and so are not compared. Desk only, standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e194/desk/roundtrip_e194.py    # prints ROUND TRIP PASS or FAIL
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E194 = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E194, "..", "..", ".."))


def load_fc():
    spec = importlib.util.spec_from_file_location("forecast_e194_rt", os.path.join(E194, "forecast_e194.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def leaves(x, path=()):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, path + (k,))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, path + (i,))
    else:
        yield path, x


def get(x, path):
    for p in path:
        x = x[p]
    return x


def compare(old, new):
    n, bad = 0, []
    for part in ("configs", "counters_arm_expectations"):
        for path, v in leaves(old[part], (part,)):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                continue
            n += 1
            try:
                w = get(new, path)
            except (KeyError, IndexError, TypeError):
                bad.append((path, v, "missing"))
                continue
            if w != v:
                bad.append((path, v, w))
    return n, bad


def main():
    out = {}
    ok = True
    for name, card, ref in (("E191", ("aifoundry1-c1", "c1"), "tools/claims-v3/e191/forecast-e191.json"),
                            ("E189", ("aifoundry3", "a3"), "tools/claims-v3/e189/forecast-e189.json")):
        FC = load_fc()
        FC.T0_FORECAST, FC.T0_BAND = 55.0, (52.0, 60.0)     # E189's and E191's die (their section 5)
        new = FC.build(argparse.Namespace(), card=card, f_hz=600e6)
        old = json.load(open(os.path.join(REPO, ref)))
        n, bad = compare(old, new)
        out[name] = {"card": card[0], "clock_mhz": 600, "die_band_c": [52, 60], "reference": ref, "numbers_compared": n,
                     "differing": len(bad), "first_differences": [[list(map(str, p)), a, b] for p, a, b in bad[:10]]}
        ok &= not bad
        print(f"{name}: card {card[0]} at 600 MHz: {n} numbers compared with {ref}, {len(bad)} differ")
        for p, a, b in bad[:10]:
            print("   ", "/".join(map(str, p)), a, b)
    print("ROUND TRIP " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
