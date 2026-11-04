#!/usr/bin/env python3
"""E165 (Q141(g)): the scorer's self-test, on the parent's committed data. No card, no device, no ssh; it reads committed files only and writes only
a temporary directory (the decompressed C-check file).

    python3 -B tools/claims-v3/e165/selftest_score_e165.py > tools/claims-v3/e165/selftest-score.txt      (about 5 minutes: E160's 150 bursts twice)

  1. THE PARENT'S REGISTERED VERDICTS. score_e165.py's own reduction (collect, cells_of) and rule helpers, run on E160's committed session
     (docs/reports/data/2026-11-03-e160-blind6-aifoundry2/aifoundry2/s1, with its committed ccheck-s1.json) under E160's frozen predictions and
     rules (score_parent_e160), reproduce E160's results.json field for field: every rule F1-F3, W1-W3, H1, H3, PK (n, rms, range, verdict, mean
     error, reference rms, the interval over tiles, inside, line, the over list, per burst), E160-C, R0, every pass alone, and every rule over the
     complete runs (E143's counting).
  2. Q140(l)'S END-TO-END E160 FIGURES (3.68 MHz / 0.66 W / 0.80 W). From the same reduction's cells: the 45 pool tiles that are not zeros anchors
     (their means and their passes' die starts, which must equal Q140(l)'s rows), E160's own zeros anchors as the session's reads, M8's frozen blind
     D, Q140(l)'s groups, and the E160-held-out fold's committed parameters in the frozen predictor (make_predictions_e165.Injected): through the
     unrounded path they reproduce loso.json's end_to_end_blind_D E160 to 1e-9, and through burst()'s own rounded outputs (E165's primary path) to
     0.01 MHz and 0.002 W.
  3. E165'S RULES AT KNOWN ANSWERS, on cells made up from the frozen predictions: measured = M9's part gives E165-R2 PASS and every rule PASS;
     governed clocks 5 MHz high fail G (rms and mean); 3 MHz high fail G on the mean alone; pinned boards 0.8 W high fail Bp on the mean; pinned
     boards +-1.2 W fail Bp on the rms alone; measured = M7 as frozen fails all three on the resolution; boards 3 W high fail W3; rises 2 C high fail
     H1 and H3; seven governed tiles leave G and Bg NOT SCORED and R2 NOT SCORED.
  4. THE PRIMARY'S INPUTS MOVE IT AS THE FROZEN SENSITIVITIES SAY: at burst()'s own finite-difference steps (zeros anchors 0.1 W over the fallback
     level, die starts 0.5 C over T_ref) every scored tile's clock and board move by the frozen code's own d_mhz_per_w_of_delta, d_board_per_w_of_delta
     and d_*_per_c_die_start, to its rounding; at larger steps (1 W under, 2 C over) the group means move within 10% of linear; an anchor burst at 752
     MHz is not counted; no anchor at all gives the frozen block exactly.
  5. The order, the left-out tiles and the helpers: a run whose label is not the registered order's at its idx is refused; a run of a left-out tile
     is refused; the bootstrap is reproducible; the coverage lines are E140's (21 of 25) and 46 of 52.
"""
import copy
import gzip
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e165_common as C  # noqa: E402
import make_predictions_e165 as MP  # noqa: E402
import score_e165 as S  # noqa: E402

ROOT = C.ROOT
D160 = os.path.join(ROOT, "docs/reports/data/2026-11-03-e160-blind6-aifoundry2")
P160 = json.load(open(os.path.join(ROOT, "tools/claims-v3/e160/predictions-e160.json")))
RES160 = json.load(open(os.path.join(D160, "results.json")))
P = json.load(open(os.path.join(HERE, "predictions-e165.json")))
LOSO = json.load(open(os.path.join(ROOT, C.Q140L_REL, "loso.json")))
ROWS = json.load(open(os.path.join(ROOT, C.Q140L_REL, "rows-m9a2.json")))
P6 = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry2.json")))["tiles"]
fails = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


def cmp(got, want, path=""):
    """the list of differences between two JSON-like values (exact)"""
    out = []
    if isinstance(want, dict):
        for k in want:
            out += cmp(got.get(k) if isinstance(got, dict) else None, want[k], f"{path}.{k}")
    elif got != want:
        out.append(f"{path}: {got!r} != {want!r}")
    return out


