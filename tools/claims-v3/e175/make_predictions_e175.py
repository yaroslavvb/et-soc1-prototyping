#!/usr/bin/env python3
"""E175 (Q143(g)): writes frozen-sha256-e175.json and predictions-e175.json, everything E175 scores, frozen before any claim and any launch.
No card. E173's make_predictions_e173.py with E175's pool, sets, order and lines (tools/claims-v3/e175/E175.md, lab c50ff493). NOTHING IS
FITTED OR REFITTED HERE: every predicted number is the frozen predictor's own output for E175's pool on aifoundry2
(tools/claims-v3/e175/frozen/predictions-pool8-aifoundry2.json, from Q142(p)'s predict_pool8_a2.py predict, 97765c0a), copied by key after its
sha256 is checked, or that predictor's burst mode, called unchanged.

    python3 -B tools/claims-v3/e175/make_predictions_e175.py > tools/claims-v3/e175/predictions-e175.txt

WHAT IT WRITES
  frozen-sha256-e175.json  every input E175 reads, with its sha256 from the committed tree, each matched against the committed hash list that
             already names it (E175's registration list, its design's SHA256SUMS, the pool's SHA256SUMS, the predictor's SHA256SUMS and
             SHA256SUMS-a2, POOL8-SHA256SUMS, the watcher's own pin of run_hpl.py), and the last commit that touched it; refused if any file differs
             from its list or is not committed clean.
  recheck    predict_pool8_a2.burst with no session read (anchors None, no die starts) reproduces every tile's frozen M10.a2_fallback and
             M9.a2_fallback block field for field (27 tiles, both models): the primary's recompute is the frozen file's own code path.
  tiles      E175's 27 tiles (the three zeros anchors and the 24 kept): type, the run value and label, the manifest's sha256, the GROUP fixed by
             the frozen file (M10.a2_fallback.group), the design's set and stratum, the admission estimate (the larger of M10's and M9's 95%
             upper peaks; none is over 82 W: the selection replaced every candidate over it).
  sets       scored 24: governed 16 (four strata of 4 by M10 carried's fallback clock), pinned 8; the design's record beside.
  order      5 passes of 29: each pass opens with the three zeros anchors in a seeded order, then the 24 kept tiles and E80's two replicate tiles
             shuffled, one generator Random(175) over the passes (E165's and E173's form). 145 bursts. The dry twin's short order beside.
  lines      every E175 rule's line at the planned n, from the frozen engine (predict_pool8.boot_range through predict_pool8_a2.P(), the rule ids
             E175-A2-*), equal to design-power-e175.json's lines where the planned n is the registration's (16, 8, 24).
  rules      the stops, the admission line and lock, the check of C's rule, the C-log list, the DMA rule (E160's), R0's lines, the paired engine,
             GS's form, the window.
"""
import json
import os
import random
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e175_common as C  # noqa: E402

TOP = C.TOP
PD_SUMS = f"{C.PD_REL}/SHA256SUMS"
PD_SUMS_A2 = f"{C.PD_REL}/SHA256SUMS-a2"
POOL8_SUMS = "tools/claims-v3/m10/POOL8-SHA256SUMS"
E165_QUEUE_REL = "docs/reports/data/2026-11-04-e165-blind7-aifoundry2/aifoundry2/queue.jsonl"
E165_RESULTS_REL = "docs/reports/data/2026-11-04-e165-blind7-aifoundry2/results.json"
SCORE_E165_REL = "tools/claims-v3/e165/score_e165.py"
KINDS_REL = "tools/claims-v3/kinds/kinds.json"
DESIGN_SUMS = f"{C.DESIGN_REL}/SHA256SUMS"
POWER_REL = "tools/claims-v3/e175/design-power-e175.json"
GEN_REL = "tools/claims-v3/e175/make_e175_pool.py"
A1_REL = "tools/claims-v3/e175/E175.md.dated-note-A1.md"
A1PY_REL = "tools/claims-v3/e175/make_e175_pool_a1.py"
A1_SUMS = "tools/claims-v3/e175/SHA256SUMS-e175-a1"
E165_LAUNCHES_REL = "docs/reports/data/2026-11-04-e165-blind7-aifoundry2/aifoundry2/s1/launches.jsonl.gz"
FROZEN_PATHS = [C.MAN_REL, C.POOL_SUMS_REL, C.PRED_REL, C.SELECT_REL, DESIGN_SUMS, C.REGISTRATION_REL, C.REG_SUMS_REL, GEN_REL, POWER_REL,
                A1_REL, A1PY_REL, A1_SUMS,
                C.A2PY_REL, C.P8PY_REL, PD_SUMS, PD_SUMS_A2, C.REG_REL, C.REG_A1_REL, C.REG_A2_REL, C.REG_JSON_REL, POOL8_SUMS,
                C.M9A2_REL, C.PM9A2_REL, C.E165_PRED_REL, "tools/claims-v3/e165/e165_common.py", SCORE_E165_REL, C.WATCHER_REL, C.RUN_HPL_REL,
                E165_QUEUE_REL, E165_RESULTS_REL, E165_LAUNCHES_REL, KINDS_REL, "tools/claims-v3/e173/p8gov.py"]
