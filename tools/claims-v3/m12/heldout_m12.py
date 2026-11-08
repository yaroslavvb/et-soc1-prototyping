#!/usr/bin/env python3
"""M12 (Q157): the held-out test (REFIT.md section 4), POST HOC: M12 as fitted in m12.json, never refitted here, against rows it never
read: E178's 40 committed kinds and his pair E178-H-int8, and pool 8's class S on aifoundry3 (E171) and, secondary, card 1 (E172).

    /usr/bin/python3 -B tools/claims-v3/m12/heldout_m12.py --root .            # writes heldout-m12.json and heldout-m12.md beside it
    /usr/bin/python3 -B tools/claims-v3/m12/heldout_m12.py --root . --check    # recomputes in memory, compares both files byte for byte
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m12_common as C  # noqa: E402


def interval(e, sd, n, se_pred):
    hw = math.sqrt((C.t975(n - 1) * sd / math.sqrt(n)) ** 2 + (1.96 * se_pred) ** 2) if n >= 2 else float("nan")
    return [e - hw, e + hw], hw


def mean_sd(xs):
    n = len(xs)
    m = sum(xs) / n
    return m, (math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else float("nan")), n


def build(root):
    here = os.path.join(root, "tools/claims-v3/m12")
    m = json.load(open(os.path.join(here, "m12.json")))
    s8 = C.load(root, f"{C.E178D}/scored.json")
    f8 = C.load(root, C.E178F)["kinds"]
    r8 = C.load(root, f"{C.E178D}/e178.json")
    K = s8["primary"]["reported"]["kinds"]
    b8, cov8 = m["int8"]["b"], m["int8"]["cov"]
    b1, cov1 = m["arm_1K"]["b"], m["arm_1K"]["cov"]
    bko, covko = m["arm_KO"]["b"], m["arm_KO"]["cov"]
    bf, covf = m["float"]["b"], m["float"]["cov"]
    bg, covg = m["arm_G"]["b"], m["arm_G"]["cov"]
    og = m["arm_M10_OG"]
    s1_shift = r8["items"]["int8.full"]["D"]["mean"] - m["arm_S1"]["D_int8_full_e182_w"]
    inputs = ["tools/claims-v3/m12/m12.json", f"{C.E178D}/scored.json", C.E178F, f"{C.E178D}/e178.json",
              f"{C.E171D}/scored.json", f"{C.E172D}/scored.json", f"{C.B8}/MANIFEST"]
    out = {"_what": "M12's held-out test (heldout_m12.py; REFIT.md section 4): residual e = measured D - model, W, aifoundry3 unless marked",
           "label": "held out, post hoc", "inputs_sha256": {p: C.sha(os.path.join(root, p)) for p in inputs},
           "arm_S1_shift_w": s1_shift, "rows": {}, "groups": {}, "gain_offset": {}}
    rows = out["rows"]
    # ---- E178's 40 kinds
    for k in sorted(K):
        t = k.split(".")[0]
        v, fk = K[k], f8[k]
        lm = fk["flips_i"]["launch_mean"]
        pa, pb = fk["popcount_a_word"], fk["popcount_b_word"]
        D, sd, n, P = v["D_w"], v["sd_w"], v["n"], v["P_w"]
        pred = {"M10": (P, 0.0)}
        if t == "int8":
            r = C.int8_row(v["rate_per_s"], lm, pa, pb)
            r1 = C.int8_row_1k(v["rate_per_s"], lm, pa, pb)
            pred["M12"] = (C.dot(r, b8), C.se_of(r, cov8))
            pred["M12-1K"] = (C.dot(r1, b1), C.se_of(r1, cov1))
            pred["M12-KO"] = (C.dot(r1, bko), C.se_of(r1, covko))
            pred["M12-S1"] = (pred["M12"][0] + s1_shift, pred["M12"][1])
            pred["M10-O"] = (P + og["int8"]["c_w"], 0.0)
            pred["M10-G"] = (og["int8"]["g"] * P, 0.0)
        else:
            r = C.float_row(pa, pb)
            pred["M12"] = (P + C.dot(r, bf), C.se_of(r, covf))
            rg = [P, pa, pb]
            pred["M12-G"] = (C.dot(rg, bg), C.se_of(rg, covg))
            if t == "fp16":
                pred["F16-NOHB"] = (P + bf[0], math.sqrt(covf[0][0]))
            pred["M10-O"] = (P + og["fp32"]["c_w"], 0.0)
            pred["M10-G"] = (og["fp32"]["g"] * P, 0.0)
        row = {"set": "E178", "type": t, "D_w": D, "sd_w": sd, "n": n, "P10_w": P, "a_word": fk["a_word"], "b_word": fk["b_word"],
               "pc_a": pa, "pc_b": pb, "models": {}}
        for mod, (p, se) in pred.items():
            e = D - p
            iv, hw = interval(e, sd, n, se)
            row["models"][mod] = {"pred_w": p, "se_pred_w": se, "e_w": e, "e95": iv, "zero_inside": iv[0] <= 0 <= iv[1]}
        rows[f"E178:{k}"] = row
    # his pair, E178-H-int8
    h = s8["primary"]["rules"]["E178-H-int8"]
    a, b = "int8.e178_v5", "int8.e178_v4"
    ra = C.int8_row(K[a]["rate_per_s"], f8[a]["flips_i"]["launch_mean"], f8[a]["popcount_a_word"], f8[a]["popcount_b_word"])
    rb = C.int8_row(K[b]["rate_per_s"], f8[b]["flips_i"]["launch_mean"], f8[b]["popcount_a_word"], f8[b]["popcount_b_word"])
    dr = [x - y for x, y in zip(ra, rb)]
    ra1 = C.int8_row_1k(K[a]["rate_per_s"], f8[a]["flips_i"]["launch_mean"], f8[a]["popcount_a_word"], f8[a]["popcount_b_word"])
    rb1 = C.int8_row_1k(K[b]["rate_per_s"], f8[b]["flips_i"]["launch_mean"], f8[b]["popcount_a_word"], f8[b]["popcount_b_word"])
    dr1 = [x - y for x, y in zip(ra1, rb1)]
    hp = {"measured_w": h["mean_w"], "measured95": [h["lo95_w"], h["hi95_w"]], "statistic": h["form"], "n_passes": h["n"],
          "M10_w": h["dP_w"], "M12_w": C.dot(dr, b8), "M12_se_w": C.se_of(dr, cov8), "M12-1K_w": C.dot(dr1, b1), "M12-KO_w": C.dot(dr1, bko)}
    hp["M12_inside_measured95"] = h["lo95_w"] <= hp["M12_w"] <= h["hi95_w"]
    hp["M10_inside_measured95"] = h["lo95_w"] <= hp["M10_w"] <= h["hi95_w"]
    out["his_pair_E178"] = hp
    # ---- pool 8's class S
    man = {}
    for ln in open(os.path.join(root, C.B8, "MANIFEST")):
        f = ln.split()
        if len(f) >= 3:
            man[f[2]] = (f[0], f[1])
    for exp, rel, card in (("E171", C.E171D, "a3"), ("E172", C.E172D, "c1")):
        sc = C.load(root, f"{rel}/scored.json")
        for k, v in sorted(sc["primary"]["rows"].items()):
            if v.get("case") != "S":
                continue
            h256, path = man[k]
            raw = open(os.path.join(root, C.B8, path), "rb").read()
            assert hashlib.sha256(raw).hexdigest() == h256, k
            pa, pb, na, nb = C.tile_popcounts(raw)
            D, sd, n = mean_sd(v["per_pass"])
            assert abs(D - v["D_w"]) < 1e-9, (k, D, v["D_w"])
            P = v["M10_primary_w"]
            kap = 1.0 if card == "a3" else C.CARD1_FLOAT
            r = C.float_row(pa, pb)
            pred = {"M10": (P, 0.0), "M12": (P + kap * C.dot(r, bf), kap * C.se_of(r, covf))}
            rg = [P, pa, pb]
            pred["M12-G"] = (P + kap * (C.dot(rg, bg) - P), kap * C.se_of(rg, covg))
            if v["type"] == "fp16":
                pred["F16-NOHB"] = (P + kap * bf[0], kap * math.sqrt(covf[0][0]))
            kind = "rerun" if v.get("rerun_of") else ("new p1" if v["priority"] == 1 else "new p2")
            row = {"set": f"{exp} class S", "card": card, "type": v["type"], "D_w": D, "sd_w": sd, "n": n, "P10_w": P, "pc_a": pa, "pc_b": pb,
                   "distinct_a_words": na, "distinct_b_words": nb, "kind": kind, "priority": v["priority"], "rerun_of": v.get("rerun_of"), "models": {}}
            for mod, (p, se) in pred.items():
                e = D - p
                iv, hw = interval(e, sd, n, se)
                row["models"][mod] = {"pred_w": p, "se_pred_w": se, "e_w": e, "e95": iv, "zero_inside": iv[0] <= 0 <= iv[1]}
            rows[f"{exp}:{k}"] = row
    # ---- groups
    def sel(pred):
        return sorted(r for r in rows if pred(rows[r]))
    groups = {
        "E178 int8 (13)": sel(lambda r: r["set"] == "E178" and r["type"] == "int8"),
        "E178 fp32 (14)": sel(lambda r: r["set"] == "E178" and r["type"] == "fp32"),
        "E178 fp16 (13)": sel(lambda r: r["set"] == "E178" and r["type"] == "fp16"),
        "E178 all (40)": sel(lambda r: r["set"] == "E178"),
        "E171 class S new (10)": sel(lambda r: r["set"] == "E171 class S" and r["kind"] != "rerun"),
        "E171 class S new, priority 1 (8)": sel(lambda r: r["set"] == "E171 class S" and r["kind"] == "new p1"),
        "E171 class S re-runs (3)": sel(lambda r: r["set"] == "E171 class S" and r["kind"] == "rerun"),
        "E172 class S new (10), card 1": sel(lambda r: r["set"] == "E172 class S" and r["kind"] != "rerun"),
        "E172 class S new, priority 1 (8), card 1": sel(lambda r: r["set"] == "E172 class S" and r["kind"] == "new p1"),
        "E172 class S re-runs (3), card 1": sel(lambda r: r["set"] == "E172 class S" and r["kind"] == "rerun")}
    for g, ks in groups.items():
        mods = sorted(set.intersection(*[set(rows[k]["models"]) for k in ks]))
        gg = {"rows": ks, "models": {}}
        for mod in mods:
            e = [rows[k]["models"][mod]["e_w"] for k in ks]
            st = C.group_stats(e)
            st["zero_inside"] = sum(1 for k in ks if rows[k]["models"][mod]["zero_inside"])
            if mod != "M10":
                st["vs_M10"] = C.boot_rms_diff(e, [rows[k]["models"]["M10"]["e_w"] for k in ks])
            gg["models"][mod] = st
        out["groups"][g] = gg
    # ---- gain against offset (E178, by format)
    for g, gk in (("E178 int8 (13)", ("M10-G", "M10-O")), ("E178 fp32 (14)", ("M10-G", "M10-O")), ("E178 fp16 (13)", ("M10-G", "M10-O"))):
        ks = groups[g]
        bt = C.boot_rms_diff([rows[k]["models"][gk[0]]["e_w"] for k in ks], [rows[k]["models"][gk[1]]["e_w"] for k in ks])
        bt["word"] = C.gain_offset_word(bt)
        out["gain_offset"][f"{g}: M10-G against M10-O"] = bt
    for g in ("E178 fp32 (14)", "E178 fp16 (13)"):
        ks = groups[g]
        bt = C.boot_rms_diff([rows[k]["models"]["M12-G"]["e_w"] for k in ks], [rows[k]["models"]["M12"]["e_w"] for k in ks])
        bt["word"] = C.gain_offset_word(bt)
        out["gain_offset"][f"{g}: M12-G against M12"] = bt
    return out


def md(o):
    L = ["# M12's held-out test, POST HOC (heldout_m12.py; REFIT.md section 4)", "",
         "Residual e = measured D - model (W over the format's zeros); 95% = the row's t interval over its passes combined with 1.96 x the "
         "model's se. M10 is its frozen predictor's scored P (E178: s = 1.00590; pool 8: M10's primary at the session's s). Never fitted on "
         "these rows; they were seen before the refit's rules were written (REFIT.md section 6).", ""]
    hp = o["his_pair_E178"]
    L.append(f"**His pair (E178-H-int8, int8 5s - 4s):** measured {hp['measured_w']:+.4f} W [{hp['measured95'][0]:+.4f}, {hp['measured95'][1]:+.4f}]; "
             f"M12 {hp['M12_w']:+.4f} (se {hp['M12_se_w']:.4f}, {'inside' if hp['M12_inside_measured95'] else 'outside'}); M10 {hp['M10_w']:+.4f} "
             f"({'inside' if hp['M10_inside_measured95'] else 'outside'}); M12-1K {hp['M12-1K_w']:+.4f}; M12-KO {hp['M12-KO_w']:+.4f}.")
    L.append("")
    L.append("## Groups")
    L.append("")
    L.append("| group | model | n | rms | bias | centred rms | 0 inside 95% | rms - M10's rms [95%] |")
    L.append("|---|---|---:|---:|---:|---:|---:|---|")
    for g, gg in o["groups"].items():
        for mod in ["M10", "M12"] + [x for x in gg["models"] if x not in ("M10", "M12")]:
            if mod not in gg["models"]:
                continue
            s = gg["models"][mod]
            d = s.get("vs_M10")
            ds = f"{d['diff']:+.4f} [{d['lo95']:+.4f}, {d['hi95']:+.4f}]" if d else ""
            L.append(f"| {g} | {mod} | {s['n']} | {s['rms']:.4f} | {s['bias']:+.4f} | {s['centred_rms']:.4f} | {s['zero_inside']} | {ds} |")
    L.append("")
    L.append("## Gain against offset (rms of the gain form minus the offset form's, E178's rows)")
    L.append("")
    for k, v in o["gain_offset"].items():
        L.append(f"- {k}: {v['diff']:+.5f} W [{v['lo95']:+.5f}, {v['hi95']:+.5f}]: **{v['word']}**")
    L.append("")
    L.append(f"Arm M12-S1's shift (E178's D(int8.full) - E182's): {o['arm_S1_shift_w']:+.4f} W.")
    L.append("")
    L.append("## Every row (M12 and M10; the arms are in heldout-m12.json)")
    L.append("")
    L.append("| row | D, W | M12, W | e (M12) [95%] | M10, W | e (M10) [95%] |")
    L.append("|---|---:|---:|---|---:|---|")
    for k, r in o["rows"].items():
        a, b = r["models"]["M12"], r["models"]["M10"]
        L.append(f"| {k} | {r['D_w']:.4f} | {a['pred_w']:.4f} | {a['e_w']:+.4f} [{a['e95'][0]:+.4f}, {a['e95'][1]:+.4f}] | {b['pred_w']:.4f} | "
                 f"{b['e_w']:+.4f} [{b['e95'][0]:+.4f}, {b['e95'][1]:+.4f}] |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    here = os.path.join(root, "tools/claims-v3/m12")
    o = build(root)
    js = json.dumps(o, indent=1, sort_keys=True) + "\n"
    tx = md(o)
    if a.check:
        ok = open(os.path.join(here, "heldout-m12.json")).read() == js and open(os.path.join(here, "heldout-m12.md")).read() == tx
        print("CHECK PASS" if ok else "CHECK FAIL")
        return 0 if ok else 1
    open(os.path.join(here, "heldout-m12.json"), "w").write(js)
    open(os.path.join(here, "heldout-m12.md"), "w").write(tx)
    print(tx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
