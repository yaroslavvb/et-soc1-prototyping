#!/usr/bin/env python3
"""Tests for reduce_dtf.py.

  python3 test_reduce_dtf.py [--e60-data <dir>] [--work <dir>]

1. The t machinery against the quantiles the plan publishes in §9.1-§9.2 (4.53 / 4.28 / 4.09 /
   5.51 / 9.22 at 8 / 9 / 10 / 6 / 4 passes, the Holm ladder 3.50 / 3.34 / 3.13 / 2.84 / 2.36 at
   8 passes, and "|t| = 3 is p = 0.0199 at 8 passes").
2. The per-run machinery on E60's OWN committed raw data: a small dtf-format manifest is built for
   the xin (and ain) items and reduce_dtf is run over aifoundry3's eight hl passes.  The xin slope
   must reproduce E60's 20.83 fJ board / 16.28 fJ rail to within 1%, and ain_h8's one-rung slope
   E60's 28.10 fJ.
3. A synthetic dtf campaign with planted per-flip energies, exercising every family, every gate and
   every §9 verdict row end to end, and checking that the planted coefficients come back.
"""
import argparse
import gzip
import json
import math
import os
import random
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_dtf as R                                     # noqa: E402

FAILS = []
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    if not ok:
        FAILS.append(name)
    print("  %-62s %s   %s" % (name, "PASS" if ok else "FAIL", detail))


def close(a, b, rel):
    return a is not None and b is not None and abs(a - b) <= rel * abs(b)


# =================================================================================================
# 1. the t machinery
# =================================================================================================
def test_t():
    print("\n[1] the t machinery against the plan's published quantiles")
    for npass, want in ((8, 4.53), (9, 4.28), (10, 4.09), (6, 5.51), (4, 9.22)):
        got = R.t_crit(R.THREE_SIGMA_P, npass - 1)
        check("3-sigma |t| at %d passes = %.2f" % (npass, want), close(got, want, 0.005),
              "got %.3f" % got)
    for k, want in ((5, 3.50), (4, 3.34), (3, 3.13), (2, 2.84), (1, 2.36)):
        got = R.t_crit(R.HOLM_ALPHA / k, 7)
        check("Holm alpha=0.05/%d at 8 passes = %.2f" % (k, want), close(got, want, 0.01),
              "got %.3f" % got)
    for npass, want in ((8, 0.0199), (9, 0.0171), (10, 0.0150), (4, 0.0577)):
        got = R.t_p_two(3.0, npass - 1)
        check("p(|t|>3) at %d passes = %.4f" % (npass, want), close(got, want, 0.02),
              "got %.5f" % got)


# =================================================================================================
# 2. the per-run machinery on E60's committed data
# =================================================================================================
def xin_manifest(path):
    """A dtf-format manifest for E60's xin/ain ladder items (counts re-derived from the plan's §4:
    8h flipping bits per port per 256-bit op, 16 changed source words, no result flips)."""
    items = [{"name": "anchor_pi", "family": "anchor", "kind": "fma", "op": None,
              "operands": "pi", "harts": 1, "shires": None, "ops_per_iter": None, "zero": None,
              "h": None, "L": None, "delta": None,
              "counts": {"vs1": 0, "vs2": 0, "result": 0, "cell": 0, "carry": 0, "addr": 0,
                         "src_words": 0, "res_words": 0},
              "zero_word": False, "dup": 2, "participants_expected": 1024, "pair": None}]
    for fam_op, pre, hh in (("fxor.pi", "xin", (0, 4, 8, 16, 24, 32)),
                            ("fand.pi", "ain", (0, 4, 8, 16, 24, 32))):
        for h in hh:
            items.append({
                "name": "%s_h%d" % (pre, h), "family": "X", "kind": "ec", "op": fam_op,
                "operands": "file", "harts": 1, "shires": None, "ops_per_iter": 64,
                "zero": None if h == 0 else "%s_h0" % pre, "h": h, "L": None, "delta": None,
                "counts": {"vs1": 8 * h, "vs2": 8 * h, "result": 0, "cell": 0, "carry": 0,
                           "addr": 5.25, "src_words": 16, "res_words": 0},
                # at h = 32 ain's x is the all-zero word (E60 amendment A1's excluded corner)
                "zero_word": bool(pre == "ain" and h == 32),
                "dup": 1, "participants_expected": 1024, "pair": None})
    json.dump({"seed": 1, "modes": {"fxor.pi": 179, "fand.pi": 177}, "items": items},
              open(path, "w"), indent=1)
    return path


