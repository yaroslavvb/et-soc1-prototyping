#!/usr/bin/env python3
"""E109 desk: every arm through the RTL bench that bench_e109.sh built. Per TensorFMA op on one minion: cycles (the FSM's own pace, +period=1),
issued micro-ops, ungated slots, scratchpad reads (the bench's count of dcache_ctrl.scp_req.read_en: an A word or a B half-line), and register bits
clocked with the enable high / seeing a clock edge / changing, in total and by unit (txfma, tima, the rest of the VPU). Also each format's base at the
card's period (546 / 318), as Q132(b) ran it.
    python3 tools/claims-v3/e109/desk/bench_arms_e109.py <scratch dir>/obj_lean/Vtb > tools/claims-v3/e109/desk/bench-arms.txt     # from the repo root
writes tools/claims-v3/e109/desk/bench-arms.json. The bench has no dcache and no core, and the lane register files are latch arrays its accounting does
not count, so it cannot see operand data moving into the register files (rtl-sim/fma_toggle_v2/tb_vpu.sv header; Q132(b) section 14).
SPDX-License-Identifier: Apache-2.0"""
import json, os, struct, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
KINDS = os.path.join(ROOT, "tools", "claims-v3", "kinds")
K = json.load(open(os.path.join(KINDS, "kinds.json")))
BIN = sys.argv[1]
def run(fmt, path, rows=16, cols=16, mask=None, period=1, ops=4):
    raw = open(path, "rb").read()
    assert len(raw) == 2048, (path, len(raw))
    words = list(struct.unpack("<512I", raw)) + [0] * 256
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "t.hex")
        open(h, "w").write("\n".join(f"{w:08x}" for w in words) + "\n")
        args = [BIN, f"+tiles={h}", f"+fmt={fmt}", "+warm=1", f"+ops={ops}", "+first=1", f"+period={period}", f"+rows={rows}", f"+cols={cols}"]
        if mask is not None:
            args.append(f"+mask={mask:x}")
        out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    acct = unit = None
    for l in out.splitlines():
        if l.startswith("ACCT "): acct = json.loads(l[5:])
        elif l.startswith("ACCTU "): unit = [int(x) for x in l.split()[1:]]
    n = acct["ops"]
    r = {k: acct[k] / n for k in ("cycles", "busy", "uops", "txfma_valid", "tima_valid", "scp_reads", "ff_clocked_bits", "ff_toggles", "ff_present_bits")}
    for i, u in enumerate(("txfma", "tima", "rest")):
        r[f"{u}_clocked"], r[f"{u}_toggles"], r[f"{u}_present"] = unit[3 * i] / n, unit[3 * i + 1] / n, unit[3 * i + 2] / n
    return r
ARMS = {"base": (16, 16, None), "m0": (16, 16, 0x0000), "k8": (16, 8, None), "r8": (8, 16, None), "m0k8": (16, 8, 0x0000)}
TILES = [("fp32", "zeros", f"{KINDS}/tiles/fp32/zeros.bin", ARMS), ("int8", "zeros", f"{KINDS}/tiles/int8/zeros.bin", ARMS),
         ("fp32", "a_zeros_b_randn", f"{KINDS}/tiles/fp32/a_zeros_b_randn.bin", {a: ARMS[a] for a in ("base", "m0")}),
         ("fp32", "a_nz_b_randn", f"{KINDS}/e93/tiles/fp32/a_nz_b_randn.bin", {a: ARMS[a] for a in ("base", "m0")}),
         ("fp32", "pi", f"{KINDS}/tiles/fp32/pi.bin", {a: ARMS[a] for a in ("base", "m0")}),
         ("fp32", "randn", f"{KINDS}/tiles/fp32/randn.bin", {a: ARMS[a] for a in ("base", "m0")})]
res = {"what": __doc__.split("\n")[0], "per_op": {}, "card_period": {}}
for fmt, kind, path, arms in TILES:
    if kind == "zeros":
        res["card_period"][f"{fmt}.zeros"] = run(fmt, path, period=546 if fmt != "int8" else 318)
    for arm, (rows, cols, mask) in arms.items():
        r = run(fmt, path, rows, cols, mask)
        res["per_op"][f"{arm}.{fmt}.{kind}"] = r
        print(f"{arm:5s} {fmt}.{kind:16s} cycles {r['cycles']:6.1f} uops {r['uops']:5.0f} ungated {r['txfma_valid'] + r['tima_valid']:6.0f} scp_reads {r['scp_reads']:5.0f} "
              f"clocked {r['ff_clocked_bits']:9.0f} edges {r['ff_present_bits']:9.0f} changing {r['ff_toggles']:8.0f} | lane units: edges txfma {r['txfma_present']:8.0f} "
              f"tima {r['tima_present']:7.0f} | rest: clocked {r['rest_clocked']:8.0f} edges {r['rest_present']:8.0f}", flush=True)
for k, r in res["card_period"].items():
    print(f"card period {k}: cycles {r['cycles']:.1f} (the window; Q132(b)'s 545 / 317)")
json.dump(res, open(os.path.join(HERE, "bench-arms.json"), "w"), indent=1)
