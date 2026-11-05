#!/usr/bin/env python3
"""E173 (Q142(kg)): writes frozen-sha256-e173.json and predictions-e173.json, everything E173 scores, frozen before any claim and any launch.
No card. NOTHING IS FITTED OR REFITTED HERE: every predicted number is Q142(x)'s (predictions-pool8-aifoundry2.json, lab 4576fb90), copied by key
after its sha256 is checked, or the frozen predictor's own output (Q142(p)'s predict_pool8_a2.py burst mode, 97765c0a), called unchanged.

    python3 -B tools/claims-v3/e173/make_predictions_e173.py > tools/claims-v3/e173/predictions-e173.txt

WHAT IT WRITES
  frozen-sha256-e173.json  every input E173 reads, with its sha256 from the committed tree, each matched against the committed hash list that
             already names it (the freeze's SHA256SUMS, the predictor's SHA256SUMS and SHA256SUMS-a2, POOL8-SHA256SUMS, the watcher's own
             pin of run_hpl.py), and the last commit that touched it; refused if any file differs from its list or is not committed clean.
  recheck    predict_pool8_a2.burst with no session read (anchors None, no die starts) reproduces every tile's frozen M10.a2_fallback and
             M9.a2_fallback block field for field (64 tiles, both models): the primary's recompute is the frozen file's own code path.
  tiles      pool 8's 64 tiles: type, priority, anchor role, re-run of, case, real, the run value and label, the manifest's sha256; LEFT OUT
             (by name: the 11 tiles the frozen file marks admission_82w_out, the larger of M10's and M9's 95% upper peaks over 82 W); the GROUP,
             fixed by the frozen file (M10.a2_fallback.group: governed = M10 carried predicts the burst below 795 MHz at the fallback and T_ref);
             SCORED = N1 less the 82 W admissions (registration section 7, dated note A2-3 (f)); the admission estimate (the same larger peak).
  sets       scored 24 (governed 3, pinned 21), left out 11, run 53, and the two REPORTED governed sets GX7 (the governed new kinds of N1 and of
             priority 2) and GX10 (GX7 and the three fp16 random anchors), never a verdict.
  order      3 passes of 55: each pass opens with the three zeros anchors in a seeded order, then the other 50 admitted tiles and E80's two
             replicate tiles shuffled, one generator Random(173) over the passes (E165's form). 165 bursts. The dry twin's short order beside.
  lines      every P8 rule's line for aifoundry2 at the planned n, from predict_pool8_a2.lines_a2 (the same function and seed as the committed
             intervals-pool8.json, which it must equal field for field), and the registered verdict form of each.
  rules      the stops, the admission line and lock, the check of C's rule, the C-log list, the DMA rule (E160's), R0's lines, the paired engine.
"""
import json
import os
import random
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e173_common as C  # noqa: E402

TOP = C.TOP
FREEZE_SUMS = f"{C.FREEZE_REL}/SHA256SUMS"
PD_SUMS = f"{C.PD_REL}/SHA256SUMS"
PD_SUMS_A2 = f"{C.PD_REL}/SHA256SUMS-a2"
POOL8_SUMS = "tools/claims-v3/m10/POOL8-SHA256SUMS"
E165_QUEUE_REL = "docs/reports/data/2026-11-04-e165-blind7-aifoundry2/aifoundry2/queue.jsonl"
E165_RESULTS_REL = "docs/reports/data/2026-11-04-e165-blind7-aifoundry2/results.json"
SCORE_E165_REL = "tools/claims-v3/e165/score_e165.py"
KINDS_REL = "tools/claims-v3/kinds/kinds.json"
FROZEN_PATHS = [C.MAN_REL, C.MANIFEST_REL, C.POOL_SUMS_REL, C.PRED_REL, C.INTERVALS_REL, FREEZE_SUMS, C.FREEZE_NOTE_REL,
                C.A2PY_REL, C.P8PY_REL, PD_SUMS, PD_SUMS_A2, C.REG_REL, C.REG_A1_REL, C.REG_A2_REL, C.REG_JSON_REL, POOL8_SUMS,
                C.M9A2_REL, C.PM9A2_REL, C.E165_PRED_REL, "tools/claims-v3/e165/e165_common.py", SCORE_E165_REL, C.WATCHER_REL, C.RUN_HPL_REL,
                E165_QUEUE_REL, E165_RESULTS_REL, KINDS_REL]