print(f"E165 scorer self-test: score_e165.py sha256 {C.sha256_file(S.__file__)}, predictions-e165.json {C.sha256_file(os.path.join(HERE, 'predictions-e165.json'))}")
print(f"  parent: E160 results.json {C.sha256_file(os.path.join(D160, 'results.json'))}, predictions-e160.json {P160 and C.sha256_file(os.path.join(ROOT, 'tools/claims-v3/e160/predictions-e160.json'))}")

# 1 ----------------------------------------------------------------------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as td:
    ccp = os.path.join(td, "ccheck-s1.json")
    with gzip.open(os.path.join(D160, "ccheck-s1.json.gz"), "rb") as f, open(ccp, "wb") as g:
        shutil.copyfileobj(f, g)
    ok(C.sha256_file(ccp) == RES160["ccheck_files"]["ccheck-s1.json"], f"E160's ccheck-s1.json decompressed is the file its results name ({C.sha256_file(ccp)[:16]}...)")
    runs = S.collect([os.path.join(D160, "aifoundry2", "s1")], S.load_ccheck([ccp]), S.pass_by_rep)
meta6, zeros6 = S.parent_meta(P160)
ok(len(runs) == RES160["runs"] == 150 and sum(m["counted"] for m in runs) == RES160["runs_counted"] and sum(m["complete"] for m in runs) == RES160["runs_complete"],
   f"E160's s1 reduced again: {len(runs)} runs, {sum(m['complete'] for m in runs)} complete, {sum(m['counted'] for m in runs)} counted (results.json: "
   f"{RES160['runs']}, {RES160['runs_complete']}, {RES160['runs_counted']})")
cells = S.cells_of(runs, meta6, zeros6)
sc = S.score_parent_e160(cells, P160, 2)
d = cmp(sc["rules"], RES160["score"]["rules"])
ok(not d and sc["tiles_scored"] == RES160["score"]["tiles_scored"] == 48,
   f"E160's registered rules reproduced field for field ({len(RES160['score']['rules'])} rules, {sum(len(v) for v in RES160['score']['rules'].values())} fields, "
   f"{len(d)} differ): " + "; ".join(f"{k} {v['verdict']}" for k, v in sc["rules"].items()) + (f" | {d[:3]}" if d else ""))
cr = S.c_rule(runs, True)
d = cmp(cr, {k: RES160["c_check"][k] for k in ("verdict", "launches", "by_verdict", "runs_not_all_pass")})
ok(not d and cr["verdict"] == "PASS" and cr["launches"] == 2596, f"E160-C reproduced: {cr['verdict']}, {cr['launches']} launches {cr['by_verdict']} ({len(d)} differ)")
rp = S.replicate(cells, P160["replicate"], P160["rules"], beside=("e143",))
d = cmp(rp, RES160["replicate"])
ok(not d and rp["verdict"] == "PASS", f"E160-R0 reproduced: {rp['verdict']} ({len(d)} differ)")
dp = []
for p in RES160["passes"]:
    sp = S.score_parent_e160(S.cells_of(runs, meta6, zeros6, passes={p}), P160, 1)
    mine = {k: {kk: v.get(kk) for kk in ("n", "rms", "inside", "verdict")} for k, v in sp["rules"].items()}
    dp += cmp(mine, RES160["per_pass"][str(p)], f"pass{p}")
ok(not dp, f"E160's every pass alone reproduced ({len(RES160['passes'])} passes, {len(dp)} differ): "
   + "; ".join(f"pass {p} F1 {RES160['per_pass'][str(p)]['E160-F1']['verdict']}, W2 {RES160['per_pass'][str(p)]['E160-W2']['verdict']}" for p in RES160["passes"]))
cc = S.cells_of(runs, meta6, zeros6, key="complete")
scc = S.score_parent_e160(cc, P160, 2)
d = cmp(scc["rules"], RES160["as_e143_counted"]["score_rules"])
ok(not d, f"E160's rules over the complete runs (C not required) reproduced ({len(d)} differ)")

