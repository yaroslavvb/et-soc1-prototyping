#!/usr/bin/env python3
"""E72's reduction: E60's own `reduce_hl.py`, unmodified, with one behaviour forced.

    python3 tools/claims-v3/lq6/reduce_e72.py <pass dirs...> --gen <hl-gen> --pred <E60 predictions.json>
            --out <results.json> [--csv runs.csv] [--leak auto|<W/C>]

`reduce_hl.py` chooses its measurement window per card:

    gov_free = not card_.startswith("aifoundry3")   # aifoundry3 is pinned at 600 MHz by its boot service

and for a `gov_free` card it starts the window 0.5 s after the clock first reads `busy_mhz=800`, because
on such a card the governor raises the clock during the launch. On E72's card the governor is pinned at
the vmin-LUT floor by TDP 0, so there is no ramp and no 800 MHz sample ever appears: the aifoundry3
branch is the correct one. This wrapper forces `gov_free=False` for every pass it reduces and changes
nothing else - the window, the gates, the leakage fit, the per-pass slopes and the V^2 block are
reduce_hl.py's own code, so E72's numbers are produced by the same estimator as E60's and E68's.

The clock itself is NOT forced anywhere: reduce_hl.py infers it from the data
(`clock = median of the single-clock runs`) and then gates every run against it, so a run that was not
at the pinned clock is dropped by E60's registered gate, not by anything written here.
"""
import importlib.util
import os
import sys

HL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hl", "reduce_hl.py")


def load(path, name="reduce_hl"):
    spec = importlib.util.spec_from_file_location(name, os.path.abspath(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    rh = load(HL)
    orig = rh.runs_of_pass

    def pinned(d, man, gov_free=False, busy_mhz=800):
        return orig(d, man, gov_free=False, busy_mhz=busy_mhz)

    rh.runs_of_pass = pinned           # main() resolves the name through the module globals
    rh.main()


if __name__ == "__main__":
    main()