def test_e60(data, work):
    print("\n[2] the per-run machinery on E60's committed raw data (aifoundry3, hl p1-p8)")
    dirs = sorted(os.path.join(data, "aifoundry3", "hl", "p%d" % i) for i in range(1, 9))
    dirs = [d for d in dirs if os.path.isdir(d)]
    if not dirs:
        check("E60 data present", False, "no pass dir under %s" % data)
        return None
    man = xin_manifest(os.path.join(work, "manifest-xin.json"))
    out = os.path.join(work, "xin.json")
    rc = R.main([*dirs, "--manifest", man, "--out", out, "--txt", os.path.join(work, "xin-reduce.txt"),
                 "--csv", os.path.join(work, "xin-runs.csv"), "--quiet"])
    check("reduce_dtf ran over E60's eight passes", rc == 0)
    res = json.load(open(out))
    C = (res.get("cards") or {}).get("aifoundry3") or {}
    g = C.get("gates") or {}
    print("    card: %s MHz, %.1f mV, passes %s, runs kept %s/%s, leak %.3f W/C (E60 0.203)"
          % (C.get("clock_mhz"), (C.get("v_mean") or 0) * 1000, C.get("passes"), g.get("kept"),
             g.get("runs"), C.get("leak_W_per_C") or 0))
    check("leak slope reproduces E60's 0.203 W/C", close(C.get("leak_W_per_C"), 0.203, 0.01),
          "got %.4f" % (C.get("leak_W_per_C") or 0))
    check("all eight passes survive (E60 set none aside)", C.get("n_passes") == 8,
          "passes %s, set aside %s" % (C.get("passes"), C.get("passes_set_aside")))
    check("the new ec rate gate fails no run on E60's data",
          not any("rate " in w for p, i, po, why in (g.get("failed") or []) for w in why),
          "%d gate failures in total" % len(g.get("failed") or []))
    tie = (C.get("derived") or {}).get("e_in_fxor_E60fit") or {}
    print("    e_in(fxor), E60's own ec fit  = %.3f +- %.3f fJ board, %.3f fJ rail, %d passes "
          "(E60: 20.83 +- 0.10 / 16.28)"
          % (tie.get("fJ") or float('nan'), tie.get("se_fJ") or 0, tie.get("rail_fJ") or float('nan'),
             tie.get("n_passes") or 0))
    check("xin slope reproduces E60's 20.83 fJ board within 1%", close(tie.get("fJ"), 20.83, 0.01),
          "got %s fJ" % R.fmt(tie.get("fJ"), 3))
    check("xin rail slope reproduces E60's 16.28 fJ within 1%", close(tie.get("rail_fJ"), 16.28, 0.01),
          "got %s fJ" % R.fmt(tie.get("rail_fJ"), 3))
    check("its SE reproduces E60's +-0.10 fJ", close(tie.get("se_fJ"), 0.10, 0.15),
          "got %s fJ" % R.fmt(tie.get("se_fJ"), 3))
    d = (C.get("derived") or {}).get("e_in_fxor") or {}
    print("    e_in(fxor), the plan's §8.4 fit = %.3f +- %.3f fJ, intercept %.4f W "
          "(the plan quotes 19.71 fJ and +0.273 W for this form)"
          % (d.get("fJ") or float('nan'), d.get("se_fJ") or 0,
             ((C.get("derived") or {}).get("intercept_X_W") or {}).get("value") or float('nan')))
    check("the §8.4 fit reproduces the 19.7 end of the registered e_in interval",
          close(d.get("fJ"), 19.78, 0.01), "got %s fJ" % R.fmt(d.get("fJ"), 3))
    check("the §8.4 intercept reproduces E60's +0.273 W within 2%",
          close(((C.get("derived") or {}).get("intercept_X_W") or {}).get("value"), 0.2692, 0.02),
          "got %s W" % R.fmt(((C.get("derived") or {}).get("intercept_X_W") or {}).get("value"), 4))
    da = (C.get("derived") or {}).get("e_in_fand") or {}
    print("    e_in(fand) from ain_h8 alone = %s fJ (E60: 28.10 +- 0.70)" % R.fmt(da.get("fJ"), 2))
    check("ain_h8 one-rung slope reproduces E60's 28.10 fJ within 3%",
          close(da.get("fJ"), 28.10, 0.03), "got %s fJ" % R.fmt(da.get("fJ"), 3))
    check("ain_h32 is excluded from the fand fit and reported as the zero-word corner",
          "ain_h32_zero_word_corner_W" in (C.get("derived") or {}),
          "corner dW %s W" % R.fmt(((C.get("derived") or {}).get("ain_h32_zero_word_corner_W") or {}).get("value"), 3))
    check("every derived quantity carries value + SE + rail + passes + family (§8.11)",
          all(all(k in v for k in ("value", "se", "rail_value", "n_passes", "family"))
              for v in (C.get("derived") or {}).values()),
          "%d derived quantities" % len(C.get("derived") or {}))
    check("the missing-data report names the families that did not run",
          any("family" in m and "never ran" in m for m in (res.get("missing") or [])),
          "%d notes" % len(res.get("missing") or []))
    # the plan's registered fit (nonzero rungs only, free intercept) against E60's own ec fit,
    # which forced the (0,0) point: the two must agree to well inside the 1% window
    return res


# =================================================================================================
# 3. a synthetic dtf campaign, end to end
# =================================================================================================
PLANT = {"e_in": 20.83e-15, "e_out": 30.5e-15, "e_cell": 1.4e-15, "e_carry": 1.7e-15,
         "e_addr": 0.8e-15, "w_word": 48.0e-15, "zero_word_fJ_per_op": -120e-15,
         "base_w": 31.0, "ipc": 0.5791, "clock_hz": 600e6, "harts": 1024, "mv": 522,
         "noise_w": 0.010}


