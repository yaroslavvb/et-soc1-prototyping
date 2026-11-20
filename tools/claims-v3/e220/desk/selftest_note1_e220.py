#!/usr/bin/env python3
"""E220 (Q233, lane fix-e220, Fri 20 Nov 2026, before any E220 datum): THE DESK TEST OF DATED NOTE 1's READING in step 6n's judgement
(desk/neverrun_card_e220.py's note1(); tools/claims-v3/e220-notes/E220.md.dated-note-1.md section 1; verify-e220's F1 and the orchestrator's
ruling 1): a point counts as run on its arm's card only by a session record on that card.

    /usr/bin/python3 -I -B tools/claims-v3/e220/desk/selftest_note1_e220.py [<a step-6n folder> ...]
        S1-S11: note1() on stand-in scans (each reading's sides: a session file in a lane folder naming the card; desk copies in folders naming
        no card; a capped listing on the card (unresolved: labelled); a dry pass; a committed data folder naming the card; XY's mask named only
        in a card-less copy, and named on the card in a session file; MM1-v3.2's measured points; arm A's folder naming aifoundry1 but no card;
        another card's session; a subtracted hit);
        then, for each step-6n folder given (neverrun_card_e220.py run's DIR: scan-e220-reg.json, neverrun-e220.json, judge-e220-<arm>.json,
        labels-e220-<arm>.json): the folder's labels re-made from its own scan and report by note1() equal its labels file and its judgement,
        every label is also a literal label, and the literal labels the judgement REPORTS equal the report's.
Prints one PASS/FAIL line per check and "SELFTEST-NOTE1-E220 <k> of <n> PASS" last. Standard library only; reads only (nothing written).
SPDX-License-Identifier: Apache-2.0
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location("neverrun_card_e220_under_test", os.path.join(HERE, "neverrun_card_e220.py"))
M = importlib.util.module_from_spec(sp)
sp.loader.exec_module(M)
res = []


def row(name, ok, info=""):
    res.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f" [{info}]" if info else ""))


C1, A2, A3 = "aifoundry1 card 1", "aifoundry2 card 0", "aifoundry3 card 0"


def S_of(tokens, masks=None, mtok=None, mmask=None):
    return {"tokens": tokens, "masks_by_card": masks or {}, "mm1_v32_measured_tokens": mtok or {}, "mm1_v32_measured_masks": mmask or {}}


def R(tok, mask="0xffffffff", reading="token"):
    return {"token": tok, "mask": mask, "reading": reading}


T = "gemmL9x9x9"
cases = [
    ("S1 a session file in a lane folder naming the card (arm A): ran",
     S_of({T: {C1: {"n": 1, "files": ["W/out/card-a1c1-desktest/runs/1/proc-00.out"]}}}), R(T), C1, "ran"),
    ("S2 hits only in folders naming no card (desk copies: W/out/data-e221/work/reg-tree/...): never",
     S_of({T: {"no card named": {"n": 2, "files": ["W/out/data-e221/work/reg-tree/tools/claims-v3/e221/desk/configs-e221.json",
                                                    "W/out/data-e221/work/reg-tree/tools/claims-v3/e221/desk/scan-e221.json"]}}}), R(T), C1, "never"),
    ("S3 a capped listing on the card with no session record listed: ran (unresolved, the conservative side)",
     S_of({T: {A2: {"n": 20, "files": [f"W/out/card-e216/logs/s{i}.txt" for i in range(8)]}}}), R(T), A2, "ran"),
    ("S4 a dry pass only, listed whole, on the card: never",
     S_of({T: {A2: {"n": 2, "files": ["W/out/card-e216/box-e216/dry/1-a2c0-E216/runs/032-y07a/proc-00.out",
                                       "W/out/card-e216/box-e216/dry/1-a2c0-E216/runs/032-y07a/run.json"]}}}), R(T), A2, "never"),
    ("S5 a committed data folder naming the card: ran",
     S_of({T: {A2: {"n": 1, "files": ["docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/README.md"]}}}), R(T), A2, "ran"),
    ("S6 XY: the token on the card but the mask named only in a card-less desk copy: never",
     S_of({T: {A2: {"n": 3, "files": ["W/out/card-e216/rb-e216/copy/sessions/1/runs/1/proc-00.out", "a", "b"]},
               "no card named": {"n": 1, "files": ["W/out/data-e219/work/reg-tree/x.json"]}}},
          masks={T: {A2: ["0x101"], "no card named": ["0x3030"]}}), R(T, "0x3030", "config"), A2, "never"),
    ("S7 XY: the mask named on the card in a session file: ran",
     S_of({T: {A2: {"n": 1, "files": ["W/out/card-e216/rb-e216/copy/sessions/1/runs/1/proc-00.out"]}}}, masks={T: {A2: ["0x3030"]}}),
     R(T, "0x3030", "config"), A2, "ran"),
    ("S8 MM1-v3.2's measured points hold the token on the card: ran",
     S_of({T: {"no card named": {"n": 1, "files": ["W/out/data-x/y.json"]}}}, mtok={T: [f"rgm136 on {C1}"]}), R(T), C1, "ran"),
    ("S9 arm A: a session file in a folder naming aifoundry1 but no card: ran (the conservative side)",
     S_of({T: {"aifoundry1 (card not named)": {"n": 1, "files": ["W/out/a1-x/sessions/1/queue.json"]}}}), R(T), C1, "ran"),
    ("S10 a session file on another card (aifoundry3 card 0) only: never",
     S_of({T: {A3: {"n": 1, "files": ["docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/runs/1/proc-00.out"]}}}), R(T), C1, "never"),
    ("S11 a subtracted hit (E220's own card lane) only: never",
     S_of({T: {"SUBTRACTED": {"n": 1, "files": ["W/out/card-e220a/runs/1/proc-00.out"]}}}), R(T), C1, "never"),
]
for name, S, r, card, want in cases:
    k, why, fl = M.note1(S, r, card)
    row(name, k == want, f"{k}: {why[:140]}")

for d in sys.argv[1:]:
    try:
        S = json.load(open(os.path.join(d, "scan-e220-reg.json")))
        Rp = json.load(open(os.path.join(d, "neverrun-e220.json")))
        jf = [f for f in os.listdir(d) if f.startswith("judge-e220-") and f.endswith(".json")]
        J = json.load(open(os.path.join(d, jf[0])))
        arm = J["arm"]
        L = json.load(open(os.path.join(d, f"labels-e220-{arm}.json")))["ran_before_points"][arm]
    except (OSError, ValueError, KeyError, IndexError) as e:
        row(f"K {d}: the folder reads", False, f"{type(e).__name__}: {e}")
        continue
    mine = {q["id"] for q in M.arm_points(arm)}
    v = [x for x in Rp["points"] if x["arm"] == arm and x["id"] in mine]
    lit = sorted(x["id"] for x in v if not x["never_run"])
    lab1 = sorted(x["id"] for x in v if not x["never_run"] and M.note1(S, x, M.CARD[arm])[0] == "ran")
    row(f"K{arm} {os.path.basename(os.path.normpath(d))}: the labels re-made by note1() from the folder's own scan and report equal its labels "
        f"file and its judgement; every label is a literal label; the REPORTED literal labels equal the report's",
        lab1 == sorted(L) == sorted(J["ran_before_labelled"]) and set(lab1) <= set(lit) and sorted(J["literal_reading_REPORTED"]["ran_before"]) == lit,
        f"arm {arm}: {len(v)} points; note 1 labels {lab1 or 'none'}; literal {len(lit)} ({J['literal_reading_REPORTED']['n_never_run']} never ran)")
print(f"SELFTEST-NOTE1-E220 {sum(res)} of {len(res)} PASS")
sys.exit(0 if all(res) else 1)
