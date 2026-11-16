#!/usr/bin/env python3
"""E202's counts from the simulator runs (sysemu_check.sh), and their scaling to a card's launches (desk check of code).

Reads the counter's counts-log.json of runs S0b (1 group per minion, P = 2), S0c (2 groups per minion, P = 2), S2
(1 group per minion, P = 32: a card's shire-round) and, if present, S0a, S0r, S1 (scp staging, 32 shires x 1 minion),
S3 and S3x (the padding path) and S1b (scp staging, 32 shires x 2 minions, one padding group), and prints / writes:
  - per working hart of each run: instructions, the classes, tensor operations by kind with their bytes by region, and
    the past-L1 stores' bytes by region;
  - per group (P = 2) = S0c - S0b, minion by minion: exact for every tensor operation and every instruction outside the
    barrier polls (the `sync` class and the poll loop's branches follow the simulator's timing, not the card's);
  - per launch (P = 2) = S0b - per group;
  - per group at P = 32 = S2's minion minus S0b's per-launch part (the launch part differs at P = 32 only by its share
    of chunk 0's first copy: at most 14 tiles' copy loop, against about 600,000 instructions a group);
  - the padding path: S3 - S0c and S3x - S3, minion by minion (a padding group runs a whole group's work on input
    group 0 and writes its slot's discard line, so the work counts, TensorIMA8A32, TensorLoad, TensorLoadB,
    TensorLoadL2Scp and fswg.ps, must be equal; S3 also stores the debug logits, one 1 KiB TensorStore a group, and S0c
    does not, so that store and its few instructions are the rest of S3 - S0c beside the argmax's branch outcomes and
    the polls; S3x repeats S3 with another expected-logits file, a host-side change only);
  - every counted hart's tensor operations against a desk derivation from the code (exact by construction): the
    TensorIMA8A32, TensorLoad and TensorLoadB counts, and TensorLoadL2Scp by source (the group's input tiles from DRAM;
    the chunk copies, tile t of a chunk copied by minion t mod P, from DRAM or from the keeping shire's scratchpad;
    with scp staging the resident copy, tile k of the shire's kept tiles copied by minion k mod P, from DRAM);
  - each planned launch's exact accounting: shire-rounds = ceil(groups / P), group slots = P x rounds (a padding group
    issues a whole group's work), padding groups, the rounds of the busiest shire (working shire i takes rounds i,
    i + 32, ...; a launch's seconds follow the busiest shire) and how many shires take that many; tensor operations and
    bytes per slot; chunk copies 10,892 tiles a shire-round; the resident copy 10,892 tiles a launch (scp); and the
    instructions by class at the P = 32 pattern x slots (the scaling the code allows: every group runs the same path;
    the data change only the argmax's branch outcomes; the `sync` class and the poll loops follow the simulator's
    timing; the per-launch part, about 14,000 instructions a minion at P = 2 with dram staging, is listed apart).
Usage: python3 -I -B counts_scale.py RUNS_DIR OUT.json      (RUNS_DIR holds S0b/counts-log.json, S0c/..., S2/...)
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

OPS_PER_GROUP = 10892
GROUPS_PER_PASS = 3750
TEST_GROUPS = 625
TILES_PER_ROUND = 10892
NCHUNKS = 449
CHUNK_TILES = [13] * 112 + [28] * 337          # issue order: layer 1's 112 blocks, then layers 2-4's, then layer 5's one
FSWG_PER_GROUP = 224 * 16                      # 224 pairs of column blocks x 16 image lines
assert sum(CHUNK_TILES) == TILES_PER_ROUND and len(CHUNK_TILES) == NCHUNKS
# The launches a card day may make (P = 32 on 32 shires): the R-pass training launches and one pass of the test split.
PLANNED = {"train_R1": GROUPS_PER_PASS, "train_R16": 16 * GROUPS_PER_PASS, "train_R96": 96 * GROUPS_PER_PASS,
           "test_R1": TEST_GROUPS}
# The simulator runs' configurations (sysemu_check.sh): stage, shire mask, P, groups.
RUNS = {"S0a": ("dram", 0x1, 2, 2), "S0b": ("dram", 0x1, 2, 2), "S0c": ("dram", 0x1, 2, 4), "S0r": ("dram", 0x1, 2, 2),
        "S1": ("scp", 0xFFFFFFFF, 1, 32), "S2": ("dram", 0x1, 32, 32), "S3": ("dram", 0x1, 2, 3),
        "S3x": ("dram", 0x1, 2, 3), "S1b": ("scp", 0xFFFFFFFF, 2, 63)}


def load(d, name):
    p = os.path.join(d, name, "counts-log.json")
    return json.load(open(p)) if os.path.exists(p) else None


def flat(h):
    """One hart's counts as a flat dict of numbers."""
    out = {"instructions": h["instructions"]}
    for k, v in h["by_class"].items():
        if v:
            out["class." + k] = v
    for kind, t in h.get("tensor", {}).items():
        for f, v in t.items():
            if isinstance(v, (int, float)):
                out[f"tensor.{kind}.{f}"] = v
    for cls, regions in h.get("memory", {}).items():
        for reg, t in regions.items():
            for f, v in t.items():
                if isinstance(v, (int, float)):
                    out[f"memory.{cls}.{reg}.{f}"] = v
    return out


