#!/usr/bin/env python3
"""E85: write protocol-e85.json (the card session) and protocol-e85-dry.json (the pipeline check).

    python3 make_protocol_e85.py            # writes both beside this file

The geometry is E63 amendment A1's, unchanged (also E73's): 6 minions in each of the 32 shires
(192 harts, mask 0xffffffff), one launch per phase of `--seconds 8.5 --budget 9.5` under `timeout 10`,
idled out to a 10 s dwell (`pad_to_dwell`), so two arms alternate on a fixed 20 s grid: 0.05 Hz.

What E85 changes is only WHAT the arms compute.  Each kind block switches one kind of number against
its own type's zeros (the Q130(s) revision 2 tiles, the files E80 and E83 measured on this card):

    E85-F32   fp32 randn   vs fp32 zeros      (--type fp32)
    E85-I8    int8 full    vs int8 zeros      (--type int8)
    E85-F16   fp16 randn   vs fp16 zeros      (--type fp16)
    E85-SP90  fp32 sparse90 vs fp32 zeros     (--type fp32; the near-null kind, ~0.3 W)

and E63's own reference rung pair (lq_h23 vs lq_h0, fp32, E60's operand files) runs three times,
first, in the middle and last, to track the camera's gain drift (E63: 59 -> 42 mK/W in an hour).
Every kind block sits next to a reference block.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SHIRES = list(range(32))
MASK = "0xffffffff"
PER_SHIRE = 6
HARTS = 192
DWELL = 10.0
KT = "tools/claims-v3/kinds/tiles"


def _set(values, typ, note):
    return {"shires": SHIRES, "mask": MASK, "per_shire": PER_SHIRE, "harts": HARTS,
            "type": typ, "values": values, "note": note}


SETS = {
    "REF23": _set("file:build/hl-gen2/tiles/lq_h23.bin", "fp32",
                  "E60 lq_h23, E63's top rung: A = 1.0, B alternates every cycle between b and b ^ "
                  "(all 23 mantissa bits): 94,208 designed B bit flips per op per minion"),
    "REF0": _set("file:build/hl-gen2/tiles/lq_h0.bin", "fp32",
                 "E60 lq_h0, the rung's zero: the same tiles with no B flips"),
    "F32R": _set(f"file:{KT}/fp32/randn.bin", "fp32",
                 "Q130(s) rev 2 fp32 randn (A and B standard normal), the tile E80 and E83 ran"),
    "F32Z": _set(f"file:{KT}/fp32/zeros.bin", "fp32",
                 "Q130(s) rev 2 fp32 zeros: every element +0.0, every lane gated"),
    "F16R": _set(f"file:{KT}/fp16/randn.bin", "fp16",
                 "Q130(s) rev 2 fp16 randn, the tile E80 and E83 ran"),
    "F16Z": _set(f"file:{KT}/fp16/zeros.bin", "fp16",
                 "Q130(s) rev 2 fp16 zeros (the same 2,048 zero bytes as fp32 zeros, run as fp16)"),
    "I8F": _set(f"file:{KT}/int8/full.bin", "int8",
                "Q130(s) rev 2 int8 full (= E64's int8 randn: uniform over the whole byte range)"),
    "I8Z": _set(f"file:{KT}/int8/zeros.bin", "int8",
                "Q130(s) rev 2 int8 zeros (the same 2,048 zero bytes, run as int8)"),
    "F32S90": _set(f"file:{KT}/fp32/sparse90.bin", "fp32",
                   "Q130(s) rev 2 fp32 sparse90: 90% of elements +0.0, the rest standard normal"),
}


def block(bid, role, fmt, kind, a, b, laps, warmup, title):
    return {"id": bid, "title": title, "kind": "lockin", "role": role, "format": fmt,
            "kind_name": kind, "n_per_arm": 1, "lap_s": 2 * DWELL, "f_hz": 1.0 / (2 * DWELL),
            "cycles": laps, "warmup_cycles": warmup,
            "lap_phase_orders": [[a, b] for _ in range(laps)],
            "phases": [{"set": a, "dwell_s": DWELL, "launches": 1},
                       {"set": b, "dwell_s": DWELL, "launches": 1}],
            "predicted": f"predictions.json blocks[{bid!r}]",
            "pass_rule": "README, Decision rules"}


def blocks_main():
    ref = "lq_h23 vs lq_h0 (E63's reference rung pair, fp32), 192 minions, 0.05 Hz"
    return [
        block("E85-REF1", "ref", "fp32", "lq_h23", "REF23", "REF0", 18, 6,
              "Reference 1: " + ref + "; six warm-up laps, as the session's first load"),
        block("E85-F32", "kind", "fp32", "randn", "F32R", "F32Z", 18, 3,
              "fp32 randn against fp32 zeros, 192 minions, 0.05 Hz"),
        block("E85-I8", "kind", "int8", "full", "I8F", "I8Z", 21, 3,
              "int8 full against int8 zeros, 192 minions, 0.05 Hz (three more laps: the smallest "
              "of the three main kinds' signals)"),
        block("E85-REF2", "ref", "fp32", "lq_h23", "REF23", "REF0", 15, 3, "Reference 2: " + ref),
        block("E85-F16", "kind", "fp16", "randn", "F16R", "F16Z", 18, 3,
              "fp16 randn against fp16 zeros, 192 minions, 0.05 Hz"),
        block("E85-SP90", "kind", "fp32", "sparse90", "F32S90", "F32Z", 15, 3,
              "fp32 sparse90 against fp32 zeros, 192 minions, 0.05 Hz: the near-null kind"),
        block("E85-REF3", "ref", "fp32", "lq_h23", "REF23", "REF0", 15, 3, "Reference 3: " + ref),
    ]


def blocks_dry():
    return [
        block("E85-REF1", "ref", "fp32", "lq_h23", "REF23", "REF0", 5, 1, "dry: reference"),
        block("E85-F32", "kind", "fp32", "randn", "F32R", "F32Z", 5, 1, "dry: fp32 randn"),
        block("E85-REF2", "ref", "fp32", "lq_h23", "REF23", "REF0", 5, 1, "dry: reference"),
    ]


def protocol(blocks, dry=False):
    card_s = sum(b["cycles"] * b["lap_s"] for b in blocks)
    idle = 20 if dry else 60
    return {
        "experiment": "E85",
        "request": "Q130",
        "card": "aifoundry2",
        "version": 2,
        "title": ("The thermal camera's view of different kinds of numbers: each kind against its own "
                  "type's zeros at 0.05 Hz, with E63's reference rung interleaved, filmed from the back "
                  "of the board" + (" (DRY: the pipeline check, no card)" if dry else "")),
        "pad_to_dwell": True,
        "pad_to_dwell_note": (
            "Each phase is one launch of --seconds 8.5 (a device hold of about 8.6-9.3 s, never over "
            "--budget 9.5) idled out to its 10 s dwell, exactly as E63 A1 and E73: the two arms "
            "switch on a fixed 20 s grid, 0.05 Hz, and the idle tail lands on 2f."),
        "heater": {
            "bin": "build/sparsity_t2/host/sparsity_host",
            "kernel": "build/sparsity_t2/kernel/sparsity.elf",
            "test": "fma", "type": "fp32", "pattern": "none", "values": "ones",
            "values_note": ("Only defaults: every set names its own --values AND its own --type "
                            "(run_hlk.py).  E62's heater build on this card, the one E63, E73, E80 and "
                            "E83 ran (host sha256 7adadf4f..., kernel 990807f4...); its --values file: "
                            "path reads A then B, 1,024 bytes each, in the chosen type's layout."),
            "seconds": 8.5, "budget": 9.5, "seed": 1, "expected_launch_s": 8.9,
        },
        "safety": {
            "abs_stop_c": 80, "board_cap_w": 70, "cap_consecutive": 2, "die_consecutive": 1,
            "sampler_stale_s": 3,
            "note": ("E63 A1's caps, unchanged.  The heaviest arm, fp32 randn on 192 minions, is "
                     "predicted at about 40 W on the board (E63 A1's lq_h23 arm read 38.6 W) and a die "
                     "below 60 C.  70 W on two consecutive samples or an 80 C die ends the session.  "
                     "Holding 800 MHz is measured, not enforced: README, Hold."),
        },
        "sets": SETS,
        "blocks": blocks,
        "session": {"pre_idle_s": idle, "post_idle_s": idle, "block_gap_s": 0,
                    "block_order": [b["id"] for b in blocks]},
        "camera": {"url": "http://p3-phone:8080/stream.raw.z",
                   "settings": "unchanged: preset visualize, automatic shutter on"},
        "caps": ({"max_card_min": 8, "max_wall_min": 12} if dry
                 else {"max_card_min": 44, "max_wall_min": 55}),
        "planned_block_seconds": card_s,
        "revision": ("E85 v1, pre-registered Sat 31 Oct 2026 (week 44) before the claim and the first "
                     "launch" + ("; the dry protocol only checks the pipeline" if dry else "")),
    }


def main():
    for name, blocks, dry in (("protocol-e85.json", blocks_main(), False),
                              ("protocol-e85-dry.json", blocks_dry(), True)):
        p = protocol(blocks, dry)
        with open(os.path.join(HERE, name), "w") as f:
            json.dump(p, f, indent=1)
            f.write("\n")
        idle = p["session"]["pre_idle_s"] + p["session"]["post_idle_s"]
        print(f"wrote {name}: {len(blocks)} blocks, {p['planned_block_seconds'] / 60:.2f} min of blocks "
              f"+ {idle / 60:.2f} min idle; cap {p['caps']['max_card_min']} card-min")
        for b in blocks:
            print(f"  {b['id']:9s} {b['role']:4s} {b['format']} {b['kind_name']:9s} laps {b['cycles']:3d} "
                  f"({b['warmup_cycles']} warm-up)  {b['cycles'] * b['lap_s'] / 60.0:5.2f} min")


if __name__ == "__main__":
    main()