# 2 ----------------------------------------------------------------------------------------------------------------------------------------------
A2 = C.m9a2()
p_fold = LOSO["arms"][MP.FOLD_ARM]["params"]["E160"]
rows = {r["name"]: r for r in ROWS["rows"] if r["session"] == "E160" and r["name"] in P6}
lab2 = {t["label"]: n for n, t in P160["tiles"].items()}
mine = {lab2[lab]: c for lab, c in cells.items() if lab in lab2}
same = all(mine[n]["burst_mhz"] == r["mhz"] and mine[n]["burst_w"] == r["w"] and mine[n]["die_start_runs"] == [x["T"] for x in r["runs"]] for n, r in rows.items())
anc = {}
for n, t in P160["tiles"].items():
    if t["anchor"] and n.endswith("anchor6_zeros"):
        c = mine[n]
        anc[t["type"]] = [{"burst_w": w, "burst_mhz": f, "die_start": T} for w, f, T in zip(c["burst_w_runs"], c["burst_mhz_runs"], c["die_start_runs"])]
anc_rows = {t: [{"burst_w": r["w"], "burst_mhz": r["mhz"], "die_start": r["T"]} for r in rr] for t, rr in ROWS["anchors"]["E160"].items()}
ok(len(rows) == 45 and same and anc == anc_rows, f"the scorer's own E160 cells equal Q140(l)'s rows: 45 tiles' means and die starts, and the three zeros anchors' "
   f"reads ({sum(len(v) for v in anc.values())} bursts)")
ex, rd = [], []
with MP.Injected(A2, p_fold) as M:
    delta, dsrc = M.session_delta(anc)
    for n, r in sorted(rows.items()):
        cmine = mine[n]
        Dn = P6[n]["M8"]["D600_a3_footing_w"]
        f, Pw = M._cell(M.CZ[r["type"]] + M.G * Dn, r["type"], delta, [float(x) for x in cmine["die_start_runs"]])
        ex.append((r["group"], cmine["burst_mhz"] - f, cmine["burst_w"] - Pw))
        b = C.primary(Dn, r["type"], anc, cmine["die_start_runs"], 0.0)
        rd.append((r["group"], cmine["burst_mhz"] - b["burst_mhz"], cmine["burst_w"] - b["burst_board_w"]))


def three(xs):
    g = [x for x in xs if x[0] == "governed"]
    p = [x for x in xs if x[0] == "pinned"]
    return {"G": (C.rms([x[1] for x in g]), C.mean([x[1] for x in g])), "Bg": (C.rms([x[2] for x in g]), C.mean([x[2] for x in g])),
            "Bp": (C.rms([x[2] for x in p]), C.mean([x[2] for x in p])), "n": (len(g), len(p))}


want = LOSO["end_to_end_blind_D"]["E160"][MP.FOLD_ARM]
ge, gr = three(ex), three(rd)
w_ex = max(max(abs(ge[q][0] - want[q]["rms"]), abs(ge[q][1] - want[q]["mean"])) for q in ("G", "Bg", "Bp"))
w_rd = {q: abs(gr[q][0] - want[q]["rms"]) for q in ("G", "Bg", "Bp")}
ok(w_ex < 1e-9 and ge["n"] == (17, 28), f"Q140(l)'s end-to-end E160 figures from the scorer's own cells, unrounded: governed clock {ge['G'][0]:.4f} MHz ({ge['G'][1]:+.3f}), "
   f"governed board {ge['Bg'][0]:.4f} W ({ge['Bg'][1]:+.3f}), pinned board {ge['Bp'][0]:.4f} W ({ge['Bp'][1]:+.3f}); n {ge['n']}; loso.json's to {w_ex:.1e} "
   f"({want['G']['rms']:.2f} / {want['Bg']['rms']:.2f} / {want['Bp']['rms']:.2f}); anchors {dsrc}")
ok(w_rd["G"] <= 0.01 and w_rd["Bg"] <= 0.002 and w_rd["Bp"] <= 0.002, f"the same through burst()'s rounded outputs (E165's primary path): {gr['G'][0]:.4f} MHz, "
   f"{gr['Bg'][0]:.4f} W, {gr['Bp'][0]:.4f} W (differences {w_rd['G']:.4f} MHz, {w_rd['Bg']:.4f} W, {w_rd['Bp']:.4f} W)")
ok(abs(round(ge["G"][0], 2) - 3.68) < 1e-9 and abs(round(ge["Bg"][0], 2) - 0.66) < 1e-9 and abs(round(ge["Bp"][0], 2) - 0.80) < 1e-9,
   "they read 3.68 MHz / 0.66 W / 0.80 W at two decimals, as Q140(l)'s README and the critic quote them")

