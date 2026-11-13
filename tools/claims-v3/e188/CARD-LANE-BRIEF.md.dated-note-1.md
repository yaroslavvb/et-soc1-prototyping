# E188's card-lane brief, dated note 1: steps 2 and 9 are v2 from the kit's dated note 1 on, and the go's lines (Q165, before any E188 datum)

*Thu 12 Nov 2026 (week 46), PST, on the Intel, in Q165 (lane `fix-e188`), desk only: no card claimed, no device command sent, no lab box
reached, nothing posted. [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) (`726a6b64`) stays as committed; where this note differs, this note
governs. It goes with the kit's [dated note 1](KIT.md.dated-note-1.md) and the registration's
[dated amendment A1](E188.md.dated-amendment-A1.md). **No E188 datum exists.** It changes no rule, forecast, threshold, plan, cap or stop.*

## 1. The steps that change (the brief's section 2 table)

| # | the step from this note on | what to do with its exit |
|---|---|---|
| 2 | `rb/s03_desk_e188_v2.sh` (read `~/git0/flush-util/load_guard --status` first: calm or warm only, never hot). It runs step 2 v1 unchanged inside it, then pins the kit's dated note 1's lists | as the brief's step 2: anything but 0 is no box step that day, whatever it names (v1's own codes pass through; 16 names a list against its pin) |
| 9 | `rb/s11_a3_session_e188_v2.sh FULL yes` (or `PASSES no` in the fallback). It sends the rest rule v2 (`rb/rest_rule_e188_v2.sh`): a session of ours with no "session end" counts as ended at its run's latest write, not at its last log line | 0 launched (its rest line in the runbook log); 10 refused (the rest, a session or job of ours, no dry pass or build today): read its REFUSED line, wait, run step 9 v2 again; never around it |

Every other step, its order and its exits are the brief's section 2, unchanged: the look before the post, steps 5, 6, 7, 8, 10 and 11,
the data commit and step 13. The dry listing is `rb/list_steps_e188_v2.sh`. **Never that day:** step 2 v1 (`rb/s03_desk_e188.sh`) alone,
step 9 v1 (`rb/s11_a3_session_e188.sh`), or `rb/rest_rule_e188.sh` by hand.

## 2. The go's anchor lines (the brief's section 1, fourth item)

The kit's lines stay as they are (the kit's commit `726a6b64` an ancestor; `SHA256SUMS-e188-kit` and step 2 v1 unchanged since it and at
their sha256, 106 of 106 OK; `SHA256SUMS-e188-registration` 20 of 20 OK; no E188 datum in any ref before step 1). They gain three:

- the kit's dated note 1's commit an ancestor of HEAD;
- `SHA256SUMS-e188-a1`, `SHA256SUMS-e188-kit-note1` and `rb/s03_desk_e188_v2.sh` unchanged since that commit (`git diff --quiet`), each at
  the sha256 the go names (a file cannot hold its own list's sha256, so the go carries them);
- `shasum -a 256 -c` reads every entry OK: `SHA256SUMS-e188-a1` 2 of 2, `SHA256SUMS-e188-kit-note1` 10 of 10.

## 3. Two readings the lane needs (the registration's dated amendment A1)

- **Step 13, october-forecast-model's arms (A1-1):** the gate's outputs stay outside the repository, as step 13 already writes them; their
  readings go to the private Horace Hub only; public records name the arms by their committed files (`ofm-e188.json`, `arm_read_e188.py`,
  `rb/check_arms_e188.py`), with no reading.
- **A stop during the smoke's train processes (A1-2):** the session itself runs the registered fallback (PASSES) under the live stops; no
  train runs that day and none is retried. Nothing is done on the box. At step 10 read the session log ("the train smoke's gate failed");
  the records name the stop from the smoke's train part's STOP line, and every train rule reads NOT SCORED.

## 4. Labels

Every figure here is **registered** (E188.md with its dated amendment A1) or a **desk check of code** (the kit's dated note 1). Nothing here
is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
