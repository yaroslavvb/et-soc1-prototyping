#!/usr/bin/env python3
"""M12 (Q157): candidate kinds for a next one-number TensorFMA run (REFIT.md section 5), with M12's and M10's forecasts and each train's
power at E182's train noise. A candidate for the next registration; nothing is registered here.

    /usr/bin/python3 -B tools/claims-v3/m12/candidates_m12.py --root . stage      # tiles/ and kinds-m12.json (the bench's input)
    (bench/bench_m12.sh runs the toggle bench on the mini -> bench/counts-m12.json)
    /usr/bin/python3 -B tools/claims-v3/m12/candidates_m12.py --root . forecast   # candidates-m12.json and candidates-m12.md
    /usr/bin/python3 -B tools/claims-v3/m12/candidates_m12.py --root . check      # recomputes both stages in memory, compares bytes

The forecast stage needs a C compiler (E178's flip model, compiled unchanged) and numpy (M10's feature chain, unchanged).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import statistics
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m12_common as C  # noqa: E402

HW_TRAIN = 0.0051   # E182's train half-width at 32 units (E182.md section 6; 76 fp32 processes give 38 units at the same half-width)
F1 = 0x3F800000     # fp32 1.0
H1 = 0x3C00         # fp16 1.0


def i8w(x):
    return (x & 0xFF) * 0x01010101


def h16w(h):
    return (h << 16) | h


def nm8(x):
    return ("m" if x < 0 else "") + str(abs(x))


def kinds_rule():
    """REFIT.md section 5, in its order: (type, name, a_word, b_word, set, tile source or None for new)"""
    out = []
    for b in (3, 63):
        for a_, b_ in ((1, b), (b, 1), (-1, -b), (-b, -1)):
            out.append(("int8", f"m12_a{nm8(a_)}_b{nm8(b_)}", i8w(a_), i8w(b_), "C8", None))
    out.append(("fp32", "ones", F1, F1, "C32B/C32A reference", "tools/claims-v3/kinds/tiles/fp32/ones.bin"))
    out.append(("fp32", "e182_a1_b3fffffff", F1, 0x3FFFFFFF, "C32B reference", "tools/claims-v3/e182/tiles/fp32/e182_a1_b3fffffff.bin"))
    for w in (0x3F8000FF, 0x3F80FFFF):
        out.append(("fp32", f"m12_a1_b{w:08x}", F1, w, "C32B", None))
        out.append(("fp32", f"m12_a{w:08x}_b1", w, F1, "C32A", None))
    for w in (0x3F80000F, 0x3FF80000):  # four low and four high mantissa bits, popcount 11 each (REFIT.md.dated-note-1.md)
        out.append(("fp32", f"m12_a1_b{w:08x}", F1, w, "CEQ", None))
        out.append(("fp32", f"m12_a{w:08x}_b1", w, F1, "CEQ", None))
    out.append(("fp16", "m12_a3c00_b3fff", h16w(H1), h16w(0x3FFF), "C16", None))
    out.append(("fp16", "m12_a3fff_b3c00", h16w(0x3FFF), h16w(H1), "C16", None))
    return out


TRAINS = [  # (id, first, second, set, what)
    ("Q3-swap", "int8.m12_a1_b3", "int8.m12_a3_b1", "C8", "A and B swap at product 3: (1, 2) against (2, 1) bits a byte"),
    ("Q3-sign", "int8.m12_am1_bm3", "int8.m12_a1_b3", "C8", "the sign flip at product 3: (8, 7) against (1, 2) bits a byte"),
    ("Q63-swap", "int8.m12_a1_b63", "int8.m12_a63_b1", "C8", "A and B swap at product 63: (1, 6) against (6, 1)"),
    ("Q63-sign", "int8.m12_am1_bm63", "int8.m12_a1_b63", "C8", "the sign flip at product 63: (8, 3) against (1, 6)"),
    ("X8", "int8.m12_a1_b63", "int8.m12_a1_b3", "C8", "across products 63 and 3 at A = 1: the walk, the A/B switching and B's held bits"),
    ("B23-B15", "fp32.m12_a1_b3f80ffff", "fp32.m12_a1_b3f8000ff", "C32B", "B gains 8 held bits, A = 1.0"),
    ("B15-B7", "fp32.m12_a1_b3f8000ff", "fp32.ones", "C32B", "B gains 8 held bits from 1.0, A = 1.0"),
    ("A23-A15", "fp32.m12_a3f80ffff_b1", "fp32.m12_a3f8000ff_b1", "C32A", "A gains 8 held bits, B = 1.0"),
    ("A15-A7", "fp32.m12_a3f8000ff_b1", "fp32.ones", "C32A", "A gains 8 held bits from 1.0, B = 1.0"),
    ("S15", "fp32.m12_a1_b3f8000ff", "fp32.m12_a3f8000ff_b1", "C32S", "8 held bits moved from A to B (T5 moved 23)"),
    ("S23", "fp32.m12_a1_b3f80ffff", "fp32.m12_a3f80ffff_b1", "C32S", "16 held bits moved from A to B"),
    ("H16", "fp16.m12_a3c00_b3fff", "fp16.m12_a3fff_b3c00", "C16", "the fp16 swap: 20 held bits a 32-bit word moved from A to B"),
    ("EB", "fp32.m12_a1_b3ff80000", "fp32.m12_a1_b3f80000f", "CEQ", "B's four mantissa bits at the top against the bottom (popcount 11 each)"),
    ("EA", "fp32.m12_a3ff80000_b1", "fp32.m12_a3f80000f_b1", "CEQ", "the A-side mirror")]


def committed_tile_dirs(root):
    return [os.path.join(root, d) for d in ("tools/claims-v3/kinds/tiles", "tools/claims-v3/e178/tiles", "tools/claims-v3/e182/tiles")]


def stage(root, out_dir):
    rows, blobs = [], {}
    seen = {}
    for d in committed_tile_dirs(root):
        for t in ("int8", "fp32", "fp16"):
            dd = os.path.join(d, t)
            if os.path.isdir(dd):
                for f in sorted(os.listdir(dd)):
                    if f.endswith(".bin"):
                        seen.setdefault(hashlib.sha256(open(os.path.join(dd, f), "rb").read()).hexdigest(), os.path.relpath(os.path.join(dd, f), root))
    for t, name, aw, bw, st, src in kinds_rule():
        raw = struct.pack("<I", aw) * 256 + struct.pack("<I", bw) * 256
        h = hashlib.sha256(raw).hexdigest()
        if src is None:
            assert h not in seen, f"{t}.{name} repeats the bytes of committed {seen.get(h)}"
            tile = f"tools/claims-v3/m12/tiles/{t}/{name}.bin"
            blobs[tile] = raw
        else:
            assert open(os.path.join(root, src), "rb").read() == raw, f"{t}.{name}: the committed tile differs from its words"
            tile = src
        rows.append({"type": t, "name": name, "key": f"{t}.{name}", "a_word": f"0x{aw:08x}", "b_word": f"0x{bw:08x}",
                     "popcount_a_word": C.popcount(aw), "popcount_b_word": C.popcount(bw), "hamming_a_b_word": C.popcount(aw ^ bw),
                     "set": st, "tile": tile, "new": src is None, "sha256": h})
    if out_dir:
        for rel, raw in blobs.items():
            p = os.path.join(out_dir, os.path.relpath(rel, "tools/claims-v3/m12"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(raw)
        json.dump({"_what": "M12's candidate kinds (candidates_m12.py stage; REFIT.md section 5): one-number tiles, operand words only",
                   "n": len(rows), "kinds": rows}, open(os.path.join(out_dir, "kinds-m12.json"), "w"), indent=1)
    return rows, blobs


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def forecast(root):
    m = json.load(open(os.path.join(HERE, "m12.json")))
    kj = json.load(open(os.path.join(HERE, "kinds-m12.json")))["kinds"]
    counts = json.load(open(os.path.join(HERE, "bench", "counts-m12.json")))["rows"]
    e178c = C.load(root, "tools/claims-v3/e178/bench/counts-e178.json")["rows"]
    f182 = C.load(root, C.E182F)
    sc = C.load(root, f"{C.E182D}/scored.json")
    red = C.load(root, f"{C.E182D}/e182.json")
    K = sc["reported"]["kinds"]
    rate = {"int8": m["int8"]["mean_rate_per_s"],
            "fp32": statistics.median(K[k]["rate_per_s"] for k in K if k.startswith("fp32.")),
            "fp16": statistics.median(red["per_pass"][p]["fp16.randn"]["rate"] for p in red["per_pass"])}
    N = f182["N_launch"]
    sys.path.insert(0, os.path.join(root, "tools/claims-v3/e182"))
    sys.path.insert(0, os.path.join(root, C.M10D))
    import forecast_e182 as FE  # noqa: E402  (run_flips, launch_points and N_CALIB only)
    import fit_m10 as FM        # noqa: E402  (the feature chain only)
    import predict_m10 as PM    # noqa: E402
    m10 = PM.load_m10()
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    out = {"_what": "M12's candidate forecasts for a next one-number TensorFMA run (candidates_m12.py; REFIT.md section 5); a candidate for "
                    "the next registration, NOT registered", "label": "forecast, frozen; post hoc model; blind for a run only if a later "
                    "registration commits this file before its first datum", "card": "aifoundry3, s = 1, W over each format's zeros",
           "rates_per_s": rate, "rates_rule": "int8: the mean over E182's 20 int8 kinds; fp32: the median over E182's 4 fp32 kinds; fp16: the "
           "median of E182's fp16.randn anchor's per-pass rates", "N_launch": N,
           "train_noise": {"halfwidth_w": HW_TRAIN, "units": 32, "se_w": HW_TRAIN / C.t975(31)},
           "inputs_sha256": {p: C.sha(os.path.join(root, p)) for p in (
               "tools/claims-v3/m12/m12.json", "tools/claims-v3/m12/kinds-m12.json", "tools/claims-v3/m12/bench/counts-m12.json",
               "tools/claims-v3/e178/bench/counts-e178.json", C.E182F, f"{C.E182D}/scored.json", f"{C.E182D}/e182.json",
               f"{C.M10D}/m10.json", "tools/claims-v3/e178/flipmodel_e178.c", "rtl-sim/fma_toggle_v2/accum.c")},
           "checks": {}, "kinds": {}, "trains": {}}
    # the bench check: each format's zeros and the committed reference tiles against E178's committed counts
    bc = {}
    for key in ("int8.zeros", "fp32.zeros", "fp16.zeros", "fp32.ones"):
        bc[key] = {"equal": counts[key]["mean"] == e178c[key]["mean"], "vpu_nets_map": counts[key]["mean"]["vpu"]["nets_map"]}
    bc["check_mismatch_all_zero"] = all(p["check_mismatch"] == 0 for k in counts for p in counts[k]["points"])
    out["checks"]["bench"] = bc
    assert all(v["equal"] for k, v in bc.items() if k != "check_mismatch_all_zero") and bc["check_mismatch_all_zero"], bc
    b8, cov8 = m["int8"]["b"], m["int8"]["cov"]
    b1, cov1 = m["arm_1K"]["b"], m["arm_1K"]["cov"]
    bf, covf = m["float"]["b"], m["float"]["cov"]
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "flipmodel_e178")
        subprocess.run(["cc", "-O2", "-std=gnu11", f'-DACCUM_C="{os.path.join(root, "rtl-sim/fma_toggle_v2/accum.c")}"', "-o", exe,
                        os.path.join(root, "tools/claims-v3/e178/flipmodel_e178.c"), "-lm"], check=True)
        # the flip model's check: E182's committed flips for three of its kinds, reproduced
        fk = f182["kinds"]
        chk = {}
        for key in ("int8.ones", "int8.e182_a1_b15", "fp32.e178_v4"):
            t = key.split(".")[0]
            fl = FE.run_flips(exe, t, fk[key]["a_word"], fk[key]["b_word"], N[t])
            chk[key] = fl["launch_mean"] == fk[key]["flips_i"]["launch_mean"]
        out["checks"]["flip_model_reproduces_e182"] = chk
        assert all(chk.values()), chk
        for k in kj:
            t, key = k["type"], k["key"]
            fl = FE.run_flips(exe, t, k["a_word"], k["b_word"], N[t])
            lm = fl["launch_mean"]
            f = FM.chain_feats(counts[key], os.path.join(root, k["tile"]), t, zeros, zr)
            P = PM.d600(f, t, rate[t], "a3", m10, 1.0)
            row = {"type": t, "a_word": k["a_word"], "b_word": k["b_word"], "pc_a": k["popcount_a_word"], "pc_b": k["popcount_b_word"],
                   "set": k["set"], "tile": k["tile"], "new_tile": k["new"], "flips_launch_mean": lm, "P10_w": P}
            if t == "int8":
                r = C.int8_row(rate[t], lm, k["popcount_a_word"], k["popcount_b_word"])
                r1 = C.int8_row_1k(rate[t], lm, k["popcount_a_word"], k["popcount_b_word"])
                row["design_row"] = r
                row["M12_w"], row["M12_se_w"] = C.dot(r, b8), C.se_of(r, cov8)
                row["M12-1K_w"] = C.dot(r1, b1)
                row["_r1"] = r1
            else:
                r = C.float_row(k["popcount_a_word"], k["popcount_b_word"])
                row["design_row"] = r
                row["M12_w"], row["M12_se_w"] = P + C.dot(r, bf), C.se_of(r, covf)
            out["kinds"][key] = row
    se_T = out["train_noise"]["se_w"]
    for tid, a, b, st, what in TRAINS:
        A, B = out["kinds"][a], out["kinds"][b]
        dr = [x - y for x, y in zip(A["design_row"], B["design_row"])]
        if A["type"] == "int8":
            dM12, sM12 = C.dot(dr, b8), C.se_of(dr, cov8)
            d1 = [x - y for x, y in zip(A["_r1"], B["_r1"])]
            arms = {"M12-1K_w": C.dot(d1, b1)}
        else:
            dM12, sM12 = (A["P10_w"] - B["P10_w"]) + C.dot(dr, bf), C.se_of(dr, covf)
            arms = {"F16-NOHB_w (M10's difference alone)": A["P10_w"] - B["P10_w"]} if A["type"] == "fp16" else {}
        dM10 = A["P10_w"] - B["P10_w"]
        sig = math.sqrt(se_T ** 2 + sM12 ** 2)
        out["trains"][tid] = {
            "first": a, "second": b, "set": st, "what": what, "M12_w": dM12, "M12_se_w": sM12, "M10_w": dM10, **arms,
            "d_pc_a": A["pc_a"] - B["pc_a"], "d_pc_b": A["pc_b"] - B["pc_b"],
            "d_flips": {c: A["flips_launch_mean"][c] - B["flips_launch_mean"][c] for c in A["flips_launch_mean"]},
            "power_excludes_0_if_M12": norm_cdf((dM12 - HW_TRAIN) / sig) + norm_cdf((-dM12 - HW_TRAIN) / sig),
            "power_excludes_0_if_M10": norm_cdf((dM10 - HW_TRAIN) / se_T) + norm_cdf((-dM10 - HW_TRAIN) / se_T),
            "separation_M12_M10_in_se": abs(dM12 - dM10) / sig}
    for k in out["kinds"].values():
        k.pop("_r1", None)
    return out


def md(o):
    L = ["# M12's candidate kinds and frozen forecasts (candidates_m12.py; REFIT.md section 5)", "",
         "A candidate for the next one-number registration, **not registered**. aifoundry3, s = 1, W over each format's zeros; rates "
         + ", ".join(f"{t} {v:.6e} /s" for t, v in o["rates_per_s"].items()) + ". M12 is post hoc (fitted on E182); these forecasts become blind "
         "only if a registration commits them before its first datum.", "",
         f"Each train at E182's train noise: half-width {o['train_noise']['halfwidth_w']} W at {o['train_noise']['units']} units (se "
         f"{o['train_noise']['se_w']:.5f} W). Power = the chance the train's 95% interval excludes 0; separation = |M12 - M10| over the train's "
         "se combined with M12's.", "",
         "| train | first - second | M12, W (se) | M10, W | power if M12 | power if M10 | separation (se) |", "|---|---|---:|---:|---:|---:|---:|"]
    for tid, v in o["trains"].items():
        L.append(f"| {tid} | {v['first']} - {v['second']} | {v['M12_w']:+.4f} ({v['M12_se_w']:.4f}) | {v['M10_w']:+.4f} | "
                 f"{v['power_excludes_0_if_M12']:.2f} | {v['power_excludes_0_if_M10']:.2f} | {v['separation_M12_M10_in_se']:.1f} |")
    L += ["", "| kind | A word | B word | pc A / B | M12, W (se) | M10, W | new tile |", "|---|---|---|---|---:|---:|---|"]
    for key, v in o["kinds"].items():
        L.append(f"| {key} | {v['a_word']} | {v['b_word']} | {v['pc_a']} / {v['pc_b']} | {v['M12_w']:.4f} ({v['M12_se_w']:.4f}) | "
                 f"{v['P10_w']:.4f} | {'yes' if v['new_tile'] else 'committed'} |")
    L += ["", "Checks: " + json.dumps(o["checks"], sort_keys=True)]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("what", choices=("stage", "forecast", "check"))
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    if a.what == "stage":
        rows, blobs = stage(root, HERE)
        print(f"staged {len(rows)} kinds, {len(blobs)} new tiles")
        return 0
    if a.what == "forecast":
        o = forecast(root)
        open(os.path.join(HERE, "candidates-m12.json"), "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
        open(os.path.join(HERE, "candidates-m12.md"), "w").write(md(o))
        print(md(o))
        return 0
    rows, blobs = stage(root, None)
    ok = json.load(open(os.path.join(HERE, "kinds-m12.json")))["kinds"] == rows and all(
        open(os.path.join(root, p), "rb").read() == raw for p, raw in blobs.items())
    o = forecast(root)
    ok = ok and open(os.path.join(HERE, "candidates-m12.json")).read() == json.dumps(o, indent=1, sort_keys=True) + "\n" and \
        open(os.path.join(HERE, "candidates-m12.md")).read() == md(o)
    print("CHECK PASS" if ok else "CHECK FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
