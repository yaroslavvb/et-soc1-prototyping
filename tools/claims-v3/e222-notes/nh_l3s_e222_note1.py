#!/usr/bin/env python3
"""E222, dated note 1, section 2 (round Q236, lane fix-e222, Fri 20 Nov 2026, written before any E222 datum): how often NH-L3S FAILS and how
often L3S joins MM1-v3.3, by simulating the REGISTERED rules with the frozen scorer's own functions (score_e222.nh_rule, h_cases and decide,
imported unchanged), and a printer that puts those rates beside a scored day's NH-L3S, HC-L3S and SEL verdicts. No rule, margin, point,
forecast or verdict changes. Standard library only (the frozen scorer and E220's scorer it imports at its pin are too).

    /usr/bin/python3 -I -B tools/claims-v3/e222-notes/nh_l3s_e222_note1.py make <out.json>
    /usr/bin/python3 -I -B tools/claims-v3/e222-notes/nh_l3s_e222_note1.py beside <a scores-e222.json written by score_e222.py> [--note <json>]
    /usr/bin/python3 -I -B tools/claims-v3/e222-notes/nh_l3s_e222_note1.py selftest <a scratch folder outside the lab clone>

THE LIST FIRST (verify-e222's finding 4): before the frozen scorer is imported, every entry of tools/claims-v3/e222/SHA256SUMS-e222-registration
is checked (all 30 OK) and the list's own sha256 must be de67150b...; and this note's own list, when present, reads OK for this script and the
note's table (exit 4 otherwise). The frozen scorer's load_frozen() reads its pins from that list, and skips a file the list does not name.

THE MODEL OF A DAY (verify-e222's finding 2; the same model as E222.md section 1's power): a truth (a frozen forecaster for each point group);
at every registered point (families T, L3b, Y3, G3, G3t: 66 points; family R is in no rule) the measured wall cycles an op = the truth's wall x
exp(s z1 + b), seconds a GEMM = the truth's seconds x exp(s z1 + b), the measured op time = that wall / 600 MHz, and the measured W over idle =
(the truth's A_W + B_W_us / that op time) x exp(s z2); z1, z2 standard normal, independent per point and per day; b a shared ln bias, 0 except
in the bias table, where it is added at G3 and G3t only (the two groups where NH-L3S can FAIL). Each day is read by the frozen scorer:
NH-L3S = nh_rule(M, F, R, P, 'MM1-v3.2 + L3S') (margin 0.5 point, at least 5 points a group: as registered); HC-L3S =
decide(h_cases(M, F, R, 'MM1-v3.2 + L3S', 'MM1-v3.2', 'wall', L3b and T-L3 points), minimum 10, alpha 0.05: as registered); L3S JOINS
MM1-v3.3 when HC-L3S reads 'MM1-v3.2 + L3S BETTER' and NH-L3S reads PASS (SEL's clause for L3S; the other candidates do not enter it).
Seeds are fixed strings, one a cell, so a cell reads the same in any order and on any run.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
E = "tools/claims-v3/e222"
REG_LIST = (E + "/SHA256SUMS-e222-registration", "de67150bee12bde15c50d0f1067d042a0cd0ca3a9a8ad74af577145d077acef7", 30)
NOTE_LIST = "tools/claims-v3/e222-notes/SHA256SUMS-e222-note1"
V32, L3S = "MM1-v3.2", "MM1-v3.2 + L3S"
F_MHZ = 600.0
SIGMAS = (0.005, 0.01, 0.02, 0.03, 0.05)
BIASES = (-0.04, -0.02, 0.0, 0.02, 0.04)
DAYS_GRID, DAYS_BIAS = 20000, 10000
# verify-e222's own simulation (its logs/v08_rules.txt, 17:42 PST Fri 20 Nov 2026: numpy, its own generator, 5,000 days a cell, the wall at G3
# and G3t only), printed beside this note's figures; not an input to anything here
VERIFY_E222 = {"truth MM1-v3.2 + L3S": {"0.005": 0.0, "0.01": 0.009, "0.02": 0.049, "0.03": 0.085, "0.05": 0.125},
               "truth MM1-v3.2": {"0.005": 0.911, "0.01": 0.619, "0.02": 0.388, "0.03": 0.298, "0.05": 0.251},
               "P(L3S joins | L3S right), about": 0.14}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def check_lists():
    """the registration's list at its pin, every entry OK; this note's list, when present, OK for its own entries"""
    rel, pin, n = REG_LIST
    p = os.path.join(REPO, rel)
    if not os.path.exists(p) or sha(p) != pin:
        print(f"nh_l3s_e222_note1: REFUSED, {rel} is not at its pin {pin[:12]}")
        sys.exit(4)
    ok, bad = 0, []
    for ln in open(p):
        if not ln.strip() or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        f = f.strip()
        if os.path.exists(os.path.join(REPO, f)) and sha(os.path.join(REPO, f)) == h:
            ok += 1
        else:
            bad.append(f)
    if bad or ok != n:
        print(f"nh_l3s_e222_note1: REFUSED, {rel}: {ok} of {n} OK; not OK: {bad[:5]}")
        sys.exit(4)
    note = {"list": rel, "own_sha256": pin, "entries_ok": ok}
    q = os.path.join(REPO, NOTE_LIST)
    if os.path.exists(q):
        nok, nbad = 0, []
        for ln in open(q):
            if not ln.strip() or ln.startswith("#"):
                continue
            h, f = ln.split(None, 1)
            f = f.strip()
            if os.path.exists(os.path.join(REPO, f)) and sha(os.path.join(REPO, f)) == h:
                nok += 1
            else:
                nbad.append(f)
        if nbad:
            print(f"nh_l3s_e222_note1: REFUSED, {NOTE_LIST}: not OK: {nbad[:5]}")
            sys.exit(4)
        print(f"nh_l3s_e222_note1: {NOTE_LIST}: {nok} entries OK (printed only, never written into an output, so a make reads the same with or "
              f"without the note's list)")
    return note


def scorer():
    spec = importlib.util.spec_from_file_location("score_e222_frozen", os.path.join(REPO, E, "score_e222.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def day(S, P, F, R, regs, truth_of_group, sig_of_model, rng, s=None, bias=0.0):
    """one simulated day: the measured side in the frozen reader's output form (the keys predicted(), h_cases() and nh_rule() read)"""
    M = {}
    for pid, g in regs:
        model = truth_of_group(g)
        x = S.fcv(F, pid, model)
        sg = s if s is not None else sig_of_model[model]
        b = bias if g in ("G3", "G3t") else 0.0
        k = math.exp(sg * rng.gauss(0.0, 1.0) + b)
        wall = x["cycles_per_op_wall"] * k
        top = wall / F_MHZ
        w = None
        if x.get("A_W") is not None:
            w = (x["A_W"] + x["B_W_us"] / top) * math.exp(sg * rng.gauss(0.0, 1.0))
        t = x["seconds_per_gemm"] * k
        M[pid] = {"wall": wall, "mean": x["cycles_per_op_mean"] * k, "t": t, "Top": top, "Top_e": top, "t_e": t, "W": w,
                  "J": (w * t) if w is not None else None, "prest": S.fcv(F, pid, V32).get("rest_law_W"), "n_runs": 2}
    return M