def sub(a, b):
    keys = set(a) | set(b)
    return {k: a.get(k, 0) - b.get(k, 0) for k in sorted(keys) if a.get(k, 0) - b.get(k, 0)}


def working(c):
    """Harts that ran the kernel's work (more than a few instructions)."""
    return {int(k): flat(v) for k, v in c["harts"].items() if v["instructions"] > 1000}


def derive(stage, mask, P, groups, hart):
    """The tensor operations of one hart, from the code (kernel/mnistmlp.c run() and the host's assignOwners)."""
    shires = [s for s in range(32) if (mask >> s) & 1]
    shire, mi = hart >> 6, (hart >> 1) & 31
    sidx = shires.index(shire)
    rounds = -(-groups // P)
    r_s = len(range(sidx, rounds, len(shires)))                      # rounds this shire takes
    owner = [shires[q % len(shires)] for q in range(NCHUNKS)]
    share = [len(range(mi, n, P)) for n in CHUNK_TILES]               # tiles of each chunk this minion copies
    l2 = {"ops": 0, "bytes_dram": 0, "bytes_scratchpad_own": 0, "bytes_scratchpad_remote": 0}

    def add(n, region):
        l2["ops"] += n
        l2[region] += n * 1024
    add(13 * r_s, "bytes_dram")                                       # the group's input tiles, every round
    if stage == "scp":
        kept = [n for q, n in enumerate(CHUNK_TILES) if owner[q] == shire]
        add(len(range(mi, sum(kept), P)), "bytes_dram")              # the resident copy (tile k by minion k mod P)
        for q in range(NCHUNKS):
            add(r_s * share[q], "bytes_scratchpad_own" if owner[q] == shire else "bytes_scratchpad_remote")
    else:
        add(r_s * sum(share), "bytes_dram")
    l2["bytes"] = l2["bytes_dram"] + l2["bytes_scratchpad_own"] + l2["bytes_scratchpad_remote"]
    return {"tensor.fma_int8.ops": r_s * OPS_PER_GROUP, "tensor.load.ops": r_s * OPS_PER_GROUP,
            "tensor.load_tenb.ops": r_s * OPS_PER_GROUP, "class.store_past_l1": r_s * FSWG_PER_GROUP,
            **{f"tensor.load_l2scp.{k}": v for k, v in l2.items()}}


def launch(groups, P=32, nshires=32):
    """A launch's exact accounting (desk check of code)."""
    rounds = -(-groups // P)
    slots = rounds * P
    busiest = -(-rounds // nshires)
    return {
        "groups": groups, "per_shire": P, "nshires": nshires, "shire_rounds": rounds, "group_slots": slots,
        "padding_groups": slots - groups, "busiest_shire_rounds": busiest,
        "shires_at_busiest": rounds - (busiest - 1) * nshires, "mean_shire_rounds": rounds / nshires,
        "fma_int8_ops_issued": slots * OPS_PER_GROUP, "fma_int8_ops_real_groups": groups * OPS_PER_GROUP,
        "fma_int8_macs_issued": slots * OPS_PER_GROUP * 16 * 64 * 16,
        "tensorload_a_ops": slots * OPS_PER_GROUP, "tensorload_a_bytes_scratchpad_own": slots * OPS_PER_GROUP * 1024,
        "tensorload_b_ops": slots * OPS_PER_GROUP, "tensorload_b_bytes_scratchpad_own": slots * OPS_PER_GROUP * 1024,
        "l2scp_input_ops": slots * 13, "l2scp_input_bytes_dram": slots * 13 * 1024,
        "fswg_activation_stores": slots * FSWG_PER_GROUP, "fswg_bytes_scratchpad_own": slots * FSWG_PER_GROUP * 32,
        "label_lines": groups, "discard_lines": slots - groups, "label_line_bytes_dram": slots * 64,
        "chunk_copy_tiles": rounds * TILES_PER_ROUND, "chunk_copy_bytes": rounds * TILES_PER_ROUND * 1024,
        "scp_resident_copy_tiles": TILES_PER_ROUND, "scp_resident_copy_bytes": TILES_PER_ROUND * 1024,
        "shire_barriers_per_minion_busiest": busiest * NCHUNKS,
        "busiest_minion_fma_int8_ops": busiest * OPS_PER_GROUP,
        "note": ("group slots = P x shire-rounds; a padding group (G >= groups, the last round only) reads input group 0, "
                 "issues a whole group's work and writes its slot's discard line; the records count "
                 "shire_barriers_per_minion_busiest, and each shire also passes one barrier after chunk 0's first "
                 "copy and, with scp staging, one shire barrier and one chip barrier after the resident copy")}


def main(d, outp):
    runs = {n: load(d, n) for n in RUNS}
    res = {"tool": "counts_scale.py", "runs_present": [n for n, c in runs.items() if c]}
    for n, c in runs.items():
        if c:
            res[f"{n}_harts"] = {str(h): v for h, v in working(c).items()}
    if runs["S0b"] and runs["S0c"]:
        b, cc = working(runs["S0b"]), working(runs["S0c"])
        res["per_group_p2"] = {str(h): sub(cc[h], b[h]) for h in b}
        res["per_launch_p2"] = {str(h): sub(b[h], sub(cc[h], b[h])) for h in b}
        for h in b:
            g = res["per_group_p2"][str(h)]
            assert g.get("tensor.fma_int8.ops") == OPS_PER_GROUP, (h, g.get("tensor.fma_int8.ops"))
    if runs["S2"] and runs["S0b"] and runs["S0c"]:
        s2 = working(runs["S2"])
        launch0 = res["per_launch_p2"]["0"]
        res["per_group_p32"] = {str(h): sub(v, launch0) for h, v in s2.items()}
        res["per_group_p32_note"] = ("S2 minion minus S0b minion 0's per-launch part (P = 2); minion 0 copies 1 tile "
                                     "of every chunk at P = 32, minion 27 1 tile of a 28-tile chunk and none of a "
                                     "13-tile chunk, minion 31 none")
    # The padding path: S3 - S0c (one group of minion 1's second round is a padding group) and S3x - S3 (a repeat).
    pad = {}
    if runs["S3"] and runs["S0c"]:
        s3, cc = working(runs["S3"]), working(runs["S0c"])
        pad["S3_minus_S0c"] = {str(h): sub(s3[h], cc[h]) for h in s3 if h in cc}
    if runs["S3x"] and runs["S3"]:
        s3x, s3 = working(runs["S3x"]), working(runs["S3"])
        pad["S3x_minus_S3"] = {str(h): sub(s3x[h], s3[h]) for h in s3x if h in s3}
    work = ("tensor.fma_int8.", "tensor.load.", "tensor.load_tenb.", "tensor.load_l2scp.", "class.store_past_l1")
    for k, v in list(pad.items()):
        pad[k + "_work_count_differences"] = sorted({f for h in v.values() for f in h if f.startswith(work)})
    if pad:
        pad["note"] = ("the work counts (TensorIMA8A32, TensorLoad, TensorLoadB, TensorLoadL2Scp, fswg.ps) must be "
                       "equal; S3 runs with debug logits and S0c without, so S3 - S0c also holds the debug TensorStore "
                       "(tensor.store: one 1 KiB store a group) and its instructions")
        res["padding_path"] = pad
    # Every counted hart against the desk derivation.
    checks, bad = {}, 0
    for n, c in runs.items():
        if not c:
            continue
        stage, mask, P, groups = RUNS[n]
        for h, v in working(c).items():
            want = derive(stage, mask, P, groups, h)
            diff = {k: [v.get(k, 0), w] for k, w in want.items() if v.get(k, 0) != w}
            checks[f"{n}/{h}"] = "EQUAL" if not diff else diff
            bad += bool(diff)
    res["derivation_checks"] = checks
    res["derivation_checks_unequal"] = bad
    # The planned launches, exact by construction.
    per_group_tensor = {
        "fma_int8_ops": OPS_PER_GROUP, "fma_int8_macs": OPS_PER_GROUP * 16 * 64 * 16,
        "tensorload_a_ops": OPS_PER_GROUP, "tensorload_a_bytes_scratchpad_own": OPS_PER_GROUP * 1024,
        "tensorload_b_ops": OPS_PER_GROUP, "tensorload_b_bytes_scratchpad_own": OPS_PER_GROUP * 1024,
        "l2scp_input_ops": 13, "l2scp_input_bytes_dram": 13 * 1024,
        "fswg_activation_stores": FSWG_PER_GROUP, "fswg_bytes_scratchpad_own": FSWG_PER_GROUP * 32,
        "label_line_bytes_dram": 64}
    res["per_group_tensor_exact"] = per_group_tensor
    res["launch_scaling"] = {k: launch(g) for k, g in PLANNED.items()}
    if "per_group_p32" in res:
        g = res["per_group_p32"]["0"]
        cls = {k: v for k, v in g.items() if k.startswith("class.") or k == "instructions"}
        res["per_pass_instructions_by_class_minion0_pattern"] = {k: v * GROUPS_PER_PASS for k, v in cls.items()}
        for k, L in res["launch_scaling"].items():
            L["instructions_by_class_slots_x_p32_minion0"] = {f: v * L["group_slots"] for f, v in cls.items()}
            L["instructions_busiest_minion_p32_minion0"] = cls["instructions"] * L["busiest_shire_rounds"]
        res["per_launch_part_p2_minion0"] = {k: v for k, v in res["per_launch_p2"]["0"].items()
                                             if k.startswith("class.") or k == "instructions"}
    json.dump(res, open(outp, "w"), indent=1, sort_keys=True)
    # A short table on stdout.
    for key in ("per_group_p2", "per_launch_p2", "per_group_p32"):
        if key in res:
            print(f"== {key}")
            for h, v in res[key].items():
                show = {k: v[k] for k in v if k == "instructions" or k.startswith("class.") or
                        k.startswith("tensor.") and k.endswith(".ops")}
                print(f"  hart {h}: {json.dumps(show)}")
    if pad:
        print("== padding_path")
        for k, v in pad.items():
            print(f"  {k}: {json.dumps(v)}")
    print(f"== derivation_checks: {len(checks)} harts, {bad} unequal")
    for k, v in checks.items():
        if v != "EQUAL":
            print(f"  {k}: {json.dumps(v)}")
    print("== launch_scaling")
    for k, L in res["launch_scaling"].items():
        print(f"  {k}: groups {L['groups']}, rounds {L['shire_rounds']}, slots {L['group_slots']}, padding "
              f"{L['padding_groups']}, busiest shire {L['busiest_shire_rounds']} rounds ({L['shires_at_busiest']} "
              f"shires), TensorIMA8A32 issued {L['fma_int8_ops_issued']:,}")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
