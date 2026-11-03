#!/usr/bin/env python3
"""E156 (Q139): the frozen predictions, prices, rules, plan and stops, written from committed files only, before any E156 pass.

    python3 tools/claims-v3/e156/make_predictions_e156.py docs/reports/data/2026-11-03-e156-memory-images-card1/gen
        -> tools/claims-v3/e156/predictions-e156.json and predictions-e156.txt

The price is E139's (docs/reports/data/2026-11-02-e139-memory-split-more-passes/e139.json, its registered primary: E139's eight headline
passes on aifoundry3 card 0, the board meter's dips removed, leakage auto): the encoded wide-path residuals E56 and E448 per encoded 64-bit
toggle at E139's line rate, 0.4628 and 0.4632 pJ, whose mean is the registered price (reading A). The other readings put the same two
residuals on another count (each fitted to E56 and E448 the same way), so all five agree on E139's images and differ on E156's E32 and on
E132's E192. Counts are the images' own (gen/counts.json, make_e156.py --check). Standard library only.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E139 = "docs/reports/data/2026-11-02-e139-memory-split-more-passes/e139.json"
PAIRS = {"E56": ("eh_64", "el_64"), "E448": ("vl_64", "c3_64"), "E192": ("vl_128", "c3_128"), "E7": ("e7_64", "e2_64"), "E32": ("eh_32", "el_32")}
READ = {"A": ("e64", "E139's reading: per encoded toggle between consecutive 64-bit pieces of a line (the count E139's 0.46 pJ is per)"),
        "B": ("e32", "per encoded toggle between consecutive 32-bit pieces"),
        "C": ("e64_plus_e128", "per encoded toggle between consecutive 64-bit pieces plus between consecutive 128-bit pieces"),
        "E": ("t_enc", "per encoded pin toggle between beats beyond V16's price (the pins mispriced, the residual on the pins)"),
        "F": ("tx_enc", "per encoded pin toggle from a line's last beat to the next line's first on a channel (the line edge)")}


def sha(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()


def main():
    gen = sys.argv[1]
    e139 = json.load(open(os.path.join(ROOT, E139)))
    counts = json.load(open(os.path.join(gen, "counts.json")))
    lr3 = e139["headline"]["lines_per_s"]
    B = e139["headline"]["contrasts"]["board"]
    R4 = e139["verdicts"]["R4_encoded_board"]
    pc = {}
    for pn, (x, y) in PAIRS.items():
        cx, cy = counts["items"][x], counts["items"][y]
        d = {k: cx[k] - cy[k] for k in ("hi", "t_enc", "e32", "e64", "e128", "tx_enc", "w", "t_raw", "r32", "r64", "r128", "half", "tx_raw")}
        d["e64_plus_e128"] = d["e64"] + d["e128"]
        pc[pn] = d
    prices = {}
    for rd, (cnt, what) in READ.items():
        v = [B[pn]["mean"] / (pc[pn][cnt] * lr3) * 1e12 for pn in ("E56", "E448")]
        prices[rd] = {"count": cnt, "what": what, "pJ": sum(v) / 2.0, "from_E56_E448_pJ": v}
    assert abs(prices["A"]["from_E56_E448_pJ"][0] - R4["E56"]["pJ_per_encoded_toggle"]) < 1e-12
    assert abs(prices["A"]["from_E56_E448_pJ"][1] - R4["E448"]["pJ_per_encoded_toggle"]) < 1e-12
    pairs = {}
    for pn, (x, y) in PAIRS.items():
        pairs[pn] = {"image": x, "twin": y, "counts": pc[pn],
                     "residual": "(%s - %s) - (%.0f/496) V16 - (%.0f/192) Hp" % (x, y, pc[pn]["t_enc"], pc[pn]["hi"]),
                     "predicted_W_at_E139_line_rate": {rd: prices[rd]["pJ"] * 1e-12 * pc[pn][prices[rd]["count"]] * lr3 for rd in READ},
                     "k_vs_E56": {rd: pc[pn][prices[rd]["count"]] / pc["E56"][prices[rd]["count"]] for rd in READ},
                     "E139_measured_W": ({"mean": B[pn]["mean"], "lo": B[pn]["lo"], "hi": B[pn]["hi"]} if pn in B else None)}
    reg = {
        "exp": "E156", "card": "aifoundry1-c1",
        "written": "Tue 3 Nov 2026, before any E156 pass, from committed files only",
        "E139_source": {"file": E139, "sha256": sha(E139), "line_rate_lines_per_s": lr3, "passes_headline": e139["passes_headline"],
                        "arm": "primary: E139's passes alone, the board meter's dips removed, leakage auto"},
        "prices": prices,
        "registered_reading": "A",
        "formula": "predicted encoded residual (W) = price_pJ x 1e-12 x count x lines_per_s, lines_per_s = this session's headline mean line "
                   "rate (reduce_e132's lines_per_s: the mean over passes of each pass's mean ops_per_s over its DRAM runs)",
        "pairs": pairs,
        "E132_frozen_W": 0.185,
        "E139_ties_W": {cn: B[cn]["mean"] for cn in ("S64", "S128", "V16", "V64", "V128", "U4z", "Hp", "RH64", "RH128")},
        "rules": {
            "N1": {"pairs": ["E7", "E32"], "what": "the critic's rule on the two new images: |mean - prediction(A)| <= 0.05 W for each; PASS if both, "
                   "FAIL if either; NOT-SCORED below 3 headline passes. The 95% interval is reported against prediction +- 0.05 W "
                   "(decided inside, decided outside, or straddling)"},
            "C1": {"pairs": ["E56", "E448"], "what": "E139's own images on this card, the same price and the same rule; E132's R4 class reading beside it, "
                   "and each against E132's frozen +0.185 W"},
            "N2": {"pairs": ["E32", "E192"], "what": "the width reading inside the session: for each reading X, per pass d_X = E_pair - k_X (E56 + E448)/2 "
                   "with k_X the pair's count over E56's under X; X is consistent on a pair when the 95% interval of d_X contains 0; the verdict is "
                   "the set of readings consistent on both E32 and E192 ('A ONLY', ..., 'SEVERAL: ...', 'NONE'). E7 is reported (every reading "
                   "gives it k = 5/7)"},
            "D": {"what": "read DBI evident on this card: Hp present on the board at E132's class (mean >= 0.10 W, interval above 0) -> EVIDENT; "
                  "absent -> NOT EVIDENT (every encoded prediction assumes read DBI on, as on aifoundry3); else UNRESOLVED"},
        },
        "decision": {"within_W": 0.05, "min_headline_passes": 3, "warmup_pass": 15610, "board_absent_half_W": 0.10, "board_present_W": 0.10,
                     "ddr_moves_mV": 0.30, "ddr_still_half_mV": 0.30},
        "plan": {
            "passes": {"stoptest": 15602, "smoke": 15601, "warmup": 15610, "headline": "15611 onward, up to 15619, as the budget allows"},
            "items_per_pass": "anchor_pi first and last, the 16 memory items once each in runitems.py's shuffled order (seed '<card>|<pass>|<pass>'), "
                              "two burn-in launches of anchor_pi",
            "smoke_items": "anchor_pi,e7_64,eh_32,eh_64,c3_128",
            "budget_card_minutes": 40, "budget_s": 2400, "reserve_s": 150, "first_pass_estimate_s": 330,
            "no_session_after": "2026-11-03 10:30 PST", "last_pass_end": "2026-11-03 11:20 PST",
            "stops": {"board_w": 66.0, "die_hottest_shire_c": 72.0, "stale_line_s": 1.5, "runitems_max_c_minshire0": 70.0,
                      "stoptest_board_w": 1.0, "stoptest_die_c": 1.0, "stoptest_stale_s": 0.0},
            "launch": "58 C after a 59 C preheat (E139's, runitems.py's defaults), 4 s runs",
        },
        "expectation": "not a line: E7 near +0.15 W and E32 near 0 if reading A holds and card 1 prices encoded toggles as aifoundry3 does; E56 and "
                       "E448 near +0.21 W; Hp present.",
    }
    # the harness: every reused file the box runs, E156's own run-time files, and on the box the binaries and the images
    box_runs = ["tools/claims-v3/lib.sh", "tools/claims-v3/runitems.py", "tools/claims-v3/text_hash.sh", "tools/claims-v3/e128/ettelem_guard.sh",
                "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "tools/claims-v3/e110/smoke_gate_e110.py",
                "tools/claims-v3/dm/build_host.sh", "tools/claims-v3/dm/make_host_src.py", "workloads/enercat/host/main.cpp",
                "workloads/sparsity/host/main.cpp"]
    own = ["tools/claims-v3/e156/" + f for f in ("block_e156.sh", "run_e156.py", "session_e156.sh", "queue_e156.sh", "check_e156.py",
                                                  "preflight_e156.sh", "collect_e156.sh", "box-binaries.txt")]
    reduction = ["tools/claims-v3/e156/reduce_e156.py", "tools/claims-v3/e156/reduce_e156.sh", "tools/claims-v3/dp/posthoc_dips.py",
                 "tools/claims-v3/hl/reduce_hl.py", "tools/claims-v3/mf/reduce_mf.py", "tools/claims-v3/e110/reduce_e110.py",
                 "tools/claims-v3/e132/reduce_e132.py", "tools/claims-v3/e156/make_e156.py", "tools/claims-v3/dm/dm_enc.py",
                 "tools/claims-v3/mf/make_mf.py", "tools/claims-v3/e110/make_e110.py"]
    box = {}
    for line in open(os.path.join(HERE, "box-binaries.txt")):
        if line.strip() and not line.startswith("#"):
            p, h = line.split()
            box[p] = h
    gsha = {}
    for line in open(os.path.join(gen, "gen.sha256")):
        h, f = line.split()
        gsha["build/e156-gen/" + f] = h
    box.update(gsha)
    reg["harness"] = {"reused_unchanged_sha256": {p: sha(p) for p in box_runs + own},
                      "box_binaries_sha256": box,
                      "reduction_sha256": {p: sha(p) for p in reduction},
                      "gen_sha256_file": {"path": os.path.relpath(os.path.join(gen, "gen.sha256"), ROOT),
                                          "sha256": hashlib.sha256(open(os.path.join(gen, "gen.sha256"), "rb").read()).hexdigest()},
                      "counts_json_sha256": hashlib.sha256(open(os.path.join(gen, "counts.json"), "rb").read()).hexdigest()}
    out = os.path.join(HERE, "predictions-e156.json")
    json.dump(reg, open(out, "w"), indent=1, sort_keys=False)
    L = ["E156 frozen predictions (written from %s, sha256 %s...; line rate %.6g lines/s)" % (E139, reg["E139_source"]["sha256"][:12], lr3),
         "prices per reading (each from E139's E56 and E448):"]
    for rd, p in prices.items():
        L.append("  %s %-14s %.4f pJ  (E56 %.4f, E448 %.4f)  %s" % (rd, p["count"], p["pJ"], p["from_E56_E448_pJ"][0], p["from_E56_E448_pJ"][1], p["what"]))
    L.append("pairs: counts (image - twin) and each reading's prediction at E139's line rate, W:")
    for pn, x in pairs.items():
        c = x["counts"]
        L.append("  %-5s %s - %s: d_e64 %+.0f d_e32 %+.0f d_e128 %+.0f d_t_enc %+.0f d_tx_enc %+.0f d_hi %+.0f | %s" % (
            pn, x["image"], x["twin"], c["e64"], c["e32"], c["e128"], c["t_enc"], c["tx_enc"], c["hi"],
            " ".join("%s %.4f" % (rd, v) for rd, v in x["predicted_W_at_E139_line_rate"].items())))
    for k, r in reg["rules"].items():
        L.append("rule %s: %s" % (k, r["what"]))
    open(os.path.join(HERE, "predictions-e156.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
