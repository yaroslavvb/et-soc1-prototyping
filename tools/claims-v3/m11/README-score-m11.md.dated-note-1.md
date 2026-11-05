# Dated note 1 beside README-score-m11.md (Thu 5 Nov 2026; Q143(k)'s fix pass): `score_m11_v2.py` supersedes `score_m11.py` for every M11 session, with three scorer duties v1 did not meet

*Written on the Intel, desk only, before any M11 hold: no E176 or E177 data exists in any ref. The fix pass wrote `score_m11_v2.py` and a
first draft of this note at about 13:47-13:57 PST on Thu 5 Nov 2026; its account's weekly limit then cut it before any commit. Its takeover
finished both from about 14:20 PST. `score_m11.py`, its self-test output, its README and `SHA256SUMS-score-m11` (lab `03582d2f`) stay as
committed. The README above is right about what v1 does; this note says where v1 fell short, and that M11 sessions are scored by v2. For the
kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8.*

## What v1 did not do (the verifier of Q143(k), Thu 5 Nov 2026, about 12:52-13:30 PST)

- **(a) The lines were not written first.** A4-8 says the scorer "writes a and g to its output before it reads L2's e", and A2's duty
  reads "before it reads any later hold's e". v1's `read_session_a3` reads every hold's e before any line is computed, and v1 writes one
  JSON at the end. No reading changes: the code is deterministic, committed before any M11 hold, and its lines never read a later hold.
  But the duty was not met, and the README did not say so (fault 4 (a)).
- **(b) A2's miss on L2 alone was not printed.** A4-2 and A4-8 list A2's calibrated miss on L2 beside RMS_c(I8). v1 prints A2's RMS_c over
  all three later holds only (fault 4 (b)).
- **(c) Its self-test covered 3 of A4-8's read-rule cases.** The other cases appear only in A4's design printout, § 2, through the same
  imported `cal_i8_by_name` (fault 4 (c)).
- **Two printed reasons were wrong** (fault 3). The decision was right in both:
  - with HM-CAL-I8 NOT SCORED, v1 printed "nothing from A4: the int8 holds' misses read as noise (E4′)";
  - with HM-E144 NOT SCORED, it printed "nothing from A4: HM-E144 DOES NOT REPEAT".
- **Not covered:** A1-4's BOTH paths that carry a term (fault 5, a nit; v1 decides them right).
- **No A5:** v1 predates A5 (lab `9b084c66`, 13:46:11 PST), so it never reads HM-CAL-AG or HM-I8-AG. It would state every entry as A2's
  and A4's tables did before A5-1.

## What v2 does