def synth_manifest(path):
    items = []

    def add(name, family, op, counts, zero=None, h=None, L=None, delta=None, opi=64, dup=1,
            zero_word=False, pair=None, harts=1, shires=None, parts=1024, kind="ec", operands="file"):
        c = {"vs1": 0, "vs2": 0, "result": 0, "cell": 0, "carry": 0, "addr": 0,
             "src_words": 0, "res_words": 0}
        c.update(counts)
        items.append({"name": name, "family": family, "kind": kind, "op": op, "operands": operands,
                      "harts": harts, "shires": shires, "ops_per_iter": opi, "zero": zero, "h": h,
                      "L": L, "delta": delta, "counts": c, "zero_word": zero_word, "dup": dup,
                      "participants_expected": parts, "pair": pair})

    add("anchor_pi", "anchor", None, {}, kind="fma", operands="pi", dup=2, opi=None)
    # X
    for h in (0, 8, 16, 32):
        add("xin_h%d" % h, "X", "fxor.pi", {"vs1": 8 * h, "vs2": 8 * h, "addr": 5.25, "src_words": 16},
            zero=None if h == 0 else "xin_h0", h=h)
    for h in (0, 8, 32):
        add("ain_h%d" % h, "X", "fand.pi", {"vs1": 8 * h, "vs2": 8 * h, "addr": 5.25, "src_words": 16},
            zero=None if h == 0 else "ain_h0", h=h, zero_word=(h == 32))
    # N: d1n (a zero word) and d1nz (none), 8 changed source words, one port, one result
    for h in (0, 8, 16, 32):
        for pre, zw in (("d1n", True), ("d1nz", False)):
            add("%s_h%d" % (pre, h), "N", "fnot.pi",
                {"vs1": 8 * h, "result": 8 * h, "addr": 3.50, "src_words": 8, "res_words": 8},
                zero=None if h == 0 else "%s_h0" % pre, h=h, zero_word=zw)
    # V: the 16-op pair, cell bits only in 1b
    for h in (0, 16, 32):
        add("d1a_h%d" % h, "V", "fnot.pi",
            {"vs1": 8 * h, "result": 8 * h, "addr": 3.50, "src_words": 8, "res_words": 8},
            zero=None if h == 0 else "d1a_h0", h=h, opi=128, pair="d1b_h%d" % h,
            dup=2 if h == 32 else 1)
        add("d1b_h%d" % h, "V", "fnot.pi",
            {"vs1": 8 * h, "result": 8 * h, "cell": 8 * h, "addr": 3.375, "src_words": 8, "res_words": 8},
            zero="d1a_h0", h=h, opi=128, pair="d1a_h%d" % h, dup=2 if h == 32 else 1)
    # B: the 2x2
    for h in (0, 16, 32):
        for cell, op, res_flips, zw in (("d2A", "fand.pi", 0, True), ("d2B", "fand.pi", 8 * h, False),
                                        ("d2C", "for.pi", 0, False), ("d2D", "for.pi", 8 * h, True)):
            add("%s_h%d" % (cell, h), "B", op,
                {"vs1": 8 * h, "result": res_flips, "addr": 3.25, "src_words": 8,
                 "res_words": 8 if res_flips else 0},
                zero=None if h == 0 else "%s_h0" % cell, h=h, zero_word=zw,
                dup=2 if h == 32 else 1,
                pair=["%s_h%d" % (c2, h) for c2 in ("d2A", "d2B", "d2C", "d2D")
                      if c2 != cell] if h else None)
    # gate: fxor and fadd rungs of the matched ladder
    for pre, op in (("d2X", "fxor.pi"), ("d3z", "fadd.pi")):
        for h in (0, 32):
            add("%s_h%d" % (pre, h), "gate", op,
                {"vs1": 8 * h, "result": 8 * h, "addr": 3.25, "src_words": 8,
                 "res_words": 8 if h else 0},
                zero=None if h == 0 else "%s_h0" % pre, h=h, zero_word=True,
                pair="d2D_h%d" % h if h else None)
    # C: the carry ladder
    for L in (0, 2, 8, 16, 29):
        add("d3_L%d" % L, "C", "fadd.pi",
            {"vs1": 8, "result": 8 * (L + 1), "carry": 8 * L, "addr": 3.25, "src_words": 8,
             "res_words": 8},
            zero=None if L == 0 else "d3_L0", L=L, pair="d3p_L29" if L == 29 else None)
    add("d3p_L29", "C", "fadd.pi",
        {"vs1": 8, "result": 240, "carry": 232, "addr": 3.25, "src_words": 8, "res_words": 8},
        zero="d3_L0", L=29, zero_word=True, pair="d3_L29")
    # M: four k_adj levels at xin_h16's counts, plus the complement pair and the page-exact extra
    for nm, k, zw in (("m_phase0", 0.031, False), ("m_nib", 0.969, False), ("m_nib_c", 0.969, False),
                      ("m_pair", 1.469, False), ("m_byte", 1.719, False), ("m_solid_z", 0.0, True)):
        it = {"vs1": 128, "vs2": 128, "addr": 5.25, "src_words": 16}
        add(nm, "M", "fxor.pi", it, zero="xin_h0", h=16, zero_word=zw)
        items[-1]["k_adj"] = k
    # A: the address ladder, gated and live
    for dv in (0, 1, 3, 5):
        add("d5_a%d" % dv, "A", "fxor.pi", {"addr": 2 * dv + 1.75},
            zero=None if dv == 0 else "d5_a0", delta=dv, zero_word=True)
    for dv in (0, 3):
        add("d5n_a%d" % dv, "A", "fxor.pi", {"addr": 2 * dv + 1.75},
            zero=None if dv == 0 else "d5n_a0", delta=dv)
    # Z
    add("d6_zero", "Z", "fmadd.ps", {"addr": 7.0}, zero=None, zero_word=True)
    add("d6_one", "Z", "fmadd.ps", {"addr": 7.0}, zero="d6_zero")
    # R
    add("r_not_c1", "R", "fnot.pi", {}, zero=None)
    add("r_not_r1", "R", "fnot.pi", {"vs1": 95.556, "result": 95.556, "src_words": 8, "res_words": 8},
        zero="r_not_c1")
    add("r_and_c1", "R", "fand.pi", {}, zero=None)
    add("r_and_r1", "R", "fand.pi", {"vs1": 191.111, "vs2": 95.556, "result": 48.370,
                                     "src_words": 16, "res_words": 8}, zero="r_and_c1")
    add("r_and_c2", "R", "fand.pi", {}, zero=None, harts=2)
    add("r_and_r2", "R", "fand.pi", {"vs1": 191.111, "vs2": 95.556, "result": 48.370,
                                     "src_words": 16, "res_words": 8}, zero="r_and_c2", harts=2)
    json.dump({"seed": 1,
               "modes": {"df.c2.fand": 300, "df.c2.for": 301, "df.c2.fadd": 302, "df.c2.fxor": 303,
                         "df.un1a.fnot": 304, "df.un1b.fnot": 305, "df.addr.a0": 306,
                         "df.addr.a1": 307, "df.addr.a3": 308, "df.addr.a5": 309},
               "items": items}, open(path, "w"), indent=1)
    return path