def cell(S, P, F, R, regs, own_ids, name, truth_of_group, sig_of_model, days, s=None, bias=0.0):
    rng = random.Random(f"E222 dated note 1|NH-L3S|{name}|s={s}|b={bias}")
    hc_min = R["candidate_head_to_head"]["HC-L3S"]["minimum_decided"]
    n = {"NH FAIL": 0, "NH FAIL wall": 0, "NH FAIL Wg": 0, "NH PASS": 0, "NH NO DATA": 0, "HC L3S BETTER": 0, "HC MM1-v3.2 BETTER": 0,
         "HC NOT DECIDED": 0, "HC TOO FEW": 0, "HC NO DATA": 0, "JOIN": 0}
    for _ in range(days):
        M = day(S, P, F, R, regs, truth_of_group, sig_of_model, rng, s, bias)
        nh = S.nh_rule(M, F, R, P, L3S)
        hc = S.decide(S.h_cases(M, F, R, L3S, V32, "wall", own_ids), L3S, V32, minimum=hc_min)
        n["NH " + nh["verdict"]] += 1
        if nh["verdict"] == "FAIL":
            fq = {q for r in nh["groups"].values() for q in r["fails"]}
            n["NH FAIL wall"] += "wall" in fq
            n["NH FAIL Wg"] += "Wg" in fq
        hv = hc["verdict"]
        n["HC " + ("L3S BETTER" if hv == f"{L3S} BETTER" else ("MM1-v3.2 BETTER" if hv == f"{V32} BETTER" else hv))] += 1
        n["JOIN"] += (hv == f"{L3S} BETTER" and nh["verdict"] == "PASS")
    rec = {"truth": name, "sigma": s if s is not None else {k: round(v, 6) for k, v in sig_of_model.items()}, "shared_bias_ln_at_G3_G3t": bias,
           "days": days, "seed": f"E222 dated note 1|NH-L3S|{name}|s={s}|b={bias}"}
    rec.update({"P(" + k + ")": round(v / days, 4) for k, v in n.items()})
    return rec


