# E172's run kit: blind pool 8 on aifoundry1 card 1 at 600 MHz, M10 primary, every session's C checked (Q142(k6); registered, not yet run)

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only (Q142(k6)): no card was claimed, no device command was sent, no ssh to a lab box
was made. The registration is [`E172.md`](E172.md), committed first with E171's and nothing else (`4441083f`, 03:38:53 PST); the scorer
followed (`tools/claims-v3/p8-600/`, `a518aa11`, 03:55:27). It answers item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) (with items 8 and 9) and the Q142(r)/(p)/(d)
critic's `next` rank 2 for card 1. The kit is E164's last form on this card: `box/` steps, the corrected launcher, the login scrub in the
collector. Nothing here changes a rule of E172.md.*

## What it does to predicting power and heat

It makes pool 8's blind test of M10 runnable and scorable on the second 600 MHz card as registered: M10's power and 4.5 s heat for 31 new
kinds against M9, the session scale against its a-priori arm, the check anchors (KA pooled with E171) and the re-runs' level or gain
against E157 and E164. No frozen prediction changes (Q142(x)'s `4576fb90`). The before is M10's held-out error on card 1 (pool 7's kinds
0.187 W; the 4.5 s law 0.31-0.32 °C for floats); the after is what the card measures.

## Checked at the desk

- **The scorer** (`../p8-600/`, all six self-test parts PASS): E164's 12 committed rule readings, intervals and verdicts reproduced with
  E164's registered seeds; its C-session check lists E164's 5 C-logged sessions and finds each checked to the end.
- **The items and orders** (`e172_common.py --verify`, 0 problems): 64 pool tiles, the five frozen pool files, a pass of 84 runs holding
  exactly the 64, 75 with `E172_DROP_P2=1`, the ten smoke items, re-derived by `make_plan_e172.py` from the frozen card-1 predictions.
- **The watcher** ([`selftest_watcher_e172.py`](selftest_watcher_e172.py) → [`logs/selftest-watcher.txt`](logs/selftest-watcher.txt), K1-K5
  PASS), with card 1's stop on the hottest minion-shire field (E164's rule).
- **The device commands**: `dmcmd_audit.py` unchanged on the session's file set **GO, 32 send sites, 0 disallowed**, every command READ, with
  E153's one exception (`lib.sh:154`; NO-GO without it, exactly there) ([`dmcmd-audit.txt`](dmcmd-audit.txt),
  [`dmcmd-audit-noexcept.txt`](dmcmd-audit-noexcept.txt)); the desk files and E164's login scrub GO, 0 sites
  ([`dmcmd-audit-desk.txt`](dmcmd-audit-desk.txt)); the six box steps GO, 0 sites ([`dmcmd-audit-box-steps.txt`](dmcmd-audit-box-steps.txt)).
- **The Intel dry pass** (`drypass_intel_e172.sh` → [`logs/dry-intel.txt`](logs/dry-intel.txt), E164's with E163's python3 shim and stand-in
  `ssh`, `rsync` and `scp` that log and refuse): `check_e172.py --desk` HARNESS OK (99 files), `--verify` 0 problems, the preflight GO; a
  pass (86 launches through the C wrapper), the smoke (10), a pass with the priority-2 switch (77); the stop-path test ends 1 as a dry run
  must; card 0 and a missing `V3_DEVICE` refused; the queue's deadline, budget and STOP rules on a stub block; the session without a deadline
  refused; the whole session dry; **no network call**.
- The public-text scan over every file (the lab's fixed list and the lane's; the privacy table is absent on the Intel).

## Card-minutes and the cap

