#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q145(b) fix: the class-S lane's verifier's faults, re-run on the committed code and data (REGISTRATION.md.dated-note-2.md).

Every figure this file writes is POST HOC: term S's outputs (6f9ae408) and an independent verifier's readings of them were read
before it was written. It decides nothing. It imports term_s_v2.py (6f9ae408) and changes none of its code: `fit99` replaces only
term_s_v2's list of training steps (term_s_v2.list_steps, plus the E67 steps the census finds) and its FL3 slope lookup (term_s_v2.k_law,
plus E67's runs.csv), and then calls term_s_v2.run_fit, the registered fit, unchanged.

    python3 -B term_s_note2.py census                        # structure only: T_S on every committed tile of the seven price lists
    python3 -B term_s_note2.py fit99 --out <dir> --tmp <dir>  # the registered fit on the 99 steps of section 3.1, both footings
    python3 -B term_s_note2.py checks --out <dir>            # E1 resampled by run; S0's in-sample rows; M10's step error by list and
                                                             # A word; the structure classes with steps and whole tiles apart; the
                                                             # registered band on pool 8's class S; the rounding and range checks
    python3 -B term_s_note2.py compare --a <dir> --b <dir> [--a-scratch <dir> --b-scratch <dir>]
                                                             # two output directories file by file (a re-run against the committed one)

Standard library and numpy 1.26 (through term_s_v2). It writes only under --out and --tmp; `compare` prints file names relative to the
directories it is given and never a path.
SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse  # noqa: E402
import glob  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import term_s_v2 as TS  # noqa: E402  (the committed fit, 6f9ae408; nothing of it is edited)

DD, CV, TOP, M10D, B8 = TS.DD, TS.CV, TS.TOP, TS.M10D, TS.B8
QD = os.path.join(DD, "2026-11-06-q145b-m10-s")
load, fsha, REL, rms, mean = TS.load, TS.fsha, TS.REL, TS.rms, TS.mean
E67D = os.path.join(DD, "2026-10-27-e67-a-side-bit-prices")
HL_COUNTS = os.path.join(DD, "2026-11-01-q132-rtl-bench", "counts-hl.json")
LISTS_HL = (("E65", "2026-10-26-e65-bit-prices-hart-ladder", "hl", "hl.json"),
            ("E67", "2026-10-27-e67-a-side-bit-prices", "hl", "hl.json"),
            ("E70", "2026-10-27-e70-saturation-ladder", "hl", "hl.json"),
            ("E79", "2026-10-31-e79-fp16-int8-bit-prices", "hlp", "hlp.json"))
LISTS_FILE = (("E102", os.path.join(CV, "kinds", "e102"), "e102.json", None),
              ("E134", os.path.join(CV, "e134", "e134"), "e134-tiles.json", os.path.join(CV, "e134", "predictions-e134.json")),
              ("E147", os.path.join(CV, "e147", "e147"), "e147-tiles.json", os.path.join(CV, "e147", "predictions-e147.json")))
ORIG_LIST_STEPS, ORIG_K_LAW = TS.list_steps, TS.k_law
DRAWS_RUNS, SEEDS_RUNS = 10000, (146, 147, 148)


def stop(msg):
    raise SystemExit("NOTE 2 STOPPED: " + msg)


def ts_both(raw):
    """T_S under both float formats (a single bit can pass under at most one; a zero passes under both)"""
    return {fmt: s for fmt in ("fp32", "fp16") for s in [TS.t_s(raw, fmt)] if s is not None}


def key95():
    return {(s["run"], s["fmt"], s["item"]) for s in ORIG_LIST_STEPS()}


