#!/usr/bin/env python3
"""E143 (Q138): the self-test, run before the registration's commit. No card.

    python3 tools/claims-v3/e143/selftest_e143.py > tools/claims-v3/e143/selftest.txt

  1. the frozen inputs hash as committed, and every pool tile is the manifest's;
  2. a tile with one byte changed, or of the wrong size, is refused;
  3. predictions-e143.json holds Q138(x)'s numbers for every tile and model, unchanged; the groups are 19 governed and 17 pinned;
  4. the runner's preflight refuses a protocol without the watcher's stop keys and binaries that are not E80's;
  5. the bootstrap is reproducible and the coverage line is E140's (21 of 25);
  6. the scoring at known answers: measured = M7's predictions gives every rule PASS (better than the reference says) with rms 0; governed clocks
     30 MHz low fail F1 and F3 but not F2; boards 5 W high fail W1, W2 and W3; rises 2 C high fail H1 and H3; a replicate 30 MHz off fails R0.
"""
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e143_common as C  # noqa: E402
import reduce_e143 as RD  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e143.json")))
fails = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


# 1
bad = C.check_frozen()
M = C.manifest()
tb = [C.check_tile(C.ROOT, t) for t in M.values()]
ok(not bad and not any(tb) and len(M) == 36, f"frozen inputs and 36 tiles as committed ({len(M)} tiles, {sum(1 for x in tb if x)} bad)")

# 2
with tempfile.TemporaryDirectory() as td:
    t = M["fp32.anchor_randn"]
    dst = os.path.join(td, C.POOL_REL, t["file"])
    os.makedirs(os.path.dirname(dst))
    src = os.path.join(C.ROOT, C.POOL_REL, t["file"])
    b = bytearray(open(src, "rb").read())
    b[1500] ^= 0x01
    open(dst, "wb").write(bytes(b))
    w1 = C.check_tile(td, t)
    open(dst, "wb").write(bytes(b[:2047]))
    w2 = C.check_tile(td, t)
    ok(w1 is not None and "sha256 whole" in w1 and w2 is not None and "2047 bytes" in w2, f"a changed byte and a short file are refused ({w1[:60]}...; {w2})")

# 3
Q = json.load(open(os.path.join(C.ROOT, C.PRED_REL)))
same = all(P["tiles"][n]["models"][m][k] == Q["tiles"][n][m][k] for n in Q["tiles"] for m in ("M7", "M6", "M5") for k in P["tiles"][n]["models"][m])
ng = sum(1 for t in P["tiles"].values() if t["group"] == "governed")
ok(same and len(P["tiles"]) == 36 and ng == 19, f"predictions-e143.json = Q138(x)'s numbers for 36 tiles x 3 models; {ng} governed, {36 - ng} pinned")

# 4
import run_e143 as RN  # noqa: E402
proto = json.load(open(os.path.join(HERE, "protocol.json")))
p2 = copy.deepcopy(proto)
p2["safety"] = {"die_c": 80, "board_w": 93, "board_samples": 3}
w = RN.preflight(p2, "/nonexistent")
ok(w is not None and "lacks abs_stop_c" in w and "lacks board_cap_w" in w, f"preflight refuses E136's stop keys: {w[:110]}")
w = RN.preflight(proto, "/nonexistent")
ok(w is not None and "sha256 None" in w, f"preflight refuses missing binaries: {w[:110]}")
ok(proto["safety"] == {"abs_stop_c": 80, "board_cap_w": 93, "cap_consecutive": 3} and proto["limit_p800_w"] == 86.0,
   f"the protocol's stops {proto['safety']} and admission limit {proto['limit_p800_w']} W")
est = max(a["fixed_p800_w"] for a in proto["admission"].values())
labs = {r["label"] for b in proto["blocks"] for r in b["runs"]}
ok(all(l in proto["admission"] for l in labs) and est <= proto["limit_p800_w"], f"every label in the admission table, highest estimate {est} W <= the limit")

# 5
a1 = C.boot_rms_range(P["reference"]["governed"]["mhz_err"], 19)
a2 = C.boot_rms_range(P["reference"]["governed"]["mhz_err"], 19)
ok(a1 == a2 and C.coverage_line(25) == 21 and C.coverage_line(36) == 31, f"bootstrap reproducible {tuple(round(x, 3) for x in a1)}; coverage lines 25 -> {C.coverage_line(25)}, 36 -> {C.coverage_line(36)}")


# 6
def cells_at(fn_mhz=lambda n, v: v, fn_w=lambda n, v: v, fn_rise=lambda n, v: v, rep_mhz=0.0):
    cells = {}
    for n, t in P["tiles"].items():
        m = t["models"]["M7"]
        cells[t["label"]] = {"label": t["label"], "name": n, "n": 3, "passes": [1, 2, 3], "burst_mhz": fn_mhz(n, m["burst_mhz"]),
                             "burst_w": fn_w(n, m["burst_board_w"]), "rise_c": fn_rise(n, m["burst_die_rise_c"]), "D_w": m["burst_D_w"],
                             "burst_mhz_runs": [], "burst_w_runs": [], "rise_runs": [], "die_start_runs": [], "D_runs": [], "p800_w_runs": [], "first_down": []}
    for lab, r in P["replicate"].items():
        cells[lab] = {"label": lab, "n": 3, "burst_mhz": r["ref_burst_mhz"] + rep_mhz, "burst_w": r["ref_burst_w"], "rise_c": 5.0}
    return cells


sc = RD.score(cells_at(), P, 2)
v = {k: x["verdict"] for k, x in sc["rules"].items()}
ok(all(x.startswith("PASS") for x in v.values()) and sc["rules"]["E143-F1"]["rms"] == 0.0, f"at M7's numbers: {v}")
gov = {n for n, t in P["tiles"].items() if t["group"] == "governed"}
sc = RD.score(cells_at(fn_mhz=lambda n, x: x - 30 if n in gov else x), P, 2)
v = {k: x["verdict"] for k, x in sc["rules"].items()}
ok(v["E143-F1"] == "FAIL" and v["E143-F3"] == "FAIL" and v["E143-F2"].startswith("PASS"), f"governed clocks 30 MHz low: F1 {v['E143-F1']}, F2 {v['E143-F2']}, F3 {v['E143-F3']}")
sc = RD.score(cells_at(fn_w=lambda n, x: x + 5), P, 2)
v = {k: x["verdict"] for k, x in sc["rules"].items()}
ok(v["E143-W1"] == "FAIL" and v["E143-W2"] == "FAIL" and v["E143-W3"] == "FAIL", f"boards 5 W high: W1 {v['E143-W1']}, W2 {v['E143-W2']}, W3 {v['E143-W3']}")
sc = RD.score(cells_at(fn_rise=lambda n, x: x + 2), P, 2)
v = {k: x["verdict"] for k, x in sc["rules"].items()}
ok(v["E143-H1"] == "FAIL" and v["E143-H3"] == "FAIL", f"rises 2 C high: H1 {v['E143-H1']}, H3 {v['E143-H3']}")
r0 = RD.replicate(cells_at(rep_mhz=30.0), P)
r1 = RD.replicate(cells_at(), P)
ok(r0["verdict"] == "FAIL" and r1["verdict"] == "PASS", f"a replicate 30 MHz off: R0 {r0['verdict']}; at the reference: {r1['verdict']}")

print("\nALL PASS" if not fails else f"\n{len(fails)} FAILED")
sys.exit(1 if fails else 0)
