#!/usr/bin/env python3
"""E131 (Q136): write E131's freeze, before the claim of aifoundry1 card 1 and the first launch.

    python3 tools/claims-v3/e131/make_predictions_e131.py          # writes predictions-e131.json and predictions-e131.txt

E131 adds no new prediction for any tile. It freezes:
  * that E95's frozen claims C1-C12 (Q132(r)'s real2/predictions-real2.json, 6ae4c3d5) are scored on the card-1 view E112 froze
    (tools/claims-v3/e112/predictions-real2-card1.json: every watt figure a claim reads divided by E82's per-type card scale), by
    score_e95.py's own functions and E112b's two ports (score_e112b.py), unchanged;
  * E112b's cross-card rules X1, X4 and X5 against E95's committed reductions, with their thresholds, unchanged (renamed E131-X*),
    and their power re-simulated at four and five passes (make_predictions_e112.simulate, unchanged);
  * E131's set-aside rule, the reduction (card 1's frame, leakage frozen at E82's 0.2414 W/C), the arms, the passes, the budget,
    the stops, the device commands, and the sha256 of every file the session runs or the desk reduces with.
Every number is read from a committed file named here (checked by sha256), never retyped. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = "tools/claims-v3/kinds"
E = "tools/claims-v3/e131"
E112 = "tools/claims-v3/e112"
D95 = "docs/reports/data/2026-11-01-e95-real-tensors-energy"
D82 = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1"
D112 = "docs/reports/data/2026-11-01-e112-real-replicates"
TYPES = ("fp32", "fp16", "int8")
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def last_commit(rel):
    r = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%h", "--", rel], capture_output=True, text=True)
    return r.stdout.strip() or None


def frozen(rel, want=None):
    h = sha(rel)
    if want and h != want:
        raise SystemExit(f"{rel}: sha256 {h} != the recorded {want}")
    return {"path": rel, "sha256": h, "commit": last_commit(rel)}


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


REG112 = load(f"{E112}/predictions-e112.json")
assert hashlib.sha256(open(os.path.join(ROOT, E112, "predictions-e112.json"), "rb").read()).hexdigest().startswith("4c940b53"), \
    "predictions-e112.json is not the freeze E112's README names (4c940b53...)"
I112 = REG112["inputs_frozen"]
INPUTS = {
    "e112_predictions": frozen(f"{E112}/predictions-e112.json"),
    "card1_view": frozen(REG112["b"]["card1_view"]["path"], REG112["b"]["card1_view"]["sha256"]),
    "real2_predictions": frozen(I112["real2_predictions"]["path"], I112["real2_predictions"]["sha256"]),
    "real2_json": frozen(I112["real2_json"]["path"], I112["real2_json"]["sha256"]),
    "real_json": frozen(I112["real_json"]["path"], I112["real_json"]["sha256"]),
    "e82_scored": frozen(I112["e82_scored"]["path"], I112["e82_scored"]["sha256"]),
    "e82_reduction": frozen(I112["e82_reduction"]["path"], I112["e82_reduction"]["sha256"]),
    "e95_reduction": frozen(I112["e95_reduction"]["path"], I112["e95_reduction"]["sha256"]),
    "e95_nodips": frozen(I112["e95_nodips"]["path"], I112["e95_nodips"]["sha256"]),
    "e95_scored": frozen(I112["e95_scored"]["path"], I112["e95_scored"]["sha256"]),
    "e95_nodips_scored": frozen(I112["e95_nodips_scored"]["path"], I112["e95_nodips_scored"]["sha256"]),
    "e95_leak0.1994": frozen(I112["e95_leak0.1994"]["path"], I112["e95_leak0.1994"]["sha256"]),
    "e95_leak0.3803": frozen(I112["e95_leak0.3803"]["path"], I112["e95_leak0.3803"]["sha256"]),
    "e95_leak0": frozen(I112["e95_leak0"]["path"], I112["e95_leak0"]["sha256"]),
    "e112b_reduction": frozen(f"{D112}/b-e95-card1/e112b.json"),
    "e112b_scored": frozen(f"{D112}/b-e95-card1/scored.json"),
}

# the card code the session runs, unchanged (E95's freeze lists E78's; E95's own card files; the guard and the checker)
CARD_CODE = [
    "tools/claims-v3/lib.sh", f"{K}/e78_common.py", f"{K}/run_e78.py", f"{K}/reduce_e78.py", f"{K}/kinds.json",
    f"{K}/e95_common.py", f"{K}/predictions-e95.json", f"{K}/real/real.json", f"{K}/real2/real2.json",
    f"{K}/real2/predictions-real2.json", "tools/claims-v3/e128/ettelem_guard.sh", "tools/claims-v3/dmcmd_audit.py",
    "tools/claims-v3/dmcmd_table.json", "workloads/sparsity/host/main.cpp",
]
# the desk code E131 scores with, unchanged
DESK_CODE = [f"{K}/score_e95.py", f"{E112}/score_e112b.py", f"{E112}/make_predictions_e112.py", f"{K}/selftest_e78.py"]
E131_CARD_FILES = [f"{E}/run_e131.py", f"{E}/block_e131.sh", f"{E}/queue_e131.sh", f"{E}/session_e131.sh", f"{E}/check_e131.py",
                   f"{E}/preflight_e131.sh", f"{E}/smoke_gate_e131.py"]
E131_DESK_FILES = [f"{E}/reduce_e131.py", f"{E}/score_e131.py", f"{E}/collect_e131.sh", f"{E}/selftest_e131.py",
                   f"{E}/make_predictions_e131.py"]
# the binaries the session executes on aifoundry1 (~/nekko), read there on Mon 2 Nov 2026 10:54 PST by sha256sum
BOX_BINARIES = {
    "build/sparsity/host/sparsity_host": "e0fbecce35f252c546e6e8390f6a4694519674dc4d6dea359b0db9c4d1a3fbbe",
    "build/ettelem/ettelem": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325",
}


def claim_types(F):
    """The formats each frozen claim reads: every tile key or item name inside the claim's block; C12 reads all three."""
    out = {}
    for key, c in F["claims"]["E95"].items():
        acc = set()

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(k)
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
            elif isinstance(o, str):
                m = re.match(r"^(fp32|fp16|int8)[./]", o)
                if m:
                    acc.add(m.group(1))
        walk(c)
        short = key.split("_", 1)[0]
        out[short] = sorted(acc) if acc else list(TYPES)
    return out