# ------------------------------------------------------------------ the census (structure only)
def census():
    in95 = key95()
    res = {"label": "structure only: T_S (term_s_v2.t_s) on the committed tile bytes of the seven lists; no model value, "
                    "prediction or error is read", "lists": {}, "single_B_bits": []}
    for run, ddir, sub, jn in LISTS_HL:
        d = os.path.join(DD, ddir)
        c = load(os.path.join(d, jn))["cards"]["aifoundry3"]
        items = c["items"]
        files = {}
        for pd in sorted(glob.glob(os.path.join(d, "aifoundry3", sub, "p*"))):
            p = os.path.basename(pd)[1:]
            if not p.isdigit():
                continue
            for f in glob.glob(os.path.join(pd, "tiles", f"*.b{p}.bin")):
                files.setdefault(os.path.basename(f)[: -len(f".b{p}.bin")], []).append(f)
        n_single, differing = 0, []
        for name, fl in sorted(files.items()):
            if len({fsha(f) for f in fl}) != 1:
                # a tile whose copies differ between passes (a kernel-generated random anchor): never a training step; it is read
                # only to show that no copy is a single B bit
                if any(not s.get("zero") for f in fl for s in ts_both(open(f, "rb").read()).values()):
                    stop(f"{run} {name}: the committed copies differ and one reads as a single B bit")
                differing.append(name)
                continue
            got = ts_both(open(fl[0], "rb").read())
            for fmt, s in got.items():
                if s.get("zero"):
                    continue
                n_single += 1
                it = items.get(name, {})
                zero = it.get("zero")
                if zero is None and run == "E65":
                    for fam in ("bits", "bits_pi"):
                        for k, v in c.get(fam, {}).items():
                            if ("bit_" if fam == "bits" else "bpi_") + k == name:
                                zero = v.get("zero")
                zrow = None
                if zero and zero in files:
                    zs = ts_both(open(files[zero][0], "rb").read()).get(fmt)
                    zrow = bool(zs and zs.get("zero") and zs["a_word"] == s["a_word"])
                step = it.get("d_p80") if it.get("d_p80") is not None else it.get("dW")
                rec = {"run": run, "item": name, "fmt": fmt, "bit": s["bit"], "one_base": s["one_base"], "a_word": f"{s['a_word']:08x}",
                       "zero": zero, "zero_passes_T_S_as_zero": zrow, "registered_step": step is not None or (run, fmt, name) in in95,
                       "in_the_95": (run, fmt, name) in in95, "passes_with_a_copy": len(fl)}
                rec["training_step_by_3_1"] = bool(rec["in_the_95"] or (zrow and rec["registered_step"]))
                res["single_B_bits"].append(rec)
        res["lists"][run] = {"tiles": len(files), "single_B_bits": n_single, "copies_differ_none_a_single_bit": differing}
    for run, d, jn, predf in LISTS_FILE:
        spec = load(os.path.join(d, jn))["tiles"]
        preg = load(predf)["items"] if predf else {}
        n_single = 0
        for name, t in sorted(spec.items()):
            p = os.path.join(d, t["file"]) if t.get("file") else None
            if not p or not os.path.exists(p):
                continue
            fmt0, item = name.split(".", 1)
            s = TS.t_s(open(p, "rb").read(), fmt0) if fmt0 in TS.ONE else None
            if not s or s.get("zero"):
                continue
            n_single += 1
            zero = (t.get("zero") or (preg.get(name) or {}).get("zero"))
            zrow = None
            if zero and zero in spec and spec[zero].get("file"):
                zs = TS.t_s(open(os.path.join(d, spec[zero]["file"]), "rb").read(), fmt0)
                zrow = bool(zs and zs.get("zero") and zs["a_word"] == s["a_word"])
            rec = {"run": run, "item": item, "fmt": fmt0, "bit": s["bit"], "one_base": s["one_base"], "a_word": f"{s['a_word']:08x}",
                   "zero": zero, "zero_passes_T_S_as_zero": zrow, "in_the_95": (run, fmt0, item) in in95}
            rec["training_step_by_3_1"] = rec["in_the_95"]
            res["single_B_bits"].append(rec)
        res["lists"][run] = {"tiles": len(spec), "single_B_bits": n_single}
    sb = res["single_B_bits"]
    res["summary"] = {"single_B_bits_found": len(sb), "in_the_95": sum(1 for r in sb if r["in_the_95"]),
                      "steps_by_3_1_not_in_the_95": [f"{r['run']}:{r['fmt']}.{r['item']}" for r in sb
                                                     if r["training_step_by_3_1"] and not r["in_the_95"]],
                      "single_bits_not_steps": [f"{r['run']}:{r['fmt']}.{r['item']} (zero {r['zero']}, zero passes {r['zero_passes_T_S_as_zero']})"
                                                for r in sb if not r["training_step_by_3_1"]],
                      "the_95_all_found": len({(r["run"], r["fmt"], r["item"]) for r in sb if r["in_the_95"]}) == len(key95())}
    return res


