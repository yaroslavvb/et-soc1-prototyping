# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 22:00 PST: D1's collection route, fixed for later card days (Q142(s))

*Written beside [`README.md`](README.md) and not inside it, as the link back from this complaint to its fixes (the owner's rule of 29
Oct 2026: a fix always links the original complaint). The README (`4293d151`) and its three dated notes stay as committed. Nothing in
E163 changes: no file of this directory, no pass, no verdict, no number. Desk only: no card, no device command, no lab box.*

**The complaint.** It sits in two places:
- **D1** (§ Registered against what happened): the runbook's `s22_collect.sh e163` copies into an absolute `build/e163-raw`.
  `reduce_e78.py` records the pass directories as given (`dirs`, line 428), so that route would have written the Intel's home path into
  `e163.json` and every arm. This session was collected over a repo-relative copy instead.
- **[Dated note 1](README.md.dated-note.md) § 4**: both runbook versions' `s22_collect.sh e163` (v1 line 55, v2 line 59) copy into
  the absolute `$RB_REPO/build/e163-raw`.

**The fixes, for later card days.**
- **Runbook v3** (lab `326f1293`, 20:14:12 PST): [`v3/README.md`](../../../../tools/claims-v3/q141k-runbook/v3/README.md), faults 1
  and 2.
  - The raw copy is repo-relative, `build/e163-raw`.
  - A desk-path gate reads every file a collection wrote before the step says "collected".
  - Its desk case Y1r ran the registered `reduce_e163.py` on this directory's pass p16310 by each route. By v2's, the clone's path
    entered `e163.json`'s `dirs` and 97 rows of `runs.csv`; by v3's, neither
    ([`v3/logs/selftest.txt`](../../../../tools/claims-v3/q141k-runbook/v3/logs/selftest.txt)).
- **Runbook v3.1** (this round): [`v3.1/README.md`](../../../../tools/claims-v3/q141k-runbook/v3.1/README.md). It keeps v3's route.
  - Its end-to-end run of the real collector, reducer, check of C and scorer, over this directory's committed raw layout, reproduces
    this directory's 43 top-level outputs byte for byte once the pass prefix is normalised. All 28 verdicts are identical, and no desk
    path is written ([`v3.1/logs/e2e-ccheck.txt`](../../../../tools/claims-v3/q141k-runbook/v3.1/logs/e2e-ccheck.txt)).
  - It also stops a collection whose check of C did not finish (its fault 1): with the check crashed, the scorer would have left 17 of
    the 28 rules NOT SCORED and 5 C rules reading FAIL.
  - This session's own check, [`ccheck/ccheck-all.json`](ccheck/ccheck-all.json), reads finished: 4,062 launches, all PASS (v3.1's
    case Z0).

SPDX-License-Identifier: Apache-2.0