def make(out_path):
    lists = check_lists()
    S = scorer()
    P, F, R = S.load_frozen(check=True)
    S.P_GLOBAL[0] = P
    grp = {p["id"]: S.group(p) for p in P["points"]}
    regs = [(pid, grp[pid]) for pid in S.P_REG(P)]
    own = set(R["candidate_head_to_head"]["HC-L3S"]["own_family"])
    own_ids = {pid for pid, g in regs if g in own}
    sig_reg = {L3S: R["candidate_head_to_head"]["HC-L3S"]["power_REPORTED"]["sigma_first"],
               V32: R["candidate_head_to_head"]["HC-L3S"]["power_REPORTED"]["sigma_second"]}
    truths = {"L3S": ("MM1-v3.2 + L3S everywhere", lambda g: L3S), "V32": ("MM1-v3.2 everywhere", lambda g: V32),
              "MIX": ("MM1-v3.2 + L3S on L3b and T-L3, MM1-v3.2 elsewhere (the harm NH-L3S is for)", lambda g: (L3S if g in own else V32))}
    t0 = now()
    out = {"what": "E222 dated note 1 section 2: NH-L3S's FAIL rate and L3S's chance to join MM1-v3.3 by the frozen scorer's own rule functions "
                   "on simulated days (independent errors per point; REPORTED, never a verdict; no rule changes)",
           "interpreter": f"{sys.executable} {sys.version.split()[0]}",
           "lists_checked": lists, "inputs_sha256": {f: sha(os.path.join(REPO, E, f)) for f in ("score_e222.py", "rules-e222.json",
                                                                                                 "forecast-e222.json", "points-e222.json")},
           "registered_points_simulated": len(regs), "hc_l3s_points": sorted(own_ids), "f_mhz": F_MHZ,
           "registered_beside": {"HC-L3S power (rules-e222.json, 2,000 days)": R["candidate_head_to_head"]["HC-L3S"]["power_REPORTED"]["by_scenario"],
                                 "NH-L3S frozen move bound (rules-e222.json)": R["no_harm"]["NH-L3S"]["frozen_move_bound_REPORTED"],
                                 "NH-L3S margin_pct": R["no_harm"]["NH-L3S"]["margin_pct"], "NH-L3S min_points": R["no_harm"]["NH-L3S"]["min_points"]},
           "verify_e222_beside": VERIFY_E222, "grid": [], "registered_sigmas": [], "bias": []}
    for key, (name, fn) in truths.items():
        for s in SIGMAS:
            out["grid"].append(dict(cell(S, P, F, R, regs, own_ids, name, fn, sig_reg, DAYS_GRID, s=s), key=key))
            r = out["grid"][-1]
            print(f"grid  | {name[:44]:44s} | s {s:.3f} | P(NH FAIL) {r['P(NH FAIL)']:.4f} (wall {r['P(NH FAIL wall)']:.4f}, Wg {r['P(NH FAIL Wg)']:.4f}) "
                  f"| P(HC L3S BETTER) {r['P(HC L3S BETTER)']:.4f} | P(join) {r['P(JOIN)']:.4f}", flush=True)
    for key, (name, fn) in truths.items():
        out["registered_sigmas"].append(dict(cell(S, P, F, R, regs, own_ids, name, fn, sig_reg, DAYS_GRID, s=None), key=key))
        r = out["registered_sigmas"][-1]
        print(f"regs  | {name[:44]:44s} | the registered sigmas (L3S {sig_reg[L3S]:.5f}, MM1-v3.2 {sig_reg[V32]:.5f}) | P(NH FAIL) {r['P(NH FAIL)']:.4f} "
              f"| P(HC L3S BETTER) {r['P(HC L3S BETTER)']:.4f} P(HC MM1-v3.2 BETTER) {r['P(HC MM1-v3.2 BETTER)']:.4f} | P(join) {r['P(JOIN)']:.4f}", flush=True)
    for key in ("L3S", "V32"):
        name, fn = truths[key]
        for b in BIASES:
            out["bias"].append(dict(cell(S, P, F, R, regs, own_ids, name, fn, sig_reg, DAYS_BIAS, s=0.03, bias=b), key=key))
            r = out["bias"][-1]
            print(f"bias  | {name[:44]:44s} | s 0.030, shared ln bias {b:+.2f} at G3 and G3t | P(NH FAIL) {r['P(NH FAIL)']:.4f}", flush=True)
    json.dump(out, open(out_path, "w"), indent=1, sort_keys=True)
    open(out_path, "a").write("\n")
    print(f"NH-L3S-E222-NOTE1: written {os.path.basename(out_path)} sha256 {sha(out_path)[:12]} ({t0} - {now()}; no time inside the file, so two runs "
          f"compare byte for byte)")
    return 0