DRY_SEED = 1730
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


def frozen_list():
    """every frozen input: sha256 from the tree, matched against each committed list that names it; committed clean; its last commit"""
    # every list is repo-relative (each is checked from the repo's top: predict_pool8.read_sums, POOL8-REGISTRATION.md section 9)
    lists = {FREEZE_SUMS: read_sums(FREEZE_SUMS), POOL8_SUMS: read_sums(POOL8_SUMS), PD_SUMS: read_sums(PD_SUMS), PD_SUMS_A2: read_sums(PD_SUMS_A2)}
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


def main():
    files, checked = frozen_list()
    doc = {"_note": "E173's frozen inputs (Q142(kg)): the sha256 of every file E173 reads, from the committed tree, each matched against the "
                    "committed hash list that names it (listed_in); e173_common.check_frozen() and every E173 file read this list",
           "files": files, "checked": checked}
    with open(C.FROZEN_FILE, "w") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    A = C.a2p()
    P = A.P()
    pred = load(C.PRED_REL)
    iv = load(C.INTERVALS_REL)
    man = C.manifest()
    e165 = load(C.E165_PRED_REL)
    m9 = load(C.M9A2_REL)
    assert pred["card"] == "aifoundry2" and pred["manifest"] == C.MAN_REL and pred["manifest_sha256"] == files[C.MAN_REL]
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
    if recheck["differ"] or recheck["tiles"] != 64:
        raise SystemExit("refused: the frozen predictor does not reproduce the frozen blocks: " + ", ".join(recheck["differ"][:5]))
    S = pred["sets"]
    N1 = set(S["N1"])
    out82 = sorted(n for n, r in pred["tiles"].items() if r["admission_82w_out"])
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
        assert bool(est > C.LIMIT_W) == bool(r["admission_82w_out"]), n
        lab = C.label_of(n)
        run = not r["admission_82w_out"]
        tiles[n] = {"type": t["type"], "priority": t["priority"], "anchor_role": r["anchor_role"], "rerun_of": r["rerun_of"], "case": t["case"],
                    "real": bool(t.get("real")), "zeros_anchor": n in C.ZEROS_ANCHORS, "label": lab, "values": C.tile_value(t), "sha256": t["sha256"],
                    "group": a10["group"], "group_M9": a9["group"], "left_out": not run, "N1": n in N1, "scored": run and n in N1,
                    "admission_estimate_w": est,
                    "models": {"M10": {"D600_a3_footing_w": r["M10"]["D600_a3_footing_w"], "D600_a3_95": r["M10"]["D600_a3_95"],
                                       "a2_fallback": {k: a10.get(k) for k in GROUP_KEYS}},
                               "M9": {"D600_a3_footing_w": r["M9"]["D600_a3_footing_w"], "D600_a3_95": r["M9"]["D600_a3_95"],
                                      "a2_fallback": {k: a9.get(k) for k in GROUP_KEYS}}}}
        if not run:
            tiles[n]["left_out_why"] = (f"the larger of M10's and M9's 95% upper peaks is {est} W, over 82 W: marked admission_82w_out in the frozen "
                                        "file, left out by name, not duty-cycled (no frozen prediction exists for a duty-cycled burst)")
            continue
        c_ref = (a10["P800_M8_w"] - B800) / S800
        admission[lab] = {"c_ref_w": round(c_ref, 3), "fixed_p800_w": est,
                          "what": "the larger of M10's and M9's frozen 95% upper peaks (predictions-pool8-aifoundry2.json, the 82 W rule's own value)"}
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
    run_names = [n for n in sorted(tiles) if not tiles[n]["left_out"]]
    scored = sorted(n for n in run_names if tiles[n]["scored"])
    gov = sorted(n for n in scored if tiles[n]["group"] == "governed")
    pin = sorted(n for n in scored if tiles[n]["group"] == "pinned")
    gx7 = sorted(n for n in run_names if tiles[n]["group"] == "governed" and not tiles[n]["rerun_of"] and not tiles[n]["anchor_role"])
    gx10 = sorted(gx7 + [n for n in run_names if tiles[n]["group"] == "governed" and tiles[n]["anchor_role"] in ("scale", "check")])
    _, g2, p2, o2 = A.governed_sets(pred)
    assert g2 == gov and p2 == pin and o2 == sorted(set(out82) & N1), "the scored sets differ from predict_pool8_a2.governed_sets"
    # the registered order (E165's form): each pass opens with the zeros anchors, then the rest shuffled; one generator over the passes
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
    assert per_pass == 55 and len(order) == 165
    # the dry twin's short order (the toy card only): passes 1-2 of the zeros anchors, the 3 governed scored tiles, 3 pinned scored tiles, the replicates
    dry_names = [C.label_of(n) for n in gov] + [C.label_of(n) for n in pin[:3]] + list(C.REPLICATES)
    rd = random.Random(DRY_SEED)
    dry_order = []
    for p in C.DRY_PASSES:
        z = [C.label_of(n) for n in C.ZEROS_ANCHORS]
        rd.shuffle(z)
        r = list(dry_names)
        rd.shuffle(r)
        for lab in z + r:
            dry_order.append({"idx": len(dry_order), "pass": p, "label": lab, "first_of_pass": lab in z})
    # every P8 line for aifoundry2 at the planned n: predict_pool8_a2's own function and seed, equal to the committed intervals
    L = A.lines_a2(pred)
    committed = iv["cards"]["aifoundry2"]["rules"]
    same = json.dumps(L, sort_keys=True, default=str) == json.dumps(committed, sort_keys=True, default=str)
    if not same:
        raise SystemExit("refused: predict_pool8_a2.lines_a2 does not reproduce intervals-pool8.json's aifoundry2 block")
    refs = A.e165_refs()
    # a forecast, registered (information only): Bp's two lines at n = 21 drawn from the end-to-end pinned reference
    fr = random.Random(1731)
    hit = {"Bp_mean": 0, "Bp_rms": 0, "Bp_both": 0}
    draws = 20000
    for _ in range(draws):
        e = [refs["pin_w"][fr.randrange(len(refs["pin_w"]))] for _ in range(len(pin))]
        a, b = abs(C.mean(e)) <= 0.5, C.rms(e) <= 1.0
        hit["Bp_mean"] += a
        hit["Bp_rms"] += b
        hit["Bp_both"] += a and b
    forecast = {k: round(v / draws, 4) for k, v in hit.items()}
    # card time from E165's committed queue (the same harness, card and burst): its s1's seconds per burst
    q = [json.loads(x) for x in open(os.path.join(TOP, E165_QUEUE_REL))]
    s1a = next(x["t_ms"] for x in q if x["kind"] == "session_start" and x.get("name") == "s1")
    s1b = next(x["t_ms"] for x in q if x["kind"] == "session_end" and x.get("name") == "s1")
    q0 = next(x["t_ms"] for x in q if x["kind"] == "queue_start")
    n165 = load(E165_RESULTS_REL)["runs"]
    spb = (s1b - s1a) / 1000.0 / n165
    card = {"e165_s1_bursts": n165, "e165_s1_min": round((s1b - s1a) / 60000.0, 2), "s_per_burst": round(spb, 2),
            "e165_before_s1_min": round((s1a - q0) / 60000.0, 2), "e173_bursts": len(order), "e173_session_min": round(len(order) * spb / 60.0, 1),
            "e173_card_min": round(len(order) * spb / 60.0 + (s1a - q0) / 60000.0, 1), "session_cap_min": C.CAP_CARD_MIN, "slot_min": C.SLOT_MIN,
            "subset_passes": list(C.SUBSET_PASSES), "subset_bursts": 2 * per_pass, "subset_session_min": round(2 * per_pass * spb / 60.0, 1),
            "subset_cap_min": C.SUBSET_CAP_MIN, "subset_slot_min": C.SUBSET_SLOT_MIN, "source": E165_QUEUE_REL + " (s1 start and end) and " + E165_RESULTS_REL + " runs"}
    out = {
        "experiment": C.EXPERIMENT, "request": C.REQUEST,
        "card": "aifoundry2 card 0, under its own governor (65 W static TDP, 65 C threshold: read, never set), BL2 0.22.0 by host-boot continuity",
        "_note": "frozen before any claim and any launch; nothing fitted or refitted: every prediction is Q142(x)'s, copied by key after its sha256 check, "
                 "or the frozen predictor's own output",
        "frozen_list": os.path.relpath(C.FROZEN_FILE, TOP), "frozen_list_sha256": C.sha256_file(C.FROZEN_FILE),
        "commits": {"pool8_freeze": "4576fb90", "pool8_A1": "ebf68c52", "pool8_note1": "dfe226f1", "pool8_design": "153b720f",
                    "registration": "3e97f583", "registration_A1": "8a8fa34c", "predictor": "9d81d254", "registration_A2": "68a7c322",
                    "predictor_a2": "97765c0a", "M10": ["6829c9ba", "d1581099", "c996d135"], "M9": ["1f244140", "8dfafae3"],
                    "M9_a2": ["5b98bd5c", "245caffe", "5c98c0c5"], "E165": ["3ef06839", "a5c56d17", "e3c4eafc", "fe6f4862", "a509ff8b"],
                    "E165_data": "4c6665f0", "watcher": ["abe6b0f2", "33661416"], "runbook_v3_1": "0d2cb5dd", "ccheck": "4946a992"},
        "primary": {"model": "M10 carried by rule E (POOL8-REGISTRATION.md section 5): predict_pool8_a2.py burst on predictions-pool8-aifoundry2.json, "
                             "M10 block (predict_m9_a2.burst on M10's D600 at aifoundry3's footing and the nominal rate, s = 1)",
                    "beside": "M9's aifoundry2 part on M9's D (the same call's M9 block): A2-M1's comparison",
                    "anchors": "the session's zeros-anchor reads: per format, every counted burst of its anchor7_zeros tile, {burst_w, burst_mhz, die_start}; "
                               "burst() keeps those at 795 MHz or more, fills a format with none from the others, the frozen fallback if none at all",
                    "die_starts": "the tile's own counted bursts' die starts (one per counted pass)",
                    "groups": "fixed by the frozen file: tiles.<name>.group = M10.a2_fallback.group (A2-3 (f))"},
        "recheck_frozen_blocks": recheck,
        "tiles": tiles, "left_out": out82, "n_run": len(run_names), "run": run_names,
        "sets": {"scored": scored, "governed": gov, "pinned": pin, "N1_left_out_82w": sorted(set(out82) & N1), "GX7_reported": gx7, "GX10_reported": gx10},
        "replicate": rep, "order": order, "order_seed": C.ORDER_SEED, "passes": C.PASSES, "runs_per_pass": per_pass,
        "dry_order": dry_order, "dry_order_seed": DRY_SEED,
        "lines": L, "lines_equal_intervals_pool8": same, "intervals_sha256": files[C.INTERVALS_REL],
        "reference": {"source": "tools/claims-v3/e165/predictions-e165.json reference (predict_pool8_a2.e165_refs)", **refs},
        "forecast_information_only": {"Bp_lines_at_n21_from_e2e_pinned": forecast, "draws": draws, "seed": 1731},
        "admission": admission, "dry_c_w": dry_c,
        "dma": {"e143": e165["dma"]["e143"], "source": "tools/claims-v3/e165/predictions-e165.json dma (E143's launches, E160's rule)"},
        "relation": {"B800": B800, "s800": S800, "source": f"{C.M9A2_REL} M8_params_for_the_peak (E105 reports c; no rule reads it)"},
        "card_time": card,
        "rules": {"safety": C.STOPS, "limit_w": C.LIMIT_W, "peak_lock_w": C.PEAK_LOCK_W, "min_passes": C.MIN_PASSES,
                  "minimum_tiles": P.frozen()["reg"]["scoring"]["minimum_tiles"], "seed_base": P.frozen()["reg"]["scoring"]["seed_base"],
                  "bootstrap_draws": P.frozen()["reg"]["scoring"]["bootstrap_draws"], "paired_draws": P.frozen()["reg"]["scoring"]["paired_draws"],
                  "paired_engine": "rng = random.Random(80000 + the sum of the rule id's character codes); 20,000 draws, each n tile indices drawn with "
                                   "replacement (rng.randrange(n), n times) and rms(a) - rms(b) over them; sorted; the 95% interval is "
                                   "[vals[int(0.025 x 20000)], vals[int(0.975 x 20000) - 1]] (A2-3 (a)'s index form); point rms(a) - rms(b)",
                  "R0": R0_LINES,
                  "c_check": "a burst counts only if every SPARSITY line of it has a C record that reads PASS in ccheck.py check (bit-exact; ROUNDING, "
                             "UNMODELLED, FAIL and a missing record are not PASS); a tile with any launch not PASS leaves every scored set",
                  "c_log_sessions": list(C.C_LOG_SESSIONS),
                  "c_log_rule": "smoke, stoptest-board and every BURST session s1-s6 the queue started that ran a work launch must carry a C log and a "
                                "finished check of it; stoptest-die runs no launch and carries none; a missing one: the collection stops (14) and the "
                                "scorer refuses (exit 5)",
                  "dma": {"projected_held_max_s": 7.2, "budget_s": 7.5, "launches": 17,
                          "rule": "E160's: the smoke's median launch gap less E143's smoke median is the C log's extra time per launch (delta); the session "
                                  "runs only if E143's longest device-held time (s1, 6.57 s) + 17 x delta <= 7.2 s, else QUEUE-HALT"}},
    }
    p = os.path.join(HERE, "predictions-e173.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1, sort_keys=False)
    print(f"frozen-sha256-e173.json: {len(files)} files, every one matched against the committed list that names it "
          f"({sum(1 for v in checked.values() if v['listed_in'])} listed; the others committed clean and recorded with their last commit)")
    print(f"predictions-e173.json sha256 {C.sha256_file(p)}")
    print(f"recheck: no session read reproduces the frozen M10 and M9 blocks on {recheck['tiles']} tiles, {recheck['fields']} fields, "
          f"{len(recheck['differ'])} differ")
    print(f"{len(tiles)} tiles; left out by name ({len(out82)}): {out82}")
    print(f"run {len(run_names)} pool tiles + {len(C.REPLICATES)} replicates; scored {len(scored)} (governed {len(gov)}, pinned {len(pin)})")
    print(f"governed scored: {gov}")
    print(f"GX7 (reported) {len(gx7)}: {gx7}")
    print(f"GX10 (reported) {len(gx10)}: {gx10}")
    print(f"order: {len(order)} bursts, {C.PASSES} passes of {per_pass}, each opening with the zeros anchors; seed {C.ORDER_SEED}; dry twin "
          f"{len(dry_order)} runs (passes {list(C.DRY_PASSES)})")
    print(f"lines equal intervals-pool8.json's aifoundry2 block: {same}")
    for k, v in L.items():
        if k.startswith("_"):
            print(f"  {k}: {json.dumps(v)}")
            continue
        print(f"  {k:10s} n {v.get('n')} min {v.get('minimum')} scored_at_planned_n {v.get('scored_at_planned_n')} "
              f"{'line ' + str(v.get('line')) if v.get('line') else ''}{'range ' + str([round(x, 4) for x in v['range_95']]) if v.get('range_95') else ''}")
    print(f"forecast (information only) Bp at n {len(pin)} from the end-to-end pinned reference: {json.dumps(forecast)}")
    top = sorted(((v["fixed_p800_w"], k) for k, v in admission.items()), reverse=True)[:5]
    print(f"admission: highest estimates {top}; limit {C.LIMIT_W} W, lock {C.PEAK_LOCK_W} W; stops {C.STOPS}")
    print("card time:", json.dumps(card))
    for n, t in sorted(tiles.items(), key=lambda kv: (kv[1]["left_out"], kv[1]["group"], kv[1]["type"], kv[0])):
        a = t["models"]["M10"]["a2_fallback"]
        tag = "LEFT OUT " if t["left_out"] else ("input    " if t["zeros_anchor"] else ("scored   " if t["scored"] else "run      "))
        print(f"  {tag}{t['group']:8s} p{t['priority']} {t['case']} {n:42s} M10 {a['burst_mhz']:7.2f} MHz {a['burst_board_w']:7.3f} W "
              f"rise {a['burst_die_rise_c']:5.2f} est {t['admission_estimate_w']:6.2f} W")


if __name__ == "__main__":
    main()