def synth_cam_manifest(items):
    """family 7's four arms, appended to an existing manifest file's items"""
    out = []
    for side, mask in (("w", "0x3131733b"), ("e", "0xcece8cc4")):
        for lvl, res_flips, zw in (("hi", 256, False), ("lo", 0, True)):
            out.append({"name": "d7%s_%s" % (side, lvl), "family": "7", "kind": "ec",
                        "op": "df.c2.fand", "operands": "file", "harts": 1, "shires": mask,
                        "ops_per_iter": 64, "zero": None if lvl == "lo" else "d7%s_lo" % side,
                        "h": 32, "L": None, "delta": None,
                        "counts": {"vs1": 256, "vs2": 0, "result": res_flips, "cell": 0, "carry": 0,
                                   "addr": 3.25, "src_words": 8, "res_words": 8 if res_flips else 0},
                        "zero_word": zw, "dup": 1, "participants_expected": 512, "pair": None})
    return items + out


def synth_power(man, name, rng):
    """the planted truth: base + per-flip energies x the designed counts x the op rate"""
    it = man.items[name]
    c = it["counts"]
    parts = it.get("participants_expected") or 1024
    harts = it.get("harts") or 1
    rate = PLANT["ipc"] * PLANT["clock_hz"] * parts * harts          # instructions/s, whole card
    if it["kind"] == "fma":
        return PLANT["base_w"] + 7.0, rate / 64.0
    e = (PLANT["e_in"] * (c["vs1"] + c["vs2"]) + PLANT["e_out"] * c["result"]
         + PLANT["e_cell"] * c["cell"] + PLANT["e_carry"] * c["carry"]
         + PLANT["e_addr"] * c["addr"]
         + PLANT["w_word"] * (c["src_words"] + c["res_words"]))
    if it.get("zero_word"):
        e += PLANT["zero_word_fJ_per_op"]
    return PLANT["base_w"] + e * rate, rate


def write_pass(d, card, man, names, pnum, rng, target=58.0, mhz=600, mv=522, parts_of=None):
    os.makedirs(d, exist_ok=True)
    t = 1800000000000 + pnum * 600000
    tel, runs, marks = [], [], []
    order = list(names)
    rng.shuffle(order)
    order = ["anchor_pi"] + order + ["anchor_pi"] if "anchor_pi" in man.items else order
    for pos, name in enumerate(order):
        it = man.items[name]
        pw, rate = synth_power(man, name, rng)
        pw += rng.gauss(0, PLANT["noise_w"])
        t0 = t
        # 10 Hz telemetry for 5 s of run, the board reading flat inside the window
        for i in range(50):
            tt = t0 + i * 100
            tel.append({"t_ms": tt, "board_w": round(pw if i >= 8 else PLANT["base_w"], 4),
                        "sp": {"minion_w": [round(0.75 * (pw - 24.0), 4)]},
                        "die_mv": {"minion": mv}, "temp_c": {"minshire": [target]},
                        "mhz": {"minion": mhz}})
        nl = 10
        parts = (parts_of or {}).get(name) or it.get("participants_expected") or 1024
        cyc = 240000000
        ops = rate / (PLANT["ipc"] * PLANT["clock_hz"] * parts) * PLANT["ipc"] * cyc * parts
        for j in range(nl):
            r = {"card": card, "block": pnum, "pos": pos, "item": name, "kind": it["kind"],
                 "attempt": 1, "start_c": target, "start_hot_c": target + 1, "heats": 0,
                 "wait_s": 0.2, "pattern": it.get("op") or "none",
                 "operands": it.get("operands"), "harts": it.get("harts") or 1,
                 "participants": parts, "shire_mask_used": (it.get("shires") or "0xffffffff"),
                 "ops": ops, "cycles_max": cyc, "cycles_mean": cyc,
                 "ops_per_cycle_per_hart": ops / cyc / parts,
                 "t_start_ms": t0 + 800 + j * 400, "t_end_ms": t0 + 800 + (j + 1) * 400, "ok": True}
            if it["kind"] == "fma":
                r.update({"iters": 535297, "minions": 1024, "launch": j - 1,
                          "cycles_per_op": 546.0, "ops": None})
            runs.append(r)
        marks.append({"kind": "run", "item": name, "block": pnum, "t_start_ms": t0 + 800,
                      "t_end_ms": t0 + 800 + nl * 400, "pos": pos, "attempt": 1, "rc": 0,
                      "launches": nl, "start_c": target, "start_hot_c": target + 1, "heats": 0,
                      "wait_s": 0.2, "on_protocol": True})
        t = t0 + 6000
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as f:
        for s in tel:
            f.write(json.dumps(s) + "\n")
    with open(os.path.join(d, "runs.jsonl"), "w") as f:
        for r in runs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(d, "marks.jsonl"), "w") as f:
        for m in marks:
            f.write(json.dumps(m) + "\n")
    json.dump({"card": card, "args": {"target": target, "preheat": target + 1}},
              open(os.path.join(d, "configs.json"), "w"))
    json.dump({"exp": "dtf" if "cam" not in d else "dtf-cam", "pass": pnum, "card": card,
               "status": "ok"}, open(os.path.join(d, "block.json"), "w"))
    open(os.path.join(d, "run.log"), "w").write("synthetic pass %d\n" % pnum)