def find(rows, key, s):
    for r in rows:
        if r["key"] == key and r["sigma"] == s:
            return r
    raise KeyError(f"no cell {key} at s {s}")


def beside_lines(sc, note):
    """the printer: a scored day's NH-L3S, HC-L3S and SEL verdicts with this note's rates beside them (REPORTED)"""
    nh = sc["no_harm"]["NH-L3S"]
    hc = sc["candidates"]["HC-L3S"]
    sel = sc["selection"]
    g = note["grid"]
    rL = [find(g, "L3S", s) for s in (0.02, 0.03, 0.05)]
    rV = [find(g, "V32", s) for s in (0.02, 0.03, 0.05)]
    rs = {r["key"]: r for r in note["registered_sigmas"]}
    worst = nh.get("worst_excess_pct")
    wg = [f"{k}: wall {v.get('wall_excess_pct', float('nan')):+.3f}" for k, v in sorted(nh.get("groups", {}).items()) if k in ("G3", "G3t")]
    L = [f"NH-L3S: {nh['verdict']} (registered rule: margin {nh.get('margin_pct')} point; worst excess "
         f"{('%+.3f' % worst) if worst is not None else '-'} point; {'; '.join(wg) or 'G3/G3t no data'})"
         + (f" [{nh['label']}]" if nh.get("label") else ""),
         "   beside it (E222 dated note 1, simulated, REPORTED): P(NH-L3S FAIL) if 'MM1-v3.2 + L3S' is right "
         + "/".join(f"{r['P(NH FAIL)']:.3f}" for r in rL) + " at 2/3/5% independent errors; if MM1-v3.2 is right "
         + "/".join(f"{r['P(NH FAIL)']:.3f}" for r in rV) + " (it can FAIL only at G3 and G3t, on the wall)",
         f"HC-L3S: {hc['verdict']} (L3S closer {hc.get('first_closer', '-')}, MM1-v3.2 closer {hc.get('second_closer', '-')}, "
         f"ties {hc.get('ties', '-')}, p {hc.get('p', '-')})" + (f" [{hc['label']}]" if hc.get("label") else ""),
         f"SEL: {sel['verdict']}" + (f" [{sel['label']}]" if sel.get("label") else ""),
         "   beside it: P(L3S joins MM1-v3.3) at the registered sigmas: "
         + "; ".join(f"{k}: {rs[c]['P(JOIN)']:.3f}" for k, c in (("if 'MM1-v3.2 + L3S' is right", "L3S"), ("if MM1-v3.2 is right", "V32"),
                                                                ("if L3S is right only on L3b and T-L3", "MIX"))),
         "READING (E222 dated note 1, section 3): a NOT DECIDED or TOO FEW on HC-posimb or HC-L3S reads 'not shown', never 'rejected'; NH-posimb "
         "and NH-AF4 cannot FAIL by construction (a PASS there says nothing about harm); HC-AF4 tests AF4 at G3 (R4 = 0, NB 5-6) and T-G2 only."]
    return L


