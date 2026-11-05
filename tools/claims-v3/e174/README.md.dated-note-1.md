# E174's kit README, dated note 1: the box steps run through step_e174_v2.sh (Q142(kg) fix pass)

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only. [`README.md`](README.md) (lab `5a2a9ba0`) stays as committed. This note supersedes its
box-step lines for the card day, after the kits' verifier's fault 1. The rules this note follows are in
[`E174.md.dated-note-1.md`](E174.md.dated-note-1.md) (lab `5db9df6b`, committed before this note and before any E174 data). It answers item 6 of
the kinds page's section 11 ([§ 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)), as the kit does.*

## The box steps, in order (superseding "The box steps, in order")

First `export RB_OUT=<this card day's directory, outside the repo> RB_LOCK=<the round's lock file>` and, once,
`bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <day> <last start> <last end>`. Every step is
`bash tools/claims-v3/e174/box/step_e174_v2.sh <step>`. **Never `step_e174.sh`'s `check` or `launch`**: they lack the two gates below.

1. `look`: read only, any time; this is how E172's end is read. It shows the host's boot against E84's read, et-who (card 0's lines empty;
   nothing of ours on card 1), E172's `session end` lines if its records are on the box, the logins, `/home`'s room, the three binaries against
   their pins, and our device processes.
2. `sync`: **only once E172 has ended**. One 60 s read first refuses (10) while a card session of ours or a dry pass of the runbook runs on
   aifoundry1. Then the one `rsync -a -c -R` of E174's harness files into `aifoundry1:nekko/`, from a clean, pushed tree.
3. `check start`: the box check as a detached dry job, `a1c0-check-e174`. It refuses (14, `JOB-REFUSED`) while a card session of ours runs on
   aifoundry1 (E172's queue, session, block or runner) or another dry pass of the runbook runs there (E172's box check). On the box it runs
   `check_box_e174.sh` and reads it. Then **`check wait`**, repeated until it exits 0 (17 = call again). 0 means **HARNESS OK 110 + 3
   binaries**, preflight **GO**, the tiles OK, pool 8's 89, the dry stop-path test rc 4, the dry smoke rc 0 and 126 runs listed, and it writes
   `RB_OUT/a1c0-check-clean-e174.txt` for the window's day. A check that reads unclean is 16; one started on another day is 10.
4. The day's one post (the card lanes, under the post's lock): aifoundry1's clause covers both cards.
5. `launch` (or `launch subset`): the window's start, end and deadline gates; then **today's clean file** (else 10, no call); then one 60 s guard
   read on the box: no dry pass of the runbook running, no card session of ours, the host booted before the firmware read, and the check job
   ended rc 0 today. A refusal there is 10 and the launcher is never sent; the identity stop is 16. Then
   `ssh ... "bash -s -- '<deadline>' '<last start>' '<last end>' [subset]" < box/launch_e174.sh`, whose own refusals are unchanged (exit 2, 3,
   4, 5, 6, 9; IDENTITY-STOP 16 at the step). It detaches `queue_e174.py` and prints `LAUNCHED e174 T0=...`.
6. `wait`, repeated: 0 ended (read `queue.jsonl`'s `s1_end` rc and `s1/end.json`), 16 halted, 17 still running. Then the day's post.
7. `pull`: a bounded copy of `aifoundry1:nekko/build/e174/` into `build/e174-raw/`.
8. `collect`, at the desk: [`collect_e174.sh`](collect_e174.sh), as before; then **the C-log gate with v2's list**
   (`../q142kg-runbook/cclist_q142kg_v2.py`: the queue's record must be there; a session whose records show a launch must carry a checked C
   log) and the desk-path gate. Then the public-text scan, then the data commit.

## The table's rows, as they now read

| step | state |
|---|---|
| the box steps, through the ported runbook | [`box/step_e174_v2.sh`](box/step_e174_v2.sh) over [`../q142kg-runbook/rb_common_v2.sh`](../q142kg-runbook/rb_common_v2.sh): its desk test, `../q142kg-runbook/logs/selftest-steps-v2.txt`, runs every case of v1's on the v2 drivers and the new gate cases K1-K12 and L0-L7 (the remote scripts run in a sandbox); its dry listing, `../q142kg-runbook/logs/dry-listing-v2.txt` (17 of 17 steps, no call) |
| everything on the box | waits for **E172's end** on card 1 (now enforced by the sync, the check and the launch), the owner's go, fresh lab approvals and the day's post |

`box/step_e174.sh` and the rest of the kit are unchanged: the runner, queue, protocols, harness, preflight, `check_box_e174.sh`,
`launch_e174.sh`, `look_e174.sh`, `wait_e174.sh` and `collect_e174.sh`. The harness (`harness-e174.json`, 110 files) pins none of the step
drivers, which run on the Intel, so it is unchanged and reads HARNESS OK.

SPDX-License-Identifier: Apache-2.0