[`score_m11_v2.py`](score_m11_v2.py) imports `score_m11.py` unchanged. Every reading and decision v1 makes is v2's too, and v2 refuses
(exit 1) if its A4-3 decision ever differs from v1's. Besides that, v2:
- **reads in three stages.** Every session's H_E and Z are read, and its A2 line is appended to the lines file (`--lines`, fsync'd).
  Only then are L1 and S read, and the A4 line appended; only then is L2 read. The reading order is printed in the JSON. This meets (a).
  The lines are the decision's own arithmetic (`design_power_heat_a2.cal_line`, and A4-1's two-point line), so where the decision reads a
  session its line equals the stage line; a stage line the decision does not read is one that a fact known only after stage 3 rules out
  (A2: fewer than two later holds scored; A4: L2 not scored, or outside the pair's span);
- **prints A2's line on L2 alone** beside RMS_c(I8), which meets (b);
- **reads HM-CAL-AG and HM-I8-AG** (A5-2) and states an entry's form by A5-3. An entry made while HM-LG counted one session is labelled
  (A5-4);
- **prints A4-3's reasons as A5-4 says**, read before `i8_entry`;
- **checks `SHA256SUMS-a5` and `SHA256SUMS-score-m11` first,** before v1's own checks on import, and counts A5's commit in the blind
  precedence.

## Its self-test

[`selftest-score-m11-v2.txt`](selftest-score-m11-v2.txt) and `.json` read **PASS**. The committed run was 14:30:50-14:33:47 PST. A
development run into the fix lane's scratch, 14:27:44-14:30:10, gave byte-identical files. It covers:
- `score_m11.py`'s own self-test, re-run unchanged: PASS;
- all ten of A4-8's read-rule cases: every hold scored; H_E not scored (A4 still reads); L2, S or L1 not scored; L2 run before S ended; a
  span of 2.9 °C; L2 above L1's P or below S's; a span of exactly 3.0 °C;
- A5-4's two reasons, with what v1 printed beside each;
- the three BOTH paths that carry a term: both enter; gain enters, refitted alone; level enters, refitted alone;
- A5's readings on synthetic sessions:
  - an A4 entry stated per session and one stated common;
  - an A2 entry stated per session;
  - an entry while HM-LG counted one session;
  - one session;
  - the two forms of X²_AG on 200 random pairs, equal to 9.9e-14;
- A5's committed cell through v2's rules, equal (§ 0.1's case on the likeliest pattern: A2 21.1 / 0.5, A4 45.3 / 14.2, all four forms
  exercised);
- the staged reading on E154's committed pass with its holds renamed to M11's (H_M→H_E, K_S→Z, K_Q→L1, K_L→S, K_O→L2). Every hold equals
  v1's reading and every decision equals v1's; the lines come before the later holds. Both stage lines are null there (the pair spans
  0.511 °C, under A2's 6.0; L1 and S 1.717 °C, under A4's 3.0), and each null line goes with a NOT SCORED decision; the order read from the
  launch records alone equals the final order. It is labelled post hoc, as a 3 Nov session must be;
- **added by the takeover**, because the value check above cannot run where both lines are null:
  - the same pass under a second renaming (H_M→H_E, K_S→L1, K_Q→S, K_L→Z, K_O→L2). L1 and S span 5.699 °C with L2 inside (w 0.9374), so
    A4's line is read: stage 2 wrote a = −0.40575 °C, g = 0.072469, and the decision reads −0.4058 / 0.0725 at its printed precision. A2's
    line is null and NOT SCORED (its pair is not run first, a reordering). Holds and decisions equal v1's;
  - 4,000 synthetic sessions, a quarter of them within 0.02 °C of a registered line (A2's 6.0 °C span, A4's 3.0 °C span, L2 at an end of
    the span): the stage lines equal the decision's lines bit for bit wherever the decision reads (A2 873, A4 626), every null stage line
    goes with a NOT SCORED decision, and every stage line the decision does not read is ruled out only by a fact known after stage 3 (A2 49,
    A4 951). No problem;
- the precedence with A5's commit.

```
/usr/bin/python3 -B tools/claims-v3/m11/score_m11_v2.py --self-test --workdir <a new scratch dir> --json <out>
/usr/bin/python3 -B tools/claims-v3/m11/score_m11_v2.py score --a3 <pass dir> [--a3 <pass dir>] --lines <out.jsonl> --json <out> --md <out>
```

**Which scorer runs.** E176's collection runs v2, through the q143k runbook's step 22 v2 (`../q143k-runbook/s22_collect_q143k_v2.sh`),
which calls `../e176/collect_e176_v2.sh`. Both come in this fix pass's next commit. Never `score_m11.py` by itself, never `collect_e176.sh`, and
never `s22_collect_q143k.sh`. [`SHA256SUMS-score-m11-v2`](SHA256SUMS-score-m11-v2) pins v2, its self-test output, this note,
`SHA256SUMS-score-m11` and `SHA256SUMS-a5`.

## Compute

Desk only, on the Intel, at nice 10 through the round's local slot, one job at a time on one core. The cut pass: a development run
(13:52:23-13:54:10) and a run into the repo (13:54:30-13:56:19), both without the takeover's two checks, uncommitted and replaced. The
takeover: a development run (14:27:44-14:30:10) and the committed run (14:30:50-14:33:47). No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0
