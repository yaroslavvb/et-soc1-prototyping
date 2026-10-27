#!/usr/bin/env python3
"""E73: write protocol-e73.json, the frequency ladder of the camera lock-in.

    python3 make_protocol_e73.py --out protocol-e73.json

The geometry is E63 amendment A1's, unchanged: 6 minions in each of the 32 shires (192 harts), one
launch per phase of `--seconds 8.5 --budget 9.5` under `timeout 10`, idled out to a 10 s dwell
(`pad_to_dwell`).  The ONLY thing E73 changes is how many 10 s phases make up a half period:

    N phases per arm  ->  lap = 20 N s  ->  f0 = 0.05 / N Hz

so N = 1 is E63's own 0.05 Hz, N = 2 is 0.025 Hz and N = 5 is 0.01 Hz.  Keeping the 10 s dwell is why
the ladder lands on 0.025 and 0.01 rather than on a round 0.02: a half period has to be a whole number
of launches, because `timeout 10` caps a device hold at 10 s (AGENT.md) and lengthening the idle tail
instead is the one change E63 measured a hazard for (the governor's idle-reset dip, ~1 launch in 45).

Each new-frequency block is bracketed by a 0.05 Hz reference block of the SAME rung pair, because the
camera's gain drifts with temperature (E63: 59 -> 42 mK/W over an hour).  REF1 F25 REF2 F10 REF3.
"""
from __future__ import annotations

import argparse
import json

SHIRES = list(range(32))
MASK = "0xffffffff"
PER_SHIRE = 6
HARTS = 192
DWELL = 10.0


def _set(values, note):
    return {"shires": SHIRES, "mask": MASK, "per_shire": PER_SHIRE, "harts": HARTS,
            "values": values, "note": note}


def block(bid, title, n_per_arm, total_laps, warmup, predicted):
    names = ["TOP23"] * n_per_arm + ["ZERO"] * n_per_arm
    phases = [{"set": s, "dwell_s": DWELL} for s in names]
    return {"id": bid, "title": title, "kind": "lockin",
            "n_per_arm": n_per_arm, "lap_s": 2 * n_per_arm * DWELL,
            "f_hz": 1.0 / (2 * n_per_arm * DWELL),
            "cycles": total_laps, "warmup_cycles": warmup,
            "lap_phase_orders": [list(names) for _ in range(total_laps)],
            "phases": phases, "predicted": predicted,
            "pass_rule": "README, Decision rules"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="protocol-e73.json")
    a = ap.parse_args()

    ref_pred = {"board_fundamental_w": [1.8, 3.0], "camera_roi_fundamental_mk": [40, 220],
                "phase_lag_deg": [70, 125],
                "note": "E63 A1 measured 119 +- 13 mK and H(0.05 Hz) = 47.8 +- 5.1 / 42.4 +- 9.7 mK/W"}
    blocks = [
        block("E73-REF1", "Reference: the top rung against its zero at 0.05 Hz, E63 A1's own block",
              1, 15, 3, ref_pred),
        block("E73-F25", "The same rung pair at 0.025 Hz (two launches an arm)",
              2, 12, 2, {"board_fundamental_w": [1.6, 2.8],
                         "camera_roi_fundamental_mk": [70, 420],
                         "H_over_ref": [1.45, 2.05],
                         "phase_lag_deg": [40, 90]}),
        block("E73-REF2", "Reference again, between the two new frequencies", 1, 15, 3, ref_pred),
        block("E73-F10", "The same rung pair at 0.01 Hz (five launches an arm)",
              5, 11, 1, {"board_fundamental_w": [1.5, 2.7],
                         "camera_roi_fundamental_mk": [110, 700],
                         "H_over_ref": [2.0, 3.6],
                         "phase_lag_deg": [18, 55]}),
        block("E73-REF3", "Reference a third time, after the lowest frequency", 1, 15, 3, ref_pred),
    ]
    order = [b["id"] for b in blocks]
    card_s = sum(b["cycles"] * b["lap_s"] for b in blocks)

    p = {
        "experiment": "E73",
        "request": "Q129",
        "card": "aifoundry2",
        "version": 2,
        "title": ("The heat path's time constants: E60's top rung against its zero at 0.05, 0.025 and "
                  "0.01 Hz, filmed from the back of the board"),
        "pad_to_dwell": True,
        "pad_to_dwell_note": (
            "Each phase is one launch of --seconds 8.5 (a device hold of about 8.6-9.3 s, never over "
            "--budget 9.5) idled out to its 10 s dwell, exactly as E63.  A block's half period is "
            "n_per_arm of those phases, so the lap is 20 * n_per_arm seconds and the fundamental is "
            "0.05 / n_per_arm Hz.  The idle tail is the same in both arms, so it lands on the even "
            "harmonics, not on f."),
        "heater": {
            "bin": "build/sparsity_t2/host/sparsity_host",
            "kernel": "build/sparsity_t2/kernel/sparsity.elf",
            "test": "fma", "type": "fp32", "pattern": "none", "values": "ones",
            "values_note": ("Only a default: every set names its own --values.  E62's heater build on "
                            "this card; its kernel is byte-identical to build/sparsity's, which E60 ran "
                            "these operand files through (sha256 990807f4...)."),
            "seconds": 8.5, "budget": 9.5, "seed": 1, "expected_launch_s": 8.9,
        },
        "safety": {
            "abs_stop_c": 80, "board_cap_w": 70, "cap_consecutive": 2, "die_consecutive": 1,
            "sampler_stale_s": 3,
            "note": ("E63 A1's caps, unchanged: the heaviest arm, lq_h23 on 192 minions, sat at about "
                     "40 W and a 60-61 C die.  70 W on two consecutive samples or an 80 C die ends the "
                     "session.  Holding 800 MHz is measured, not enforced: see README, Hold gate."),
        },
        "sets": {
            "TOP23": _set("file:build/hl-gen2/tiles/lq_h23.bin",
                          "E60 lq_h23: A = 1.0, B alternates every cycle between b and b ^ (all 23 "
                          "mantissa bits): 94,208 designed B bit flips per op per minion"),
            "ZERO": _set("file:build/hl-gen2/tiles/lq_h0.bin",
                         "E60 lq_h0: the ladder's zero, B constant, no designed flip"),
        },
        "blocks": blocks,
        "session": {"pre_idle_s": 60, "post_idle_s": 60, "block_gap_s": 0, "block_order": order},
        "camera": {"url": "http://p3-phone:8080/stream.raw.z"},
        "caps": {"max_card_min": 52, "max_wall_min": 65},
        "planned_block_seconds": card_s,
        "revision": "E73 v1, pre-registered Tue 27 Oct 2026 (week 44) before the first launch",
    }
    with open(a.out, "w") as f:
        json.dump(p, f, indent=1)
        f.write("\n")
    print(f"wrote {a.out}: {len(blocks)} blocks, {card_s/60.0:.2f} min of blocks "
          f"+ {(p['session']['pre_idle_s']+p['session']['post_idle_s'])/60.0:.2f} min idle")
    for b in blocks:
        print(f"  {b['id']:10s} n_per_arm {b['n_per_arm']}  lap {b['lap_s']:5.0f} s  "
              f"f {b['f_hz']:.4f} Hz  laps {b['cycles']:3d} ({b['warmup_cycles']} warm-up)  "
              f"{b['cycles']*b['lap_s']/60.0:5.2f} min")


if __name__ == "__main__":
    main()