def test_synthetic(work):
    print("\n[3] a synthetic dtf campaign with planted energies, end to end")
    root = os.path.join(work, "synth")
    if os.path.isdir(root):
        shutil.rmtree(root)
    mpath = synth_manifest(os.path.join(work, "manifest-synth.json"))
    raw = json.load(open(mpath))
    raw["items"] = synth_cam_manifest(raw["items"])
    json.dump(raw, open(mpath, "w"), indent=1)
    man = R.Manifest(mpath)
    rng = random.Random(7)
    a3 = [n for n in man.items if man.family(n) not in ("R", "7")]
    dirs = []
    for p in range(1, 9):
        d = os.path.join(root, "aifoundry3", "dtf", "p%d" % p)
        write_pass(d, "aifoundry3", man, [n for n in a3 if n != "anchor_pi"], p, rng)
        dirs.append(d)
    a1 = [n for n in man.items if man.family(n) in ("R",)] + ["xin_h0", "xin_h32", "anchor_pi"]
    for p in range(1, 10):
        d = os.path.join(root, "aifoundry1-c0", "dtf", "p%d" % p)
        write_pass(d, "aifoundry1-c0", man, [n for n in a1 if n != "anchor_pi"], p, rng,
                   target=57.0, mhz=800, mv=604)
        dirs.append(d)
    for p in range(1, 5):
        d = os.path.join(root, "aifoundry2", "dtf-cam", "p%d" % p)
        write_pass(d, "aifoundry2", man, ["d7w_hi", "d7e_hi", "d7w_lo", "d7e_lo"], p, rng,
                   mhz=800, mv=617)
        dirs.append(d)
    out = os.path.join(work, "synth.json")
    rc = R.main([*dirs, "--manifest", mpath, "--out", out,
                 "--txt", os.path.join(work, "synth-reduce.txt"),
                 "--csv", os.path.join(work, "synth-runs.csv"), "--quiet"])
    check("reduce_dtf ran over the synthetic campaign", rc == 0)
    res = json.load(open(out))
    C = (res.get("cards") or {}).get("aifoundry3") or {}
    D = C.get("derived") or {}
    print("    recovered on aifoundry3 (planted in brackets):")
    # RECON 4: the registered e_carry estimator takes e_out(add) from d3z's own one-rung slope
    # through d3z_h0, and this campaign plants `w_word` on (src_words + res_words), which differ by
    # 8 words per op between those two rungs.  So the registered route carries
    # 2 x 8 x w_word / 512 bits of the planted changed-word term -- XCHK 7's one-rung-bridge warning,
    # reaching the d3z leg -- and the planted truth FOR THAT ESTIMATOR is e_carry minus that term.
    # The family-B route (the wf3 build's, which §4 forbids) is the one that recovers 1.70.
    _d3z_dw = 8.0
    _d3z_bits = 512.0
    E_CARRY_REGISTERED = PLANT["e_carry"] - 2.0 * _d3z_dw * PLANT["w_word"] / _d3z_bits
    for key, want in (("e_in_fxor", PLANT["e_in"]), ("e_out_bridge", PLANT["e_out"]),
                      ("e_cell", PLANT["e_cell"]), ("e_carry", E_CARRY_REGISTERED),
                      ("e_addr", PLANT["e_addr"])):
        d = D.get(key) or {}
        print("      %-14s %9s fJ  [%5.2f]  SE %s  n=%s"
              % (key, R.fmt(d.get("fJ"), 3), want * 1e15, R.fmt(d.get("se_fJ"), 3), d.get("n_passes")))
        if key == "e_addr":
            # §9: family A's resolution is ~20 fJ/bit against a 0-2 fJ prior, so the only sane
            # check is consistency within its own window, which is the plan's whole point.
            t = (abs((d.get("fJ") or 0) - want * 1e15) / d["se_fJ"]) if d.get("se_fJ") else None
            check("synthetic e_addr is consistent with its planted value inside its own window",
                  t is not None and t < (R.t_crit(R.THREE_SIGMA_P, d.get("df")) or 0),
                  "|t| = %s against the 3-sigma window %s; SE %s fJ is %.0fx the planted value"
                  % (R.fmt(t, 2), R.fmt(R.t_crit(R.THREE_SIGMA_P, d.get("df")), 2),
                     R.fmt(d.get("se_fJ"), 2), (d.get("se_fJ") or 0) / (want * 1e15)))
            continue
        if key == "e_carry":
            # an absolute tolerance: the registered target is 0.20 fJ, so a 5% RELATIVE band would be
            # 0.01 fJ against a realised SE of ~0.11 fJ.  The test is |t| inside the 3-sigma window.
            t = (abs((d.get("fJ") or 0) - want * 1e15) / d["se_fJ"]) if d.get("se_fJ") else None
            check("synthetic e_carry recovers its planted value under the REGISTERED d3z "
                  "estimator (planted %.2f fJ = %.2f - the 2x8x%.0f/512 changed-word term)"
                  % (want * 1e15, PLANT["e_carry"] * 1e15, PLANT["w_word"] * 1e15),
                  t is not None and t < (R.t_crit(R.THREE_SIGMA_P, d.get("df")) or 0),
                  "got %s, |t| = %s against the 3-sigma window %s"
                  % (R.fmt(d.get("fJ"), 3), R.fmt(t, 2),
                     R.fmt(R.t_crit(R.THREE_SIGMA_P, d.get("df")), 2)))
            alt = D.get("e_carry_alt_from_B") or {}
            check("synthetic e_carry via the SUPERSEDED family-B route recovers the planted 1.70 fJ",
                  close(alt.get("fJ"), PLANT["e_carry"] * 1e15, 0.05),
                  "got %s (that route has no changed-word term: the 2x2 cancels it)"
                  % R.fmt(alt.get("fJ"), 3))
            r2 = D.get("e_carry_R2_corrected") or {}
            check("the R2-corrected e_carry is reported beside the registered one",
                  r2.get("fJ") is not None,
                  "got %s; on THIS campaign the correction is ~0 because every N rung changes the "
                  "same number of words, so the N ladder's intercept -- which §5.1 makes the price "
                  "of a changed word -- measures nothing here" % R.fmt(r2.get("fJ"), 3))
            continue
        check("synthetic %s recovers its planted value" % key,
              close(d.get("fJ"), want * 1e15, 0.05), "got %s" % R.fmt(d.get("fJ"), 3))
    zw = D.get("zero_word_term") or {}
    print("      zero_word     %9s fJ/op [%5.1f]" % (R.fmt(zw.get("fJ_per_op"), 1),
                                                     PLANT["zero_word_fJ_per_op"] * 1e15))
    check("the zero-word term recovers its planted fJ/op",
          close(zw.get("fJ_per_op"), PLANT["zero_word_fJ_per_op"] * 1e15, 0.1),
          "got %s" % R.fmt(zw.get("fJ_per_op"), 1))
    j = ((C.get("joint_fit") or {}).get("coefs") or {})
    print("      joint fit: " + ", ".join("%s %s fJ" % (k, R.fmt((j.get(k) or {}).get("fJ"), 2))
                                          for k in R.JOINT_COEFS))
    check("the joint fit recovers e_in and e_out", close((j.get("e_in") or {}).get("fJ"),
                                                         PLANT["e_in"] * 1e15, 0.1)
          and close((j.get("e_out") or {}).get("fJ"), PLANT["e_out"] * 1e15, 0.1))
    check("the joint fit prints a condition number and VIFs",
          (C.get("joint_fit") or {}).get("condition_number") is not None
          and bool((C.get("joint_fit") or {}).get("vif")))
    check("no joint-fit SE is quoted for a single-contrast coefficient (§8.5)",
          all((j.get(k) or {}).get("se_quoted") is False for k in ("e_cell", "e_carry", "e_addr")))
    check("the phase term is ~0 when nothing depends on k_adj",
          abs(((D.get("phase_term") or {}).get("value") or 9.9)) < 0.05,
          "%s W" % R.fmt((D.get("phase_term") or {}).get("value"), 4))
    check("rho comes out ~1.000 with sharing preserved",
          close((((res["cards"].get("aifoundry1-c0") or {}).get("derived") or {})
                 .get("rho_harts2_over_harts1") or {}).get("value"), 1.0, 0.02),
          "%s" % R.fmt(((((res["cards"].get("aifoundry1-c0") or {}).get("derived") or {})
                         .get("rho_harts2_over_harts1")) or {}).get("value"), 4))
    check("family 7 is reduced from its own dtf-cam unit",
          any("dtf-cam" in k for k in res["cards"]),
          ", ".join(sorted(res["cards"])))
    vs = res.get("verdicts") or []
    print("    verdicts: %d rows" % len(vs))
    for v in vs:
        print("      %-24s %-16s %s" % (v["claims"], v["verdict"], v["quantity"][:46]))
    check("every §9 claim row has a verdict", len(vs) >= 15, "%d rows" % len(vs))
    check("no verdict is left blank", all(v.get("verdict") for v in vs))
    check("Holm ran over the five confirmatory coefficients",
          len((res.get("holm") or {}).get("rows") or []) == 5)
    check("the across-cards table carries the E60 ties",
          all("E60_per_bit_tie" in e for k, e in (res.get("across_cards") or {}).items()
              if not k.startswith("_")))
    check("reduce.txt was written and is non-trivial",
          os.path.getsize(os.path.join(work, "synth-reduce.txt")) > 4000,
          "%d bytes" % os.path.getsize(os.path.join(work, "synth-reduce.txt")))
    return res