# ------------------------------------------------------------------ the 99 steps: term_s_v2's list plus the census's E67 steps
def e67_steps(cen):
    j = load(os.path.join(E67D, "hl.json"))
    c = j["cards"]["aifoundry3"]
    k = j["gates"]["aifoundry3"]["leak_W_per_C"]
    names = [r["item"] for r in cen["single_B_bits"] if r["run"] == "E67" and r["training_step_by_3_1"] and not r["in_the_95"]]
    out = []
    for name in names:
        it = c["items"][name]
        mg = c["ix"]["margins"].get(name)
        if mg is None or abs(mg["dW"] - it["d_p80"]) > 1e-12 or abs(mg["se"] - it["d_p80_se"]) > 1e-12:
            stop(f"E67 {name}: the grid's margin and the item's step disagree")
        out.append({"run": "E67", "card": "a3", "fmt": "fp32", "item": name, "zero": it["zero"], "dW": it["d_p80"], "dW_se": it["d_p80_se"],
                    "k_list": k, "rate": it["rate"], "passes": c["passes"], "tiles": ("hl", E67D, "p{}"), "counts": [HL_COUNTS],
                    "src": f"{REL(os.path.join(E67D, 'hl.json'))} cards.aifoundry3.items.{name}.d_p80"})
    return out


def patch(cen):
    extra = e67_steps(cen)

    def list_steps_99():
        return ORIG_LIST_STEPS() + [dict(x) for x in extra]

    def k_law_99(st):
        if st["run"] == "E67":
            csvp = os.path.join(E67D, "runs.csv")
            return TS.FLAW.k_session(os.path.join(TS.FLD, "footing-law.json"), TS.LAW_CARD[st["card"]], csvp), REL(csvp)
        return ORIG_K_LAW(st)
    TS.list_steps, TS.k_law = list_steps_99, k_law_99
    return [x["item"] for x in extra]


def fit99(out_dir, tmp):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tmp, exist_ok=True)
    cen = census()
    added = patch(cen)
    if sorted(added) != ["ix_b0", "ix_b16", "ix_b22", "ix_b8"]:
        stop(f"the census's E67 steps are {added}, not the four ix_b margins: write that up before any fit")
    summary = {"label": "POST HOC: the registered fit (term_s_v2.run_fit, unchanged) on the 99 steps REGISTRATION.md section 3.1 "
                        "defines, the 95 of term_s_v2 plus E67's four; written after the 95-step outputs and the verifier's reading",
               "added_steps": ["E67:fp32." + a for a in sorted(added)]}
    for footing, base in (("reg", None), ("law", os.path.join(QD, "m10-law.json"))):
        res, name = TS.run_fit(tmp, footing, base)
        com = load(os.path.join(QD, f"term-s-{footing}.json"))
        old = {(s["run"], s["item"]): s for s in com["steps"]}
        worst = 0.0
        for s in res["steps"]:
            o = old.get((s["run"], s["item"]))
            if o is None:
                continue
            for q in ("meas_w", "pred_w", "r_w"):
                worst = max(worst, abs(float(s[q]) - float(o[q])))
        n_common = sum(1 for s in res["steps"] if (s["run"], s["item"]) in old)
        if n_common != 95 or worst > 1e-12 or res["n_steps"] != 99:
            stop(f"{footing}: the 95 committed steps do not reproduce (common {n_common}, worst {worst}) or n is {res['n_steps']}")
        res["note2"] = dict(summary, footing=footing, committed_95_reproduce={"steps": n_common, "worst_abs_w": worst})
        fn = f"note2-term-s-{footing}-99.json"
        json.dump(res, open(os.path.join(out_dir, fn), "w"), indent=1, default=str)
        e = res["entry"]
        summary[footing] = {"file": fn, "n_steps": res["n_steps"], "best": e["best_form"], "enters": e["enters"],
                            "E1": {k: e["E1"][k] for k in ("d_rms_w", "lo95", "hi95", "holds")}, "E2": e["E2"],
                            "E3": {k: e["E3"][k] for k in ("d_rms_w", "lo95", "hi95", "holds", "rms_M10_heldout_w", "rms_M10S_w")},
                            "forms_all": {f: res["by_form"][f]["all"] for f in TS.FORMS},
                            "run_E67": {f: res["by_form"][f].get("run E67") for f in TS.FORMS},
                            "sigma_S_w": res["sigma_S_w"]}
        if footing == "reg":
            p8 = res["posthoc_pool8"]
            summary[footing]["posthoc_pool8"] = {r: (p8[r]["class_S_N1"] if r in ("E171", "E172") else p8[r]["class_S_scored"])
                                                 for r in ("E171", "E172", "E173", "E174")}
            for r in ("E173", "E174"):
                summary[footing]["posthoc_pool8"][r] = {k: v for k, v in summary[footing]["posthoc_pool8"][r].items() if k != "tiles"}
            summary[footing]["B1"] = {r: {"F1": p8[r]["F1_B1"], "F1_without_S": p8[r]["F1_without_S"]} for r in ("E171", "E172")}
        else:
            p8 = res["posthoc_pool8"]
            summary[footing]["posthoc_pool8_law"] = {r: p8[r]["class_S_N1"] for r in ("E171", "E172")}
    json.dump({"census": cen, "fit99": summary}, open(os.path.join(out_dir, "note2-census-fit99.json"), "w"), indent=1, default=str)
    print(json.dumps({"census": cen["summary"], "fit99": {k: v for k, v in summary.items() if k in ("reg", "law")}}, indent=1, default=str))
    return 0


