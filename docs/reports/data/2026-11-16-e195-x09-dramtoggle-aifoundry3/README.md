# E195, 2026-11-16, aifoundry3 card 0 at 600 MHz as found: RAN SHORT by the registered 38-minute rule - the smoke and 7 of 8 passes (910-916) in 38.22 card-minutes, reads only, no stop

*Mon 16 Nov 2026 (week 47), PST, Q191's card lane `card-e195`, orchestrated from aifoundry2. The model session's proposal X09 (posted
Sun 15 Nov 2026 10:11:09 PST: 31 arms pricing a 64-byte memory line's parts, read and written). Registered in `bd39ab4a`
([`E195.md`](../../../../tools/claims-v3/e195/E195.md)), kitted in `391b459b` ([`KIT.md`](../../../../tools/claims-v3/e195/KIT.md),
[`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e195/CARD-LANE-BRIEF.md)), verified, fixed and readiness-checked (READY WITH GAPS), all
before any E195 datum; no E195 file changed since the kit (step 0: 43 of 43 anchor lines as stated at HEAD `72514ce5`; step 2: HISTORY OK).
**The freeze line:** the model session's sealed forecast is known to the lab only by its sha256,
`b950de393cf6f8052c73a4c4185dc8b703b40152088ae0806a1715246578168a` (E195.md section 0). **No forecast number and no score are in this
directory:** the model session scores its sealed forecast privately, after this commit, against the prices the reduction's dated note
publishes. The session, T0 1794820366 = 01:12:46 PST, ran to its `session end` at 01:51:00 PST: **38.22 card-minutes** from its first card
command (the holder check, 01:12:47), against the registered estimate of about 43 and the cap of 45. Nothing was set on the card.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every arm, value, order, window,
threshold, stop, rule and the cap is **registered** (E195.md; the kit). The per-pass sample counts, the clock count, the peaks' cross-check
and the order check below are **desk arithmetic of the measured records** (each pass's `telemetry.jsonl.gz` and `runs.jsonl`, read at the
desk), not prices and not rules. The reducer's prices are **not here**: step 13 (`rb/s24_reduce_e195.sh`, the registered `reduce_x09.py`)
runs on this directory only after it is committed, and its outputs are committed by a later lane in a dated note. The desk steps ran under
`/usr/bin/python3` 3.12.3 on aifoundry2.

## Departures and notes (dated Mon 16 Nov 2026, PST; 1-10 set by his go, the kit and the round's plan before the session; 11-13 after the collection, said so; all written here after the collection)

1. **The go, his words, verbatim, Sun 15 Nov 2026 (PST).** Standing: **10:05:42** "continue, all machines are up"; **10:22:36** "don't
   worry about discord post, just use the machines, nobody is using them" (E195.md 13 reads them as the go for an idle card's registered run
   once kitted, verified and readiness-checked); **17:21:16** "Feel free to use more cards in parallel, I don't need to reserve them (things
   are automatically updated on [the lab dashboard's page]), currently I see only 1 card is being used, feel free to use more in parallel";
   **"Try again"** (received at or before 21:28:59; its exact second not known); and "don't worry about hitting the limit, I will use a
   reset, feel free to run things overnight and in parallel" (received at or before 21:51:09). Beside them, a report of his words (not his
   own text), the round's Discussion at 19:34:12: "The aifoundry cards are all free right now (I can see it on the lab dashboard's live
   view, though a collector is running on them); feel free to use them." **His words name no experiment: the registered items are taken as
   their defaults** (E195.md 13): aifoundry3 card 0, 600 MHz as found, reads only, nothing set; about 43 card-minutes, cap 45; the
   40-minute rests; the window of E195.md 6; the full variant (passes 910-917).
2. **The card day: Mon 16 Nov 2026**, moved from Sunday by the round's weekly-usage-limit stop at about 18:05 PST Sun 15 Nov (E195 had
   not been booked and had sent nothing to any card then).
3. **G = the booking:** the card lane's `book.sh take aifoundry3 card-e195` printed BOOKED at **00:58:48 PST** Mon 16 Nov: last start
   G+1:30 and last end G+3:00 (E195.md 6), each rounded up to the whole minute: **02:29 and 03:59 PST** (`s02_window_e195.sh 2026-11-16
   02:29 03:59`, written by step 1 at 01:06:22; the window file's `RB_GO_EPOCH`, 1794819982 = 01:06:22 PST, is the moment step 1 wrote it,
   not his go). The round's generic outer bound (G+3:30, 04:29) was not used: the registered, narrower last end binds.
4. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim (step 3) and no release. Every other
   etiquette check stood: k6's look before the session (et-who, who, uptime, the holder rule: FREE at 01:08:29), step 7's reads (et-who
   clean at 01:09:08), the session's holder check before its first card command (`et-who --check` exit 0) and its closing `et-who` at
   01:50:58 ("No process holds an ET-SoC-1 device node or card lock."), and the runner's plain `timeout 10` a device process.
5. **The host's package counter: not read** (his words do not name it): no E195 file has a step or option that reads it.
6. **A fresh network-access approval: nothing to name.** The session was orchestrated from aifoundry2, a lab box that reaches aifoundry3
   by the kit's ssh without a login link. The kit's login-link stop stayed live; no step met a login link (the round's lock file of checks
   held 70 lines before and after every step).
7. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3; the box's interpreter was
   Python 3.12.3 (facts' `interpreter_on_the_box`). The orchestrating session is the round's session on its yvb3 Claude account, which took
   the round over on Sat 14 Nov 2026 after aifoundry2 went down abruptly at about 16:53 PST on Fri 13 Nov.
8. **The memory shires' counters: not read** (KIT.md section 4, the registered fallback, E195.md 4 and 12): every `x9_` item ran
   `--no-ms` (the manifest `gen-e195-noms/`); C6 reads NO DATA, and **every write price is labelled as assuming that a full-line store
   reaches memory once, unread** (E195.md 4, request.md section 7).
9. **The kit's port** (KIT.md section 1, before any datum): the runner `runitems_e195.py` reads each host record whole, so no runtime line
   can split it (runtime lines dropped: 0 runs, facts' `runtime_lines_dropped_runs`); the blocks' signal path and the sampler's stop
   (`lib_e195.sh`) send no SIGKILL to any process: no sampler was stuck (facts' `sampler_stuck`: none) and no stop file was written (facts'
   `stop_files`: none).
10. **THE QUIET DESK FLAG and the order of the day's lanes.** The E194 session on aifoundry2's own card raised the round's quiet-desk flag at
    00:13:37 and lowered it after its collection; this lane booked aifoundry3 only once that flag was down and no other lane of ours was in
    its collection span (00:58:44), so that its desk span (steps 0-2, 00:58:57-01:08:24) never held another lane's collection. The steps
    themselves were run as the go lines name them; step 2 (the desk check, the kit's runner in its dry mode) ran inside the round's CPU
    slot and its no-device sandbox, with the flag absent.
11. **The 38-minute rule ended the queue before p917 (a note after the collection; a registered fallback, E195.md 5 and 12).** Pass 916
    ended at 01:50:42; at 01:50:57 the session read "38 min into the session: no pass starts after 38 (before p917); passes complete: 7 of
    8 (910 the warm-up)". The passes ran 285-303 s each (the smoke about 2 minutes); E195.md 11's estimate (8 passes at about 5.09 min plus 2 min)
    put the eighth start at about the 37.6th minute, and it came at about the 38.2nd. **Six headline passes (911-916) ended ok**, at
    least the five below which every scored verdict is UNRESOLVED (E195.md 5); p917 is not replaced (E195.md 5). No live stop, no gate stop,
    no failed pass, no stuck sampler.
12. **The card time** came in under the estimate because p917 did not start: 38.22 card-minutes against about 43 and the cap 45. Step 7's
    config read (01:09:08, a card command for the rests) is reported apart: 41.87 minutes from it to the session end (desk arithmetic).
13. **The box build's kernel ELF differs from the registration's desk build by its file hash; its `.text` and its disassembly are the
    same** (`build/x09mem-built.txt`: "same_as_registration_desk_build elf no text yes disassembly yes (reported, never judged)").
    `check_elf` read "CHECK OK: five timed loops as designed".

## 1. Results first (measured; the card's own records)

- **Passes complete: 7 of 8** (910 the registered warm-up; 911-916 the headline); every pass's `block.json` reads ok, the smoke 901
  included; the main passes for the reducer (facts' `main_passes_for_the_reducer`): p910-p916.
- **Card-minutes: 38.22** from the session's first card command (its holder check, 01:12:47 PST; `session/first-card-command.txt` 1794820367)
  to its `session end` (01:51:00 PST), against the cap 45 (KIT.md section 4's dated reading). **Step 7's config read**, reported apart:
  01:09:08 PST (the round's runbook log), 41.87 minutes before the session end.
- **How the queue ended:** "38 min into the session: no pass starts after 38 (before p917); passes complete: 7 of 8 (910 the warm-up)"
  (the session log's `queue end:` line). No stop.
- **The smoke gates:** "smoke gate PASS: 60 runs, 1182 telemetry samples; the memory shires' counters not asked (--no-ms):
  x9_rd_rnd,x9_wr_u4,x9_wrh_nst,x9_wrh_rnd" (the registered `smoke_gate_x09.py`), and "SMOKE-PEAK PASS: highest board 53.32 W, highest
  die 61 C over 1182 samples (the heater bursts included); the kit's gate: below 65 W and below 65 C (E195.md 5)".
- **Peaks per pass** (facts' `peaks`: `board_w` and `temp_c.minshire[0]`; against the live stops 70 W and 70 °C), each matched by a desk
  read of the pass's telemetry:

| pass | role | ended (PST) | its time | samples | 600 MHz samples | peak board | peak die |
|---|---|---|---|---|---|---|---|
| p901 | the smoke (never reduced) | 01:14:50 | about 2 min | 1,182 | 1,182 | 53.32 W | 61 °C |
| p910 | the warm-up | 01:19:44 | 294 s | 2,898 | 2,898 | 53.46 W | 61 °C |
| p911 | headline | 01:24:52 | 293 s | 2,895 | 2,895 | 53.60 W | 61 °C |
| p912 | headline | 01:30:04 | 297 s | 2,943 | 2,943 | 53.47 W | 61 °C |
| p913 | headline | 01:35:22 | 303 s | 2,994 | 2,994 | 53.54 W | 61 °C |
| p914 | headline | 01:40:22 | 285 s | 2,809 | 2,809 | 53.42 W | 61 °C |
| p915 | headline | 01:45:33 | 296 s | 2,928 | 2,928 | 53.55 W | 61 °C |
| p916 | headline | 01:50:42 | 294 s | 2,908 | 2,908 | 53.48 W | 61 °C |
| p917 | headline | not started (the 38-minute rule) | - | - | - | - | - |

  The highest board reading of the session, 53.60 W (p911), sits 16.40 W under the 70 W stop and matches E132's heater bursts on this card
  (53.60 W, E195.md 10); the die never read above 61 °C, 9 °C under the 70 °C stop. **The clock: 21,557 of 21,557 telemetry samples read
  the minion clock at 600 MHz** (`mhz.minion`; desk arithmetic).
- **The config reads:** start "TDP 0 W, 65 C, minion 600 MHz as found" (`session/config-session-start.json`: TDP 0 W, threshold 65 °C,
  600 MHz, 523 mV); closing, at 01:50:58, "TDP 0 W, 65 C, minion 600 MHz, as at the start" (`session/config-session-end.json`, the same
  values; the closing `et-who`: "No process holds an ET-SoC-1 device node or card lock."). Step 7's read, the same values.
- **Runtime lines dropped by the kit's reader: 0 runs** (facts' `runtime_lines_dropped_runs`, 0 expected on aifoundry3).
- **The prices:** after step 13 only, in its own dated note (the registered reducer's prices, ratios, rules and checks, and what the
  reducer leaves). None is here.

## 2. Registered against happened

| registered (E195.md) | happened |
|---|---|
| 3: aifoundry3 card 0, 600 MHz as found (pinned by its zero TDP), nothing set | aifoundry3 card 0; TDP 0 W / 65 °C / 600 MHz / 523 mV at step 7, at the session's start and at its close; 21,557 of 21,557 samples at 600 MHz; nothing set |
| 2: 31 `x9_` arms, the host's table and counts from its bytes | the box build's generator: "CHECK OK: 31 arms from this host's bytes (numpy 1.26.4); manifest.json and counts.json byte-equal to gen-e195-noms/"; the arm table byte-equal to `desk/arm-table-e195.json` and `.txt` |
| 4 / KIT.md 4: every `x9_` item `--no-ms` (the registered fallback) | every item ran `--no-ms` (the smoke gate's line: "the memory shires' counters not asked"); C6 NO DATA |
| 5: the order, `random.Random("aifoundry3|<pass>|<pass>")` over the 31 items, the anchor first and last, two burn-ins | the dry pass "E195-DRY OK: 288 device calls" (01:09:15-01:12:34); each pass's `runs.jsonl` against `desk/order-e195-aifoundry3.txt`: **SAME in every pass** (33 positions a pass, 6 in the smoke; 0 runs with attempt above 1; desk arithmetic) |
| 5: the smoke 901, its gate and the kit's 65 W / 65 °C peak gate | both PASS (section 1) |
| 5: passes 910-917, 15 s apart; 910 the warm-up; no pass after the 38th minute or past `X9_DEADLINE` | 910-916 ran and ended ok; p917 not started by the 38-minute rule (Departures 11) |
| 6: the window, last start G+1:30, last end G+3:00 | G 00:58:48; last start 02:29; last end 03:59; launched 01:12:51 (T0 01:12:46); `X9_DEADLINE` 01:57:46 (the earlier of the last end and the launch + 45 minutes); the session end 01:51:00, inside |
| 6: the rest before, 40 minutes after our previous session on aifoundry3 card 0, before E195's first card command of any kind | the previous: E188, its session end 16:40:25 PST Sun 15 Nov; step 7 read "rest: 508 minutes since E188's session end (2026-11-15 16:40:25 PST; dry sessions and blocks that opened no device skipped)" before its config read (01:09:07); step 9 read "rest: 512 minutes ..." |
| 6: the rest after | the next session of ours on aifoundry3 card 0 no earlier than 02:31:00 PST Mon 16 Nov (40 minutes after 01:51:00) |
| 6 / 11: the cap, 45 card-minutes from the first card command | 38.22; step 7's read reported apart (section 1) |
| 10: live stops: 70 W on three samples in a row (`watch_x09.py`), 70 °C, a stale sampler, a holder, a failed pass | none tripped; the watcher ran from 01:12:49 to the session's end; peaks 53.60 W / 61 °C |
| 10: reads only; `dmcmd_audit` GO | the session's preflight: "dmcmd_audit: GO (44 send site(s), 0 disallowed; allow-list: none)"; see Device commands sent |
| 10: no SIGKILL, no signal to a device process | none sent; plain `timeout 10` the runner's own backstop; no stuck sampler |
| 12: the fallbacks | one acted: the 38-minute rule (the queue ended; the passes that ended ok are reduced as they stand, 910 still the warm-up) |
| 13: the post | waived (Departures 4) |
| the closing config read only while `et-who --check` reads the card free | read at 01:50:58 (the same values as at the start) |

## 4. The day's records

- **The box build** (step 6, 01:08:42-01:08:49 PST on aifoundry3, the first of the day's two allowed starts; `build/x09mem-built.txt`):
  host `a240b7f068d2b200...`, kernel ELF `4fa4f66639e1284b...`, its `.text` `007a355d2da5b420...`, its disassembly `b59a6caf9abec79b...`;
  beside the registration's desk build (E195.md section 17 item 5: ELF `7c5faea8...`, `.text` `007a355d...`, disassembly `b59a6caf...`):
  **ELF DIFFERENT, `.text` SAME, disassembly SAME** (reported, never judged). `check_elf`: "CHECK OK: five timed loops as designed"; the
  arm table byte-equal; the generator's check as in section 2. The box's sampler and heater at their recorded hashes (`16037641ab75bdbe`,
  `20e760c20e9b99c7`); the box check "BOXCHECK-E195 OK".
- **The copy-back:** the box's `MANIFEST.sha256` (98 files) and step 11's COPY EXACT; the collection's own `SHA256SUMS` (111 entries: every
  file but itself; this README is not in it).
- **Our login masked** (facts' `login_masked`: 310 lines in the files it names); the scrub "SCRUB-CHECK OK: no holder line, process entry or
  /home path names another account"; the tree scrub "OK (104 files in 13 directories read, 0 left)"; the desk-path gates CLEAN.
- **`dmcmd_audit`:** GO (44 send sites, 0 disallowed), at step 2 and at the session's preflight.
- **The interpreters:** on the box Python 3.12.3; at the desk `/usr/bin/python3` 3.12.3.
- **The commits:** the registration `bd39ab4a` and the kit `391b459b`, both ancestors of this data commit (steps 0 and 2 read them at
  HEAD `72514ce5`). The data commit's own sha is in the repository's history.

## Device commands sent

Reads only, by the kit's runbook and session (E195.md 10; KIT.md section 7): step 7's single config read through the lab's guard
(`ettelem config`) and `et-who` (01:09:07-01:09:08); the dry pass on the kit's doubles (no device); the session's holder check (`et-who
--check`), its start and closing config reads through the guard, the sampler (`ettelem sample`, no `--reset-ms`), the heater
(`sparsity_host`) between runs, and the host `x09mem_host`, which opens the ops node only (the runtime's launches, copies and allocations). No statistics reset, no set of
any kind, no reset, no power cycle, no firmware query, no PMIC command.

## Privacy and the public-text scan

Our box login is masked in every collected file (`<box-login>`); no other account's name, holder line or process entry is in this
directory (step 11's scrub; the scrub's check again before the commit: "OK (105 files in 13 directories read, 0 left)"). Before the commit
the round's public-text scans read this directory, this README and the commit message. The path scan's 321 hits in the collected files are
all the kit's masked box path: the same 310 lines facts' `login_masked` names, and 11 config keys that name that masked path; no file holds
a login (0 files), a credential, an access path or a desk path. The tier scan's matches: this README's line quoting his words about the
post, and four collected files (the arm table's two copies and the two config reads' error streams) that name the card's own on-chip
memory of the word the scan's path class lists, not a path. No number from any private source; no forecast number (the forecast is
sealed: only its sha256 is here).

## 5. Files

| path | what |
|---|---|
| `session/` | the session's own records: `session.log`, `passes.log`, `smoke.log`, `smoke-gate.txt`, `smoke-peak.txt`, `watch.log`, `first-card-command.txt`, `config-session-start.json`, `config-session-end.json`, the et-who reads, `harness.txt`, `hashes.txt`, `preflight.txt`, `session.rc`, `session-end.time`, `MANIFEST.sha256` |
| `passes/p901/` | the smoke (never reduced) |
| `passes/p910/` - `passes/p916/` | the passes (910 the warm-up): each `block.json`, `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `run.log`, `manifest.txt`, `configs.json`, `gen.sha256`, `code.sha256`, `text.sha256` |
| `build/` | `x09mem-built.txt` (the hashes and checks), `x09mem/` (the build's records), `build-logs/`, `build-attempts.txt` |
| `launch.out` | step 9's launch output |
| `box-manifest.txt` | the box's manifest of the copied files |
| `facts-e195.json` | step 11's facts (passes, peaks, gates, config reads, card-minutes, masking) |
| `SHA256SUMS` | every collected file's sha256 (not this README) |

## 6. Re-make it

From the repository's top, after the commit:

```
D=docs/reports/data/2026-11-16-e195-x09-dramtoggle-aifoundry3
(cd $D && sha256sum -c SHA256SUMS)                                       # every entry OK
/usr/bin/python3 -I -B tools/claims-v3/e195/proposal/src/reduce_x09.py $D/passes/p91[0-6] \
    --gen tools/claims-v3/e195/gen-e195-noms --out /tmp/x09.json --warmup 910   # the passes whose block.json reads ok; never --forecast
/usr/bin/python3 -I -B tools/claims-v3/e195/check_e195.py leftover tools/claims-v3/e195/proposal/src/reduce_x09.py \
    tools/claims-v3/e195/gen-e195-noms $D/passes/p91[0-6] --warmup 910
```

Step 13 (`rb/s24_reduce_e195.sh`) does the same after checking each pass's records against the session's `MANIFEST.sha256` and its
`gen.sha256` against `gen-e195-noms/`.

## Next

The reduction (step 13) on this directory once it is committed; its outputs in a dated note by a later lane. The model session scores its
sealed forecast privately. On aifoundry3, the next session of ours (E196) no earlier than 02:31:00 PST Mon 16 Nov.

SPDX-License-Identifier: Apache-2.0
