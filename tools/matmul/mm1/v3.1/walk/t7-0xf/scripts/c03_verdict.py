#!/usr/bin/env python3
"""t7-0xf (Q221) c03: the registered T7 trace check's verdict by DECLARED-v31.md section 4's words, from this lane's computed records:
  - criteria (a), (b), (c) at both masks: c02_criteria.py over the 10 scrubbed land summaries (criteria-land.json);
  - verify-v31trace's verdict (HOLDS WITH FIXES) and whether its fixes were applied and the check re-run: the 0xf run (u2), the landed
    check_v31.py on all 10 scrubbed summaries equal key for key to the original checks (compare-checks.json), its v04 over all 10 runs
    (v04_all10.json), the scrub (SCRUB.json in the land dir), the restated wording and the named limits (the land READMEs, checked present);
  - T7's desk precondition: LAB's t7_v31.py --check re-run (t7_v31_check.json).
PASS = (a), (b) and (c) at both masks, and verify-v31trace HOLDS (or HOLDS WITH FIXES, with its fixes applied and the check re-run).
FAIL = any mismatch. NOT RUN = the traces cannot show (a) to (c) (a log set below (a)'s minimum, ...), or the desk precondition failed.
    /usr/bin/python3 -I -B c03_verdict.py <recheck dir> <land walk dir> > T7-TRACE-CHECK.json
Desk; standard library."""
import json
import os
import sys


def main():
    rd, lw = sys.argv[1], sys.argv[2]
    crit = json.load(open(os.path.join(rd, "criteria-land.json")))
    cmpc = json.load(open(os.path.join(rd, "compare-checks.json")))
    v04 = json.load(open(os.path.join(rd, "v04_all10.json")))
    t7c = json.load(open(os.path.join(rd, "t7_v31_check.json")))
    scrub = json.load(open(os.path.join(lw, "SCRUB.json")))
    wt = open(os.path.join(rd, "walk_tests_land.log")).read().strip().splitlines()[-1]
    readme = open(os.path.join(lw, "README.md")).read() if os.path.exists(os.path.join(lw, "README.md")) else ""
    wreadme = open(os.path.join(lw, "walk", "README.md")).read()
    masks = crit["masks"]
    pre = all(v.get("pass") for v in t7c["checks"].values())
    v04_ok = all(r["working_traced_equal_model"] == r["working_selected"] == r["trace_sha_eq_frozen"] == r["criterion_b_equal"]
                 == r["criterion_c_equal"] and not r["first_differences"] for r in v04["runs"].values())
    recheck_ok = all(v["n_keys_differing"] == 0 and v["verdict_land"] == "EXACT" for v in cmpc.values()) and len(cmpc) == 10
    fixes = {
        "1 the 0xf run in u1's form (every hart of every compute shire logged)": "u2" in crit["runs"] and crit["runs"]["u2"]["logged_harts"] == 2048,
        "2 'every off-mask hart ran no user-mode instruction' restated as what was logged": ("16 logged off-mask harts" in readme),
        "3 'distinct tiles per shire-step' with section 4's caveat": ("distinct tiles per shire-step" in readme and "5.33" in readme),
        "4 the post hoc tallies per pair": ("3 of 8" in readme and "3 of 10" in readme and "3 of 11" in readme),
        "5 the three model limits named in walk/README.md": all(w in wreadme for w in ("firmware tensor operations", "C-store placement",
                                                                                         "Instruction killed")),
        "6 home paths and logins scrubbed, old and new sha256 recorded": bool(scrub["rewritten"]) and scrub["frozen"]["unchanged_bytes"],
    }
    applied = all(fixes.values())
    a_b_c = {mk: {k: masks[mk][k] for k in ("criterion_a", "criterion_b", "criterion_c")} for mk in masks}
    fail = any("FAILS" in v.values() for v in a_b_c.values()) or not v04_ok
    undecided = any(v["criterion_a"].startswith("UNDECIDED") for v in a_b_c.values()) or len(masks) != 2
    if not pre:
        verdict, why = "NOT RUN", "T7's desk precondition failed"
    elif fail:
        verdict, why = "FAIL", "a mismatch in (a), (b) or (c)"
    elif undecided:
        verdict, why = "NOT RUN", "a log set below (a)'s minimum at a mask"
    elif not (applied and recheck_ok):
        verdict, why = "NOT RUN", "verify-v31trace's fixes not all applied or the check not re-run"
    else:
        verdict, why = "PASS", "(a), (b) and (c) hold at both masks over every traced run; verify-v31trace HOLDS WITH FIXES with its fixes applied and the check re-run; the desk precondition holds"
    out = {"what": "MM1-v3.1's registered T7 trace check (DECLARED-v31.md section 4, sha256 d58601fa..., landed 7375bc9c): the verdict",
           "verdict": verdict, "why": why, "labels": "simulated (sys_emu traces on aifoundry3, not the card); registered rule; desk code",
           "frozen_predictions": crit["frozen_predictions"], "criteria_by_mask": a_b_c,
           "masks": masks, "per_run": crit["runs"],
           "desk_precondition_t7_v31_check": {k: v.get("pass") for k, v in t7c["checks"].items()},
           "t7_v31_sha256": t7c.get("t7_v31_sha256"),
           "check_re_run_on_scrubbed_land": {"check_v31_runs_equal_key_for_key": sum(1 for v in cmpc.values() if v["n_keys_differing"] == 0),
                                             "check_v31_exact": sum(1 for v in cmpc.values() if v["verdict_land"] == "EXACT"),
                                             "v04_all_runs_equal_frozen": v04_ok, "walk_tests": wt},
           "verify_v31trace": {"verdict": "HOLDS WITH FIXES", "fixes_applied": fixes},
           "per_kernel_reading_note": ("The registered words judge the minimum log set per mask ('at each mask the traces log at least ...; one "
                                       "run per mask that logs every hart of the chip also meets this'). u2 meets it alone at 0xf and u1 at "
                                       "0x1111 (rgm136 gemmL 1x1x16). Read per kernel, rgm211 gemmLn and rgm136 gemmLnc (2x4x16, 40 of 64 harts "
                                       "a shire logged) would leave (a) undecided for those kernels: not the registered reading.")}
    json.dump(out, sys.stdout, indent=1, default=str)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