# ------------------------------------------------------------------ the checks
def e1_by_runs(steps, best):
    """E1's paired difference resampled by run (a run = one list: its session, base words and reduction), with a jackknife"""
    runs = sorted({s["run"] for s in steps})
    by = {R: [s for s in steps if s["run"] == R] for R in runs}

    def d_of(sel):
        return rms([s["heldout_w"][best] for s in sel]) - rms([s["heldout_w"]["S0"] for s in sel])
    out = {"n_steps": len(steps), "runs": {R: len(by[R]) for R in runs}, "best": best, "d_rms_w": d_of(steps), "by_seed": {}}
    for seed in SEEDS_RUNS:
        rng = random.Random(seed)
        ds = []
        for _ in range(DRAWS_RUNS):
            pick = [runs[rng.randrange(len(runs))] for _ in runs]
            ds.append(d_of([s for R in pick for s in by[R]]))
        ds.sort()
        out["by_seed"][str(seed)] = {"draws": DRAWS_RUNS, "lo95": ds[int(0.025 * DRAWS_RUNS)], "hi95": ds[int(0.975 * DRAWS_RUNS) - 1],
                                     "frac_at_or_above_0": sum(1 for x in ds if x >= 0) / DRAWS_RUNS}
    jk = {R: d_of([s for s in steps if s["run"] != R]) for R in runs}
    m = sum(jk.values()) / len(jk)
    out["jackknife"] = {"drop_one_run_d_rms_w": jk, "se_w": math.sqrt((len(runs) - 1) / len(runs) * sum((x - m) ** 2 for x in jk.values()))}
    out["by_run_d_rms_w"] = {R: d_of(by[R]) for R in runs}
    keys = list(range(len(steps)))
    rng = random.Random(TS.SEED_STEPS)
    ds = []
    for _ in range(TS.NB):
        pick = [keys[rng.randrange(len(keys))] for _ in keys]
        ds.append(d_of([steps[i] for i in pick]))
    ds.sort()
    out["step_bootstrap_as_registered"] = {"draws": TS.NB, "seed": TS.SEED_STEPS, "lo95": ds[int(0.025 * TS.NB)], "hi95": ds[int(0.975 * TS.NB) - 1],
                                           "note": "the registered draws (term_s_v2.paired_boot: the same seed, the same picks over the steps in their committed order)"}
    return out


