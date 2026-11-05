#!/usr/bin/env python3
"""E174 (Q142(kg)): writes frozen-sha256-e174.json and predictions-e174.json, the machine form of the registration, frozen before any E174 data.
No card. It fits nothing and adds no prediction: every model number is Q142(x)'s (predictions-pool8-aifoundry1c0.json, lab 4576fb90), copied by
key after its sha256 is checked, or the frozen predictor's own code (predict_pool8_a2.py, 97765c0a); and it writes beside them what E174's rules
need: the admission by E170's formula, the tiles left out by name, the tiers, the registered order, the lines at the planned scored n, the
references, the stops and the rules.

    python3 -B tools/claims-v3/e174/make_predictions_e174.py > tools/claims-v3/e174/predictions-e174.txt

THE ADMISSION (E170's, unchanged in form; the round's brief: "E174 applies E170's admission and its 66 W / 72 C stops; the predictions hold no
card-0 admission"): a tile runs only if its card-0 estimate is at most 60 W. The estimate is e170_common.est_card0 (E170.md "Safety") on the
tile's aifoundry2 admission value, which for pool 8 is the larger of M10's and M9's frozen 95% upper peaks (the 82 W rule's own value, rule E's
section 5), less the gap between that block's predicted 800 MHz zeros level and card 0's measured one (E84's p800), less 5% of the block's
predicted switching at 800 MHz, taken for each model's block and the LARGER of the two kept (the conservative one). Tier A at most 52 W, tier B
52-60 W.
"""
import copy
import json
import os
import random
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e174_common as C  # noqa: E402

TOP = C.TOP
C173 = C.C173
FREEZE_SUMS = f"{C173.FREEZE_REL}/SHA256SUMS"
POOL8_SUMS = "tools/claims-v3/m10/POOL8-SHA256SUMS"
E170_RES_REL = "docs/reports/data/2026-11-04-e170-blind7-card0/results.json"
E170_QUEUE_REL = "docs/reports/data/2026-11-04-e170-blind7-card0/aifoundry1-c0/queue.jsonl"
E170_GATE_REL = "docs/reports/data/2026-11-04-e170-blind7-card0/aifoundry1-c0/state-gate.json"
E170_HARNESS_REL = "tools/claims-v3/e170/harness-e170.json"
E84_REL = C.C170.E84_RESULTS_REL
FROZEN_PATHS = [C.MAN_REL, C173.MANIFEST_REL, C173.POOL_SUMS_REL, C.PRED_REL, C.INTERVALS_REL, FREEZE_SUMS, C173.FREEZE_NOTE_REL, C173.A2PY_REL,
                C173.P8PY_REL, f"{C173.PD_REL}/SHA256SUMS", f"{C173.PD_REL}/SHA256SUMS-a2", C173.REG_REL, C173.REG_A1_REL, C173.REG_A2_REL,
                C173.REG_JSON_REL, POOL8_SUMS, C173.M9A2_REL, C173.PM9A2_REL, C173.E165_PRED_REL, "tools/claims-v3/e165/e165_common.py",
                "tools/claims-v3/e165/score_e165.py", "tools/claims-v3/e170/e170_common.py", "tools/claims-v3/e170/score_e170.py", C.GUARD_REL,
                E170_HARNESS_REL, E84_REL, C.C170.E118_README_REL, E170_RES_REL, E170_QUEUE_REL, E170_GATE_REL, C173.WATCHER_REL, C173.RUN_HPL_REL]
