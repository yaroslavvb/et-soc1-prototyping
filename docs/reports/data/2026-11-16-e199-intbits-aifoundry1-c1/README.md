# E199 data: E192's reference session on aifoundry1 card 1, 2026-11-16 (RAN FULL)

*Written by the card lane `card-e199` (round Q191) at step 12 on Mon 16 Nov 2026, in the form of E199's kit
(`tools/claims-v3/e199/rb/data-readme-form-e199.md`). Every figure comes from the session's own files (`session/session.log`,
`run/gate.jsonl`, `run/runs.jsonl`, `run/telemetry.jsonl.gz`, `facts-e199.json`, the build record) and the day's runbook log, read after
the collection and before the reduction and the transport scorer ran. It holds **no forecast number of any sealed forecast and no score**:
step 13's outputs (E199's transport verdicts) are committed by a records lane after this commit, in their own files. Every figure says which
it is: **measured** (this session's records), **registered** (E199.md, E192.md), **desk check of code**, **REPORTED**.*

## Results first (measured; no forecast number, no score here)

- **Passes complete: 9 of 9** (pass 0 the registered warm-up). **Launches recorded: 3,255**: the smoke's 3 runs of 5, then 36 runs of 10
  in each pass. Every launch record reads rc 0 and ok, with 0 bad check lines and 1,024 participants. No run was dropped and no pass was
  cut. **Card time 3,617 s = 60.28 card-minutes**, from the first card command (the start config read, 03:42:15 PST) to the session end
  (04:42:32 PST). Cap 65; registered about 60; E192 measured 59.52.
- **The sampler: pvt**, in the wrapper's words "its probe answered with 34 sensors on every tick". All 36,150 samples carry the 34 codes.
- **THE IDENTITY GATE (a)**, the start config read: "IDENT-A OK: /dev/et1_mgmt, physical device ID 1, minion_mv 499, TDP 65 W / 65 C /
  600 MHz; runtime lines dropped 1".
- **THE IDENTITY GATE (b)**: OK, 0.14 s after the first sample. The gate's counts:
  - ours on card 1's management node: 1; ours on card 1: 1;
  - ours on card 0: 0; ours elsewhere: 0;
  - another login's on card 1: 0; another login's on card 0: 0.
  The sampler's node was /dev/et1_mgmt.
- **The end config read** (recorded): "exit 0; IDENT-A OK: /dev/et1_mgmt, physical device ID 1, minion_mv 499, TDP 65 W / 65 C / 600 MHz;
  runtime lines dropped 1 (recorded, not a gate)".
- **Every runtime identity line names card 1:** all 676 "PCIe target" lines in `run/stderr.txt` name card 1's ops node, /dev/et1_ops, and
  all 676 "Physical device ID" lines read 1.
- **The smoke gate: GO.** nop, add.a.f2 and add.cr.l31 each gave rc 0, 5 of 5 launches ok and 0 bad check lines. The heater check's highest
  board reading was 56.91 W over 33 samples (its line 70 W). 4 smoke device processes, 4 on card 1.
- **No STOP.** No stop file, no live stop, no cap. The gate's cap check before each of the 9 passes read OK; before pass 8, 694.9 s were
  left.
- **The watch**: no other card named or held. It saw 677 device processes of the session; none held a node other than card 1's or card
  0's lock file, and none named another card on its stderr.
- **Card 1's live stops: none fired.** 0 samples at or above 65 W; 0 at or above 70 C; 0 above 80 W.
- **Peaks** (measured): board **60.07 W** at 04:12:40.864 PST; minshire[0] **61.0 C** at 04:42:06.464 PST. The predicted peak was 60.90 W
  (registered); card 1's line is 65 W. The lowest readings were 30.32 W and 53.0 C.
- **600 MHz: 36,150 of 36,150 samples.** Card 1 does not raise its clock (docs/findings/14-card-behaviour.md). minion_mv read 499 mV in
  27,696 samples and 498 mV in 8,454.

## Registered against happened (E199.md sections 2-11; E192.md sections 3-10 by reference)

| item | registered | happened |
|---|---|---|
| card, clock, selection | aifoundry1 card 1, 600 MHz as found, ET_DEVICES=1, card 1's lock | aifoundry1 card 1; 600 MHz in 36,150 of 36,150 samples; "ET_DEVICES=1, LOCK /run/lock/etsoc-shire1.lock" (the wrapper's running line); nothing sent to card 0, no node or lock of it opened |
| the order | `order-e199-aifoundry1.txt` (E192's rule for hostname aifoundry1) | The dry pass: "E199-DRY OK: 328 device calls (327 host, 1 heater), every one under timeout 10 with --stop-file". The order run: SAME in the smoke and in all 9 passes (the lane's read of `run/runs.jsonl` against the file: a desk check, post hoc) |
| the smoke, the passes, the gaps | E192's (3 smoke runs; 36 runs a pass; 30 s gaps with the holder check) | 3 smoke runs (GO); 9 passes of 36 runs; the gate's gap 30 s |
| stops | card 1's 65 W / 70 C beside E192's own | none fired (peaks 60.07 W, 61.0 C) |
| cap, rests | 65 card-minutes; 40 minutes before and after on aifoundry1 | 60.28 card-minutes (3,617 of 3,900 s). Step 9's rest line: "rest: 192 minutes since E191's session end (2026-11-16 00:30:05 PST; dry sessions and blocks that opened no device skipped; every tree of ours on aifoundry1 read)". The end was 04:42:32 PST, so our next session on aifoundry1 starts no earlier than 05:22:32 PST |
| window | G = the booking 03:37:03 PST; last start 05:08, last end 07:08 | first card command 03:42:15 PST (launched 03:42:20 by step 9's clock); session end 04:42:32 PST |
| post | waived by the owner's standing words of Sun 15 Nov 2026 10:22:36 PST | no post |
| sealed card-1 freeze lines | E199.md's freeze line 2: the model session's sealed card-1 forecast (1c5d8fa3..., posted 01:28:51 PST Mon 16 Nov 2026, registered before the land). A later one only by a dated note at tools/claims-v3/sealed-card1/e199-freeze-lines.md committed before this day | Step 2's line: "sealed card-1 freeze lines: E199.md line 2 1c5d8fa3efa054272451017538cd42018b589050493b9e504a5d5d90bc1009c3 (registered); the later note: none (no dated note at tools/claims-v3/sealed-card1/e199-freeze-lines.md)". The round's list held no other E199 line (step S0, 03:36:31 PST) |

## Departures, dated

*Mon 16 Nov 2026, PST. Items 1-11 were set by his go, the round's brief and E199's go lines before the session; item 12 was read at the
collection. All were written here after the collection and before the reduction and the scorer ran.*

1. **The go.** His standing words of Sun 15 Nov 2026:
   - "continue, all machines are up" (10:05:42);
   - "don't worry about discord post, just use the machines, nobody is using them" (10:22:36);
   - "Feel free to use more cards in parallel, I don't need to reserve them ..., feel free to use more in parallel" (17:21:16);
   - "Try again" (received at or before 21:28:59, after the account's usage-limit stop).

   Beside them stands the round's coordination thread, #2.5.1 (19:34:12 PST): the model session's report of his words, "The aifoundry cards
   are all free right now (I can see it on the lab dashboard's live view, though a collector is running on them); feel free to use them."
   His words name no experiment, so E199's registered items stand as its defaults, unchanged.
2. **The card day: Mon 16 Nov 2026**, the day of the booking. It moved from Sunday because the account's weekly usage limit stopped the
   round at about 18:05 PST Sun 15 Nov.
3. **G = the booking: 03:37:03 PST**, when this lane took the round's booking of aifoundry1.
   - The window, by E199.md section 10's form through plan_e199.window: last start 05:08, last end 07:08 (G at 20:29:00 or earlier: yes).
   - Step 1 wrote it at 03:40:29.
4. **The post: waived.** "the owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST". No claim, no release.
5. **The host's package counter: not read.** No E199 or E192 file names it (git grep at HEAD for rapl, powercap or energy_uj, any case:
   0 files).
6. **No network-access approval to name.** The session was orchestrated from aifoundry2, a lab box that reaches aifoundry1 without that
   check. The kit's login-link stop stayed live, and no step met a login link: the round's lock file read 70 lines before and after every
   step.
7. **The desk and the session.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3. The orchestrating session is
   the round's session on its yvb3 Claude account.
8. **The order on aifoundry1 card 1.** The round's plan put E198 before E199. E198's card lane returned SKIPPED at about 02:56 PST without a
   booking: its registered runner arranges a SIGKILL one second after a device process's timeout, which the lab never sends, so a dated
   amendment comes first. E199 therefore ran next after the E191 repeat (its session ended 00:30:05 PST), behind the 40-minute rest (item
   "cap, rests" above).
9. **The sampler.** The audit table for command 74 is E144's (`tools/claims-v3/e144/dmcmd_table_e144.json`), the default, so the per-sensor
   probe ran first and the per-sensor sampler ran. The go did not name `--plain-sampler`.
10. **G9** (one more launch after a launch refused with "no device opened"): not used. There was one launch.
11. **The sealed card-1 forecast** is E199.md's freeze line 2: sha256 1c5d8fa3..., posted as #2.5.1.2.3 at 01:28:51 PST Mon 16 Nov 2026 and
    registered before the land. No later note was needed or made. It stays sealed: no number of it is in this directory or any lab file.
12. **Notes, not departures.**
    - The build job runs `build_e199.sh` under `timeout -k 15 900` (step 6, as kitted). It opens no device (the host runs only with
      `--list`), so the round's standing kill rule (Mon 16 Nov 2026 02:56:14 PST: no SIGKILL to a device process) does not reach it. Every
      device process ran under a plain `timeout 10` with `--stop-file` (the dry pass's line above).
    - Step 10's wait looks for the session by `ours_live 'session_e199.sh'`, and step 9 launches `setsid nohup bash .../session_e199.sh`:
      the same name, read by hand before step 9.

## The day's records

- **The build on aifoundry1** (`build/build/intbits/BUILD-E199.txt`):
  - kernel ELF a987904b6cd322bff51e5913e3fe2af709f24e1d2dabf82c4138b552c0b4d6ea;
  - .text aafdba4b7bce846c7ef18c41f3dbf2c776581179c20f39634bc168c23ca1e42f;
  - host f29c0a5f93bdd7ec3477c6e8738dfd429c426fc6323c1295ecb172ce4cb177a4.

  Set beside E192's builds (reported, never judged): the ELF and the .text are the same as E192's desk build; against E192's card-day build
  on aifoundry3 the ELF differs and the .text is the same. check_elf read "loops 16, bad 0"; loop_order 16 of 16; the arm table was byte for
  byte E192's; ET_DEVICES was in the host, the reader and the heater ("BOXCHECK-E199 OK").
- **The box's manifest** (`box-manifest.txt`): COPY EXACT at step 11 (34 files at the box's sha256, nothing else; the session's own
  MANIFEST.sha256 holds for its 26 files). The mask for our own box login (`<box-login>`) found nothing to mask (0 lines). The scrub
  check read OK, and k6's desk-path gate read CLEAN on the copy and on this directory.
- **Device commands sent** (`dmcmd_audit`: the plain chain GO with the stock table; the per-sensor chain GO with E144's table):
  - `ettelem config`: the start and end reads, and step 7's config read before the session;
  - `pvt_sample.py`: READs only;
  - the hosts and the heater on card 1's ops node.

  No statistics reset, no set of any kind, no firmware query, nothing to card 0. With ET_DEVICES=1 the device layer opened card 1 alone (the
  676 runtime lines above). Its runtime creation's stock abort of pending work on the submission queues (the lab-wide note of Mon 16 Nov
  2026) therefore reached card 1's queues only, on a card held by this session alone.
- **The commits:** the data commit (this directory). A records lane commits step 13's outputs (intbits-e199.json, checks-e199.json,
  scores-e199.json, the unfiltered reduction).

SPDX-License-Identifier: Apache-2.0
