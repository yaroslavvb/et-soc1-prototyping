# Dated note 2 beside the q143k runbook's README (Thu 5 Nov 2026; the records round Q143(r), after E176's session): the rest rule counted a dry session, no registered rule reads a C FAIL for M11's holds, and the scorer writes before the gates

*Written on the Intel from about 19:55 PST on Thu 5 Nov 2026, desk only: no card, no device command, no lab box, no post.
[`README.md`](README.md) (lab `92a1b27f`), [`README.md.dated-note-1.md`](README.md.dated-note-1.md) (`6b013ad9`) and every file the two
hash lists pin (`SHA256SUMS-q143k`, `SHA256SUMS-q143k-v2`) stay as committed; no code changes. This note records what E176's session (Thu 5
Nov 2026, 17:21-17:28 PST, refused at G0, nothing scored) showed about the runbook, and the two minor faults of the line-by-line verifier
of Q143(k)'s later fix commits (16:23-16:50 PST, before any E176 datum: holds with fixes), as the evening round's critic
confirmed them. For the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
items 9 and 8.*

## 1. Step 11's rest rule counts a V3_DRY session's "session end" (a defect, found on the day)

`s11_a3_session_q143k.sh` takes the card's rest from the last "session end" line in the box's `build/e176/session.log` (its line 35).
Step 10's dry session (`s10_a3_dry_q143k.sh`, V3_DRY) runs `session_e176.sh` with the same log and writes its own "session end" there. On
Thu 5 Nov it did so at 16:40:26 (the log's line 76), so step 11 refused for 40 minutes after step 10, until 17:20:26; E176 launched at
17:21:20, after four bounded waits. Neither the runbook's desk test (its case S3 used E171's end) nor the readiness critic's timeline
caught it. E176's outcome was not affected: the card's idle floor at 17:21 already read 53.202 °C, above G0's 53.0 °C line. **For a kit
v4:** the rest rule skips a V3_DRY session's end, or step 10 runs at least 40 minutes before step 11 and the timeline counts it.

## 2. No registered rule reads a C FAIL for M11's holds (the verifier's fault 1)

Neither M11's registration with its amendments A1-A5 nor E176's kit registers a C rule; E166's form, which E176 keeps, reports the check of
C per launch and never makes it a verdict. So two sentences overclaim, and are withdrawn:
- dated note 1, "What it does to predicting power and heat": "A session scored by step 22 v2 is known to have computed every measured
  launch correctly";
- dated note 1, "What replaces it: step 22 v2", item 3, and `cclaunch_q143k.py` (lines 22 and 189): a C FAIL in a matched row
  "reaches the registered C rule".

**Read them so:** step 22 v2's launch gate checks that every launch the marks record was checked for C, and counts the checked launches
against the marks; a C FAIL in a matched row stops nothing and reaches no registered rule. A record quotes the `CCHECK-DONE` line
(launches, PASS, FAIL, all_pass) and the `COUNT-OK` lines, says "every launch the marks record was checked for C, N FAIL", and says
"computed correctly" only when all_pass is True. For E176: `CCHECK-DONE … 57 launches, PASS 57, ROUNDING 0, UNMODELLED 0, FAIL 0,
all_pass True`, `COUNT-OK p17601: 57 checked launches in 7 processes`, `NO-LAUNCH p17620`. No heat reading depends on C, so no score
changes.

## 3. The scorer writes before the gates (the verifier's fault 2, seen on real data)

`../e176/collect_e176_v2.sh` runs `score_m11_v2.py` whenever p17620's marks exist, and step 22 v2's `cc_gate` and launch gate run after it.
On E176's real collection (18:08:44-55 PST) the launch gate read NO-LAUNCH and the step exited 14 after `scored-m11.json`, `.md` and
`-lines.jsonl` had been written into the data directory. The verifier's fix was followed: on that exit 14 the lane committed nothing and
moved the collection out of the lab clone. **Read the fix so:** an exit 14 or 16 means nothing is committed **as scored**. The records round
then committed the collection unchanged as labelled evidence of the gate, under a README headed "G0-REFUSED: no hold ran, nothing scored,
not a failed prediction" ([`2026-11-05-e176-m11-holds-aifoundry3/`](../../../docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/README.md);
[E176's dated note 3](../e176/README.md.dated-note-3.md)), with the scorer's NOT SCORED files kept as written: "do not score" is not "do not
record". **For a kit v4:** the scorer runs only after both gates, or writes under a staging name that the step renames after "collected and
scored"; and, from the same verifier, `cclaunch` requires distinct `t_start_ms`, and `rb_run.py` and `nopath_q142s.py` are pinned by the
runbook's own list.

## What it does to predicting power and heat

Nothing to any number. A later M11 session's records say what step 22's gates do establish (every launch the marks record was checked for
C, with its FAIL count) and no more; the rest rule and the scorer's order are fixed before any reuse.

SPDX-License-Identifier: Apache-2.0