def s0_in_sample(reg):
    """S0 ('M10 as frozen') on the steps whose rows M10 was fitted on: E147's 15 and E102's steps with item and zero rows"""
    rows = {(r["exp"], r["key"]): r for r in load(os.path.join(M10D, "rows-m10.json"))}
    out = {}
    for run in ("E147", "E102"):
        lane, ins, held, n = [], [], [], 0
        for s in reg["steps"]:
            if s["run"] != run:
                continue
            ki, kz = (rows.get((run, f"{s['fmt']}.{s['item']}")), rows.get((run, f"{s['fmt']}.{s['zero']}")))
            if run == "E147":
                if ki is None:
                    continue
                ins.append(ki["D"] - ki["M10_insample_pred_w"])
                held.append(ki["err_w"]["B+a+b"])
            else:
                if ki is None or kz is None:
                    continue
                ins.append((ki["D"] - ki["M10_insample_pred_w"]) - (kz["D"] - kz["M10_insample_pred_w"]))
                held.append(ki["err_w"]["B+a+b"] - kz["err_w"]["B+a+b"])
            lane.append(s["r_w"])
            n += 1
        out[run] = {"steps_with_M10_rows": n, "steps_in_the_list": sum(1 for s in reg["steps"] if s["run"] == run),
                    "lane_S0": {"rms_w": rms(lane), "bias_w": mean(lane)},
                    "M10_in_sample_step_residual": {"rms_w": rms(ins), "bias_w": mean(ins)},
                    "M10_held_out_step_error": {"rms_w": rms(held), "bias_w": mean(held)},
                    "optimism_rms_w": rms(held) - rms(ins)}
    return out


def by_list_and_a(steps):
    g = {}
    for s in steps:
        g.setdefault(f"{s['run']} {s['fmt']} A {s['a_word']}", []).append(s["r_w"])
    out = {k: {"n": len(v), "bias_w": mean(v), "rms_w": rms(v)} for k, v in sorted(g.items())}
    ga = {}
    for s in steps:
        ga.setdefault(f"{s['fmt']} A {s['a_word']}", []).append(s["r_w"])
    shared = {}
    for s in steps:
        if s["fmt"] == "fp32" and s["card"] == "a3" and s["bit"] in (0, 8, 16, 22):
            shared.setdefault(str(s["bit"]), []).append({"run": s["run"], "item": s["item"], "a_word": s["a_word"], "meas_w": s["meas_w"],
                                                         "pred_w": s["pred_w"], "r_w": s["r_w"]})
    return {"label": "POST HOC: S0's residual (measured step - M10's frozen step) by list and A word", "by_list_and_A": out,
            "by_A": {k: {"n": len(v), "bias_w": mean(v), "rms_w": rms(v)} for k, v in sorted(ga.items())},
            "fp32_bits_0_8_16_22_aifoundry3": shared}