def beside(path, note_path=None):
    note_path = note_path or os.path.join(HERE, "nh-l3s-e222-note1.json")
    try:
        sc = json.load(open(path))
        note = json.load(open(note_path))
        lines = beside_lines(sc, note)
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"nh_l3s_e222_note1 beside: NOT A SCORER OUTPUT ({type(e).__name__}: {e})")
        return 10
    print("\n".join(lines))
    return 0


def selftest(scratch):
    """two stand-in days made by the frozen scorer's own makers in memory (every point at 'MM1-v3.2 + L3S', and at MM1-v3.2), scored by the
    frozen score() in memory, written ONLY under the scratch folder given; the printer must print each day's own NH-L3S, HC-L3S and SEL verdicts"""
    check_lists()
    if os.path.abspath(scratch).startswith(REPO + os.sep):
        print("nh_l3s_e222_note1 selftest: REFUSED, the scratch folder is inside the lab clone")
        return 10
    S = scorer()
    P, F, R = S.load_frozen(check=True)
    S.P_GLOBAL[0] = P
    note = os.path.join(HERE, "nh-l3s-e222-note1.json")
    res = []
    for tag, model in (("l3s", L3S), ("v32", V32)):
        def fn(p, model=model):
            tr = S.truth_of(F, p["id"], model)
            return None if tr["W"] is None else tr
        out = S.score(S.make(P, F, fn), P, F, R)
        d = os.path.join(scratch, f"standin-{tag}")
        os.makedirs(d, exist_ok=True)
        pth = os.path.join(d, "scores-e222.json")
        json.dump(out, open(pth, "w"), indent=1, sort_keys=True, default=str)
        lines = beside_lines(json.load(open(pth)), json.load(open(note)))
        want = [f"NH-L3S: {out['verdicts']['NH-L3S']}", f"HC-L3S: {out['verdicts']['HC-L3S']}", f"SEL: {out['verdicts']['SEL']}"]
        ok = all(any(ln.startswith(w + " ") or ln == w for ln in lines) for w in want)
        res.append(ok)
        print(f"selftest {tag}: {'PASS' if ok else 'FAIL'}: day verdicts {want}")
        print("   " + "\n   ".join(lines))
    bad = os.path.join(scratch, "not-a-scorer-output.json")
    json.dump({"x": 1}, open(bad, "w"))
    rc = beside(bad, note)
    res.append(rc == 10)
    print(f"selftest refusal: {'PASS' if rc == 10 else 'FAIL'} (a file without the scorer's keys: exit {rc}, want 10)")
    print(f"NH-L3S-E222-NOTE1 SELFTEST: {sum(res)} of {len(res)} PASS")
    return 0 if all(res) else 1


def main(argv):
    if len(argv) >= 2 and argv[0] == "make":
        return make(argv[1])
    if len(argv) >= 2 and argv[0] == "beside":
        return beside(argv[1], argv[argv.index("--note") + 1] if "--note" in argv else None)
    if len(argv) >= 2 and argv[0] == "selftest":
        return selftest(argv[1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
