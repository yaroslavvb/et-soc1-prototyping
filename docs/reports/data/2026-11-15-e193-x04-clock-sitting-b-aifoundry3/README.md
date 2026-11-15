# E193 sitting B, 2026-11-15, aifoundry3 card 0 at 600 MHz as found: RAN WHOLE - all 9 registered passes (pass 0 the warm-up) of block C in one session of 27.83 card-minutes, reads only, no stop, the smoke gate GO; the registered reducer runs after this commit

*Sun 15 Nov 2026 (week 46), PST, Q182's card lane `card-e193b` (sitting B of the E193 day; the day's booking owner `card-e193`),
orchestrated from aifoundry2. The model session's proposal X04 (request 1113-x04-clock revision 2), registered as E193 in `b17d58a4`
([`E193.md`](../../../../tools/claims-v3/e193/E193.md): its 34 arms and an anchor, the order, the passes, the smoke, the two sittings, the
reduction by sha256, the checks, the stops, the card time) with its two forecasts sealed by sha256 (`d6ac4fb9...` top-down, `f7dc8210...`
from a gate-level simulation; contents sealed), kitted in `45d45c12` ([`KIT.md`](../../../../tools/claims-v3/e193/KIT.md),
[`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e193/CARD-LANE-BRIEF.md)), both on Sat 14 Nov 2026 before any E193 datum, verified
(`verify-e193`: HOLDS WITH FIXES, fixed in place by `fix-e193` before the land) and readiness-checked (`ready-e193`: READY WITH GAPS);
run on the owner's go of Sun 15 Nov 2026, 10:05:42 PST, his words "continue, all machines are up". Sitting B: block C, the same day as
sitting A (blocks S, D, W, T; its data in [`../2026-11-15-e193-x04-clock-sitting-a-aifoundry3/`](../2026-11-15-e193-x04-clock-sitting-a-aifoundry3/README.md),
commit `fe08ed67`). Nothing was set on the card. **Blind:** both freeze lines were in the registration before the first card command of
either sitting (sitting A's, 10:25:17 PST); block C's passes ran in this session only (each sitting's registered smoke runs one call of
block C's `faddps_p1`). **The forecasts stay sealed:** no forecast number is in this directory, and nothing here scores E193 against them;
the model session scores them privately against the reduced prices the lab publishes.*

*Departures, dated Sun 15 Nov 2026 and set before the session (in full under Departures below): the go, by the owner's words at 10:05:42
PST, "continue, all machines are up", answering a message that named E193's registered items, which stand unchanged; one day (form (a) of
the go lines), sitting B's window G+3:30 / G+5:00 from G = 10:05:42, written to the whole minute as 13:36 / 15:06 PST, its first card
command at least 40 minutes after sitting A's end; the day's post: the route not named at 10:05:42, read by the orchestrator as no post
(with his Saturday words "it's fine not to announce, the cards are unused"), then waived by the owner in his own words at 10:22:36 PST; the
host's package counter not read; no network-access approval to name from aifoundry2 (the login-link stop stayed live); the desk aifoundry2
under `/usr/bin/python3` 3.12.3; the orchestrating session the round's session on its yvb3 Claude account.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every plan figure, threshold and rule
is **registered** (E193.md, the kit). The pass spans, peak times, clock counts, the idle-down waits by pass and the order check below are
**desk arithmetic of the measured records** (`x04/runs.jsonl`, `x04/events.jsonl`, `x04/run.log`, the two `telemetry.jsonl.gz`), not prices
and not checks: the prices are the registered reducer's (`proposal/src/reduce_x04.py`, sha256 `98bbc174...`, unchanged) and E193.md section
8's nine checks are the kit's checker's (`check_e193.py`), both run only on this directory once it is committed (`rb/s24_reduce_e193.sh B`);
their outputs, `x04-e193-B.json` and `checks-e193-B.json`, are committed by a later lane. The desk steps ran under `/usr/bin/python3` 3.12.3
on aifoundry2.

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| the sitting's card-minutes, first card command to "session end" | **27.83** (11:48:51 to 12:16:41 PST, 1,670 s; cap 50) | measured (the session's clock) |
| device processes of the main run, by exit status | **135, every one exit 0** | measured |
| passes run (pass 0 the registered warm-up, set aside by the reduction) | **9 of 9** (passes 0-8, 15 runs each): **8 measured passes** | measured |
| launches, and how many were ok | **1,350 / 1,350** | measured (the host's X04 lines) |
| how the main run ended | **no stop: done**; the session's line "main run end: runner rc 0, every pass (no stop: done)" at 12:16:41 PST; session.rc 0 | measured |
| the smoke (10 device processes, --blocks S,D,W,T,C) and its gate | "SMOKE GO: 10 of 10 device processes exit 0 as registered, 57 launches all ok, the train 12 of 12 (3 a segment); telemetry 1035 samples, every one at 600 MHz, board max 32.19 W, die max 50 C (below every stop)" (11:50:35 PST) | measured |
| telemetry samples of the main run, and those not at 600 MHz | **15,638 / 0** (11:50:35-12:16:40 PST; every sample with the board, the die and the clock) | measured |
| board power, peak; die, peak (minshire[0]) | **32.84 W** (12:16:10 PST; lowest 22.60 W); **52 C** (12:16:23; lowest 49 C) | measured |
| idle-down waits; card waits; short trains; incomplete launches | **25** (1.0 to 2.5 s each, 39.0 s in all); **0; 0; 0** | measured |
| the start and closing config reads | TDP 0 W, threshold 65 C, power state max_power, minion 600 MHz, 523 mV at the start (11:48:51 PST); **the same at the close** (12:16:41) | measured (READ) |

| block | span (PST, first launch to last) | runs | launches |
|---|---|---|---|
| the smoke (its telemetry 11:48:51-11:50:34) | 11:49:16-11:50:26 | 10 | 57 |
| pass 0 (the warm-up) | 11:51:00-11:53:14 | 15 | 150 |
| pass 1 | 11:53:49-11:56:04 | 15 | 150 |
| pass 2 | 11:56:39-11:58:56 | 15 | 150 |
| pass 3 | 11:59:31-12:01:50 | 15 | 150 |
| pass 4 | 12:02:25-12:04:48 | 15 | 150 |
| pass 5 | 12:05:23-12:07:44 | 15 | 150 |
| pass 6 | 12:08:19-12:10:41 | 15 | 150 |
| pass 7 | 12:11:16-12:13:39 | 15 | 150 |
| pass 8 | 12:14:14-12:16:32 | 15 | 150 |

- **The idle references** (the median die reading of the 20 s of telemetry before each runner call's first run, the idle-down rule's base):
  49 C for the smoke and 49 C for the main run, 200 samples each (`events.jsonl`).
- **The idle-down waits.** The runner waits, idle, before a run until the die reads at most the idle reference + 2 C (here 51 C), at most
  30 s, and logs the wait when it lasts more than 0.6 s (`run_x04.py`, registered). The main run logged **25**, from 11:57:50 to 12:16:23
  PST, 1.0 to 2.5 s each and 39.0 s in all, each with the die at 51 C when it ended; by the pass of the call that followed them (desk
  arithmetic): pass 2: 2, pass 3: 3, pass 4: 5, pass 5: 4, pass 6: 5, pass 7: 4, pass 8: 2; none in passes 0 and 1 and none in the smoke.
  None came near the 30 s bound, and none is a stop or a drop (sitting A logged none).
- **The clock: 600 MHz in 15,638 of 15,638 main-run samples and 1,035 of 1,035 smoke samples.**
- **The smoke's peaks:** board 32.19 W (11:50:19 PST; lowest 22.47 W), die 50 C (11:50:26; lowest 49 C).
- **Launches a call** (desk arithmetic of `x04/run.log`): 135 calls of 10 launches (block C has no train); the smoke's 9 calls of 5
  launches and its train of 12.

## Registered against happened

| registered (E193.md, KIT.md) | happened |
|---|---|
| aifoundry3 card 0, 600 MHz as found, nothing set (E193.md 3) | card 0, its one ops node `/dev/et0_ops`; 600 MHz in every sample of both runner calls; the config reads at the start and the close of the session (and k6's step 7 read at 11:48:35 PST): TDP 0 W / 65 C / 600 MHz, as the card holds it; nothing set |
| the 40-minute rest between sitting A's end and sitting B's first card command (E193.md 6) | sitting A's session end 11:08:22 PST (its `session/session.log`), so the rest opened at 11:48:22; step 7's config read, this lane's first card command, at 11:48:35 (40 min 13 s after); the session's first card command (the holder check) at 11:48:51 (40 min 29 s after); step 9's line: "rest: 40 minutes since E193's session end (2026-11-15 11:08:22 PST; dry sessions and blocks that opened no device skipped)" |
| B never before A (E193.md 6) | step 9's line: "sitting A held first: build/e193/T1794767117" (sitting A's session on the box, its main run started and ended) |
| the smoke with --blocks S,D,W,T,C and the kit's gate (E193.md 5) | the gate's line: SMOKE GO (11:50:35 PST, Results); its 10 calls the registered ones, call for call (`desk/dry-e193-smoke-all.txt`) |
| 9 passes, the seeded order (E193.md 5) | 9 of 9 passes, 15 runs each; the 135 calls as run (block and arm, in `x04/run.log`) equal the 135 of `desk/dry-e193-B.txt`, the runner's own dry listing that E193.md 5 writes out, call for call (a desk check of the measured log with the kit's own readers in `check_e193.py`) |
| the cap: 50 card-minutes; the runner's deadline = first card command + cap - 120 s, never past the window's last end - 180 s | the deadline line: 12:36:51 PST (epoch 1794775011 = the first card command + 2,880 s; the window's last end - 180 s, 15:03:00, is later); it never fired: the main run ended at 12:16:41, 20 min 10 s before it; 27.83 card-minutes against the cap of 50 |
| the stops (E193.md 9) | none fired: board peak 32.84 W (the stop: above 65 W on three samples in a row); die peak 52 C (the stop: 70 C); every sample at 600 MHz; the telemetry file grew throughout; every device process exit 0 (no exit 1, 3, 124 or 137); no card wait; no stop file; the deadline not reached |
| the one sampler a runner call, through E128's guard; no statistics reset | two runner calls, the smoke and the main run, one sampler each: the box's `build/ettelem/ettelem` (sha256 `16037641...`) through E128's guard (`c2c4ab76...`), no `--reset-ms`; the session's preflight `dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)` |
| per-sensor codes not recorded (E193.md 4) | not recorded |
| the post-launch credit barrier on the card's build | UNCONFIRMED (E193.md 14; the kit found no worker firmware source to read: KIT.md section 8) |
| the build on aifoundry3, at most two starts a Pacific day; both sittings of one day share its build (E193.md 11, 16; KIT.md 2) | no start for sitting B: step 6's wait read the day's one build (started for sitting A, X04-BUILT at 10:24:26 PST: BODIES CHECK PASS; HOST-BEHAVIOUR OK; LISTING SAME x3, sitting B's 135 device calls among them); the kernel ELF `5577b131...` (its `.text` `fd720727...`, the desk build's), the host `e02b119e...`; the session's hashes name the same binaries |
| the dry pass: the session's own wrapper with DRY=1 (KIT.md, step 8) | "E193-DRY sitting B rc=0 smoke=0 main=0 calls=10+135 manifest=written", both listings SAME (11:48:40-11:48:46 PST) |
| the runner at its registered sha256 | the session's hashes: the runner `26d08862...` (`run_x04.py`, the registration's); the host and kernel those today's build recorded |
| the harness | "HARNESS OK: 38 files at their sha256" on the box, in the session's own log and at step 6 |
| the window | last start 13:36, last end 15:06 PST (Departures 2); launched 11:48:56 PST (T0 11:48:51), ended 12:16:41 |
| one session of ours on aifoundry3 at a time | the round's booking of aifoundry3, held for the day by the owner name `card-e193` from 10:15:45 PST (sitting A's lane) and kept for this sitting; the session's holder check found no process of ours or of another user on the card |
| the host's package counter | not read |
| the post | none: the route not named, read as no post, and waived by the owner at 10:22:36 PST (Departures 3) |

## Departures and notes (dated Sun 15 Nov 2026, PST; each set by his go, the round's brief and the orchestrator before the session, written here after the collection and before the reducer ran)

1. **The go.** The owner's words at **10:05:42 PST Sun 15 Nov 2026**, verbatim: "continue, all machines are up". They answer the
   orchestrator's message that asked for Sunday's go for E191 (aifoundry1 card 1: about 95 card-minutes, cap 110, 600 MHz as found, reads
   only, nothing on card 0) and E193 (aifoundry3: sittings of 42 and 24 card-minutes; both fit one day only on a go by 18:30) and for the
   day's post route. **E193's registered items stand unchanged** (E193.md section 12: aifoundry3 card 0, 600 MHz as found, reads only; the
   two sittings, A then B, about 70 card-minutes, caps 60 and 50; the 40-minute rests; one day or two): his words do not name them one by
   one; they answer a message that named them. **G = 10:05:42 PST**, the window running from his go.
2. **One day, form (a)** of the readiness check's go lines: with G = 10:05:42 both sittings fit today. Sitting B's last start is G+3:30 and
   its last end G+5:00, written to the whole minute, rounded up (the round's log, section 114), as **13:36 and 15:06 PST**:
   `s02_window_e193.sh B 2026-11-15 13:36 15:06`, written by step 1 at 11:22:13 in sitting B's own runbook directory (one per sitting).
   Sitting A ran first the same day, 10:25:17-11:08:22 PST, in its own window (11:36 / 13:06).
3. **The day's post.** At 10:05:42 the post route was not named: the orchestrator read his "all machines are up" with his Saturday words
   "it's fine not to announce, the cards are unused" as **no post today**. At **10:22:36 PST** the owner then waived it in his own words,
   verbatim: "don't worry about discord post, just use the machines, nobody is using them" (a standing waiver, for today and later days
   until he says otherwise). No post was made today, so none covered sitting B and there was no release line (step 3, and step 11's
   release: SKIPPED). Every other etiquette check stood: k6's look before the session (et-who, who, uptime, the holder rule: FREE at
   11:22:29 PST), step 7's reads (et-who clean at 11:48:35), the session's holder check (`et-who --check`) before its first card command,
   the card's lock by every block, `timeout -k 1 10` a device process.
4. **The host's package counter: not read** (no E193 file has a step or option that reads it; his go said nothing of it).
5. **A fresh network-access approval for aifoundry3: nothing to name.** The session was orchestrated from aifoundry2, a lab box that
   reaches aifoundry3 without that check. The kit's login-link stop stayed live (an exit 11 with its lock line ends the day's box steps);
   no step met a login link (the round's lock file held the same lines before and after every step).
6. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3, as KIT.md names. The
   orchestrating session is the round's session on its yvb3 Claude account, which took the round over on Sat 14 Nov 2026 after aifoundry2
   went down abruptly at about 16:53 PST on Fri 13 Nov.
7. **The rest between the sittings.** Sitting A's session ended at 11:08:22 PST, so sitting B's rest opened at 11:48:22. This lane ran its
   steps 0 to 6 first (11:22:00-11:23:08: they send no card command: the anchor read, the window, the desk check, the look, the sync and
   the build's wait), then waited, and ran step 7's config read, its first card command, at 11:48:35, only after the rest had opened (E192's
   data note 1's lesson), then steps 8 and 9 without delay; step 9 read the rest on the box at the launch (its line is in the table above).
8. **The day's booking, the quiet hold and the round's one-lab rule.** One booking of aifoundry3 for the day, under the owner name
   `card-e193`: taken by sitting A's lane at 10:15:45 PST and kept for this sitting, so no other lane of ours could book the card between
   the sittings; this lane releases it after this sitting's data commit (the go lines' step E). The round's quiet hold named `card-e193`
   from 11:22:09 PST (step H, LAB's status 0 lines) to this sitting's data commit. The one-lab rule kept this lane's desk steps (0, H, 1 and 2: 11:21:56-11:22:24 PST) and
   its span from the collection to the data commit's push (from 12:17:07) apart from any other lane's; it waited for neither.
9. **Notes, not departures.** The next session of ours on aifoundry3 rests until **12:56:41 PST** (this sitting's end plus 40 minutes).
   Step 10's four waits read "running" at each of the first three and ended at 12:16:52 with the box's manifest written (25 files).

## The day's records

- **The steps' exits** (the card lane's runbook log): step 0 (the anchor read, sitting B's form) 39 of 39 as stated at LAB's HEAD `fe08ed67`
  = GitHub main, status 0 lines, its B2 line sitting A's data directory at HEAD (11:22:00); step H, the round's quiet hold, LAB status 0
  lines (11:22:09); step 1 rc 0 (11:22:13); step 2 rc 0, "Already up to date", HEAD `fe08ed6705b3`, both lists at their pinned counts and
  bytes, the harness re-made, the preflight GO, "E193 data paths in any ref: 30 (sitting A's: 30)" (11:22:18-11:22:19); step 4 FREE
  (11:22:29); step 5, 39 paths synced, no file's content sent (11:23:02-11:23:03); step 6, the wait alone, rc 0 (11:23:07-11:23:08); step 7
  rc 0 (11:48:35); step 8 start and one wait, rc 0 (11:48:40-11:48:46); step 9 rc 0, launched (11:48:50-11:48:56); step 10, four waits, the
  last rc 0 (12:16:52); step 11 rc 0, COLLECTED (12:17:11-12:17:13).
- **The copy:** one read-only copy back of the session's directory, **COPY-BACK EXACT** against the box's manifest (`session/MANIFEST.sha256`:
  25 files at the box's sha256, nothing else but `session.rc`). Each `telemetry.jsonl.gz` is gzip with no name and mtime 0; its uncompressed
  bytes are the manifest's `telemetry.jsonl`.
- **Privacy:** the collector's scrub (the box's home as `~`, every holder line's user and our own box login as `<login>`: no home-folder path
  and no login left), the desk-path gate as E183 note 5 ported it (CLEAN, both readers) and the history check (HISTORY OK) all passed;
  `facts-e193-b.json` is the collector's summary. `SHA256SUMS` (the collector's) pins every file but this README and itself.
- **The device-command audit** (`dmcmd_audit.py`, no allow-list, no exception): GO, 11 send sites, every one a READ, at step 2 on the desk,
  on the box at step 6's wait, and by the session's own preflight (`session/preflight.txt`).
- **The public-text scan** before this commit read every text file here, the text inside both `.gz` and this README, with the lab's
  sanitizer (its fixed list and the local privacy table) plus the private-network, Mac-home, scratch and e-mail patterns, and the round's
  classes over this README and the commit message (see the card lane's record for its lines). The collected files carry the same words
  sitting A's did: the kit's own name for E193's folder on aifoundry3 (KIT.md section 2), matched by the sanitizer's privilege-word pattern,
  in `session/session.log` and `session/harness.txt`, and the device layer's own lines about the chip's on-die memory addressing in the two
  config reads' `.err` files and each runner call's `device-stderr.txt`; they name a folder and the hardware's memory, not an account or a
  path of ours, and are kept as collected.

## Device commands sent

READs only: the session's start and closing `ettelem config` and each runner call's `ettelem sample --every-ms 100`, all through E128's
guard (dmcmd_audit GO, KIT.md section 6); step 7's config read before the session (`ettelem config` through the same guard, k6's
`s09_a3_reads_k6.sh`) was the only other management command this lane sent. The host opened the ops node only (145 device processes: the
smoke's 10 and the main run's 135, every one exit 0); `et-who --check` sends no device command. No set of any kind (TDP, threshold, clock,
voltage), no reset, no statistics reset, no firmware-revisions query, no PMIC command, no power cycle. Nothing was killed.

## Files

| path | what |
|---|---|
| `session/` | `session.log` (the kits' session log), the two config reads (`config-start.json`, `config-end.json`, each with its guard's `.err`), the holder check's output (`etwho-start.txt`, empty: no holder), `first-card-command.txt`, the binaries' hashes (`hashes.txt`), the harness and preflight outputs (`harness.txt`, `preflight.txt`), the smoke's gate (`smoke-gate.txt`), the runner calls' own outputs (`smoke-runner.out`, `runner.out`, both empty), `MANIFEST.sha256` (the box's), `session.rc` |
| `smoke/`, `x04/` | each runner call's `run.log`, `events.jsonl`, `runs.jsonl`, `device-stdout.txt`, `device-stderr.txt`, `telemetry.jsonl.gz` (gzip, no name, mtime 0; its unpacked bytes are the box's manifest's); no `STOPPED` and no `stderr-*.txt` (no stop, no failed process) |
| `facts-e193-b.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it |

## Re-make it

From the top of the repository, nothing here opens a device; set D to this directory and R to an empty folder outside the repository
(the first line), then run the rest as they stand:

    D=docs/reports/data/2026-11-15-e193-x04-clock-sitting-b-aifoundry3; R=<an empty folder outside the repository>
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/x04" && cp "$D/x04/runs.jsonl" "$R/x04/" && gzip -dc "$D/x04/telemetry.jsonl.gz" > "$R/x04/telemetry.jsonl"
    for p in runs.jsonl telemetry.jsonl; do [ "$(awk -v p="x04/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")" = "$(shasum -a 256 "$R/x04/$p" | cut -d' ' -f1)" ] && echo "x04/$p: the box's bytes" || echo "x04/$p: not the box's bytes"; done
    /usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py "$R/x04" --out "$R/x04.json"
    /usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks "$R/x04.json" "$R/x04" --out "$R/checks.json"

They check every entry of `SHA256SUMS`; unpack the main run's telemetry and set it and `x04/runs.jsonl` against the box's own manifest
(`session/MANIFEST.sha256`: both lines must say "the box's bytes"); run the registered reducer (`proposal/src/reduce_x04.py`, sha256
98bbc174..., unchanged, no `--pvt`, no `--keep-warmup`); and read E193.md 8's nine checks with the kit's checker. Step 13
(`rb/s24_reduce_e193.sh B`) does the same from the card lane's runbook directory for this sitting.

## Next

The registered reducer and E193.md section 8's checker, after this commit only: `rb/s24_reduce_e193.sh B` checks the committed directory
(in HEAD, clean, `SHA256SUMS` every entry OK, the history check), sets `x04/runs.jsonl` and the unpacked telemetry against the box's
manifest, runs `reduce_x04.py` (unchanged) and `check_e193.py checks`, and writes `x04-e193-B.json` and `checks-e193-B.json`; a later lane
commits them beside this directory, with this README's reduced prices in a dated note. No score: the model session scores its sealed
forecasts privately against those published prices. Both sittings of E193 have now run.

## Labels

Measured: every number above, from this sitting's own files. Registered: the arms, the protocol, the caps, the stops, the reduction
(E193.md). Desk checks of code: the kit's tests (KIT.md). Desk arithmetic of the measured records: the pass spans, peak times, clock counts,
the idle-down waits by pass, launches a call and the order check. Not blind to: E193.md 13's list. Interpreter: `/usr/bin/python3` 3.12.3 on
aifoundry2 (the desk); Python 3.12.3 on aifoundry3 (the box).

SPDX-License-Identifier: Apache-2.0