def test_partial(work):
    """§8: it must run on partial data and say what is missing."""
    print("\n[4] partial data: one card, three passes, three families missing")
    root = os.path.join(work, "partial")
    if os.path.isdir(root):
        shutil.rmtree(root)
    mpath = os.path.join(work, "manifest-synth.json")
    man = R.Manifest(mpath)
    keep = [n for n in man.items if man.family(n) in ("X", "N", "anchor")]
    rng = random.Random(3)
    dirs = []
    for p in range(1, 4):
        d = os.path.join(root, "aifoundry3", "dtf", "p%d" % p)
        write_pass(d, "aifoundry3", man, [n for n in keep if n != "anchor_pi"], p, rng)
        dirs.append(d)
    out = os.path.join(work, "partial.json")
    rc = R.main([*dirs, "--manifest", mpath, "--out", out,
                 "--txt", os.path.join(work, "partial-reduce.txt"), "--quiet"])
    check("reduce_dtf ran on partial data", rc == 0)
    res = json.load(open(out))
    miss = res.get("missing") or []
    print("    missing (%d):" % len(miss))
    for m in miss[:14]:
        print("      - %s" % m)
    for fam, word in (("V", "e_cell"), ("C", "e_carry"), ("A", "e_addr")):
        check("family %s absence is reported as NOT IDENTIFIED" % fam,
              any(word in m and "NOT IDENTIFIED" in m for m in miss))
    check("the 6-pass floor is reported as BOUND ONLY",
          any("BOUND ONLY" in m for m in miss))
    byv = dict((v["claims"], v["verdict"]) for v in res.get("verdicts") or [])
    check("a cut family reads 'not run', never a fitted zero",
          byv.get("C61 C62 I-22") == "not run" and byv.get("C54 C67 C68 C87") == "not run",
          str({k: byv[k] for k in list(byv)[:4]}))
    check("Holm names the coefficients it could not test",
          all(r.get("note") for r in (res.get("holm") or {}).get("rows") or []
              if r.get("t") is None))
    return res


