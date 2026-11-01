#!/usr/bin/env python3
"""E118's reduction: E60's own `reduce_hl.py`, unmodified, with two things forced (E72's reduce_e72.py plus one).

    python3 tools/claims-v3/e118/reduce_e118.py <pass dirs...> --gen <hl-gen> --pred <E60 predictions.json>
            --out <results.json> [--csv runs.csv] [--leak auto|<W/C>] [--pinned | --free]

1. The window (E72's change): `--pinned` (the 600 MHz passes, TDP 0) forces `gov_free=False`, so the window starts
   at t0 + 1 s with no 800 MHz ramp to wait for; `--free` (the 800 MHz control at the card's own governor) forces
   `gov_free=True`, E60's amendment A2 for an 800 MHz card. Reduce the two halves SEPARATELY: the reducer infers one
   clock per card and gates every run against it.
2. The voltage source (E118's no-PMIC-read profile): the sampler never sends DM_CMD_GET_ASIC_VOLTAGE, so the
   telemetry has no `die_mv`. reduce_hl.py reads the minion voltage from `die_mv.minion` for its 3 mV run gate and
   its unit conversions; this wrapper hands it `sp.minion_mv[0]` (the SP statistics' minion-rail average, a RAM copy)
   under that name, in memory only. On E60's card-0 passes the two sources agree to 0.01 mV in the reducer's own
   windows (603.63 vs 603.64 mV, 230 runs) and on E72's to 0.00 mV (517.92), with the same runs failing the 3 mV gate
   (predict_e118.py repeats that check). A telemetry line without `sp` is dropped and counted. The output gains
   `e118_voltage_source`. Nothing else changes: window, gates, leakage fit, per-pass slopes are reduce_hl.py's.
"""
import importlib.util
import json
import os
import sys

HL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hl", "reduce_hl.py")
STATS = {"lines": 0, "filled_from_sp": 0, "dropped_no_sp": 0, "had_die_mv": 0}


def load(path, name="reduce_hl"):
    spec = importlib.util.spec_from_file_location(name, os.path.abspath(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def patch_voltage(rh, force_sp=True):
    orig = rh.load_jsonl

    def load_jsonl(path):
        rows = orig(path)
        if os.path.basename(path).startswith("telemetry"):
            out = []
            for s in rows:
                STATS["lines"] += 1
                if "die_mv" in s and not force_sp:
                    STATS["had_die_mv"] += 1
                    out.append(s)
                    continue
                sp = s.get("sp")
                if not sp or "minion_mv" not in sp or "board_w" not in s or "mhz" not in s or "temp_c" not in s:
                    STATS["dropped_no_sp"] += 1
                    continue
                s = dict(s)
                if "die_mv" in s:
                    STATS["had_die_mv"] += 1
                s["die_mv"] = {"minion": sp["minion_mv"][0]}
                STATS["filled_from_sp"] += 1
                out.append(s)
            return out
        return rows

    rh.load_jsonl = load_jsonl


def main():
    mode = None
    argv = []
    for x in sys.argv[1:]:
        if x in ("--pinned", "--free"):
            mode = x
        else:
            argv.append(x)
    if mode is None:
        raise SystemExit("give --pinned (the 600 MHz passes) or --free (the 800 MHz control)")
    rh = load(HL)
    patch_voltage(rh)
    orig = rh.runs_of_pass
    FREE = mode == "--free"

    def forced(d, man, gov_free=False, busy_mhz=800):
        return orig(d, man, gov_free=FREE, busy_mhz=busy_mhz)

    rh.runs_of_pass = forced
    sys.argv = [sys.argv[0]] + argv
    rh.main()
    out = argv[argv.index("--out") + 1]
    res = json.load(open(out))
    res["e118_voltage_source"] = {"used": "sp.minion_mv[0] (SP statistics, minion rail average) as die_mv.minion",
                                  "why": "no-PMIC-read profile: GET_ASIC_VOLTAGE is never sent", "lines": STATS,
                                  "window": "pinned (gov_free False)" if mode == "--pinned" else "free (gov_free True)"}
    json.dump(res, open(out, "w"), indent=1)
    print(f"e118 voltage source: {STATS}")


if __name__ == "__main__":
    main()