def main():
    G = load(INPUTS["card1_view"]["path"])
    scale = REG112["b"]["card_scale_e82"]
    sys.path.insert(0, os.path.join(ROOT, K))
    sys.path.insert(0, os.path.join(ROOT, E112))
    import e95_common as e95  # noqa: E402
    import make_predictions_e112 as m112  # noqa: E402  (its simulate(), unchanged; importing it re-checks E112's inputs)
    pool = list(e95.POOL)
    nod = load(INPUTS["e95_nodips"]["path"])
    X = json.loads(json.dumps(REG112["b"]["cross_card"]))
    X.pop("power", None)
    X["against"] = ("E95's committed reductions of aifoundry3 card 0 (frozen by sha256 and commit), as E112b registered them. PRIMARY "
                    "PAIRING: E131's verdict-carrying reading (dips removed, leakage 0.2414 W/C, card 1's frame) against E95's registered "
                    "dips-removed arm (dips-arm/e95-nodips.json: dips removed, leakage auto 0.299 W/C, five passes): each card at its own "
                    "slope, as E82's scale was measured (E82 at its own 0.2414 against E78's own 0.1994). Reported pairings, a verdict that "
                    "moves marked arm-sensitive: E131 auto against E95 nodips (E112b's primary pairing), E131 dips kept against E95's "
                    "registered primary (both dips kept), E131 at 0.1994 / 0.3803 / 0 against E95's arms at the same slope, E131 at 0.545 "
                    "against E95 nodips")
    X["renamed"] = "E112b-X1, E112b-X4, E112b-X5 are scored by score_e112b.cross() unchanged and reported as E131-X1, E131-X4, E131-X5"
    power = {str(n): m112.simulate(nod, pool, scale, X, n_pass=n) for n in (4, 5)}

    F = load(INPUTS["real2_predictions"]["path"])
    ctypes = claim_types(F)
    e82 = load(INPUTS["e82_reduction"]["path"])
    tie = {"what": "reported, never a verdict (E95-S1's form): the session's anchors against E82's card-1 cells (E91-R5's and E112b's "
                   "cells and bands)",
           "e82_cells": REG112["b"]["session_tie"]["e82_cells"]}
    for n, v in tie["e82_cells"].items():
        assert abs(v["D_w"] - e82["items"][n]["D"]["mean"]) < 1e-12, n

    plan = {
        "card": "aifoundry1 card 1 only: V3_DEVICE=1, so lib.sh exports ET_DEVICES=1, names the card aifoundry1-c1 and takes "
                "/run/lock/etsoc-shire1.lock; 600 MHz, about 499 mV, TDP 65 W and threshold 65 C as read, never set; release 1.4.0, "
                "BL2 0.22.0 (E82 A1's read of 31 Oct; identity by the box's uptime since, no firmware-revisions query)",
        "tree": "aifoundry1 ~/nekko (an rsynced copy, no git): tools/claims-v3/{lib.sh,kinds/,e128/ettelem_guard.sh,e131/,dmcmd_audit.py,"
                "dmcmd_table.json} and workloads/sparsity/host/main.cpp as at this commit",
        "binary": "build/sparsity/host/sparsity_host (28 Sep 20:56), the one E82, E88, E91, E108 and E112 ran on this box; no rebuild; "
                  "the heater is the same binary (lib.sh's HEATER)",
        "a_run": "sparsity_host --test fma --type <t> --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4, "
                 "1,024 minions, E78's launch reading (heat to 59 C, launch at 58 C after 2.0 s quiet), as E95 and E112b",
        "pass": "E95's 53 runs, unchanged: the anchor_pi tie, three segments of E78's six anchors and eleven of E95's 33 items (the "
                "thirty real2 tiles; fp16.real_l6_mlp_down, int8.real_l6_mlp_down, fp16.real_l6_attn_qk), the tie; two unrecorded "
                "burn-ins. Order e95_common.pass_order, Random('E95|aifoundry1-c1|<pass>'), as E112b's",
        "smoke": {"pass": 13101, "block": f"{E}/block_e131.sh 13101 --smoke", "items": list(e95.SMOKE_ITEMS),
                  "what": "E95's seven smoke items, 2 s runs, no preheat; gate smoke_gate_e131.py"},
        "passes": [13110, 13111, 13112, 13113, 13114],
        "passes_note": "four base passes, then a fifth if it fits the budget (the queue's rule); a pass in flight is never cut",
        "first_estimate_s": 560,
        "first_estimate_why": "E112's for E95's pass (E95's longest pass on aifoundry3, 537 s, plus a margin); E112b's three passes on this "
                              "card took 491-502 s, from a warm die",
        "data": "build/claims-v3/aifoundry1-c1/e131/p131<nn>/ and e131-smoke/p13101/ on aifoundry1",
        "session": f"{E}/session_e131.sh, detached on the box (setsid nohup), E131_T0 = its launch",
    }
    budget = {
        "card_seconds": 2700, "from": "E131_T0, the session's launch, just before its first config read",
        "to": "the session's closing config read (E129's and E124 A1's count, from the first device access to the last)",
        "rule": "queue_e131.sh starts a pass only if now + projected <= E131_T0 + 2700 - 60 (the reserve covers the closing config read "
                "and et-who) and now + projected <= 2026-11-02 15:50 PST; projected = 560 s until a pass ends, then the longest measured "
                "pass; exact integer seconds; 10 s between passes",
        "reserve_s": 60, "deadline": "2026-11-02 15:50 PST", "no_session_after": "15:00 PST", "runs_end_by": "16:00 PST",
        "expected": "four passes at E112b's 491-502 s (the fifth needs passes of about 505 s or less, the first one included)",
        "claim_text": "using aifoundry1 card 1 for 1 h, until ~HH:MM PST (45 min plus a margin, rounded up to the half hour), one clause "
                      "of the day's one card post, rewritten with edit_replace.mjs (EXPECT_TEXT)",
    }
    stops = {
        "board_w": 68.0, "die_hottest_shire_c": 72.0, "run_e78_max_c": 72.0, "run_e78_pmic_stop_c": 82.0,
        "what": "run_e131.py: a telemetry line with board_w >= 68 W or any minion-shire reading >= 72 C writes the pass's STOP and ends it "
                "(run_e78's EXIT_HOT); run_e78.py's own --max-c 72 on the first shire reading (and its PMIC field >= 82 C, which on this "
                "runner is a die reading, E130 A2); either stop fails the block and ends the queue. The STOP file, another user's device "
                "process or this card's lock held by anyone else stop the queue too",
        "margin_basis": "E112b's three passes of the same 53-run pass on this card (committed raw telemetry): board max 60.82 W, hottest "
                        "shire 65 C, PMIC field 62 C (desk/telemetry-max-e112b.txt); the firmware's PMIC alarm is 75 W / 75 C",
    }
    reduction = {
        "primary": "reduce_e131.py: reduce_e78.py unchanged with E95's items, card 1's 65/65 config read accepted, dips removed (E82 A2), "
                   "leakage FROZEN at 0.2414 W/C (E82's own slope on this card; E93's, E124's and E129's frame), E78's gates unchanged",
        "leak_w_per_c": 0.2414,
        "why_frozen": "E112b's registered primary fitted the slope per session (auto): it returned 0.414 and 0.417 W/C, against E82's 0.2414, "
                      "moving absolute D by about 0.5 W in fp32 and making about half of the gap between the cards (E112 README result 2; "
                      "14-card-behaviour.md, 'A session's automatic leakage slope wanders, so register one'); ratios inside a pass are "
                      "nearly unaffected",
        "arms": {"auto": "leakage auto, dips removed (E112b's registered primary)", "dips_kept": "dips kept, 0.2414",
                 "leak0.1994": "E78's slope on aifoundry3", "leak0.3803": "E95's arm", "leak0": "no leakage correction",
                 "leak0.545": "E112b's arm"},
        "arms_flags": "--no-refit on every arm (E112's)",
        "relaxed": "reduce_e131.py --relax-anchors --leak 0.2414: the set-aside rule's reduction; always reported",
    }
    set_aside = {
        "min_kept_passes": 3,
        "written": "Mon 2 Nov 2026, in this registration, before the claim and before any E131 data",
        "relaxed_reduction_gates": {"zero_mid_departure_w": 99.0, "zero_range_w": 99.0, "random_range_w": 99.0, "tie_drift_w": 99.0},
        "steps": [
            "S1, the primary: E78's pass gates unchanged (each type's zeros line departs <= 0.25 W from its straight line and spans <= 0.60 W; "
            "each random anchor spans <= 1.0 W; the pi tie drifts <= 0.60 W; at most 2 failed runs; card 1's config read). It carries "
            "every verdict if it keeps >= 3 passes",
            "S2, only if S1 keeps < 3: a pass set aside ONLY by the pi tie's drift is restored whole (pi enters no claim and no cross-card "
            "rule, only the reported session tie)",
            "S3, only if S1 and S2 keep < 3: a pass set aside only by the anchor gates of one or two formats (their zeros line's departure "
            "or span, their random anchor's span; the tie as in S2) is restored for the OTHER formats' items; the failing formats' items in "
            "that pass, anchors included, stay out. Each format's D is over its own zeros line and its r over its own random anchor, so a "
            "gate on one format's anchors says nothing of another's. A claim is scored only if every format it reads has >= 3 passes in "
            "the reading (claims_types), else NOT SCORED; a pairing across formats (C4) uses only passes that keep both",
            "Never restored in any step: a pass with more than 2 failed runs, a pass whose config read is not card 1's 65/65, a pass whose "
            "block did not end ok, an .attempt-* directory",
            "The restored passes' values come from the relaxed reduction (--relax-anchors at the same frozen slope), whose per-pass values "
            "equal the primary's for every pass both keep (a fixed slope makes each pass's reduction independent of the others; "
            "selftest_e131.py checks it to 1e-12 on E112b's passes)",
            "Fewer than 3 passes after S3: every claim and cross-card rule NOT SCORED",
            "No pass is added after any reduction is read, and no pass is chosen after the fact; every reading (S1, S2, S3) is always "
            "reported, and the verdicts name the reading that carries them",
        ],
        "claims_types": ctypes,
        "why": "E112(b) kept two of three passes: its third (11252) departed from its fp32 zeros line by -0.253 W against E78's 0.25 W, at "
               "every leakage arm, and the spare did not fit, so nothing was scored (E112 README result 3). Over the 15 committed primary "
               "reductions of E78-frame passes on card 1 (73 passes), 6 passes were set aside, every one by an anchor gate of one or two "
               "formats: four by a zeros line's departure (0.253-0.297 W against 0.25), two by a random anchor's span in E82's dips-kept "
               "primary; none by the tie, failed runs or a config read (docs/reports/data/2026-11-02-e131-real-tiles-card1/desk/"
               "history-card1.txt). So S3 would have restored five of the six for the other formats",
    }
    out = {
        "experiment": "E131", "request": "Q136", "date": "2026-11-02",
        "title": "E95's thirty real tiles on aifoundry1 card 1, four or five passes, a set-aside rule written first, cross-card rules at "
                 "E82's scale against E95",
        "registration": f"{E}/E131.md",
        "answers": {"page": "https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open",
                    "item": "item 7, 'More real tensors' (Q134 left it: 'E95's thirty tiles are still not scored on a second card')",
                    "critic": "Q134's final critic, its item 9 ('E95's pass on aifoundry1 card 1, with four or five passes and a set-aside "
                              "rule written first')"},
        "inputs_frozen": INPUTS,
        "harness": {
            "card_code_unchanged_sha256": {r: sha(r) for r in CARD_CODE},
            "e95_reused_unchanged_sha256_as_e95_froze_it": load(f"{K}/predictions-e95.json")["harness"]["reused_unchanged_sha256"],
            "desk_code_unchanged_sha256": {r: sha(r) for r in DESK_CODE},
            "e131_card_files_sha256": {r: sha(r) for r in E131_CARD_FILES},
            "e131_desk_files_sha256": {r: sha(r) for r in E131_DESK_FILES if os.path.exists(os.path.join(ROOT, r))
                                       and not r.endswith("make_predictions_e131.py")},
            "box_binaries_sha256": BOX_BINARIES,
        },
        "plan": plan, "card_budget": budget, "stops": stops, "reduction": reduction, "set_aside_rule": set_aside,
        "claims": {"what": "E95's frozen claims C1-C12 (claims.E95 of real2/predictions-real2.json) on the card-1 view, scored by "
                           "score_e95.score unchanged, C7 and C8 by score_e112b's ports (the view's scaled thresholds); E95's conventions: "
                           "fewer than 3 kept passes NOT SCORED, a claim short of its population UNDER-RESOLVED; beside every verdict, labelled "
                           "and never the verdict, the same claim at the frozen thresholds unscaled",
                   "card1_view": INPUTS["card1_view"], "card_scale_e82": scale},
        "cross_card": X,
        "cross_card_power": {"what": "make_predictions_e112.simulate unchanged at 4 and 5 passes (E112 registered 3): card 1 drawn from E95's "
                                     "dips-removed means and per-pass scatter, five worlds, 4,000 draws, seed 112", "by_passes": power},
        "session_tie": tie,
        "cross_session_reported": {"what": "reported, never a verdict: each tile's D and r beside E112b's two kept passes on this card "
                                           "(b-e95-card1/e112b.json, leakage auto 0.417) and E131's auto arm beside them, like with like",
                                   "e112b": INPUTS["e112b_reduction"]},
        "expected_not_lines": {
            "claims": "If E112b's two kept passes and its labelled three-pass post-hoc view carry (E112 README result 4; at E112b's auto "
                      "slope): C1 FAIL (GPT-2's fp16 attention cell), C7 and C8 INCONCLUSIVE, the other ten PASS; X1, X4, X5 PASS (rho 0.993 "
                      "/ 0.973 / 0.967; X4 median 1.0432; 33 of 33 tiles within X5's bands). E95 on aifoundry3: 9 PASS, 1 FAIL (C1), 2 "
                      "INCONCLUSIVE (C2, C5), 1 UNDER-RESOLVED (C7). These are expectations, not lines",
            "slope": "at 0.2414 W/C card 1's D of the hottest tiles reads about 0.4-0.5 W higher than at E112b's auto (D is linear in the "
                     "slope, E112 README result 2), so X4's median should move toward E82's 1.031",
        },
        "device_commands": {
            "source": "et-platform 836a4ab (BL2 0.22.0, card 1's running build), read by E128's desk/dmcmd-e128-022.py, run unchanged for "
                      "E131: desk/dmcmd-e131.txt, byte-identical to E128's desk/dmcmd-e128-022.txt; Q136(w)'s checker on every file the "
                      "session runs: GO with no WRITE allowed (preflight_e131.sh, one reviewed exception, lib.sh:154)",
            "sent": [
                {"by": "ettelem config (session start and end, each block's start and end), through e128/ettelem_guard.sh", "commands": [
                    "DM_CMD_GET_MODULE_STATIC_TDP_LEVEL (25): READ, a copy from SP RAM",
                    "DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS (21): READ, a copy from SP RAM",
                    "DM_CMD_GET_MODULE_POWER_STATE (23): READ, a copy from SP RAM",
                    "DM_CMD_GET_ASIC_FREQUENCIES (53): READ, PLL register reads and a strap read, an SP RAM copy",
                    "DM_CMD_GET_ASIC_VOLTAGE (32): READ, PVT voltage monitors and two PMIC voltage-register reads over I2C (allowed by the "
                    "owner's rule of 2 Nov 2026)"]},
                {"by": "ettelem sample --seconds --every-ms (the 10 Hz sampler of every block, lib.sh's 1 s die reads), through the guard",
                 "commands": [
                     "DM_CMD_GET_MODULE_POWER (33): READ, a copy from SP RAM",
                     "DM_CMD_GET_SP_STATS (60): READ, a copy of the SP's statistics, no reset",
                     "DM_CMD_GET_MODULE_CURRENT_TEMPERATURE (27): READ, PVT temperature sensors, an SP RAM copy",
                     "DM_CMD_GET_ASIC_VOLTAGE (32): READ, as above",
                     "DM_CMD_GET_MODULE_VOLTAGE (31): READ, nine PMIC voltage-register reads over I2C (allowed)",
                     "DM_CMD_GET_ASIC_FREQUENCIES (53): READ, as above"]},
                {"by": "sparsity_host (the workload and the heater, build/sparsity/host/sparsity_host)",
                 "commands": ["the Master Minion's device-ops on the ops node: DMA writes and reads of device DRAM, kernel launches, an abort "
                              "on a 6 s overrun: the workload, not a device-management command (createPcieDeviceLayer(true, false); no "
                              "management library)"]},
                {"by": "et-lab-manifest, et-holders (sudo -n, fuser), et-who", "commands": ["sysfs and fuser reads: no device node opened"]},
            ],
            "not_sent": "DM_CMD_SET_STATS_RUN_CONTROL (62; no --reset-ms, which the guard refuses), DM_CMD_SET_DM_TRACE_CONFIG (67), sptrace, "
                        "the vendor tool dev_mngt_service (lib.sh's drain is refused in block_e131.sh), DM_CMD_GET_MODULE_FIRMWARE_REVISIONS "
                        "(14; it writes the PMIC's firmware-management register), any residency read, any governor, TDP, threshold, clock or "
                        "voltage set, any reset",
            "writes": "none",
        },
    }
    p = os.path.join(HERE, "predictions-e131.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    L = ["E131 freeze (predictions-e131.json), printed by make_predictions_e131.py", "",
         f"passes {plan['passes']}, smoke {plan['smoke']['pass']}; budget {budget['card_seconds']} s from T0, reserve {budget['reserve_s']} s",
         f"stops: board >= {stops['board_w']} W, hottest shire >= {stops['die_hottest_shire_c']} C, run_e78 --max-c {stops['run_e78_max_c']}",
         f"reduction: dips removed, leakage {reduction['leak_w_per_c']} W/C frozen; arms {list(reduction['arms'])}",
         f"set-aside rule: min {set_aside['min_kept_passes']} kept; relaxed gates {set_aside['relaxed_reduction_gates']}",
         f"claims' formats: {ctypes}", f"card scale (E82): {scale}",
         f"X4 eligible: {len(X['X4']['eligible'])} tiles, band {X['X4']['band']}; X5 bands {X['X5']['band']}", "",
         "cross-card power, P(PASS):"]
    for n, w in power.items():
        for world, v in w.items():
            L.append(f"  {n} passes, {world}: X1 {v['X1_all']} (by type {v['X1_by_type']}), X4 {v['X4']}, X5 {v['X5']}")
    L.append("")
    L.append("harness (sha256):")
    for k in ("card_code_unchanged_sha256", "desk_code_unchanged_sha256", "e131_card_files_sha256", "e131_desk_files_sha256",
              "box_binaries_sha256"):
        for r, h in out["harness"][k].items():
            L.append(f"  {k.split('_sha256')[0]}: {r} {h}")
    open(os.path.join(HERE, "predictions-e131.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
