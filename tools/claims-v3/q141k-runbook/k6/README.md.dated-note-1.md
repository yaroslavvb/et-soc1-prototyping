# The k6 runbook, dated note 1: step 22 v2 (the scale anchors' C status, and the pooled KA read for the registered pair only), its dry listing, and a desk test of 35 checks

*Written Thu 5 Nov 2026 (week 45), PST, on the Intel, in Q142(k6)'s fix pass (lane `fix-desk-q142k6-kits`), desk only: no card claimed, no
device command sent, no ssh to a lab box, nothing posted. New files only: [`README.md`](README.md) and every file of `9a2630ff` stay as
committed. It follows dated note 1 beside the registrations ([`../../e171/E171.md.dated-note-1.md`](../../e171/E171.md.dated-note-1.md),
[`../../e172/E172.md.dated-note-1.md`](../../e172/E172.md.dated-note-1.md), `2502ba81`) and the scorer's v2 (`86d10a75`,
[`../../p8-600/README.md.dated-note-1.md`](../../p8-600/README.md.dated-note-1.md)). It answers faults 1, 2 and 5 of the kit's verifier
(`verify-desk-q142k6-kits`), for item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

## Results first

- **Step 22 is now `s22_collect_k6_v2.sh e171 | e172 | ka`, and the dry listing is `list_steps_k6_v2.sh`.** They supersede
  `s22_collect_k6.sh` and `list_steps_k6.sh`, which stay as committed. Every other step is unchanged.
- **What v2 adds to step 22.**
  - `scale_gate` (N2): after the collector and `cc_gate`, `score_p8_600_v2.py scale-c` writes `scale-c.json` and `scale-c.md` beside
    `scored.json`. They hold each scale anchor's C status and the `c_clean_scale` arm when an anchor in s is not C all PASS. Its refusal or
    any other non-zero exit stops the step with 14 before "collected", and the desk-path gate covers what it wrote.
  - The `ka` route (N1) goes through `score_p8_600_v2.py ka-pooled … --scale-c …`, which reads only E171's and E172's own scored sessions.
    Its refusal (6) stops the step with 16; any other non-zero exit stops it with 14. The closing line gives the pooled verdict and the
    arm's beside it.
  - The desk test's stand-ins (`K6_COLLECT_E171`, `K6_COLLECT_E172`, `K6_SCALEC`, `K6_KAPOOLED`) are read only with `RB_DESKTEST=1`.
    Set without it, the step refuses (10) before any call. v1 read its two stand-ins whenever they were set.
- **Two things in v1's `ka` route that v2 does right** (cosmetic: neither changes a number, and `ka-pooled.json` was written either way):
  1. `rb_run.py` exits 14 for any non-zero command and keeps the command's own status as `child_rc=` in its `RB_LOG` line. So v1's
     "ka-pooled exited $RB_RC" could only ever say 14. v2 reads `child_rc` right after the call.
  2. v1 ran the desk-path gate (another call) before reading the verdict, so its closing "P8-KA pooled read:" line read the gate's
     output and printed nothing after the colon. v2 reads the verdict right after the call.
- **The desk test, [`logs/selftest-v2.txt`](logs/selftest-v2.txt): 35 of 35 checks PASS** (`selftest_runbook_k6_v2.sh`). Stand-in `ssh`
  and `rsync`, first on PATH, serve stand-in boxes and refuse any other host; the steps run in a scratch copy of the tree.
- **The dry listing, [`logs/dry-listing-v2.txt`](logs/dry-listing-v2.txt):** 20 step calls, as v1's, each exit 0. It ran in the lab
  clone with stand-ins first on PATH that log and refuse every `ssh` and `rsync`; they saw no call.
- **Device commands:** see [`logs/dmcmd-audit-v2.txt`](logs/dmcmd-audit-v2.txt). `dmcmd_audit.py` over the 18 shell files of `k6/`
  (v2's among them) and `score_p8_600_v2.py`, with E128's guard beside them, reads **GO, 11 send sites, 0 disallowed**: the same 11
  READ sites as v1's audit, every one a line of the guard. v2 adds none. Without the guard
  ([`logs/dmcmd-audit-v2-bare.txt`](logs/dmcmd-audit-v2-bare.txt)) it reads NO-GO at exactly step 9's guard call
  (`s09_a3_reads_k6.sh:20`), as v1's did.

## The cases

| cases | what | from |
|---|---|---|
| A, L1-L4, C1-C6, O1 | the dry listing (now v2's); a login link at the probe (11, one lock line); a probe that never answers (12); a read past its bound (13); a preflight that reads wrong (16); a good E171 collection; a missing C log, a skipped session, a stale check, a launched stop-path test (14 each); a desk path in an output (16); `ours_live`'s names (10 of 10) | `selftest_runbook_k6.sh`'s 12, the C cases now through v2 |
| K1-K12 | e171: a FAILED pass with launches and every log checked (0); the smoke's C log missing; a FAILED pass with no C log; a C log with no host record; the check's `--out` never written; one launch not judged; no success line (14 each). e172: a good collection through `box/pull_e172.sh` (0); a pass with no C log; a launched stop-path test; a directory missing on the box, stopped before any collection (14 each). s08: a remote read that fails (non-zero) | the kit verifier's twelve |
| S1-S5 | scale-c refuses, on e171 and on e172 (14); scale-c exits 0 with no `SCALE-C` line (14); a desk path in `scale-c.md` (16); a stand-in set without `RB_DESKTEST=1` (10, nothing called) | new |
| KA1-KA5 | the pooled read and the arm beside (0); ka-pooled refuses the pair (16); ka-pooled exits 9 (14); no `scale-c.json` beside a scored file (10, ka-pooled never called); **the real `score_p8_600_v2.py`, not a stand-in, given E171's scored file in E172's place: its refusal (6) reaches the gate (16)** | new |

`score_p8_600_v2.py` itself is tested end to end (both cards, the refusals, real data) by its own self-test; here the stand-ins test the
step's routing. **Not covered** (the verifier's fault 5): step 13's own cases (the launcher's refusals, IDENTITY-STOP, a login link after
the probe) and a lost detached job's JOB-LOST (`rb_common.sh`'s job wait, which steps 10 and 12 use). Steps 10, 12 and 13 are not ported
here and stay as committed; a later port carries those cases.

## What it does to predicting power and heat

Nothing to any number. On the card day, step 22 cannot call a session collected unless the record says which anchors set its float
scale and whether each anchor's C checked. And the pooled check of term a is read only from the two sessions it was registered over.

## Compute

The Intel, through the round's local slot, one job at a time at nice 10: four runs of one job (the desk test, the dry listing and the two
audits), about 40 s each.
1. 05:53:46: 29 of 35. S1, S2, KA1-KA3 and KA5 failed: v2 read `RB_RC`, always 14, and read the verdict after the desk-path gate.
2. 05:55:12: 30 of 35. The status was read from `rb_run.py`'s printed line, which is not in the output the step reads.
3. 05:56:36: 35 of 35. This run read `child_rc` from `RB_LOG`, and the desk test copied `p8-600/SHA256SUMS`, which its `*.*` copy had
   missed, so the real v2 could refuse rather than stop.
4. 05:57:39: 35 of 35. These are the committed logs, after two cosmetic changes: one box counted per stand-in call, and the dry listing's
   wording of the `SCALE-C` line.

No lab box, no mini job, no card.

SPDX-License-Identifier: Apache-2.0