DRY_SEED = "E174|dry"


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
    lists = {FREEZE_SUMS: read_sums(FREEZE_SUMS), POOL8_SUMS: read_sums(POOL8_SUMS), "predictor SHA256SUMS": read_sums(f"{C173.PD_REL}/SHA256SUMS"),
             "predictor SHA256SUMS-a2": read_sums(f"{C173.PD_REL}/SHA256SUMS-a2")}
    h170 = load(E170_HARNESS_REL)["files_sha256"]
    lists[E170_HARNESS_REL] = h170
    lists["e170_common.PARENT_SHA256"] = dict(C.C170.PARENT_SHA256)
    sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "hpl"))
    import watcher_q142s as W  # noqa: E402
    lists["watcher_q142s.RUN_HPL_SHA256"] = {C173.RUN_HPL_REL: W.RUN_HPL_SHA256}
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
    with open(C.FROZEN_FILE, "w") as f:
        json.dump({"_note": "E174's frozen inputs (Q142(kg)): the sha256 of every file E174 reads, from the committed tree, each matched against the "
                            "committed hash list that names it (listed_in); e174_common.check_frozen() and every E174 file read this list",
                   "files": files, "checked": checked}, f, indent=1, sort_keys=True)
    A = C.a2p()
    P = A.P()
    A2 = P.a2_part()
    pred = load(C.PRED_REL)
    iv = load(C.INTERVALS_REL)
    man = C.manifest()
    E84 = load(E84_REL)
    E170 = load(E170_RES_REL)
    assert pred["card"] == "aifoundry1c0" and pred["manifest"] == C.MAN_REL and pred["manifest_sha256"] == files[C.MAN_REL]
    z0 = {t: E84["cells"][k]["p800_w"] for t, k in C.E84_ZEROS_P800_KEYS.items()}
    # the recheck: the frozen a2_fallback blocks are predict_m9_a2.burst's own output with no session read, and card0_fallback is kappa0 x its D
    recheck = {"tiles": 0, "fields": 0, "differ": []}
    for n, r in pred["tiles"].items():
        recheck["tiles"] += 1
        for lab in ("M10", "M9"):
            blk = r[lab]
            lo, hi = blk["D600_a3_95"]
            again = A2.burst(blk["D600_a3_footing_w"], r["type"], anchors=None, die_starts=None, D_band_hw=0.5 * (hi - lo))
            for k, v in blk["a2_fallback"].items():
                recheck["fields"] += 1
                if again.get(k) != v:
                    recheck["differ"].append(f"{n}.{lab}.{k}")
            recheck["fields"] += 1
            if blk["card0_fallback"]["burst_D_w"] != round(C.KAPPA0 * blk["a2_fallback"]["burst_D_w"], 3):
                recheck["differ"].append(f"{n}.{lab}.card0_fallback.burst_D_w")
    if recheck["differ"] or recheck["tiles"] != 64:
        raise SystemExit("refused: the frozen card-0 blocks do not reproduce: " + ", ".join(recheck["differ"][:5]))
    S = pred["sets"]
    N1 = set(S["N1"])
    tiles, left = {}, {}
    for n in sorted(pred["tiles"]):
        r, t = pred["tiles"][n], man[n]
        why = C.check_tile(TOP, t)
        if why:
            raise SystemExit(f"refused: {why}")
        a10, a9 = r["M10"]["a2_fallback"], r["M9"]["a2_fallback"]
        adm = max(a10["peak_board_hi95_w"], a9["peak_board_hi95_w"])
        e10 = C.est_card0(adm, a10["P800_w"], a10["zeros_board_w"], z0[t["type"]])
        e9 = C.est_card0(adm, a9["P800_w"], a9["zeros_board_w"], z0[t["type"]])
        est = max(e10, e9)
        row = {"type": t["type"], "label": C.label_of(n), "values": C.tile_value(t), "priority": t["priority"], "anchor_role": r["anchor_role"],
               "rerun_of": r["rerun_of"], "case": t["case"], "real": bool(t.get("real")), "N1": n in N1, "zeros_anchor": n in C.ZEROS_ANCHORS,
               "est_card0_peak_w": round(est, 3), "est_card0_by_model_w": {"M10": round(e10, 3), "M9": round(e9, 3)}, "adm_a2_peak_w": adm,
               "a2_group_M10": a10["group"],
               "models": {lab: {"D600_a3_footing_w": r[lab]["D600_a3_footing_w"], "D600_a3_95": r[lab]["D600_a3_95"],
                                "a2_fallback": {k: r[lab]["a2_fallback"][k] for k in ("burst_mhz", "burst_board_w", "burst_D_w", "zeros_board_w", "P800_w",
                                                                                       "peak_board_hi95_w", "group")},
                                "card0_fallback": r[lab]["card0_fallback"]} for lab in ("M10", "M9")}}
        if est <= C.ADMIT_LINE_W:
            row["tier"] = "A" if est <= C.TIER_B_ABOVE_W else "B"
            row["scored"] = n in N1
            tiles[n] = row
        else:
            left[n] = {"type": t["type"], "est_card0_peak_w": round(est, 3), "N1": n in N1,
                       "why": f"card-0 estimate {est:.2f} W > {C.ADMIT_LINE_W:g} W (E170's admission)"}
    gov = sorted(n for n, r in tiles.items() if r["a2_group_M10"] != "pinned")
    if gov:
        raise SystemExit(f"refused: an admitted tile is predicted governed at the fallback ({gov}): E170's form admits pinned tiles only")
    zeros = list(C.ZEROS_ANCHORS)
    assert all(z in tiles and tiles[z]["tier"] == "A" for z in zeros)
    TA = sorted(n for n, r in tiles.items() if r["tier"] == "A" and n not in zeros)
    TB = sorted((n for n, r in tiles.items() if r["tier"] == "B"), key=lambda n: (tiles[n]["est_card0_peak_w"], n))
    order = []
    for half, members, passes in (("A", TA, (1, 2, 3)), ("B", TB, (4, 5, 6))):
        for p in passes:
            rng = random.Random(f"E174|{half}|{p}")
            z = list(zeros)
            rng.shuffle(z)
            rest = list(members)
            if half == "A":
                rng.shuffle(rest)
            for n in z + rest:
                order.append({"idx": len(order), "pass": p, "half": half, "name": n, "label": C.label_of(n), "type": tiles[n]["type"]})
    scored = sorted(n for n in tiles if tiles[n]["scored"])
    # the dry twin's short order (the toy card only): passes 1-2 of the zeros and 6 scored tier-A tiles, pass 4 of the zeros and 3 scored tier-B
    dA = [n for n in TA if tiles[n]["scored"]][:6]
    dB = [n for n in TB if tiles[n]["scored"]][:3]
    dry_order = []
    for half, members, passes in (("A", dA, (1, 2)), ("B", dB, (4,))):
        for p in passes:
            rng = random.Random(f"{DRY_SEED}|{half}|{p}")
            z = list(zeros)
            rng.shuffle(z)
            rest = list(members)
            if half == "A":
                rng.shuffle(rest)
            for n in z + rest:
                dry_order.append({"idx": len(dry_order), "pass": p, "half": half, "name": n, "label": C.label_of(n), "type": tiles[n]["type"]})
    # the lines: predict_pool8_a2.lines_c0 on the frozen file (n = 31, equal to intervals-pool8.json), then at the planned scored n (the admitted
    # N1 tiles): the same function and seeds, the scored set in place of N1 (A2-3 (g): a verdict reads the line at the scored n)
    L31 = A.lines_c0(pred)
    committed = iv["cards"]["aifoundry1c0"]["rules"]
    same31 = json.dumps(L31, sort_keys=True, default=str) == json.dumps(committed, sort_keys=True, default=str)
    if not same31:
        raise SystemExit("refused: predict_pool8_a2.lines_c0 does not reproduce intervals-pool8.json's aifoundry1c0 block")
    pv = copy.deepcopy(pred)
    pv["sets"]["N1"] = scored
    L = A.lines_c0(pv)
    refs = A.e165_refs()
    band = A.c0_band()
    # a forecast, registered (information only): C0-W's line and C0-B's lines at n from the 42 pinned end-to-end errors (E170's read beside)
    fr = random.Random(1741)
    draws = 20000
    hit = {"W_at_or_under_line": 0, "B_mean": 0, "B_rms": 0, "B_both": 0}
    hiW = L["P8-C0-W"]["range_95"][1]
    for _ in range(draws):
        e = [refs["pin_w"][fr.randrange(len(refs["pin_w"]))] for _ in range(len(scored))]
        r_, m_ = C.rms(e), C.mean(e)
        hit["W_at_or_under_line"] += r_ <= hiW
        hit["B_mean"] += abs(m_) <= 0.5
        hit["B_rms"] += r_ <= 1.0
        hit["B_both"] += abs(m_) <= 0.5 and r_ <= 1.0
    forecast = {k: round(v / draws, 4) for k, v in hit.items()}
    # card time from E170's committed queue (the same card, harness and burst)
    q = [json.loads(x) for x in open(os.path.join(TOP, E170_QUEUE_REL))]
    s1a = next(x["t_ms"] for x in q if x["kind"] == "session_start" and x.get("name") == "s1")
    s1b = next(x["t_ms"] for x in q if x["kind"] == "session_end" and x.get("name") == "s1")
    q0 = next(x["t_ms"] for x in q if x["kind"] == "queue_start")
    n170 = E170["runs"]
    spb = (s1b - s1a) / 1000.0 / n170
    nsub = sum(1 for o in order if o["pass"] in C.SUBSET_PASSES)
    card = {"e170_s1_bursts": n170, "e170_s1_min": round((s1b - s1a) / 60000.0, 2), "s_per_burst": round(spb, 2),
            "e170_before_s1_min": round((s1a - q0) / 60000.0, 2), "e174_bursts": len(order), "e174_session_min": round(len(order) * spb / 60.0, 1),
            "e174_card_min": round(len(order) * spb / 60.0 + (s1a - q0) / 60000.0, 1), "cap_card_min": C.CAP_CARD_MIN, "slot_min": C.SLOT_MIN,
            "subset_passes": list(C.SUBSET_PASSES), "subset_bursts": nsub, "subset_session_min": round(nsub * spb / 60.0, 1),
            "subset_cap_min": C.SUBSET_CAP_MIN, "subset_slot_min": C.SUBSET_SLOT_MIN, "source": f"{E170_QUEUE_REL} (s1 start and end), {E170_RES_REL} runs"}
    c170 = E170["cells"]
    smoke_ref = {n: {k: c170[f"b7-{n}"].get(k) for k in ("burst_w", "peak_w", "rise_c", "burst_mhz", "n")} for n in C.SMOKE_TILES
                 if f"b7-{n}" in c170}
    e170_zeros = E170["score"]["reported"]["zeros_levels"]
    gate = load(E170_GATE_REL)
    top = sorted(((r["est_card0_peak_w"], n) for n, r in tiles.items()), reverse=True)[:6]
    out = {"experiment": C.EXPERIMENT, "request": C.REQUEST, "card": C.CARD,
           "_note": "E174's machine registration (E174.md); every model number copied by key from frozen files after their sha256 was checked; nothing fitted",
           "frozen_list": os.path.relpath(C.FROZEN_FILE, TOP), "frozen_list_sha256": C.sha256_file(C.FROZEN_FILE),
           "commits": {"pool8_freeze": "4576fb90", "pool8_A1": "ebf68c52", "pool8_note1": "dfe226f1", "registration": "3e97f583",
                       "registration_A1": "8a8fa34c", "predictor": "9d81d254", "registration_A2": "68a7c322", "predictor_a2": "97765c0a",
                       "M10": ["6829c9ba", "d1581099", "c996d135"], "M9": ["1f244140", "8dfafae3"], "M9_a2": ["5b98bd5c", "245caffe", "5c98c0c5"],
                       "E170": ["b5ca3e78", "574dc5b5", "57e1c6c4", "6147a9c7", "0e35ec58"], "E170_data": "81178664", "E165": ["3ef06839", "a5c56d17"],
                       "watcher": ["abe6b0f2", "33661416"], "runbook_v3_1": "0d2cb5dd", "E84": ["337b03b2", "1713a3f9"], "E118": ["28e625c9", "f37fa285"]},
           "recheck_frozen_blocks": recheck,
           "primary": {"model": "M10 carried by rule E (POOL8-REGISTRATION.md section 5) through E170's card term: predict_pool8_a2.py burst on "
                                "predictions-pool8-aifoundry1c0.json, M10 block: e170_common.pred_card0 on M10's D600 (kappa0 0.9463, the session's zeros "
                                "level in full at the tile's die starts), its die rise replaced by M10's term c2 (0.2415 C per board W over 21.5 W)",
                       "beside": "M9 carried the same way (the call's M9 block, its rise by M9's burst heat law, 0.1400 C/W): C0-M1's and C0-HK's comparisons",
                       "anchors": "the session's zeros-anchor reads: per format, every counted burst of its anchor7_zeros tile; the level reads those at "
                                  "795 MHz or more (pred_card0); no anchor burst at all: no prediction, every rule NOT SCORED"},
           "card_term": {"kappa0": C.KAPPA0, "source": "tools/claims-v3/e170/e170_common.py (E170.md 'The card term'), unchanged",
                         "E170_X0_read": "E170-X0 read 0.9766 [0.963, 0.987] (FAIL against 0.9463), 0.9312 die-start referred (post hoc): kappa0 is "
                                         "carried unchanged, as rule E registered it; a ratio is reported, never a verdict"},
           "admission": {"line_w": C.ADMIT_LINE_W, "peak_lock_w": C.PEAK_LOCK_W, "tier_b_above_w": C.TIER_B_ABOVE_W, "switch_ceiling": C.SWITCH_CEIL,
                         "card0_zeros_p800_w": z0, "card0_zeros_source": E84_REL + " cells.<type>/zeros.p800_w",
                         "formula": "for each of M10's and M9's blocks: max(M10, M9 peak_board_hi95_w) - (block zeros_board_w - card 0's E84 zeros p800) - "
                                    "0.05 x (block P800_w - block zeros_board_w); the larger of the two estimates (e170_common.est_card0)"},
           "tiles": tiles, "left_out": left, "n_admitted": len(tiles), "n_scored": len(scored), "scored": scored,
           "scored_by_type": {t: sum(1 for n in scored if tiles[n]["type"] == t) for t in ("fp32", "fp16", "int8")},
           "N1_left_out": sorted(n for n in left if left[n]["N1"]), "tier_A": TA, "tier_B": TB, "highest_estimates_w": top,
           "order": order, "order_seed": "Random('E174|<half>|<pass>')", "passes": [1, 2, 3, 4, 5, 6], "runs": len(order),
           "dry_order": dry_order, "dry_order_seed": f"Random('{DRY_SEED}|<half>|<pass>')",
           "lines": L, "lines_at_n31": L31, "lines_at_n31_equal_intervals_pool8": same31, "intervals_sha256": files[C.INTERVALS_REL],
           "reference": {"source": "tools/claims-v3/e165/predictions-e165.json reference (predict_pool8_a2.e165_refs); C0-H1: term c2's 39 "
                                   "leave-one-tile-out residuals on E170 (predict_pool8_a2.c0_band)", "pin_w": refs["pin_w"], "pin_mhz": refs["pin_mhz"],
                         "c2_residuals_c": band["residuals_c"], "c2_band_hw_c": band["hw_c"]},
           "forecast_information_only": {"at_n": len(scored), "from_42_pinned_e2e_errors": forecast, "draws": draws, "seed": 1741,
                                         "E170_read_on_this_card": "E170-W 0.727 W rms, mean -0.090 W over 39 pool-7 tiles (M9 carried); class S read "
                                                                   "+0.72 W (8 tiles); half B +0.63 W"},
           "smoke": {"tiles": list(C.SMOKE_TILES), "E170_measured_on_this_card": smoke_ref, "rest_w": C.REST_W, "stoptest_tile": C.STOPTEST_TILE},
           "E170_zeros_levels_at_the_cap": e170_zeros, "E170_state_gate": {k: gate.get(k) for k in ("continuity", "verdict", "host_boot")},
           "safety": C.SAFETY, "min_mhz_alarm": C.MIN_MHZ_ALARM, "want_config": C.WANT_CONFIG, "want_idle_mhz": C.WANT_IDLE_MHZ,
           "identity": {"e84_read_epoch": C.E84_READ_EPOCH, "e84_uptime_min": C.E84_UPTIME_MIN, "tol_min": C.UPTIME_TOL_MIN,
                        "host_boot_before": C.HOST_BOOT_BEFORE, "identity": C.C170.E84_IDENTITY},
           "card_time": card,
           "rules": {"min_passes": C.MIN_PASSES, "minimum_tiles": P.frozen()["reg"]["scoring"]["minimum_tiles"],
                     "seed_base": P.frozen()["reg"]["scoring"]["seed_base"], "bootstrap_draws": P.frozen()["reg"]["scoring"]["bootstrap_draws"],
                     "paired_draws": P.frozen()["reg"]["scoring"]["paired_draws"],
                     "paired_engine": "E173's (tools/claims-v3/e173/E173.md 'The paired engine'): rng = random.Random(80000 + the sum of the rule id's "
                                      "character codes); 20,000 draws of n tile indices with replacement; rms(a) - rms(b); [vals[int(0.025 x 20000)], "
                                      "vals[int(0.975 x 20000) - 1]]",
                     "c_check": "a burst counts only if every SPARSITY line of it has a C record that reads PASS in ccheck.py check (bit-exact); a tile "
                                "with any launch not PASS leaves every scored set",
                     "c_log_sessions": list(C.C_LOG_SESSIONS),
                     "c_log_rule": "smoke, stoptest-board and every BURST session s1-s6 the queue started that ran a work launch must carry a C log and a "
                                   "finished check of it; stoptest-die runs no launch and carries none; a missing one: the collection stops (14) and "
                                   "the scorer refuses (exit 5)",
                     "E174-S": "no safety stop, no sampler line under 590 MHz in any BURST run, no run's highest board sample at or above 62 W: PASS, "
                               "else FAIL (E170-S's form; the day's behaviour, a diagnostic)"}}
    p = os.path.join(HERE, "predictions-e174.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(f"frozen-sha256-e174.json: {len(files)} files ({sum(1 for v in checked.values() if v['listed_in'])} matched against a committed list)")
    print(f"predictions-e174.json sha256 {C.sha256_file(p)}")
    print(f"recheck: the frozen a2_fallback and card0_fallback blocks reproduce on {recheck['tiles']} tiles, {recheck['fields']} fields, "
          f"{len(recheck['differ'])} differ")
    print(f"E174: {len(tiles)} admitted ({len(scored)} scored: {out['scored_by_type']}), {len(left)} left out by name ({len(out['N1_left_out'])} of N1)")
    print(f"  kappa0 {C.KAPPA0}; card 0's 800 MHz zeros (E84) {z0}")
    print(f"  tier A {len(TA)} + 3 zeros anchors, tier B {len(TB)}; highest estimates {top}")
    print(f"  the order: {len(order)} bursts (half A passes 1-3 of {3 + len(TA)}, half B passes 4-6 of {3 + len(TB)}); dry twin {len(dry_order)} runs")
    print(f"  lines at n 31 equal intervals-pool8.json's aifoundry1c0 block: {same31}")
    for k, v in L.items():
        if k.startswith("_"):
            print(f"  {k}: {json.dumps(v)}")
            continue
        rr = v.get("range_95")
        print(f"  {k:10s} n {v.get('n')} min {v.get('minimum')} scored_at_planned_n {v.get('scored_at_planned_n')} "
              f"{'line ' + str(v.get('line')) if v.get('line') else ''}{'range ' + str([round(x, 4) for x in rr]) if rr else ''}")
    print(f"  forecast (information only) at n {len(scored)}: {json.dumps(forecast)}")
    print(f"  smoke ramp {list(C.SMOKE_TILES)}; E170 measured on this card: {json.dumps(smoke_ref)}")
    print("  card time:", json.dumps(card))
    print("admitted (card-0 estimate of the 95% upper peak, W):")
    for n in sorted(tiles, key=lambda n: tiles[n]["est_card0_peak_w"]):
        r = tiles[n]
        print(f"  {n:44s} {r['type']:4s} p{r['priority']} tier {r['tier']} {'scored' if r['scored'] else '      '} est {r['est_card0_peak_w']:6.2f} "
              f"(aifoundry2 {r['adm_a2_peak_w']:6.2f})  M10 D600 {r['models']['M10']['D600_a3_footing_w']:7.3f}")
    print("left out by name:")
    for n, r in sorted(left.items(), key=lambda kv: kv[1]["est_card0_peak_w"]):
        print(f"  {n:44s} {r['type']:4s} est {r['est_card0_peak_w']:6.2f}{'  (N1)' if r['N1'] else ''}")


if __name__ == "__main__":
    main()