# =================================================================================================
# 5. the gates, the pair-gate void, the A3 exclusion and the set-aside rule, on injected faults
# =================================================================================================
def rewrite(d, fn, mutate):
    path = os.path.join(d, fn)
    opener = gzip.open if fn.endswith(".gz") else open
    rows = [json.loads(l) for l in opener(path, "rt") if l.startswith("{")]
    rows = [r for r in (mutate(r) for r in rows) if r is not None]
    with opener(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def test_gates(work):
    print("\n[5] the gates on injected faults: the 0.2% pair void, amendment A3, the set-aside rule")
    root = os.path.join(work, "gates")
    if os.path.isdir(root):
        shutil.rmtree(root)
    mpath = os.path.join(work, "manifest-synth.json")
    man = R.Manifest(mpath)
    keep = [n for n in man.items if man.family(n) in ("X", "N", "V", "B", "anchor", "gate")]
    rng = random.Random(11)
    dirs = []
    for p in range(1, 9):
        d = os.path.join(root, "aifoundry3", "dtf", "p%d" % p)
        write_pass(d, "aifoundry3", man, [n for n in keep if n != "anchor_pi"], p, rng)
        dirs.append(d)
        # (i) pass 2: d1b_h32's device rate drifts 1% -> its pair with d1a_h32 is VOIDED and the
        #     0.5% family-zero gate fires as well
        if p == 2:
            rewrite(d, "runs.jsonl", lambda r: (dict(r, ops=r["ops"] * 1.01)
                                                if r["item"] == "d1b_h32" and r.get("ops") else r))
        # (ii) passes 1-3: d2B_h32 runs at the wrong clock -> amendment A3 excludes it by name
        if p <= 3:
            marks = [json.loads(l) for l in open(os.path.join(d, "marks.jsonl"))]
            win = [(m["t_start_ms"] - 800, m["t_end_ms"] + 1200) for m in marks
                   if m["item"] == "d2B_h32"]
            def slow(sm, win=win):
                for lo, hi in win:
                    if lo <= sm["t_ms"] <= hi:
                        sm["mhz"] = {"minion": 500}
                return sm
            rewrite(d, "telemetry.jsonl.gz", slow)
        # (iii) pass 5: five runs launch off protocol -> >5% of the pass fails -> SET ASIDE
        if p == 5:
            bad = sorted(n for n in keep if n.startswith("d1nz"))[:5]
            rewrite(d, "marks.jsonl", lambda m: (dict(m, on_protocol=False, start_c=61.0)
                                                 if m["item"] in bad else m))
    out = os.path.join(work, "gates.json")
    rc = R.main([*dirs, "--manifest", mpath, "--out", out,
                 "--txt", os.path.join(work, "gates-reduce.txt"), "--quiet"])
    check("reduce_dtf ran with injected faults", rc == 0)
    res = json.load(open(out))
    C = res["cards"]["aifoundry3"]
    voids = C.get("pair_gate_voids") or []
    print("    pair-gate voids: %s" % [(v["pass"], v["group"], round(v["spread"] * 100, 3)) for v in voids])
    check("the 0.2% pair gate voids the d1a/d1b subtraction in the faulted pass",
          any(v["pass"] == 2 and "d1b_h32" in v["group"] for v in voids))
    check("the voided pass is dropped from e_cell, not reported",
          ((C.get("derived") or {}).get("e_cell") or {}).get("n_passes") == 7,
          "e_cell n_passes %s" % ((C.get("derived") or {}).get("e_cell") or {}).get("n_passes"))
    print("    A3 excluded by name: %s %s" % (C.get("excluded_a3"), C.get("excluded_a3_detail")))
    check("amendment A3 excludes the item whose clock gate failed in 3 of the first 5 passes",
          C.get("excluded_a3") == ["d2B_h32"])
    print("    passes set aside: %s" % [(x["pass"], x["why"]) for x in C.get("passes_set_aside") or []])
    check("the pass with >5% failed runs is set aside",
          any(x["pass"] == 5 for x in C.get("passes_set_aside") or []))
    check("a set-aside pass is not replaced: the surviving count drops",
          C.get("n_passes") == 7, "n_passes %s" % C.get("n_passes"))
    check("the A3-excluded item does not count toward the pass-rejection count",
          all(not any(f[1] == "d2B_h32" for f in (C["gates"].get("failed") or []))
              for _ in (0,)))
    eb = (C.get("derived") or {}).get("e_out_bridge") or {}
    check("excluding a B cell by name drops the bridge to one rung and that is flagged, not hidden",
          eb.get("n_rungs") == 1 and eb.get("intercept_removed") is False
          and eb.get("carries_changed_word_term") is True,
          "rungs %s at h %s, intercept removed %s" % (eb.get("n_rungs"), eb.get("h_rungs"),
                                                      eb.get("intercept_removed")))
    v56 = [v for v in res["verdicts"] if v["claims"].startswith("C56")]
    check("the C56 verdict says which e_out it quoted and how far the raw bridge sits from it",
          bool(v56) and v56[0].get("joint_minus_raw_fJ") is not None,
          "joint - raw = %s fJ (raw %s, joint %s)"
          % (R.fmt((v56 or [{}])[0].get("joint_minus_raw_fJ"), 2), R.fmt(eb.get("fJ"), 2),
             R.fmt((v56 or [{}])[0].get("joint_fit_fJ"), 2)))
    return res


def test_nopass(work):
    """A pass dir whose marks carry no `block` and whose block.json carries no `pass` must be
    dropped with a reason, not crash the reduction and not leave a verdict vacuously CONFIRMED."""
    print("\n[6] a pass dir with no pass number: dropped with a reason, nothing scored on it")
    mpath = os.path.join(work, "manifest-synth.json")
    man = R.Manifest(mpath)
    root = os.path.join(work, "nopass")
    if os.path.isdir(root):
        shutil.rmtree(root)
    d = os.path.join(root, "aifoundry3", "dtf", "p1")
    keep = [n for n in man.items if man.family(n) in ("X", "anchor")]
    write_pass(d, "aifoundry3", man, [n for n in keep if n != "anchor_pi"], 1, random.Random(1))
    for fn in ("marks.jsonl", "runs.jsonl"):
        rewrite(d, fn, lambda r: dict((k, v) for k, v in r.items() if k != "block"))
    b = json.load(open(os.path.join(d, "block.json")))
    b.pop("pass", None)
    json.dump(b, open(os.path.join(d, "block.json"), "w"))
    out = os.path.join(work, "nopass.json")
    rc = R.main([d, "--manifest", mpath, "--out", out, "--csv", os.path.join(work, "nopass.csv"),
                 "--txt", os.path.join(work, "nopass-reduce.txt"), "--quiet"])
    check("reduce_dtf survives a pass dir with no pass number", rc == 0)
    res = json.load(open(out))
    check("the dropped runs are named with the reason",
          any("carry no pass number" in m for m in res.get("missing") or []))
    byv = dict((v["claims"], v["verdict"]) for v in res.get("verdicts") or [])
    check("the determinism row is 'not run', not vacuously CONFIRMED",
          byv.get("C13 C15") == "not run", str(byv.get("C13 C15")))
    check("only the design-argument row (C65) still carries a verdict",
          byv.get("C65") == "REFUTED" and
          all(byv[k] in ("not run", "REFUTED") for k in byv))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e60-data",
                    default=os.path.join(HERE, "..", "..", "..", "docs", "reports", "data", "2026-10-20-bitflip-ladder"))
    ap.add_argument("--work", default=os.path.join(HERE, "work"))
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    test_t()
    test_e60(a.e60_data, a.work)
    test_synthetic(a.work)
    test_partial(a.work)
    test_gates(a.work)
    test_nopass(a.work)
    print("\n%d checks, %d failed" % (len(CHECKS), len(FAILS)))
    for f in FAILS:
        print("  FAILED: %s" % f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