def structure():
    ps = load(os.path.join(QD, "posthoc-structure.json"))["classes"]
    out = {"label": "POST HOC: M10's committed held-out errors (rows-m10.json, err_w B+a+b) in the five classes of posthoc-structure.json, "
                    "with E147's rows (steps, each over its own zero) apart from whole tiles (D over the format's zeros)",
           "classes": {}, "float_rows": sum(v["n_rows"] for v in ps.values())}
    for c, v in ps.items():
        out["classes"][c] = {"n_rows": v["n_rows"], "bias_w": v["bias_w"], "rms_w": v["rms_w"], "by_card": v["by_card"]}
    rows8 = ps["single B bit, eight base words"]["rows"]
    steps = [r for r in rows8 if r["exp"] == "E147"]
    whole = [r for r in rows8 if r["exp"] != "E147"]
    out["eight_word_single_bits_split"] = {
        "steps_E147": {"n": len(steps), "bias_w": mean([r["e_w"] for r in steps]), "rms_w": rms([r["e_w"] for r in steps])},
        "whole_tiles": {"n": len(whole), "bias_w": mean([r["e_w"] for r in whole]), "rms_w": rms([r["e_w"] for r in whole]),
                        "rows": [f"{r['exp']} {r['card']} {r['key']}" for r in whole],
                        "by_card": {cd: {"n": len([r for r in whole if r["card"] == cd]), "bias_w": mean([r["e_w"] for r in whole if r["card"] == cd])}
                                    for cd in ("a3", "c1")}}}
    z1 = ps["zero, one word in every lane"]["rows"]
    b1 = ps["single B bit, one base word"]["rows"]
    z8 = ps["zero, eight lane words"]["rows"]

    def mb(v, cd=None):
        v = [r["e_w"] for r in v if cd is None or r["card"] == cd]
        return {"n": len(v), "bias_w": mean(v)} if v else {"n": 0, "bias_w": None}
    comp = {}
    for cd in (None, "a3", "c1"):
        lab = cd or "both cards"
        one = {"zeros": mb(z1, cd), "single_bits": mb(b1, cd)}
        eight = {"zeros": mb(z8, cd), "single_bits_whole_tiles": mb(whole, cd)}
        one["bit_minus_zeros_w"] = (one["single_bits"]["bias_w"] - one["zeros"]["bias_w"]) if one["zeros"]["n"] and one["single_bits"]["n"] else None
        eight["bit_minus_zeros_w"] = ((eight["single_bits_whole_tiles"]["bias_w"] - eight["zeros"]["bias_w"])
                                      if eight["zeros"]["n"] and eight["single_bits_whole_tiles"]["n"] else None)
        comp[lab] = {"one word in every lane": one, "eight lane words": eight}
    out["whole_tile_comparison"] = comp
    out["E147_steps_for_comparison_w"] = out["eight_word_single_bits_split"]["steps_E147"]["bias_w"]
    return out


def band_pool8(reg):
    """the band REGISTRATION.md section 4 registers, k_M10 sqrt(pool^2 + sigma_S^2 + s^2 x'Cx), computed post hoc for pool 8's
    class-S N1 tiles at 600 MHz: the scorer's M10 band half-width h (M10_primary_95) and h_S = sqrt(h^2 + (k_M10 sigma_S)^2)"""
    m10 = load(os.path.join(M10D, "m10.json"))["families"]["float"]
    k = m10["band_k"]
    sig = reg["sigma_S_w"]
    out = {"label": "POST HOC: the registered band for a T_S tile, never computed by the lane; pool 8 measured", "band_k": k,
           "sigma_S_w": sig, "runs": {}}
    for run, ddir, card in (("E171", "2026-11-05-e171-blind8-aifoundry3", "aifoundry3"), ("E172", "2026-11-05-e172-blind8-card1", "aifoundry1c1")):
        rows = load(os.path.join(DD, ddir, "scored.json"))["primary"]["rows"]
        n1 = set(load(os.path.join(B8, f"predictions-pool8-{card}.json"))["sets"]["N1"])
        tl = reg["posthoc_pool8"][run]["tiles"]
        tiles = {}
        for t, v in sorted(tl.items()):
            if v.get("case") != "S" or t not in n1:
                continue
            r = rows[t]
            lo, hi = r["M10_primary_95"]
            h = (hi - lo) / 2.0
            hs = math.sqrt(h * h + (k * sig[v["type"]]) ** 2)
            e, es = v["e_m10_w"], v["e_m10s_w"]
            if abs(e - r["e_primary"]) > 1e-9:
                stop(f"{run} {t}: e_m10 does not reproduce the scorer's e_primary")
            tiles[t] = {"type": v["type"], "t_s_bit": v["t_s_bit"], "e_m10_w": e, "h_m10_w": h, "inside_m10": abs(e) <= h,
                        "scorer_inside_power": r.get("inside_power"), "term_w": v["term_w"], "e_m10s_w": es, "h_s_w": hs,
                        "inside_m10s_band_s": abs(es) <= hs, "inside_m10_band_s": abs(e) <= hs}
        ins = [x for x in tiles.values()]
        out["runs"][run] = {"n": len(ins), "M10_inside_its_band": sum(x["inside_m10"] for x in ins),
                            "scorer_inside_power": sum(bool(x["scorer_inside_power"]) for x in ins),
                            "M10_plus_S_inside_band_S": sum(x["inside_m10s_band_s"] for x in ins),
                            "M10_inside_band_S": sum(x["inside_m10_band_s"] for x in ins),
                            "h_m10_w_range": [min(x["h_m10_w"] for x in ins), max(x["h_m10_w"] for x in ins)],
                            "h_s_w_range": [min(x["h_s_w"] for x in ins), max(x["h_s_w"] for x in ins)], "tiles": tiles}
    return out