DRY_SEED = 1750
R0_LINES = {"mhz": 25.0, "w": 3.37}     # E165-R0's (E80's and E83's mean cell, within 25 MHz and 3.37 W)
GROUP_KEYS = ("burst_mhz", "burst_mhz_95", "burst_board_w", "burst_board_95", "burst_D_w", "burst_D_95", "burst_die_rise_c", "burst_die_rise_95",
              "group", "zeros_board_w", "P800_w", "P800_M8_w", "peak_board_w", "peak_board_hi95_w", "peak_over_82w", "delta_w", "delta_source",
              "die_start_source", "die_starts_c", "d_mhz_per_c_die_start", "d_board_per_c_die_start", "d_mhz_per_w_of_delta", "d_board_per_w_of_delta")


def load(rel):
    with open(os.path.join(TOP, rel)) as f:
        return json.load(f)


def git(*a):
    return subprocess.run(["git", "-C", TOP] + list(a), capture_output=True, text=True, timeout=60).stdout.strip()


def read_sums(rel):
    out = {}
    with open(os.path.join(TOP, rel)) as f:
        for ln in f:
            if ln.strip():
                h, p = ln.split(None, 1)
                out[p.strip().lstrip("*")] = h
    return out


def read_sums_base(rel, base_rel):
    """a hash list whose paths are relative to its own directory (the pool's SHA256SUMS): its entries as repo-relative paths"""
    out = {}
    with open(os.path.join(TOP, rel)) as f:
        for ln in f:
            if ln.strip():
                h, p = ln.split(None, 1)
                out[os.path.normpath(os.path.join(base_rel, p.strip().lstrip("*")))] = h
    return out


def frozen_list():
    """every frozen input: sha256 from the tree, matched against each committed list that names it; committed clean; its last commit"""
    lists = {C.REG_SUMS_REL: read_sums(C.REG_SUMS_REL), A1_SUMS: read_sums(A1_SUMS), DESIGN_SUMS: read_sums(DESIGN_SUMS),
             C.POOL_SUMS_REL: read_sums_base(C.POOL_SUMS_REL, C.POOL_REL),
             POOL8_SUMS: read_sums(POOL8_SUMS), PD_SUMS: read_sums(PD_SUMS), PD_SUMS_A2: read_sums(PD_SUMS_A2)}
    sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "hpl"))
    import watcher_q142s as W  # noqa: E402  (its pin of run_hpl.py)
    lists["watcher_q142s.RUN_HPL_SHA256"] = {C.RUN_HPL_REL: W.RUN_HPL_SHA256}
    files, checked, bad = {}, {}, []
    for rel in FROZEN_PATHS:
        p = os.path.join(TOP, rel)
        if not os.path.isfile(p):
            bad.append(f"{rel}: missing")
            continue
        h = C.sha256_file(p)
        if git("status", "--porcelain", "--", rel):
            bad.append(f"{rel}: not committed clean")
        names = []
        for lname, d in lists.items():
            if rel in d:
                names.append(lname)
                if d[rel] != h:
                    bad.append(f"{rel}: sha256 {h}, {lname} says {d[rel]}")
        files[rel] = h
        checked[rel] = {"listed_in": names, "last_commit": git("log", "-1", "--format=%h %ad", "--date=format:%Y-%m-%d %H:%M:%S", "--", rel)}
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    return files, checked


