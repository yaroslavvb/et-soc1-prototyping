# The pool-8 runbook for E173 and E174, dated note 1: v2 of the step drivers, after the kits' verifier (Q142(kg) fix pass)

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only: nothing here has reached a lab box. [`README.md`](README.md) and every file of this
runbook committed in `5a2a9ba0` stay as committed. The kits' verifier read that commit and found it holds with fixes. This note adds v2 beside it
and corrects two of the README's statements. The rules v2 follows were registered first, before any E173 or E174 data, in
[`../e173/E173.md.dated-note-1.md`](../e173/E173.md.dated-note-1.md) and [`../e174/E174.md.dated-note-1.md`](../e174/E174.md.dated-note-1.md)
(lab `5db9df6b`). The runs answer item 6 of the kinds page's section 11
([§ 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)).*

## What v2 adds (new files only)

| file | what |
|---|---|
| [`rb_common_v2.sh`](rb_common_v2.sh) | sources `rb_common.sh` (v1, which sources v3.1's) unchanged, and changes three things: `RB_BASE` defaults to the kits' commit `5a2a9ba0`; `rb_cc_gate` reads v2's list; the steps are named `_q142kg2` |
| [`cclist_q142kg_v2.py`](cclist_q142kg_v2.py) | the stricter list of the sessions that must carry a C log (the verifier's fault 7): the queue's record must be there; a session whose records show it ran a launch must carry a C log even when its `launches.jsonl` is lost; v2 only adds sessions to v1's list (`p8gov.required_c_logs`, unchanged) |
| [`../e174/box/step_e174_v2.sh`](../e174/box/step_e174_v2.sh) | E174's steps with v3.1's two aifoundry1 gates restored (the verifier's fault 1). The box check is a detached dry job that refuses beside a session of ours or another dry pass. The launch needs that day's clean check at the desk and on the box. The sync refuses beside a session of ours. Otherwise v1's |
| [`../e173/box/step_e173_v2.sh`](../e173/box/step_e173_v2.sh) | `step_e173.sh` line for line, sourcing `rb_common_v2.sh`, with its own name; aifoundry2's steps already had both gates |
| [`selftest_steps_q142kg_v2.sh`](selftest_steps_q142kg_v2.sh) → [`logs/selftest-steps-v2.txt`](logs/selftest-steps-v2.txt) | the desk test: v1's cases on the v2 drivers, then K1-K12 (fault 1's gates) and L0-L7 (v2's list). The stand-in `ssh` runs the runbook's own generated remote scripts in a sandbox home, with only the box's tools stood in (GNU date, `uptime -s`, a `pgrep` that names a process of ours only when the case gives one and the runbook's own pattern matches it, `setsid`). So each refusal is the script's own, not a fixture's |
| [`logs/dry-listing-v2.txt`](logs/dry-listing-v2.txt) | every step of both v2 drivers with `RB_DRY=1` (each call printed, nothing run), a logging stand-in `ssh` and `rsync` on `PATH`, a made-up window |
| [`logs/dmcmd-audit-v2.txt`](logs/dmcmd-audit-v2.txt) | `dmcmd_audit.py` on the five v2 files and on `../kinds/e78_common.py`, which the kits' audit sets omit (the verifier's fault 6) |

**The card day uses the v2 drivers**: `step_e173_v2.sh` on aifoundry2 and `step_e174_v2.sh` on aifoundry1 card 0, in the order each kit's
`README.md.dated-note-1.md` gives. `s02_window_q142kg.sh` is unchanged and shared, and the note "If both pool-8 lanes share one `$RB_OUT`" still
holds: run it once. The v2 E174 check's job (`a1c0-check-e174`) and its clean file (`a1c0-check-clean-e174.txt`) have their own names, so they
share an `RB_OUT` and the box's job directory with the k6 runbook's `a1-check-e172` without a clash.

## Two corrections to the README (the verifier's fault 4)

- **"`dmcmd_audit.py` on the 26 desk files"**: the audit (`logs/dmcmd-audit-desk.txt`) covers **25** files: 11 of E173's, 10 of E174's and this
  directory's 4. Its header, "the desk files (never run on a box)", also covers `check_e173.py` and `check_e174.py`, which do run on the box.
  Their box runs are audited in each kit's preflight list.
- **The logs' order**: the committed `logs/selftest-steps.txt` and `logs/dry-listing.txt` (04:28:19-20 PST) were written before `rb_common.sh`'s
  last write (04:31:02). The verifier re-ran both on the committed bytes: the steps log byte-identical, the listing identical with dates
  masked. v2 sources that committed `rb_common.sh` unchanged, so `logs/selftest-steps-v2.txt` exercises its committed bytes too.

## What this cannot say

As the README: the steps are tested against stand-ins and a sandbox, not against the boxes, and nothing here has run on aifoundry1 or
aifoundry2. The sandbox runs the generated scripts with macOS's bash 3.2 and BSD tools beside GNU date, while the boxes run Linux and bash 5;
the scripts use nothing bash 3.2 lacks. One thing the desk cannot show: `ours_live`'s exclusion of a `--dry` command line reads `/proc`, which
macOS lacks, so in the sandbox every match counts as live. On the box that exclusion is v3.1's, unchanged.

SPDX-License-Identifier: Apache-2.0