def rounding(reg):
    p8 = load(os.path.join(QD, "p8-law.json"))
    out = {"P8_M1_law": {r: {k: p8[r]["law"]["P8-M1"].get(k) for k in ("d_rms", "lo95", "hi95", "verdict")} for r in ("E171", "E172")}}
    ex = [s for s in reg["steps"] if s["fmt"] == "fp32" and s["bit"] in (28, 29, 30)]
    out["fp32_bits_28_30"] = {"steps": [[s["run"], s["item"], s["bit"], round(s["pred_w"], 4), round(s["meas_w"], 4)] for s in ex],
                              "pred_w_range": [min(s["pred_w"] for s in ex), max(s["pred_w"] for s in ex)],
                              "meas_w_range": [min(s["meas_w"] for s in ex), max(s["meas_w"] for s in ex)]}
    b0 = [s for s in reg["steps"] if s["fmt"] == "fp32" and s["bit"] == 0]
    out["fp32_bit_0"] = [[s["run"], s["item"], s["a_word"], round(s["pred_w"], 4), round(s["meas_w"], 4)] for s in b0]
    ag = reg["agreement"]
    spans = [max(x["meas_w"] for x in v) - min(x["meas_w"] for x in v) for v in ag.values()]
    pairs = [abs(a["meas_w"] - b["meas_w"]) for v in ag.values() for i, a in enumerate(v) for b in v[i + 1:]]
    out["agreement"] = {"positions": len(ag), "median_span_w": statistics.median(spans), "median_pair_abs_diff_w": statistics.median(pairs),
                        "n_pairs": len(pairs)}
    return out