def stratum_of(mhz):
    for k, (lo, hi) in enumerate(C.STRATA_MHZ):
        if lo <= mhz < hi:
            return k + 1
    return None


def e165_spacing():
    """E165's s1 (the same harness, card and burst): the seconds from one run's first launch to the next run's, by the run's measured group"""
    import gzip
    rows = {x["run"]: x for x in load(E165_RESULTS_REL)["run_rows"]}
    first = {}
    with gzip.open(os.path.join(TOP, E165_LAUNCHES_REL), "rt") as f:
        for ln in f:
            if ln.strip():
                x = json.loads(ln)
                if x.get("run") and x.get("t_start_ms") and x["run"] not in first:
                    first[x["run"]] = x["t_start_ms"]
    ks = sorted(first, key=lambda k: first[k])
    gap = {"governed": [], "pinned": []}
    for a, b in zip(ks, ks[1:]):
        ra = rows.get(a)
        if ra and ra.get("burst_mhz") is not None:
            gap["governed" if ra["burst_mhz"] < C.GOVERNED_BELOW_MHZ else "pinned"].append((first[b] - first[a]) / 1000.0)
    return {k: {"n": len(v), "mean_s": round(sum(v) / len(v), 2)} for k, v in gap.items()}


def main():
    files, checked = frozen_list()
    doc = {"_note": "E175's frozen inputs (Q143(g)): the sha256 of every file E175 reads, from the committed tree, each matched against the "
                    "committed hash list that names it (listed_in); e175_common.check_frozen() and every E175 file read this list",
           "files": files, "checked": checked}
    with open(C.FROZEN_FILE, "w") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    A = C.a2p()
    P = A.P()
    pred = load(C.PRED_REL)
    man = C.manifest()
    design = load(C.SELECT_REL)
    power = load(POWER_REL)
    e165 = load(C.E165_PRED_REL)
    m9 = load(C.M9A2_REL)
    assert pred["card"] == "aifoundry2" and pred["manifest"] == C.MAN_REL and pred["manifest_sha256"] == files[C.MAN_REL]
    assert str(design["status"]).startswith(("FILLED", "AT CAP", "AT A1")), design["status"]
    n_all = len(pred["tiles"])
    # the recheck: no session read reproduces the frozen blocks field for field
    rb = A.burst(pred, None, {})
    recheck = {"tiles": 0, "fields": 0, "differ": []}
    for n, rec in rb["tiles"].items():
        recheck["tiles"] += 1
        for lab in ("M10", "M9"):
            want = pred["tiles"][n][lab]["a2_fallback"]
            for k, v in want.items():
                recheck["fields"] += 1
                if rec[lab].get(k) != v:
                    recheck["differ"].append(f"{n}.{lab}.{k}")
    if recheck["differ"] or recheck["tiles"] != n_all:
        raise SystemExit("refused: the frozen predictor does not reproduce the frozen blocks: " + ", ".join(recheck["differ"][:5]))
    gov_set, pin_set = list(design["governed"]), list(design["pinned"])
    B800, S800 = m9["M8_params_for_the_peak"]["B_w"]["800"], m9["M8_params_for_the_peak"]["s_f"]["800"]
    tiles, admission, dry_c = {}, {}, {}
    for n in sorted(pred["tiles"]):
        r, t = pred["tiles"][n], man[n]
        why = C.check_tile(TOP, t)
        if why:
            raise SystemExit(f"refused: {why}")
        assert r["type"] == t["type"] and r["sha256"] == t["sha256"]["whole"]
        a10, a9 = r["M10"]["a2_fallback"], r["M9"]["a2_fallback"]
        est = max(a10["peak_board_hi95_w"], a9["peak_board_hi95_w"])
        if est > C.LIMIT_W or r["admission_82w_out"]:
            raise SystemExit(f"refused: {n} reads {est} W at its 95% upper peak, over 82 W: the selection should have replaced it")
        lab = C.label_of(n)
        zs = n in C.ZEROS_ANCHORS
        st = "zeros" if zs else "governed" if n in gov_set else "pinned" if n in pin_set else None
        if st is None:
            raise SystemExit(f"refused: {n} is in the pool but in no set of the design")
        if st == "governed" and a10["group"] != "governed" or st == "pinned" and a10["group"] != "pinned":
            raise SystemExit(f"refused: {n}: the design's set {st} is not the frozen file's group {a10['group']}")
        tiles[n] = {"type": t["type"], "priority": t["priority"], "anchor_role": r["anchor_role"], "rerun_of": r["rerun_of"], "case": t["case"],
                    "real": bool(t.get("real")), "zeros_anchor": zs, "label": lab, "values": C.tile_value(t), "sha256": t["sha256"],
                    "group": a10["group"], "group_M9": a9["group"], "set": st, "stratum": stratum_of(a10["burst_mhz"]) if st == "governed" else None,
                    "left_out": False, "scored": st in ("governed", "pinned"), "admission_estimate_w": est,
                    "e175": t.get("e175"),
                    "models": {"M10": {"D600_a3_footing_w": r["M10"]["D600_a3_footing_w"], "D600_a3_95": r["M10"]["D600_a3_95"],
                                       "a2_fallback": {k: a10.get(k) for k in GROUP_KEYS}},
                               "M9": {"D600_a3_footing_w": r["M9"]["D600_a3_footing_w"], "D600_a3_95": r["M9"]["D600_a3_95"],
                                      "a2_fallback": {k: a9.get(k) for k in GROUP_KEYS}}}}
        c_ref = (a10["P800_M8_w"] - B800) / S800
        admission[lab] = {"c_ref_w": round(c_ref, 3), "fixed_p800_w": est,
                          "what": "the larger of M10's and M9's frozen 95% upper peaks (E175's frozen predictions, the 82 W rule's own value)"}
        dry_c[C.tile_value(t)] = round(c_ref, 3)
    rep = {}
    for lab in C.REPLICATES:
        r0 = e165["replicate"][lab]
        rep[lab] = dict(r0)
        admission[lab] = {"c_ref_w": None, "fixed_p800_w": r0["estimate_w"], "what": "E165's estimate for E80's tile (predictions-e165.json replicate)"}
    for v in e165["dry_c_w"]:
        if v in {rep[k]["values"] for k in rep}:
            dry_c[v] = e165["dry_c_w"][v]
    admission["rest"] = {"c_ref_w": 0.0, "fixed_p800_w": round(B800, 2), "what": "the idle card (no launch)"}
    run_names = sorted(tiles)
    gov = sorted(gov_set)
    pin = sorted(pin_set)
    scored = sorted(gov + pin)
    strata = {str(k + 1): sorted(n for n in gov if tiles[n]["stratum"] == k + 1) for k in range(len(C.STRATA_MHZ))}
    # the registered order (E165's and E173's form): each pass opens with the zeros anchors, then the rest shuffled; one generator over the passes
    rest = [C.label_of(n) for n in run_names if n not in C.ZEROS_ANCHORS] + list(C.REPLICATES)
    rng = random.Random(C.ORDER_SEED)
    order = []
    for p in range(1, C.PASSES + 1):
        z = [C.label_of(n) for n in C.ZEROS_ANCHORS]
        rng.shuffle(z)
        r = list(rest)
        rng.shuffle(r)
        for lab in z + r:
            order.append({"idx": len(order), "pass": p, "label": lab, "first_of_pass": lab in z})
    per_pass = len(order) // C.PASSES
    assert per_pass == len(scored) + 5 and len(order) == C.PASSES * per_pass
    # the dry twin's short order (the toy card only): passes 1-2 of the zeros anchors, 3 governed and 3 pinned kept tiles, the replicates
    dry_names = [C.label_of(n) for n in gov[:3]] + [C.label_of(n) for n in pin[:3]] + list(C.REPLICATES)
    rd = random.Random(DRY_SEED)
    dry_order = []
    for p in C.DRY_PASSES:
        z = [C.label_of(n) for n in C.ZEROS_ANCHORS]
        rd.shuffle(z)
        r = list(dry_names)
        rd.shuffle(r)
        for lab in z + r:
            dry_order.append({"idx": len(dry_order), "pass": p, "label": lab, "first_of_pass": lab in z})
    # every E175 line at the planned n: the frozen engine with E175's rule ids (E175.md "Decision rules")
    refs = A.e165_refs()
    mn = P.frozen()["reg"]["scoring"]["minimum_tiles"]
    ng, npn, na = len(gov), len(pin), len(scored)
    L = {"_sets": {"scored": na, "governed": ng, "pinned": npn, "strata": {k: len(v) for k, v in strata.items()}}}
    def bl(rule, quantity, set_name, n, ref, src, minimum, unit):
        return {"quantity": quantity, "set": set_name, "n": n, "minimum": minimum, "scored_at_planned_n": n >= minimum, "statistic": "rms", "unit": unit,
                "verdict_form": "PASS at or below the 97.5% point, else FAIL", "seed": P.seed_of(rule),
                "reference": {"source": src, "n": len(ref), "rms": C.rms(ref), "mean": C.mean(ref)},
                "range_95": P.boot_range(ref, n, rule, "rms") if n >= 1 else None}
    src = "tools/claims-v3/e165/predictions-e165.json reference"
    L["E175-A2-G"] = {"quantity": "burst clock, M10 carried", "set": "governed", "n": ng, "minimum": mn["A2_group"], "scored_at_planned_n": ng >= mn["A2_group"],
                      "line": "rms <= 4.0 MHz AND |mean| <= 2.0 MHz", "verdict_form": "PASS if the line holds, else FAIL"}
    L["E175-A2-Bg"] = {"quantity": "board W, M10 carried", "set": "governed", "n": ng, "minimum": mn["A2_group"], "scored_at_planned_n": ng >= mn["A2_group"],
                       "line": "|mean| <= 0.5 W", "verdict_form": "PASS if the line holds, else FAIL"}
    L["E175-A2-Bp"] = {"quantity": "board W, M10 carried", "set": "pinned", "n": npn, "minimum": mn["A2_group"], "scored_at_planned_n": npn >= mn["A2_group"],
                       "line": "|mean| <= 0.5 W AND rms <= 1.0 W", "verdict_form": "PASS if the line holds, else FAIL"}
    L["E175-A2-R2"] = {"quantity": "rank 2 on M10 carried", "components": ["E175-A2-G", "E175-A2-Bg", "E175-A2-Bp"],
                       "verdict_form": "PASS if G, Bg and Bp all PASS; FAIL if any FAILs; else NOT SCORED"}
    L["E175-A2-F1"] = bl("E175-A2-F1", "burst clock", "governed", ng, refs["gov_mhz"], src + ".e2e.governed.mhz_err", mn["A2_group"], "MHz")
    L["E175-A2-F2"] = bl("E175-A2-F2", "burst clock", "pinned", npn, refs["pin_mhz"], src + ".e2e.pinned.mhz_err", mn["A2_group"], "MHz")
    L["E175-A2-W1"] = bl("E175-A2-W1", "board W", "governed", ng, refs["gov_w"], src + ".e2e.governed.w_err", mn["A2_group"], "W")
    L["E175-A2-W2"] = bl("E175-A2-W2", "board W", "pinned", npn, refs["pin_w"], src + ".e2e.pinned.w_err", mn["A2_group"], "W")
    L["E175-A2-M1"] = {"quantity": "board W: M10 carried against M9's part on M9's D", "set": "all scored", "n": na, "minimum": mn["A2_all"],
                       "scored_at_planned_n": na >= mn["A2_all"], "line": "none before the data (paired)", "seed": P.seed_of("E175-A2-M1"),
                       "verdict_form": "BETTER if its upper end < 0, WORSE if its lower end > 0, else NOT RESOLVED"}
    L["E175-A2-H1"] = bl("E175-A2-H1", "burst die rise, aifoundry2's own law", "all scored", na, refs["heat_c"], src + ".heat.rise_err_c", mn["A2_all"], "C")
    # equal to the registration's design-power lines where the planned n is the registration's
    pl = power["lines"]
    eq = {}
    for rule, n in (("E175-A2-F1", ng), ("E175-A2-W1", ng), ("E175-A2-F2", npn), ("E175-A2-W2", npn), ("E175-A2-H1", na)):
        if str(n) in pl.get(rule, {}):
            eq[rule] = pl[rule][str(n)]["range_95"] == L[rule]["range_95"]
    if not all(eq.values()):
        raise SystemExit(f"refused: the lines differ from design-power-e175.json's at the same n: {eq}")
    # the two models' predicted difference on the kept tiles (no line: information for M1)
    d_w = [tiles[n]["models"]["M10"]["a2_fallback"]["burst_board_w"] - tiles[n]["models"]["M9"]["a2_fallback"]["burst_board_w"] for n in scored]
    d_mhz = [tiles[n]["models"]["M10"]["a2_fallback"]["burst_mhz"] - tiles[n]["models"]["M9"]["a2_fallback"]["burst_mhz"] for n in scored]
    sp = e165_spacing()
    n_g = sum(1 for o in order[:per_pass] if (C.name_of(o["label"]) in gov) or o["label"] == "k-fp16-randn")
    n_p = per_pass - n_g
    s_pass = n_g * sp["governed"]["mean_s"] + n_p * sp["pinned"]["mean_s"]
    q = [json.loads(x) for x in open(os.path.join(TOP, E165_QUEUE_REL))]
    s1a = next(x["t_ms"] for x in q if x["kind"] == "session_start" and x.get("name") == "s1")
    q0 = next(x["t_ms"] for x in q if x["kind"] == "queue_start")
    card = {"e165_spacing_s": sp, "per_pass": {"governed_bursts": n_g, "pinned_bursts": n_p, "s": round(s_pass, 1)},
            "e165_before_s1_min": round((s1a - q0) / 60000.0, 2), "e175_bursts": len(order), "e175_session_min": round(C.PASSES * s_pass / 60.0, 1),
            "e175_card_min": round(C.PASSES * s_pass / 60.0 + (s1a - q0) / 60000.0, 1), "session_cap_min": C.CAP_CARD_MIN, "slot_min": C.SLOT_MIN,
            "subset_passes": list(C.SUBSET_PASSES), "subset_bursts": len(C.SUBSET_PASSES) * per_pass,
            "subset_session_min": round(len(C.SUBSET_PASSES) * s_pass / 60.0, 1), "subset_cap_min": C.SUBSET_CAP_MIN, "subset_slot_min": C.SUBSET_SLOT_MIN,
            "source": E165_LAUNCHES_REL + " (one run's first launch to the next run's, by the run's measured group) and " + E165_QUEUE_REL}
    out = {
        "experiment": C.EXPERIMENT, "request": C.REQUEST,
        "card": "aifoundry2 card 0, under its own governor (65 W static TDP, 65 C threshold: read, never set), BL2 0.22.0 by host-boot continuity",
        "_note": "frozen before any claim and any launch; nothing fitted or refitted: every prediction is the frozen predictor's own output for E175's pool, "
                 "copied by key after its sha256 check, or the frozen predictor's burst mode",
        "frozen_list": os.path.relpath(C.FROZEN_FILE, TOP), "frozen_list_sha256": C.sha256_file(C.FROZEN_FILE),
        "commits": {"registration": "c50ff493", "registration_A1": "0e56a875", "pool8_freeze_seed": "4576fb90", "pool8_design_generator": "153b720f",
                    "pool8_registration": "3e97f583", "pool8_registration_A1": "8a8fa34c", "predictor": "9d81d254", "pool8_registration_A2": "68a7c322",
                    "predictor_a2": "97765c0a", "M10": ["6829c9ba", "d1581099", "c996d135"], "M9": ["1f244140", "8dfafae3"],
                    "M9_a2": ["5b98bd5c", "245caffe", "5c98c0c5"], "E165": ["3ef06839", "a5c56d17", "e3c4eafc", "fe6f4862", "a509ff8b"],
                    "E165_data": "4c6665f0", "E173_kit": ["c8064454", "5a2a9ba0", "5db9df6b", "c9a3e40a"], "watcher": ["abe6b0f2", "33661416"],
                    "runbook_v3_1": "0d2cb5dd", "ccheck": "4946a992"},
        "primary": {"model": "M10 carried by rule E (POOL8-REGISTRATION.md section 5): predict_pool8_a2.py burst on E175's frozen predictions, M10 block "
                             "(predict_m9_a2.burst on M10's D600 at aifoundry3's footing and the nominal rate, s = 1)",
                    "beside": "M9's aifoundry2 part on M9's D (the same call's M9 block): E175-A2-M1's comparison",
                    "anchors": "the session's zeros-anchor reads: per format, every counted burst of its anchor7_zeros tile, {burst_w, burst_mhz, die_start}; "
                               "burst() keeps those at 795 MHz or more, fills a format with none from the others, the frozen fallback if none at all",
                    "die_starts": "the tile's own counted bursts' die starts (one per counted pass)",
                    "groups": "fixed by the frozen file: tiles.<name>.group = M10.a2_fallback.group (A2-3 (f)); the design's sets equal them"},
        "recheck_frozen_blocks": recheck,
        "tiles": tiles, "left_out": [], "n_run": len(run_names), "run": run_names,
        "sets": {"scored": scored, "governed": gov, "pinned": pin, "strata": strata},
        "strata_mhz": [list(x) for x in C.STRATA_MHZ],
        "design": {"file": C.SELECT_REL, "sha256": files[C.SELECT_REL], "status": design["status"], "stopped_at_index": design["stopped_at_index"],
                   "upto": design["upto"]},
        "replicate": rep, "order": order, "order_seed": C.ORDER_SEED, "passes": C.PASSES, "runs_per_pass": per_pass,
        "dry_order": dry_order, "dry_order_seed": DRY_SEED,
        "lines": L, "lines_equal_design_power": eq, "design_power_sha256": files[POWER_REL],
        "reference": {"source": "tools/claims-v3/e165/predictions-e165.json reference (predict_pool8_a2.e165_refs)", **refs},
        "forecast_information_only": {"power_pct": power["power_pct"], "source": POWER_REL,
                                      "models_differ_on_the_kept_tiles": {"board_w_median_abs": sorted(abs(x) for x in d_w)[len(d_w) // 2],
                                                                          "board_w_max_abs": max(abs(x) for x in d_w), "mhz_max_abs": max(abs(x) for x in d_mhz),
                                                                          "board_w_over_0p2": sum(1 for x in d_w if abs(x) > 0.2), "n": len(d_w)}},
        "admission": admission, "dry_c_w": dry_c,
        "dma": {"e143": e165["dma"]["e143"], "source": "tools/claims-v3/e165/predictions-e165.json dma (E143's launches, E160's rule)"},
        "relation": {"B800": B800, "s800": S800, "source": f"{C.M9A2_REL} M8_params_for_the_peak (E105 reports c; no rule reads it)"},
        "card_time": card,
        "rules": {"safety": C.STOPS, "limit_w": C.LIMIT_W, "peak_lock_w": C.PEAK_LOCK_W, "min_passes": C.MIN_PASSES,
                  "minimum_tiles": mn, "seed_base": P.frozen()["reg"]["scoring"]["seed_base"],
                  "bootstrap_draws": P.frozen()["reg"]["scoring"]["bootstrap_draws"], "paired_draws": P.frozen()["reg"]["scoring"]["paired_draws"],
                  "paired_engine": "rng = random.Random(80000 + the sum of the rule id's character codes); 20,000 draws, each n tile indices drawn with "
                                   "replacement (rng.randrange(n), n times) and rms(a) - rms(b) over them; sorted; the 95% interval is "
                                   "[vals[int(0.025 x 20000)], vals[int(0.975 x 20000) - 1]] (A2-3 (a)'s index form); point rms(a) - rms(b)",
                  "GS": "reported: the least-squares slope of the governed clock error on M10 carried's predicted clock over the governed set, with the "
                        "2.5-97.5% range of 20,000 tile-resampled slopes (random.Random('E175-GS'))",
                  "R0": R0_LINES,
                  "c_check": "a burst counts only if every SPARSITY line of it has a C record that reads PASS in ccheck.py check (bit-exact; ROUNDING, "
                             "UNMODELLED, FAIL and a missing record are not PASS); a tile with any launch not PASS leaves every scored set",
                  "c_log_sessions": list(C.C_LOG_SESSIONS),
                  "c_log_rule": "smoke, stoptest-board and every BURST session s1-s6 the queue started that ran a work launch must carry a C log and a "
                                "finished check of it (the v3 list); stoptest-die runs no launch and carries none; a missing one: the collection stops "
                                "(14) and the scorer refuses (exit 5)",
                  "dma": {"projected_held_max_s": 7.2, "budget_s": 7.5, "launches": 17,
                          "rule": "E160's: the smoke's median launch gap less E143's smoke median is the C log's extra time per launch (delta); the session "
                                  "runs only if E143's longest device-held time (s1, 6.57 s) + 17 x delta <= 7.2 s, else QUEUE-HALT"},
                  "window": {"after_e173_s": C.AFTER_E173_S, "default_last_start": "21:00 PST", "default_last_end": "22:00 PST",
                             "rule": "E175.md, The window: after E173's queue_end plus 10 minutes, never beside it; the full session only if its 48-minute "
                                     "slot ends by the go's last end, else the subset's 31-minute slot, else skipped"}},
    }
    p = os.path.join(HERE, "predictions-e175.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1, sort_keys=False)
    print(f"frozen-sha256-e175.json: {len(files)} files, every one matched against the committed list that names it "
          f"({sum(1 for v in checked.values() if v['listed_in'])} listed; the others committed clean and recorded with their last commit)")
    print(f"predictions-e175.json sha256 {C.sha256_file(p)}")
    print(f"recheck: no session read reproduces the frozen M10 and M9 blocks on {recheck['tiles']} tiles, {recheck['fields']} fields, "
          f"{len(recheck['differ'])} differ")
    print(f"{len(tiles)} tiles; run {len(run_names)} pool tiles + {len(C.REPLICATES)} replicates; scored {len(scored)} (governed {len(gov)}, pinned {len(pin)})")
    print(f"strata: " + json.dumps({k: len(v) for k, v in strata.items()}))
    print(f"order: {len(order)} bursts, {C.PASSES} passes of {per_pass}, each opening with the zeros anchors; seed {C.ORDER_SEED}; dry twin "
          f"{len(dry_order)} runs (passes {list(C.DRY_PASSES)})")
    print(f"lines equal design-power-e175.json's at the same n: {eq}")
    for k, v in L.items():
        if k.startswith("_"):
            print(f"  {k}: {json.dumps(v)}")
            continue
        print(f"  {k:11s} n {v.get('n')} min {v.get('minimum')} scored_at_planned_n {v.get('scored_at_planned_n')} "
              f"{'line ' + str(v.get('line')) if v.get('line') else ''}{'range ' + str([round(x, 4) for x in v['range_95']]) if v.get('range_95') else ''}")
    print("models differ on the kept tiles (information for M1): " + json.dumps(out["forecast_information_only"]["models_differ_on_the_kept_tiles"]))
    top = sorted(((v["fixed_p800_w"], k) for k, v in admission.items()), reverse=True)[:5]
    print(f"admission: highest estimates {top}; limit {C.LIMIT_W} W, lock {C.PEAK_LOCK_W} W; stops {C.STOPS}")
    print("card time:", json.dumps(card))
    for n, t in sorted(tiles.items(), key=lambda kv: (kv[1]["set"], kv[1]["stratum"] or 0, kv[1]["type"], kv[0])):
        a = t["models"]["M10"]["a2_fallback"]
        b = t["models"]["M9"]["a2_fallback"]
        print(f"  {t['set']:8s} S{t['stratum'] or '-'} {t['type']} {n:40s} M10 {a['burst_mhz']:7.2f} MHz {a['burst_board_w']:7.3f} W "
              f"rise {a['burst_die_rise_c']:5.2f}; M9 {b['burst_mhz']:7.2f} MHz {b['burst_board_w']:7.3f} W; est {t['admission_estimate_w']:6.2f} W")


if __name__ == "__main__":
    main()