# 3 ----------------------------------------------------------------------------------------------------------------------------------------------
TREF = A2.TREF
scored = [n for n in P["tiles"] if P["tiles"][n]["scored"]]
gov = [n for n in scored if P["tiles"][n]["group"] == "governed"]
pin = [n for n in scored if P["tiles"][n]["group"] == "pinned"]


def made_up(fm=lambda n, v: v, fw=lambda n, v: v, fr=lambda n, v: v, src="M9", drop=(), anchors=None, ds=None):
    cells = {}
    for n in scored:
        if n in drop:
            continue
        q = P["tiles"][n]["models"]["M9"]["a2_q140l"] if src == "M9" else P["tiles"][n]["models"][src]
        t = P["tiles"][n]
        cells[t["label"]] = {"label": t["label"], "name": n, "type": t["type"], "group": t["group"], "priority": t["priority"], "anchor": t["anchor"],
                             "passes": [1, 2], "n": 2, "burst_mhz": fm(n, q["burst_mhz"]), "burst_w": fw(n, q["burst_board_w"]),
                             "rise_c": fr(n, q["burst_die_rise_c"]), "die_start_runs": ds or [TREF, TREF], "D_w": None, "kernel_mhz": None,
                             "burst_mhz_runs": [], "burst_w_runs": [], "rise_runs": [], "peak_w_runs": [50.0, 50.0], "peak_w": 50.0}
    for n, rr in (anchors or {}).items():
        t = P["tiles"][n]
        cells[t["label"]] = {"label": t["label"], "name": n, "type": t["type"], "group": t["group"], "priority": t["priority"], "anchor": True,
                             "passes": [r[0] for r in rr], "n": len(rr), "burst_w_runs": [r[1] for r in rr], "burst_mhz_runs": [r[2] for r in rr],
                             "die_start_runs": [r[3] for r in rr], "burst_mhz": rr[0][2], "burst_w": rr[0][1], "rise_c": 1.0, "peak_w_runs": [], "peak_w": None}
    return cells


def verdicts(sc):
    r2 = sc["rules"]["E165-R2"]
    return {"R2": r2["verdict"], "G": r2["G"]["verdict"], "Bg": r2["Bg"]["verdict"], "Bp": r2["Bp"]["verdict"],
            **{k: v["verdict"] for k, v in sc["rules"].items() if k != "E165-R2"}}


s0 = S.score(made_up(), P, 2, light=True)
v = verdicts(s0)
ok(all(x.startswith("PASS") for x in v.values()) and s0["tiles_scored"] == 52 and s0["rules"]["E165-R2"]["G"]["rms"] == 0.0
   and s0["rules"]["E165-R2"]["G"]["resolved_better_than_M7"] and s0["anchors"] is None,
   f"measured = M9's part (no anchor read, die starts at T_ref, so the primary is the frozen block): {s0['tiles_scored']} tiles, {v}")
v = verdicts(S.score(made_up(fm=lambda n, x: x + 5 if n in gov else x), P, 2, light=True))
ok(v["G"] == "FAIL" and v["R2"] == "FAIL" and v["Bg"] == "PASS" and v["Bp"] == "PASS", f"governed clocks 5 MHz high: G {v['G']}, Bg {v['Bg']}, Bp {v['Bp']}, R2 {v['R2']}")
s3 = S.score(made_up(fm=lambda n, x: x + 3 if n in gov else x), P, 2, light=True)
g3 = s3["rules"]["E165-R2"]["G"]
ok(g3["verdict"] == "FAIL" and g3["rms_le_line"] and not g3["mean_within_line"], f"governed clocks 3 MHz high: G {g3['verdict']} (rms {g3['rms']} within 4 MHz, mean {g3['mean']} not within 2)")
v = verdicts(S.score(made_up(fw=lambda n, x: x + 0.8 if n in pin else x), P, 2, light=True))
ok(v["Bp"] == "FAIL" and v["G"] == "PASS" and v["Bg"] == "PASS", f"pinned boards 0.8 W high: Bp {v['Bp']}, G {v['G']}, Bg {v['Bg']}")
alt = {n: (1.2 if i % 2 else -1.2) for i, n in enumerate(sorted(pin))}
sp = S.score(made_up(fw=lambda n, x: x + alt[n] if n in pin else x), P, 2, light=True)
bp = sp["rules"]["E165-R2"]["Bp"]
ok(bp["verdict"] == "FAIL" and bp["mean_within_line"] and not bp["rms_le_line"], f"pinned boards +-1.2 W: Bp {bp['verdict']} (mean {bp['mean']} within, rms {bp['rms']} over 1.0 W)")
s7 = S.score(made_up(src="M7"), P, 2, light=True)
r7 = s7["rules"]["E165-R2"]
ok(r7["G"]["resolved_better_than_M7"] is False and r7["Bg"]["resolved_better_than_M7"] is False and r7["Bp"]["resolved_better_than_M7"] is False
   and r7["verdict"] == "FAIL", f"measured = M7 as frozen: resolved better than M7 G {r7['G']['resolved_better_than_M7']}, Bg {r7['Bg']['resolved_better_than_M7']}, "
   f"Bp {r7['Bp']['resolved_better_than_M7']}; R2 {r7['verdict']}")