**At most 65 card-minutes** (3,900 s from `E172_T0`, 60 s reserved for the closing read; a pass starts only if its projected end is inside
3,840 s and before `E172_DEADLINE`). Expected **about 51-53**: the stop-path test and the smoke about 58 s, then four passes of about
735-763 s (E164's 837-869 s for 98 launches, scaled to 86) with 10 s between; a fifth would end past 3,840 s and the queue's rule stops before
it. The day's post: one aifoundry1 clause, `using aifoundry1 card 1 for 1.5 h, until ~HH:MM PST`, which card 0's E174 extends after E172 ends.

## The order on aifoundry1

E172 first; card 0's E174 (the (kg) lane's kit) starts only after E172 has ended: never two of our sessions on aifoundry1 at once (the
runners count device openers and the kernel module's use count across both cards). The launcher refuses anything of ours on either card.

## The box steps that wait for the approvals and his go

From the Intel, at the top of the lab tree after `git pull --ff-only`; each remote call is `ssh -o BatchMode=yes -o ConnectTimeout=10
aifoundry1 'bash -s' < <file>` (the runbook's steps, [`../q141k-runbook/k6/`](../q141k-runbook/k6/README.md), wrap each with the 15 s probe,
the bounds and the login-link stop):

1. **Look** (`box/look_e172.sh`): the identity by continuity (the host booted before E82's firmware read of 2026-10-31 13:45:24 PDT), et-who
   (card 1's own lines decide; nothing of ours on card 0), logins, disk, the binaries against E164's pins. Read et-who's lines; never copy a
   name.
2. **Sync** (`box/sync_e172.sh`, on the Intel): `tools/claims-v3/e172/`, `tools/claims-v3/kinds/blind8/` and the three pinned watcher files
   into `~/nekko`.
3. **Check on the box** (`box/check_box_e172.sh`): `check_e172.py` with the binaries (HARNESS OK, 103 files), the preflight (GO), the tiles,
   pool 8's SHA256SUMS (89 OK), the dry pass, the dry smoke and the dry stop-path test.
4. **The claim**: the day's one post carries the reservation (section 15's rule, rewritten with EXPECT_TEXT).
5. **Launch** with `box/launch_e172.sh` and the quoted deadline (the round's time gate less 10 minutes):
   `ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '<YYYY-MM-DD HH:MM PST>'" < tools/claims-v3/e172/box/launch_e172.sh`
   (with `E172_DROP_P2=1 bash -s -- …` only if the registered subset was chosen before the launch). It refuses with 2, 4, 3 or 9 before
   anything is launched.
6. **Wait** (`box/wait_e172.sh`, one bounded wait of at most 540 s, repeated); then the post's release edit, or the clause handed to E174.
7. **Pull, then collect**: `bash tools/claims-v3/e172/box/pull_e172.sh` (into `build/e172-raw`), then
   `PY=/usr/bin/python3 E172_DATE=<the day> [E172_OWNER=<the box login of record>] nice -n 10 bash tools/claims-v3/e172/collect_e172.sh build/e172-raw`
   → `build/e172-out/<day>-e172-blind8-card1/`; the C-session gate (`python3 -B tools/claims-v3/p8-600/ccsessions_p8.py --run E172 --raw
   build/e172-raw --ccheck <out>/ccheck/ccheck-session.json`, exit 0 or nothing is scored as registered); the collector's scrub must read OK
   (exit 7 = commit nothing); the desk-path gate; then `docs/reports/data/<day>-e172-blind8-card1/`. KA pooled with E171:
   `score_p8_600.py ka-pooled <E171 scored.json> <E172 scored.json>`.

## Files

`E172.md` (the registration); `plan-e172.json`, `make_plan_e172.py`; `e172_common.py`, `run_e172.py`, `block_e172.sh`, `queue_e172.sh`,
`session_e172.sh`, `check_e172.py`, `preflight_e172.sh`, `smoke_gate_e172.py` (the box); `box/look_e172.sh`, `sync_e172.sh`,
`check_box_e172.sh`, `launch_e172.sh`, `wait_e172.sh`, `pull_e172.sh` (the box steps); `reduce_e172.py`, `collect_e172.sh` (the desk; the
scrub is E164's `scrub_etwho_e164.py`, unchanged); `make_harness_e172.py`, `harness-e172.json`; the four `dmcmd-audit*.txt`;
`selftest_watcher_e172.py`, `logs/selftest-watcher.txt`; `drypass_intel_e172.sh`, `logs/dry-intel.txt`; this README.

## Compute

The Intel, through the round's local slot, one job at a time, at nice 10: the two port scripts (in the lane's scratch), the plan maker, the
item check, the watcher test (twice: the first failed K2, K4 and K5 on the test's own lines, which carried aifoundry3's latch value that
card 1's every-field stop reads; fixed), the harness maker, the dry pass (twice: the first ran under a Python 3.7 my PATH put first, and its
preflight failed to parse; the shim fixed it) and the four audits. No lab box, no mini job.

SPDX-License-Identifier: Apache-2.0
