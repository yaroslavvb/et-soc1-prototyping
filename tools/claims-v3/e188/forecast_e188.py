#!/usr/bin/env python3
"""E188 (Q165, registration): the kinds and trains of the third candidate list's seven-train set and its same-session kinds pass, their
tiles, and the lab's own models' lines for them (M12 as frozen, M10 frozen), computed before any E188 datum.

    /usr/bin/python3 -B tools/claims-v3/e188/forecast_e188.py --root . stage      # kinds-e188.json and tiles/ (new tiles only)
    (bench/bench_e188.sh runs the toggle bench on the mini -> bench/counts-e188.json)
    /usr/bin/python3 -B tools/claims-v3/e188/forecast_e188.py --root . forecast   # forecast-e188.json and forecast-e188.txt
    /usr/bin/python3 -B tools/claims-v3/e188/forecast_e188.py --root . check      # recomputes both stages in memory and compares bytes

M12 is used exactly as committed (tools/claims-v3/m12/m12.json, no refit; m12_common and candidates_m12 imported unchanged): a float
held-word kind is Df = P10 + c_f + gamma_A pc_A + gamma_B pc_B (REFIT.md section 2), so a train's M12 line is M10's (P10's difference)
plus gamma_A dpc_A + gamma_B dpc_B. M10 is M10 frozen (docs/reports/data/2026-11-04-q142m-m10: fit_m10.chain_feats and predict_m10.d600,
unchanged) on the toggle bench's counts of each kind's tile. The rate is candidates-m12.json's fp32 rate (E182's median measured fp32
rate), s = 1, aifoundry3; at scoring the session's s and measured rates enter by lines_at() (E188.md section 5.1).
Needs numpy (M10's chain). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import struct
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
M12D = os.path.join(HERE, "..", "m12")
sys.path.insert(0, M12D)
import m12_common as C  # noqa: E402  (unchanged)
import candidates_m12 as CM  # noqa: E402  (unchanged: HW_TRAIN, norm_cdf)

F1 = 0x3F800000
TILES_NEW = "tools/claims-v3/e188/tiles"
COMMITTED_TILE_DIRS = ["tools/claims-v3/kinds/tiles", "tools/claims-v3/e178/tiles", "tools/claims-v3/e182/tiles", "tools/claims-v3/m12/tiles",
                       "tools/claims-v3/m12/tiles-e186"]
HL_TILES = {  # the two committed multi-word or non-one-number tiles of the kinds pass, at their committed paths, under their own labels
    "fp32.lq_h0": "docs/reports/data/2026-10-20-bitflip-ladder/aifoundry3/hl/p1/tiles/lq_h0.b1.bin",
    "fp32.aq_h0": "docs/reports/data/2026-10-27-e67-a-side-bit-prices/aifoundry3/hl/p750/tiles/aq_h0.b750.bin"}

# THE SET (E188.md section 2): id, first (A word, B word), second (A word, B word); a train reads D(first) - D(second)
TRAINS = [
    ("AALL", (0x3FFFFFFF, F1), (F1, F1), "A gains all 23 mantissa bits (0x3fffffff), B 1.0 in both: one half of E182's T5"),
    ("B04", (F1, 0x3F800010), (F1, F1), "B one held mantissa bit, bit 4; A 1.0 in both"),
    ("B05", (F1, 0x3F800020), (F1, F1), "B one held mantissa bit, bit 5; A 1.0 in both"),
    ("B10", (F1, 0x3F800400), (F1, F1), "B one held mantissa bit, bit 10; A 1.0 in both"),
    ("B19", (F1, 0x3F880000), (F1, F1), "B one held mantissa bit, bit 19; A 1.0 in both"),
    ("B22", (F1, 0x3FC00000), (F1, F1), "B one held mantissa bit, bit 22; A 1.0 in both"),
    ("PAIR", (F1, 0x3F800C00), (F1, 0x3F804400), "B two held mantissa bits, adjacent (10, 11) against spaced (10, 14); A 1.0 in both; "
                                                 "equal popcounts")]
B_ONE_BIT = ("B04", "B05", "B10", "B19", "B22")
# THE KINDS PASS (E188.md section 3): fp32 kinds read as levels above 1.0 x 1.0 in the session's own kinds passes; the tie (the host's
# built-in pi) is in every pass by E78's form and is no tile
KP_ONE_NUMBER = [("1.0 x 1.0", F1, F1), ("4.0 x 4.0", 0x40800000, 0x40800000), ("5.0 x 5.0", 0x40A00000, 0x40A00000),
                 ("pi x pi (tile)", 0x40490FDB, 0x40490FDB), ("BALL (1.0, 0x3fffffff)", F1, 0x3FFFFFFF), ("AALL (0x3fffffff, 1.0)", 0x3FFFFFFF, F1)]
KP_HL = [("lq_h0", "fp32.lq_h0"), ("aq_h0", "fp32.aq_h0")]
# the bench's reference rows, re-run and checked point for point against their committed counts
REF_ROWS = [("fp32.zeros", "tools/claims-v3/kinds/tiles/fp32/zeros.bin", "tools/claims-v3/e178/bench/counts-e178.json"),
            ("fp32.ones", None, "tools/claims-v3/e178/bench/counts-e178.json"),
            ("fp32.e178_v4", None, "tools/claims-v3/e178/bench/counts-e178.json"),
            ("fp32.e182_a3fffffff_b1", None, "tools/claims-v3/e182/bench/counts-e182.json"),
            ("fp32.e182_a1_b3fffffff", None, "tools/claims-v3/m12/bench/counts-m12-e186.json"),
            ("fp32.e186_a1_b3fc00000", None, "tools/claims-v3/m12/bench/counts-m12-e186.json")]
COMMITTED_COUNTS = ["tools/claims-v3/e178/bench/counts-e178.json", "tools/claims-v3/e182/bench/counts-e182.json",
                    "tools/claims-v3/m12/bench/counts-m12.json", "tools/claims-v3/m12/bench/counts-m12-e186.json"]


def tile_bytes(aw, bw):
    return struct.pack("<I", aw) * 256 + struct.pack("<I", bw) * 256


def committed_tiles(root):
    seen = {}
    for d in COMMITTED_TILE_DIRS:
        dd = os.path.join(root, d, "fp32")
        if os.path.isdir(dd):
            for f in sorted(os.listdir(dd)):
                if f.endswith(".bin"):
                    p = os.path.join(dd, f)
                    seen.setdefault(hashlib.sha256(open(p, "rb").read()).hexdigest(), ("fp32." + f[:-4], os.path.relpath(p, root)))
    return seen


def all_committed_bins(root):
    """every committed 2,048-byte tile under tools/claims-v3 and docs/reports/data, by sha256 (the no-twin check of a new tile)"""
    h = set()
    for top in ("tools/claims-v3", "docs/reports/data"):
        for dp, _, fs in os.walk(os.path.join(root, top)):
            if "/e188/" in dp + "/":
                continue
            for f in fs:
                if f.endswith(".bin"):
                    p = os.path.join(dp, f)
                    if os.path.getsize(p) == 2048:
                        h.add(hashlib.sha256(open(p, "rb").read()).hexdigest())
    return h


def kind_of(seen, aw, bw, label_hint):
    raw = tile_bytes(aw, bw)
    sh = hashlib.sha256(raw).hexdigest()
    if sh in seen:
        key, tile = seen[sh]
        return {"key": key, "tile": tile, "sha256": sh, "new_tile": False, "tile_from": "committed tile, its own label"}, None
    f = (lambda w: "1" if w == F1 else f"{w:08x}")  # noqa: E731
    key = f"fp32.e188_a{f(aw)}_b{f(bw)}"
    tile = f"{TILES_NEW}/fp32/e188_a{f(aw)}_b{f(bw)}.bin"
    return {"key": key, "tile": tile, "sha256": sh, "new_tile": True, "tile_from": "new tile (this registration)"}, raw


def props(aw, bw):
    mm = 0x7FFFFF
    return {"a_word": f"0x{aw:08x}", "b_word": f"0x{bw:08x}", "popcount_a_word": C.popcount(aw), "popcount_b_word": C.popcount(bw),
            "mantissa_bits_a": [i for i in range(23) if (aw >> i) & 1 and (mm >> i) & 1],
            "mantissa_bits_b": [i for i in range(23) if (bw >> i) & 1 and (mm >> i) & 1]}


# ------------------------------------------------------------------ stage: the kinds, the trains, the tiles, the bench rows
def stage(root, write):
    seen = committed_tiles(root)
    kinds, blobs = {}, {}

    def add(aw, bw, role):
        k, raw = kind_of(seen, aw, bw, None)
        if k["key"] not in kinds:
            kinds[k["key"]] = {**k, "type": "fp32", **props(aw, bw), "roles": []}
            if raw is not None:
                blobs[k["tile"]] = raw
        kinds[k["key"]]["roles"].append(role)
        return k["key"]
    trains = []
    for tid, (fa, fb), (sa, sb), what in TRAINS:
        a = add(fa, fb, f"train {tid} first")
        b = add(sa, sb, f"train {tid} second")
        trains.append({"train": tid, "first": a, "second": b, "what": what})
    kp = []
    for name, aw, bw in KP_ONE_NUMBER:
        kp.append({"name": name, "key": add(aw, bw, f"kinds pass: {name}")})
    for name, key in KP_HL:
        p = HL_TILES[key]
        raw = open(os.path.join(root, p), "rb").read()
        pa, pb, na, nb = C.tile_popcounts(raw)
        aw = struct.unpack("<256I", raw[:1024])
        bw = struct.unpack("<256I", raw[1024:])
        kinds[key] = {"key": key, "tile": p, "sha256": hashlib.sha256(raw).hexdigest(), "new_tile": False,
                      "tile_from": "committed tile, its own label", "type": "fp32", "a_words": sorted({f"0x{w:08x}" for w in aw}),
                      "b_words": sorted({f"0x{w:08x}" for w in bw}), "popcount_a_mean": pa, "popcount_b_mean": pb, "distinct_a": na,
                      "distinct_b": nb, "roles": [f"kinds pass: {name}"]}
        kp.append({"name": name, "key": key})
    ref = os.path.join(root, "tools/claims-v3/kinds/tiles/fp32/zeros.bin")
    kinds_zero = {"key": "fp32.zeros", "tile": os.path.relpath(ref, root)}
    # the no-twin check: a new tile repeats no committed tile's bytes anywhere in the repository
    if blobs:
        allh = all_committed_bins(root)
        for p, raw in blobs.items():
            assert hashlib.sha256(raw).hexdigest() not in allh, ("twin", p)
    committed_rows = {}
    for f in COMMITTED_COUNTS:
        for k in C.load(root, f)["rows"]:
            committed_rows.setdefault(k, f)
    bench_rows = []
    for key, tile, src in REF_ROWS:
        t = tile if tile else kinds[key]["tile"]
        bench_rows.append({"key": key, "tile": t, "role": f"reference (checked against {src})", "check_against": src})
    for key, k in sorted(kinds.items()):
        if key not in committed_rows:
            bench_rows.append({"key": key, "tile": k["tile"], "role": "kind (no committed counts)", "check_against": None})
    out = {"_what": "E188's kinds and trains (forecast_e188.py stage): the third candidate list's seven-train set as A B B A trains and the "
                    "same-session kinds pass's eight kinds; operand words, tiles and the toggle bench's rows only",
           "trains": trains, "kinds_pass": kp, "kinds": kinds, "zeros": kinds_zero,
           "counts_source": {k: committed_rows.get(k, "tools/claims-v3/e188/bench/counts-e188.json") for k in sorted(kinds)},
           "bench_rows": bench_rows}
    if write:
        for rel, raw in blobs.items():
            p = os.path.join(root, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(raw)
        open(os.path.join(HERE, "kinds-e188.json"), "w").write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    return out, blobs


# ------------------------------------------------------------------ forecast: M12's and M10's lines
def lines_at(row, s, rate_ratio):
    """a train's lines at the session's float scale s and its measured rate over the candidates' rate (E188.md section 5.1): M10's line
    (P10's difference) takes s and the rate ratio; M12's line is that plus its float increment, which takes neither"""
    m10 = row["M10_w"] * s * rate_ratio
    return {"M10_w": m10, "M12_w": m10 + row["M12_increment_w"], "M12_se_w": row["M12_se_w"]}


def forecast(root):
    kl = json.load(open(os.path.join(HERE, "kinds-e188.json")))
    cj = json.load(open(os.path.join(M12D, "candidates-m12.json")))
    ce = json.load(open(os.path.join(M12D, "candidates-m12-e186.json")))
    m = json.load(open(os.path.join(M12D, "m12.json")))
    cnew = json.load(open(os.path.join(HERE, "bench", "counts-e188.json")))["rows"]
    rows_c = {}
    for f in COMMITTED_COUNTS:
        for k, v in C.load(root, f)["rows"].items():
            rows_c.setdefault(k, v)
    rate = cj["rates_per_s"]["fp32"]
    sys.path.insert(0, os.path.join(root, C.M10D))
    import fit_m10 as FM        # noqa: E402  (the feature chain only, unchanged)
    import predict_m10 as PM    # noqa: E402  (unchanged)
    m10 = PM.load_m10()
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    bf, covf = m["float"]["b"], m["float"]["cov"]
    se_reg = CM.HW_TRAIN / C.t975(31)
    tr182 = C.load(root, f"{C.E182D}/trains-e182.json")["trains"]
    se_meas = sum(tr182[t]["estimate"]["se"] for t in C.TRAINS32) / len(C.TRAINS32)
    df_meas = 37
    out = {"_what": "E188's lines (forecast_e188.py): M12 as committed (no refit) and M10 frozen, for the seven trains, the kinds pass's "
                    "eight kinds and the fallback's fifteen kinds; frozen by E188's registration before any E188 datum",
           "label": "forecast, frozen; M12 a post hoc model (fitted on E182), M10 frozen; blind for E188 (no E188 datum exists)",
           "card": "aifoundry3 card 0, 600 MHz, s = 1, W over fp32 zeros (kinds) or first minus second (trains)",
           "rate_fp32_per_s": rate, "rate_rule": "candidates-m12.json's fp32 rate (E182's median measured fp32 rate), unchanged",
           "train_noise": {"registered": {"halfwidth_w": CM.HW_TRAIN, "units": 38, "se_w": se_reg,
                                          "rule": "E182's sizing rule: 76 fp32 processes (38 units) at the registered sigma_q 0.03804 W"},
                           "measured": {"se_w": se_meas, "df": df_meas, "halfwidth_w": se_meas * C.t975(df_meas),
                                        "rule": "E182's fp32 trains T5 and T6, the mean of their se (as E186)"}},
           "m12": {"file": "tools/claims-v3/m12/m12.json", "sha256": C.sha(os.path.join(M12D, "m12.json")), "float_b": bf,
                   "float_names": m["float"]["names"]},
           "inputs_sha256": {p: C.sha(os.path.join(root, p)) for p in (
               "tools/claims-v3/m12/m12.json", "tools/claims-v3/m12/candidates-m12.json", "tools/claims-v3/m12/candidates-m12-e186.json",
               "tools/claims-v3/m12/m12_common.py", "tools/claims-v3/m12/candidates_m12.py", "tools/claims-v3/e188/kinds-e188.json",
               "tools/claims-v3/e188/bench/counts-e188.json", *COMMITTED_COUNTS, f"{C.M10D}/m10.json", f"{C.M10D}/fit_m10.py",
               f"{C.M10D}/predict_m10.py", f"{C.E182D}/trains-e182.json")},
           "checks": {}, "kinds": {}, "trains": {}, "kinds_pass": {}, "fallback_kinds": []}
    # the bench's reference rows equal their committed counts point for point
    bc = {}
    for b in kl["bench_rows"]:
        if b["check_against"]:
            ref = C.load(root, b["check_against"])["rows"][b["key"]]
            bc[b["key"]] = {"against": b["check_against"], "mean_equal": cnew[b["key"]]["mean"] == ref["mean"],
                            "points_equal": cnew[b["key"]]["points"] == ref["points"]}
    bc["check_mismatch_all_zero"] = all(p["check_mismatch"] == 0 for k in cnew for p in cnew[k]["points"])
    out["checks"]["bench"] = bc
    assert bc["check_mismatch_all_zero"] and all(v["mean_equal"] and v["points_equal"] for k, v in bc.items() if k != "check_mismatch_all_zero"), bc

    def counts_of(key):
        return cnew[key] if key in cnew else rows_c[key]
    for key, k in sorted(kl["kinds"].items()):
        raw = open(os.path.join(root, k["tile"]), "rb").read()
        pa, pb, na, nb = C.tile_popcounts(raw)
        f = FM.chain_feats(counts_of(key), os.path.join(root, k["tile"]), "fp32", zeros, zr)
        P = PM.d600(f, "fp32", rate, "a3", m10, 1.0)
        d = C.float_row(pa, pb)
        out["kinds"][key] = {"tile": k["tile"], "a_word": k.get("a_word") or k["a_words"], "b_word": k.get("b_word") or k["b_words"],
                             "pc_a": pa, "pc_b": pb, "P10_w": P, "M10_w": P, "M12_w": P + C.dot(d, bf), "M12_se_w": C.se_of(d, covf),
                             "design_row": d, "counts_from": "tools/claims-v3/e188/bench/counts-e188.json" if key in cnew else
                             [f for f in COMMITTED_COUNTS if key in C.load(root, f)["rows"]][0]}
    # checks against E186's frozen file: every kind it holds keeps its P10 to the last bit; E188's AALL is its R4
    ek = ce["kinds"]
    same = {key: ek[key]["P10_w"] == v["P10_w"] and ek[key]["M12_w"] == v["M12_w"] for key, v in out["kinds"].items() if key in ek}
    out["checks"]["e186_kinds_reproduced"] = {"equal": sum(same.values()), "of": len(same), "keys": sorted(same)}
    assert all(same.values()), same
    for x in kl["trains"]:
        A, B = out["kinds"][x["first"]], out["kinds"][x["second"]]
        dr = [p - q for p, q in zip(A["design_row"], B["design_row"])]
        dM10 = A["P10_w"] - B["P10_w"]
        inc, sM12 = C.dot(dr, bf), C.se_of(dr, covf)
        dM12 = dM10 + inc
        sig_r = math.sqrt(se_reg ** 2 + sM12 ** 2)
        sig_m = math.sqrt(se_meas ** 2 + sM12 ** 2)
        hw_m = se_meas * C.t975(df_meas)
        out["trains"][x["train"]] = {
            "first": x["first"], "second": x["second"], "what": x["what"], "first_words": [A["a_word"], A["b_word"]],
            "second_words": [B["a_word"], B["b_word"]], "d_pc_a": A["pc_a"] - B["pc_a"], "d_pc_b": A["pc_b"] - B["pc_b"],
            "M10_w": dM10, "M12_w": dM12, "M12_increment_w": inc, "M12_se_w": sM12,
            "registered_noise": {"se_w": se_reg, "halfwidth_w": CM.HW_TRAIN,
                                 "power_excludes_0_if_M12": CM.norm_cdf((dM12 - CM.HW_TRAIN) / sig_r) + CM.norm_cdf((-dM12 - CM.HW_TRAIN) / sig_r),
                                 "power_excludes_0_if_M10": CM.norm_cdf((dM10 - CM.HW_TRAIN) / se_reg) + CM.norm_cdf((-dM10 - CM.HW_TRAIN) / se_reg),
                                 "separation_M12_M10_in_se": abs(dM12 - dM10) / sig_r},
            "measured_noise": {"se_w": se_meas, "halfwidth_w": hw_m,
                               "power_excludes_0_if_M12": CM.norm_cdf((dM12 - hw_m) / sig_m) + CM.norm_cdf((-dM12 - hw_m) / sig_m),
                               "power_excludes_0_if_M10": CM.norm_cdf((dM10 - hw_m) / se_meas) + CM.norm_cdf((-dM10 - hw_m) / se_meas),
                               "separation_M12_M10_in_se": abs(dM12 - dM10) / sig_m}}
    r4 = ce["trains"]["R4"]
    t = out["trains"]["AALL"]
    out["checks"]["aall_is_e186_r4"] = {"M12_w": t["M12_w"] == r4["M12_w"], "M12_se_w": t["M12_se_w"] == r4["M12_se_w"],
                                        "M10_w": t["M10_w"] == r4["M10_w"], "first": r4["first"] == t["first"], "second": r4["second"] == t["second"]}
    assert all(out["checks"]["aall_is_e186_r4"].values()), out["checks"]["aall_is_e186_r4"]
    # the derived lines: one held B mantissa bit (each one-bit B train less its M10 line), A's 23 bits, the position spread
    g = {n: v for n, v in zip(m["float"]["names"], bf)}
    out["derived"] = {
        "gamma_B_w": g["gamma_B_w"], "gamma_B_se_w": m["float"]["params"]["gamma_B_w"]["se"],
        "gamma_A_w": g["gamma_A_w"], "gamma_A_se_w": m["float"]["params"]["gamma_A_w"]["se"],
        "M12_one_bit_B_increment_w": {tid: out["trains"][tid]["M12_increment_w"] for tid in B_ONE_BIT},
        "M12_position_spread_w": 0.0, "M10_held_bit_w": 0.0,
        "note": "M12 prices a held fp32 mantissa bit at one price a side, whatever its position or partner: each one-bit B train's M12 line "
                "less its M10 line is gamma_B, and PAIR's M12 line equals its M10 line (equal popcounts)"}
    # the kinds pass: each kind's level above 1.0 x 1.0, and the fallback's fifteen kinds (levels over zeros)
    ones = out["kinds"]["fp32.ones"]
    for x in kl["kinds_pass"]:
        v = out["kinds"][x["key"]]
        dr = [p - q for p, q in zip(v["design_row"], ones["design_row"])]
        out["kinds_pass"][x["name"]] = {"key": x["key"], "M10_w": v["P10_w"] - ones["P10_w"], "M12_w": v["M12_w"] - ones["M12_w"],
                                        "M12_se_w": C.se_of(dr, covf), "level_M10_w": v["P10_w"], "level_M12_w": v["M12_w"],
                                        "level_M12_se_w": v["M12_se_w"]}
    out["kinds_pass"]["pi x pi (the tie, built-in)"] = {"key": "anchor_pi (the host's built-in --values pi, 0x40490fdb both sides)",
                                                         "M10_w": out["kinds_pass"]["pi x pi (tile)"]["M10_w"],
                                                         "M12_w": out["kinds_pass"]["pi x pi (tile)"]["M12_w"],
                                                         "M12_se_w": out["kinds_pass"]["pi x pi (tile)"]["M12_se_w"],
                                                         "note": "the same words as the pi x pi tile, so the same lines (the models see words, not the "
                                                                 "launch path)"}
    out["fallback_kinds"] = sorted(out["kinds"])
    return out


def txt(o, kl):
    L = ["E188's lines (forecast_e188.py), frozen by E188's registration before any E188 datum. M12 as committed (m12.json, no refit; a post hoc",
         "model, fitted on E182), M10 frozen. aifoundry3, s = 1, fp32 rate %.6e /s (candidates-m12.json's). W." % o["rate_fp32_per_s"], "",
         "Train noise: registered half-width %.4f W at 38 units (se %.5f); measured (E182's fp32 trains) se %.5f, half-width %.4f." % (
             o["train_noise"]["registered"]["halfwidth_w"], o["train_noise"]["registered"]["se_w"], o["train_noise"]["measured"]["se_w"],
             o["train_noise"]["measured"]["halfwidth_w"]), "",
         "THE SEVEN TRAINS (first - second)", "%-5s %-24s %-24s %9s %9s %8s %9s %7s %7s" % (
             "train", "first (A, B)", "second (A, B)", "M12", "M12 se", "M10", "M12-M10", "sep reg", "sep mea")]
    for tid, v in o["trains"].items():
        L.append("%-5s %-24s %-24s %+9.5f %9.5f %+8.5f %+9.5f %7.1f %7.1f" % (
            tid, "(%s, %s)" % tuple(v["first_words"]), "(%s, %s)" % tuple(v["second_words"]), v["M12_w"], v["M12_se_w"], v["M10_w"],
            v["M12_increment_w"], v["registered_noise"]["separation_M12_M10_in_se"], v["measured_noise"]["separation_M12_M10_in_se"]))
    d = o["derived"]
    L += ["", "M12's held fp32 mantissa bit: gamma_B %+.5f (se %.5f), gamma_A %+.5f (se %.5f); one price a side at every position and beside "
          "every partner; M10: 0." % (d["gamma_B_w"], d["gamma_B_se_w"], d["gamma_A_w"], d["gamma_A_se_w"]), "",
          "THE KINDS PASS (levels above 1.0 x 1.0)", "%-30s %-34s %9s %9s %9s" % ("kind", "key", "M12", "M12 se", "M10")]
    for nm, v in o["kinds_pass"].items():
        L.append("%-30s %-34s %+9.5f %9.5f %+9.5f" % (nm, v["key"][:34], v["M12_w"], v["M12_se_w"], v["M10_w"]))
    L += ["", "EVERY KIND (levels above fp32 zeros; the fallback's fifteen)", "%-34s %9s %9s %9s %7s %7s" % ("key", "P10=M10", "M12", "M12 se", "pc A", "pc B")]
    for key, v in o["kinds"].items():
        L.append("%-34s %9.5f %9.5f %9.5f %7.3f %7.3f" % (key, v["P10_w"], v["M12_w"], v["M12_se_w"], v["pc_a"], v["pc_b"]))
    L += ["", "Checks: " + json.dumps(o["checks"], sort_keys=True)]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("what", choices=("stage", "forecast", "check"))
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    if a.what == "stage":
        out, blobs = stage(root, True)
        print(f"staged {len(out['kinds'])} kinds ({len(blobs)} new tiles), {len(out['trains'])} trains, {len(out['bench_rows'])} bench rows")
        return 0
    kl = json.load(open(os.path.join(HERE, "kinds-e188.json")))
    if a.what == "forecast":
        o = forecast(root)
        open(os.path.join(HERE, "forecast-e188.json"), "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
        open(os.path.join(HERE, "forecast-e188.txt"), "w").write(txt(o, kl))
        print(txt(o, kl))
        return 0
    out, blobs = stage(root, False)
    ok = open(os.path.join(HERE, "kinds-e188.json")).read() == json.dumps(out, indent=1, sort_keys=True) + "\n" and all(
        open(os.path.join(root, p), "rb").read() == raw for p, raw in blobs.items())
    o = forecast(root)
    ok = ok and open(os.path.join(HERE, "forecast-e188.json")).read() == json.dumps(o, indent=1, sort_keys=True) + "\n" and \
        open(os.path.join(HERE, "forecast-e188.txt")).read() == txt(o, kl)
    print("CHECK PASS" if ok else "CHECK FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