v = verdicts(S.score(made_up(fw=lambda n, x: x + 3), P, 2, light=True))
ok(v["E165-W3"] == "FAIL", f"boards 3 W high: W3 {v['E165-W3']}, W1 {v['E165-W1']}, W2 {v['E165-W2']}")
v = verdicts(S.score(made_up(fr=lambda n, x: x + 2), P, 2, light=True))
ok(v["E165-H1"] == "FAIL" and v["E165-H3"] == "FAIL", f"rises 2 C high: H1 {v['E165-H1']}, H3 {v['E165-H3']}")
v = verdicts(S.score(made_up(drop=gov[:5]), P, 2, light=True))
ok(v["G"].startswith("NOT SCORED") and v["Bg"].startswith("NOT SCORED") and v["R2"] == "NOT SCORED" and v["Bp"] == "PASS",
   f"7 governed tiles: G {v['G']}, Bg {v['Bg']}, Bp {v['Bp']}, R2 {v['R2']}")

# 4 ----------------------------------------------------------------------------------------------------------------------------------------------
fb = A2.M9["fallback_delta_w"]
Lz = {t: A2.B[800] + A2.CZ[t] * A2.S[800] for t in ("fp32", "fp16", "int8")}


def anchors_at(shift):
    return {n: [(p, round(Lz[P["tiles"][n]["type"]] + fb[P["tiles"][n]["type"]] + shift, 9), 800.0, TREF) for p in (1, 2)] for n in C.ZEROS_ANCHORS}


# (a) at burst()'s own finite-difference steps (+0.1 W of anchor offset, +0.5 C of die start) the recompute moves exactly as the frozen sensitivities
sa1 = S.score(made_up(anchors=anchors_at(0.1)), P, 2, light=True)
sd1 = S.score(made_up(ds=[TREF + 0.5, TREF + 0.5]), P, 2, light=True)
bad4 = []
for n in gov + pin:
    q = P["tiles"][n]["models"]["M9"]["a2_q140l"]
    pa, pd = sa1["reported"]["tiles"][n]["primary"], sd1["reported"]["tiles"][n]["primary"]
    for got, want, tol in ((pa["burst_mhz"] - q["burst_mhz"], 0.1 * q["d_mhz_per_w_of_delta"], 0.02), (pa["burst_board_w"] - q["burst_board_w"], 0.1 * q["d_board_per_w_of_delta"], 0.002),
                           (pd["burst_mhz"] - q["burst_mhz"], 0.5 * q["d_mhz_per_c_die_start"], 0.02), (pd["burst_board_w"] - q["burst_board_w"], 0.5 * q["d_board_per_c_die_start"], 0.002)):
        if abs(got - want) > tol:
            bad4.append(f"{n}: moved {got:+.4f}, the frozen sensitivity says {want:+.4f}")
ok(not bad4 and sa1["anchor_delta"]["delta_source"] == "the session's own zeros anchors",
   f"at burst()'s own steps (anchors 0.1 W over the fallback level, die starts 0.5 C over T_ref) every scored tile moves as its frozen sensitivities say, to the "
   f"frozen code's rounding (0.02 MHz, 0.002 W): {len(bad4)} off {bad4[:2]}")
# (b) larger steps, on the group means: anchors 1 W under the fallback level, die starts 2 C over T_ref
sa = S.score(made_up(anchors=anchors_at(-1.0)), P, 2, light=True)
sd = S.score(made_up(ds=[TREF + 2.0, TREF + 2.0]), P, 2, light=True)


def mv(sc, names, key, fkey):
    return sum(sc["reported"]["tiles"][n]["primary"][key] - P["tiles"][n]["models"]["M9"]["a2_q140l"][fkey] for n in names) / len(names)


