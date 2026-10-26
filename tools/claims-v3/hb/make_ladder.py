#!/usr/bin/env python3
"""E65 block C, the hart ladder: writes the two protocol.json files tools/claims-v3/hm/run_hm.py executes.

    python3 tools/claims-v3/hb/make_ladder.py <out-dir>      # protocol-randn.json, protocol-zeros.json

One session per stimulus (run_hm.py's `--values` is session-wide), same card, same clock, same rungs, so the pair
differs in the operand data alone. Rungs are hart counts 64 .. 1,024 at --per-shire 32, with an IDLE phase before and
after every rung so leakage is de-trended per rung (README.md, block C). The shires of an n-shire rung are
`round(i * 32 / n)`, a fixed spread over the die: E62-CAL measured power following harts and not geometry to within
+/- 0.5 W, so the spread is a precaution, not a variable.
"""
import json
import os
import sys

PER_SHIRE = 32
RUNGS = [2, 4, 8, 12, 16, 24, 32]           # shires -> 64, 128, 256, 384, 512, 768, 1,024 harts
DWELL_S = 8.5                                # one 8 s launch, as E62-CAL
IDLE_S = 20.0
CYCLES = 3                                   # laps; `alternate` reverses the odd ones, so rung order is balanced


def shires_of(n):
    s = sorted({round(i * 32 / n) for i in range(n)})
    assert len(s) == n and 0 <= s[0] and s[-1] < 32, (n, s)
    return s


def mask_of(shires):
    m = 0
    for s in shires:
        m |= 1 << s
    return m


def build(values):
    sets = {"IDLE": {"idle": True, "mask": "0x00000000", "harts": 0,
                     "note": "no launch: the bracket that de-trends leakage for the rung on either side"}}
    phases = [{"set": "IDLE", "dwell_s": IDLE_S, "launches": 0, "timed": True}]
    for n in RUNGS:
        sh = shires_of(n)
        harts = n * PER_SHIRE
        sets[f"H{harts}"] = {"shires": sh, "mask": f"0x{mask_of(sh):08x}", "per_shire": PER_SHIRE,
                             "harts": harts, "note": f"{n} shires spread round(i*32/{n}), one hart per minion"}
        phases.append({"set": f"H{harts}", "dwell_s": DWELL_S, "launches": 1})
        phases.append({"set": "IDLE", "dwell_s": IDLE_S, "launches": 0, "timed": True})
    return {
        "version": 2,
        "experiment": "E65",
        "revision": f"E65-LADDER-{values}",
        "card": "aifoundry3",
        "request": "Q126",
        "session": {"pre_idle_s": 60, "post_idle_s": 60, "block_gap_s": 0},
        "heater": {
            "bin": "build/sparsity/host/sparsity_host",
            "kernel": "build/sparsity/kernel/sparsity.elf",
            "test": "fma", "type": "fp32", "pattern": "none", "values": values,
            "seconds": 8, "budget": 9.5, "seed": 1, "expected_launch_s": 8.4,
            "note": "aifoundry3's build of the same sources as aifoundry2's build/sparsity_t2 (lib.sh:35-43); the "
                    "arguments are E62's heater block and hp/hplib.sh:400 verbatim apart from --values.",
        },
        "sets": sets,
        "blocks": [{
            "id": f"E65-LADDER-{values}",
            "name": f"E65-LADDER-{values}",
            "title": f"Hart ladder, {values} operands, idle-bracketed",
            "kind": "calibration",
            "phases": phases,
            "cycles": CYCLES,
            "warmup_cycles": 0,
            "order": "alternate",
            "movie": False,
            "predicted": {
                "what": "Board power over the bracketing idles is linear in harts. Scaling E62's 800 MHz line "
                        "(5.80 W + 55.8 mW/hart on aifoundry2) to this card by f.V^2 = (600/800)(0.523/0.618)^2 "
                        "= 0.537 gives 3.12 W + 30.0 mW/hart if the offset is switching work, or 5.80 W + "
                        "30.0 mW/hart if the offset is a fixed cost of having a launch open at all. The zeros "
                        "session's slope is 10-40% of the randn session's; its intercept is the test.",
                "direction": "no spatial claim",
                "basis": "E62's CAL ladder and finding 11; E64's zeros-vs-random per-multiply-add energies",
            },
            "pass_rule": "README.md block C, rules C1-C4. Every rung's statistic is the MEDIAN of the 10 Hz board "
                         "samples in the last 4.0 s of its launch, minus the mean of the two bracketing idles' "
                         "last 10 s medians; the raw line (no bracket subtraction) is reported beside it.",
        }],
        "safety": {"abs_stop_c": 78, "board_cap_w": 80, "cap_consecutive": 2, "die_consecutive": 1,
                   "sampler_stale_s": 3, "bloom_cycle_stop_c": 72,
                   "note": "aifoundry3 is pinned at 600 MHz, so there is no governor step to protect; 72 C on a "
                           "full-card phase and 78 C absolute keep the die well inside the lab's 90 C rule."},
        # run_hm.py's schema (hm/prereg/protocol.json): enter_below_c + max_gap_s. The gate is called only
        # BETWEEN blocks and each session has exactly one, so it never fires here; the keys are right so a reader
        # is not misled, and so a later session that adds a block inherits a live gate (A6).
        "cooldown_gate": {"enter_below_c": 60, "gap_s": 0, "max_gap_s": 75,
                          "applies_when": "the next block's dwell-weighted switched power exceeds the previous "
                                          "block's; with one block per session it is never called"},
        "budget": {"card_held_cap_min": 40, "card_session_wall_cap_min": 60},
        "conventions": {"power_window": "the last 4.0 s of a launch, median of the 10 Hz samples (E62-CAL)",
                        "idle_window": "the last 10.0 s of an IDLE phase, median"},
    }


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for values in ("randn", "zeros"):
        p = os.path.join(out, f"protocol-{values}.json")
        with open(p, "w") as f:
            json.dump(build(values), f, indent=1)
            f.write("\n")
        print(p)


if __name__ == "__main__":
    main()