def checks(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    reg = load(os.path.join(QD, "term-s-reg.json"))
    law = load(os.path.join(QD, "term-s-law.json"))
    res = {"label": "POST HOC (after term S's outputs and the verifier's reading): the checks of REGISTRATION.md.dated-note-2.md",
           "E1_by_runs": {"reg_95": e1_by_runs(reg["steps"], reg["entry"]["best_form"]),
                          "law_95": e1_by_runs(law["steps"], law["entry"]["best_form"])}}
    p99 = os.path.join(out_dir, "note2-term-s-reg-99.json")
    if os.path.exists(p99):
        r99 = load(p99)
        res["E1_by_runs"]["reg_99"] = e1_by_runs(r99["steps"], r99["entry"]["best_form"])
        res["by_list_and_A_99"] = by_list_and_a(r99["steps"])
    l99 = os.path.join(out_dir, "note2-term-s-law-99.json")
    if os.path.exists(l99):
        q = load(l99)
        res["E1_by_runs"]["law_99"] = e1_by_runs(q["steps"], q["entry"]["best_form"])
    res["S0_in_sample"] = s0_in_sample(reg)
    res["structure"] = structure()
    res["band_pool8"] = band_pool8(reg)
    res["rounding"] = rounding(reg)
    json.dump(res, open(os.path.join(out_dir, "note2-checks.json"), "w"), indent=1, default=str)
    brief = {"E1_by_runs": {k: {"d_rms_w": v["d_rms_w"], "by_seed": v["by_seed"], "jackknife_se_w": v["jackknife"]["se_w"],
                                "by_run_d_rms_w": v["by_run_d_rms_w"], "step_bootstrap_as_registered": v["step_bootstrap_as_registered"]}
                            for k, v in res["E1_by_runs"].items()},
             "S0_in_sample": res["S0_in_sample"], "by_A": res.get("by_list_and_A_99", {}).get("by_A"),
             "by_list_and_A": res.get("by_list_and_A_99", {}).get("by_list_and_A"),
             "structure": {k: v for k, v in res["structure"].items() if k != "label"},
             "band_pool8": {r: {k: v for k, v in x.items() if k != "tiles"} for r, x in res["band_pool8"]["runs"].items()},
             "rounding": res["rounding"]}
    print(json.dumps(brief, indent=1, default=str))
    return 0


# ------------------------------------------------------------------ compare two output directories (a re-run against the committed)
def _strip(x, key="dirs"):
    if isinstance(x, dict):
        return {k: _strip(v, key) for k, v in x.items() if k != key}
    if isinstance(x, list):
        return [_strip(v, key) for v in x]
    return x


def compare(a, b, a_scr=None, b_scr=None):
    names = sorted({os.path.basename(p) for p in glob.glob(os.path.join(a, "*")) if os.path.isfile(p)}
                   & {os.path.basename(p) for p in glob.glob(os.path.join(b, "*")) if os.path.isfile(p)})
    out = {"files": {}}
    for n in names:
        ha, hb = fsha(os.path.join(a, n)), fsha(os.path.join(b, n))
        out["files"][n] = {"identical": ha == hb, "sha256_a": ha, "sha256_b": hb}
    if "law-k.json" in names and not out["files"]["law-k.json"]["identical"]:
        ka, kb = load(os.path.join(a, "law-k.json")), load(os.path.join(b, "law-k.json"))
        diff = {}
        for s in sorted(set(ka) | set(kb)):
            va, vb = ka.get(s), kb.get(s)
            if va == vb:
                continue
            keys = sorted(k for k in set(va or {}) | set(vb or {}) if (va or {}).get(k) != (vb or {}).get(k))
            diff[s] = {"keys": keys}
            if a_scr and b_scr and keys == ["law_sha256"]:
                fa = os.path.join(a_scr, "law", va["law_reduction"])
                fb = os.path.join(b_scr, "law", vb["law_reduction"])
                if os.path.exists(fa) and os.path.exists(fb):
                    ja, jb = load(fa), load(fb)
                    diff[s].update({"a_file_hash_is_a_law_sha256": fsha(fa) == va["law_sha256"],
                                    "b_file_hash_is_b_law_sha256": fsha(fb) == vb["law_sha256"],
                                    "identical_apart_from_dirs": _strip(ja) == _strip(jb),
                                    "dirs_name_each_run_s_own_scratch": (json.dumps(ja.get("dirs", "")).count(os.path.abspath(a_scr)) > 0
                                                                         and json.dumps(jb.get("dirs", "")).count(os.path.abspath(b_scr)) > 0)})
        out["law-k.json differences"] = diff
        same = {s for s in set(ka) & set(kb) if ka[s] == kb[s]}
        out["law-k.json sessions identical"] = len(same)
    if a_scr and b_scr:
        la = {os.path.basename(p) for p in glob.glob(os.path.join(a_scr, "law", "*.json"))}
        lb = {os.path.basename(p) for p in glob.glob(os.path.join(b_scr, "law", "*.json"))}
        same_bytes, same_content, differ = 0, 0, []
        for n in sorted(la & lb):
            fa, fb = os.path.join(a_scr, "law", n), os.path.join(b_scr, "law", n)
            if fsha(fa) == fsha(fb):
                same_bytes += 1
            elif _strip(load(fa)) == _strip(load(fb)):
                same_content += 1
            else:
                differ.append(n)
        out["law reductions"] = {"in_both": len(la & lb), "byte_identical": same_bytes, "identical_apart_from_dirs": same_content,
                                 "differ": differ}
    print(json.dumps({k: v for k, v in out.items() if k != "files"} | {"files": {n: v["identical"] for n, v in out["files"].items()}}, indent=1))
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["census", "fit99", "checks", "compare"])
    ap.add_argument("--out")
    ap.add_argument("--tmp")
    ap.add_argument("--a")
    ap.add_argument("--b")
    ap.add_argument("--a-scratch")
    ap.add_argument("--b-scratch")
    a = ap.parse_args(argv)
    if a.cmd == "census":
        c = census()
        print(json.dumps(c["summary"] | {"lists": c["lists"]}, indent=1))
        return 0 if c["summary"]["the_95_all_found"] else 1
    if a.cmd == "fit99":
        return fit99(a.out, a.tmp)
    if a.cmd == "checks":
        return checks(a.out)
    return compare(a.a, a.b, a.a_scratch, a.b_scratch)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