pb, gm = mv(sa, pin, "burst_board_w", "burst_board_w"), mv(sd, gov, "burst_mhz", "burst_mhz")
gma, pbd = mv(sa, gov, "burst_mhz", "burst_mhz"), mv(sd, pin, "burst_board_w", "burst_board_w")
lin = {"pb": -1.0 * sum(P["tiles"][n]["models"]["M9"]["a2_q140l"]["d_board_per_w_of_delta"] for n in pin) / len(pin),
       "gm": 2.0 * sum(P["tiles"][n]["models"]["M9"]["a2_q140l"]["d_mhz_per_c_die_start"] for n in gov) / len(gov),
       "gma": -1.0 * sum(P["tiles"][n]["models"]["M9"]["a2_q140l"]["d_mhz_per_w_of_delta"] for n in gov) / len(gov),
       "pbd": 2.0 * sum(P["tiles"][n]["models"]["M9"]["a2_q140l"]["d_board_per_c_die_start"] for n in pin) / len(pin)}
ok(all(abs(a - lin[k]) <= 0.10 * abs(lin[k]) for k, a in (("pb", pb), ("gm", gm), ("gma", gma), ("pbd", pbd))),
   f"larger steps, group means: anchors 1 W under the fallback level move the pinned boards {pb:+.3f} W (linear {lin['pb']:+.3f}; beta 0.648) and the governed "
   f"clocks {gma:+.2f} MHz (linear {lin['gma']:+.2f}); die starts 2 C over T_ref move the governed clocks {gm:+.2f} MHz (linear {lin['gm']:+.2f}) and the pinned "
   f"boards {pbd:+.3f} W (linear {lin['pbd']:+.3f}); within 10% (the dither curves near the cap's edge, so single tiles there differ more)")
low = anchors_at(-1.0)
mixed = dict(low)
mixed["fp16.anchor7_zeros"] = low["fp16.anchor7_zeros"] + [(3, 30.0, 752.0, TREF)]
sm = S.score(made_up(anchors=mixed), P, 2, light=True)
ok(sm["anchor_delta"]["delta_w"] == sa["anchor_delta"]["delta_w"], f"an anchor burst at 752 MHz is not counted (delta {sm['anchor_delta']['delta_w']})")
again = {n: C.primary(P["tiles"][n]["models"]["M9"]["D600_a3_footing_w"], P["tiles"][n]["type"], None, None, P["tiles"][n]["models"]["M9"]["D_band_hw"]) for n in P["tiles"]}
ok(all(again[n] == P["tiles"][n]["models"]["M9"]["a2_q140l"] for n in P["tiles"]), "with no session read the primary is the frozen block on all 61 tiles, field for field")

# 5 ----------------------------------------------------------------------------------------------------------------------------------------------
f = S.pass_by_order(P)
o = P["order"]
good = f({"idx": 60, "label": o[60]["label"], "run": "x"}) == o[60]["pass"] == 2
try:
    f({"idx": 60, "label": o[61]["label"], "run": "BURST-60-x-r1"})
    refused = False
except SystemExit:
    refused = True
ok(good and refused and all(x["first_of_pass"] == (x["idx"] % 57 < 3) for x in o) and all(C.name_of(x["label"]) in C.ZEROS_ANCHORS for x in o if x["first_of_pass"]),
   "the order: idx 60 is pass 2; a run whose label is not the order's at its idx is refused; each pass opens with the three zeros anchors")
stray = S.stray_left_out([{"label": C.label_of("fp32.uniform_pm1")}, {"label": C.label_of("fp16.randn_x8")}], P)
ok(stray is not None and "fp32.uniform_pm1" in stray and "fp16.randn_x8" not in stray and len(P["left_out"]) == 6,
   f"a run of a left-out tile is refused ({stray}); 6 tiles left out by name")
b1 = C.boot_rms_range(P["reference"]["e2e"]["governed"]["mhz_err"], 12)
b2 = C.boot_rms_range(P["reference"]["e2e"]["governed"]["mhz_err"], 12)
ok(b1 == b2 and C.coverage_line(25) == 21 and C.coverage_line(52) == 46, f"bootstrap reproducible {tuple(round(x, 3) for x in b1)}; coverage lines 25 -> 21, 52 -> {C.coverage_line(52)}")

print("\nALL PASS" if not fails else f"\n{len(fails)} FAILED")
sys.exit(1 if fails else 0)
