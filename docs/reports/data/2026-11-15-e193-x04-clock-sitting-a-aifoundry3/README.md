# E193 sitting A, 2026-11-15, aifoundry3 card 0 at 600 MHz as found: RAN WHOLE - all 9 registered passes (pass 0 the warm-up) of blocks S, D, W and T in one session of 43.08 card-minutes, reads only, no stop, the smoke gate GO; the registered reducer runs after this commit

*Sun 15 Nov 2026 (week 46), PST, Q182's card lane `card-e193a` (sitting A of the E193 day; the day's booking owner `card-e193`),
orchestrated from aifoundry2. The model session's proposal X04 (request 1113-x04-clock revision 2), registered as E193 in `b17d58a4`
([`E193.md`](../../../../tools/claims-v3/e193/E193.md): its 34 arms and an anchor, the order, the passes, the smoke, the two sittings, the
reduction by sha256, the checks, the stops, the card time) with its two forecasts sealed by sha256 (`d6ac4fb9...` top-down, `f7dc8210...`
from a gate-level simulation; contents sealed), kitted in `45d45c12` ([`KIT.md`](../../../../tools/claims-v3/e193/KIT.md),
[`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e193/CARD-LANE-BRIEF.md)), both on Sat 14 Nov 2026 before any E193 datum, verified
(`verify-e193`: HOLDS WITH FIXES, fixed in place by `fix-e193` before the land) and readiness-checked (`ready-e193`: READY WITH GAPS);
run on the owner's go of Sun 15 Nov 2026, 10:05:42 PST, his words "continue, all machines are up". Sitting A: blocks S, D, W, T.
Nothing was set on the card. **Blind:** both freeze lines were in the registration before the session's first card command (10:25:17
PST), and these are the first E193 runs on any card. **The forecasts stay sealed:** no forecast number is in this directory, and nothing
here scores E193 against them; the model session scores them privately against the reduced prices the lab publishes.*

*Departures, dated Sun 15 Nov 2026 and set before the session (in full under Departures below): the go, by the owner's words at 10:05:42
PST, "continue, all machines are up", answering a message that named E193's registered items, which stand unchanged; one day (form (a) of
the go lines), sitting A's window G+1:30 / G+3:00 from G = 10:05:42, written to the whole minute as 11:36 / 13:06 PST; the day's post route
not named, read by the orchestrator as no post (with his Saturday words "it's fine not to announce, the cards are unused"); the host's
package counter not read; no network-access approval to name from aifoundry2 (the login-link stop stayed live); the desk aifoundry2 under
`/usr/bin/python3` 3.12.3; the orchestrating session the round's session on its yvb3 Claude account.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every plan figure, threshold and rule
is **registered** (E193.md, the kit). The pass spans, peak times, clock counts and the order check below are **desk arithmetic of the
measured records** (`x04/runs.jsonl`, `x04/run.log`, the two `telemetry.jsonl.gz`), not prices and not checks: the prices are the registered
reducer's (`proposal/src/reduce_x04.py`, sha256 `98bbc174...`, unchanged) and E193.md section 8's nine checks are the kit's checker's
(`check_e193.py`), both run only on this directory once it is committed (`rb/s24_reduce_e193.sh A`); their outputs, `x04-e193-A.json` and
`checks-e193-A.json`, are committed by a later lane. The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| the sitting's card-minutes, first card command to "session end" | **43.08** (10:25:17 to 11:08:22 PST, 2,585 s; cap 60) | measured (the session's clock) |
| device processes of the main run, by exit status | **234, every one exit 0** | measured |
| passes run (pass 0 the registered warm-up, set aside by the reduction) | **9 of 9** (passes 0-8, 26 runs each): **8 measured passes** | measured |
| launches, and how many were ok | **2,808 / 2,808** | measured (the host's X04 lines) |
| how the main run ended | **no stop: done**; the session's line "main run end: runner rc 0, every pass (no stop: done)" at 11:08:22 PST; session.rc 0 | measured |
| the smoke (10 device processes, --blocks S,D,W,T,C) and its gate | "SMOKE GO: 10 of 10 device processes exit 0 as registered, 57 launches all ok, the train 12 of 12 (3 a segment); telemetry 1035 samples, every one at 600 MHz, board max 32.06 W, die max 50 C (below every stop)" (10:27:01 PST) | measured |
| telemetry samples of the main run, and those not at 600 MHz | **24,771 / 0** (10:27:01-11:08:21 PST; every sample with the board, the die and the clock) | measured |
| board power, peak; die, peak (minshire[0]) | **32.47 W** (11:02:38 PST; lowest 22.33 W); **51 C** (11:07:54; lowest 49 C) | measured |
| idle-down waits; card waits; short trains; incomplete launches | **0; 0; 0; 0** | measured |
| the start and closing config reads | TDP 0 W, threshold 65 C, power state max_power, minion 600 MHz, 523 mV at the start (10:25:17 PST); **the same at the close** (11:08:22) | measured (READ) |

| block | span (PST, first launch to last) | runs | launches |
|---|---|---|---|
| the smoke (its telemetry 10:25:17-10:27:01) | 10:25:43-10:26:53 | 10 | 57 |
| pass 0 (the warm-up) | 10:27:26-10:31:27 | 26 | 312 |
| pass 1 | 10:32:02-10:36:03 | 26 | 312 |
| pass 2 | 10:36:38-10:40:38 | 26 | 312 |
| pass 3 | 10:41:14-10:45:14 | 26 | 312 |
| pass 4 | 10:45:50-10:49:50 | 26 | 312 |
| pass 5 | 10:50:25-10:54:26 | 26 | 312 |
| pass 6 | 10:55:01-10:59:02 | 26 | 312 |
| pass 7 | 10:59:37-11:03:38 | 26 | 312 |
| pass 8 | 11:04:13-11:08:13 | 26 | 312 |

- **The idle references** (the median die reading of the 20 s of telemetry before each runner call's first run, the idle-down rule's base):
  48 C for the smoke and 49 C for the main run, 200 samples each (`events.jsonl`). No idle-down wait was logged: the runner logs one when a
  run waits more than 0.6 s for the die to read at most the idle reference + 2 C, and none did.
- **The clock: 600 MHz in 24,771 of 24,771 main-run samples and 1,035 of 1,035 smoke samples.**
- **The smoke's peaks:** board 32.06 W (10:26:46 PST; lowest 22.29 W), die 50 C (lowest 48 C).
- **Launches a call** (desk arithmetic of `x04/run.log`): 162 calls of 10 launches, 9 of 20, 9 of 40 and 54 trains of 12 (3 in each of
  their 4 segments); the smoke's 9 calls of 5 launches and its train of 12.

## Registered against happened

| registered (E193.md, KIT.md) | happened |
|---|---|
| aifoundry3 card 0, 600 MHz as found, nothing set (E193.md 3) | card 0, its one ops node `/dev/et0_ops`; 600 MHz in every sample of both runner calls; the config reads at the start and the close of the session (and k6's step 7 read at 10:24:56 PST): TDP 0 W / 65 C / 600 MHz, as the card holds it; nothing set |
| the 40-minute rest before the sitting (E193.md 6) | step 9's line: "rest: 738 minutes since E192's session end (2026-11-14 22:07:08 PST; dry sessions and blocks that opened no device skipped)"; the rest opened 22:47:08 PST Sat, before step 7's config read (10:24:56) and the session's first card command (10:25:17) |
| the smoke with --blocks S,D,W,T,C and the kit's gate (E193.md 5) | the gate's line: SMOKE GO (10:27:01 PST, Results); its 10 calls the registered ones, call for call (`desk/dry-e193-smoke-all.txt`) |
| 9 passes, the seeded order (E193.md 5) | 9 of 9 passes, 26 runs each; the 234 calls as run (block and arm, in `x04/run.log`) equal the 234 of `desk/dry-e193-A.txt`, the runner's own dry listing that E193.md 5 writes out, call for call (a desk check of the measured log with the kit's own readers in `check_e193.py`) |
| the cap: 60 card-minutes; the runner's deadline = first card command + cap - 120 s, never past the window's last end - 180 s | the deadline line: 11:23:17 PST (epoch 1794770597 = the first card command + 3,480 s; the window's last end - 180 s, 13:03:00, is later); it never fired: the main run ended at 11:08:22, 14 min 55 s before it; 43.08 card-minutes against the cap of 60 |
| the stops (E193.md 9) | none fired: board peak 32.47 W (the stop: above 65 W on three samples in a row); die peak 51 C (the stop: 70 C); every sample at 600 MHz; the telemetry file grew throughout; every device process exit 0 (no exit 1, 3, 124 or 137); no card wait; no stop file; the deadline not reached |
| the one sampler a runner call, through E128's guard; no statistics reset | two runner calls, the smoke and the main run, one sampler each: the box's `build/ettelem/ettelem` (sha256 `16037641...`) through E128's guard (`c2c4ab76...`), no `--reset-ms`; the session's preflight `dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)` |
| per-sensor codes not recorded (E193.md 4) | not recorded |
| the post-launch credit barrier on the card's build | UNCONFIRMED (E193.md 14; the kit found no worker firmware source to read: KIT.md section 8) |
| the build on aifoundry3, at most two starts a Pacific day (E193.md 11, 16; KIT.md 2) | one start, 10:24:24-10:24:26 PST on the box: X04-BUILT rc=0 (BODIES CHECK PASS; HOST-BEHAVIOUR OK, three refusals before the device layer; LISTING SAME x3: the smoke's 10, sitting A's 234 and sitting B's 135 device calls); the kernel ELF `5577b131...` differs from the desk build's and from request.md's (reported, never a gate) while its `.text` (`fd720727...`, 68,358 B) is the desk build's; the host `e02b119e...`; cmake 3.28.3, riscv64-unknown-elf-gcc (g1b306039a) 15.1.0, c++ 13.3.0, the box's Python 3.12.3, 0 build warnings |
| the dry pass: the session's own wrapper with DRY=1 (KIT.md, step 8) | "E193-DRY sitting A rc=0 smoke=0 main=0 calls=10+234 manifest=written", both listings SAME (10:25:03 PST) |
| the runner at its registered sha256 | the session's hashes: the runner `26d08862...` (`run_x04.py`, the registration's); the host and kernel those today's build recorded |
| the harness | "HARNESS OK: 38 files at their sha256" on the box, in the session's own log and at step 6 |
| the window | last start 11:36, last end 13:06 PST (Departures 2); launched 10:25:22 PST (T0 10:25:17), ended 11:08:22 |
| one session of ours on aifoundry3 at a time | the round's booking of aifoundry3 held by this lane from 10:15:45 PST; the session's holder check found no process of ours or of another user on the card |
| the host's package counter | not read |
| the post | none: the route not named, read as no post (Departures 3) |

## Departures and notes (dated Sun 15 Nov 2026, PST; each set by his go, the round's brief and the orchestrator before the session, written here after the collection and before the reducer ran)

1. **The go.** The owner's words at **10:05:42 PST Sun 15 Nov 2026**, verbatim: "continue, all machines are up". They answer the
   orchestrator's message that asked for Sunday's go for E191 (aifoundry1 card 1: about 95 card-minutes, cap 110, 600 MHz as found, reads
   only, nothing on card 0) and E193 (aifoundry3: sittings of 42 and 24 card-minutes; both fit one day only on a go by 18:30) and for the
   day's post route. **E193's registered items stand unchanged** (E193.md section 12: aifoundry3 card 0, 600 MHz as found, reads only; the
   two sittings, A then B, about 70 card-minutes, caps 60 and 50; the 40-minute rests; one day or two): his words do not name them one by
   one; they answer a message that named them. **G = 10:05:42 PST**, the window running from his go.
2. **One day, form (a)** of the readiness check's go lines: with G = 10:05:42 both sittings fit today. Sitting A's last start is G+1:30 and
   its last end G+3:00, written to the whole minute, rounded up (the round's log, section 114), as **11:36 and 13:06 PST**:
   `s02_window_e193.sh A 2026-11-15 11:36 13:06`, written by step 1 at 10:23:56. Sitting B's window is 13:36 / 15:06 PST, its first card
   command at least 40 minutes after this sitting's end (11:08:22 PST, so from 11:48:22).
3. **The day's post route was not named.** The orchestrator read his "all machines are up" with his Saturday words "it's fine not to
   announce, the cards are unused" as **no post today**; he can still ask for one. No post was made, so no release line either (step 3,
   and step 11's release: SKIPPED). Every other etiquette check stood: k6's look before the session (et-who, who, uptime, the holder rule:
   FREE at 10:24:11 PST), step 7's reads (et-who clean at 10:24:56), the session's holder check (`et-who --check`) before its first card
   command, the card's lock by every block, `timeout -k 1 10` a device process.
4. **The host's package counter: not read** (no E193 file has a step or option that reads it; his go said nothing of it).
5. **A fresh network-access approval for aifoundry3: nothing to name.** The session was orchestrated from aifoundry2, a lab box that
   reaches aifoundry3 without that check. The kit's login-link stop stayed live (an exit 11 with its lock line ends the day's box steps);
   no step met a login link (the round's lock file held the same lines before and after every step).
6. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3, as KIT.md names. The
   orchestrating session is the round's session on its yvb3 Claude account, which took the round over on Sat 14 Nov 2026 after aifoundry2
   went down abruptly at about 16:53 PST on Fri 13 Nov.
7. **The rest before the sitting.** E193's rest on aifoundry3 opened at 22:47:08 PST Sat 14 Nov (E192's session end, 22:07:08, plus 40
   minutes), and no session of ours ran on aifoundry3 after E192. Step 7's config read, the card lane's first card command of the day, ran
   at 10:24:56 PST, after the rest had opened (E192's data note 1's lesson: step 7 only once the rest has opened), and step 9 read the rest
   on the box at the launch (its line is in the table above).
8. **Beside E191, and the round's one-lab rule.** E191 ran the same morning on aifoundry1 card 1, a different box, under its own booking.
   The round's rule keeps a card lane's desk steps (0, H, 1 and 2) apart from another lane's span from its collection to its data commit's
   push: this lane began after E191's step 2 (10:13:07), took the booking of aifoundry3 at 10:15:45, waited in the rule's helper from
   10:15:48 to 10:23:33 while E191 was in that span, and left its own desk span at 10:24:06, after step 2.
9. **Notes, not departures.** The next session of ours on aifoundry3 rests until **11:48:22 PST** (this sitting's end plus 40 minutes):
   sitting B's first card command comes no earlier. Step 10's wait reads the session by its real script name (`session_e193\.sh`); five
   calls, running at each of the first four, ended at 11:08:32 with the box's manifest written (25 files).

## The day's records

- **The steps' exits** (the card lane's runbook log): step 0 (the anchor read) 41 of 41 as stated at LAB's HEAD `1a4bc1e3` = GitHub main,
  status 0 lines (10:23:45); step H, the round's quiet hold, LAB status 0 lines (10:23:51); step 1 rc 0 (10:23:56); step 2 rc 0, "Already up
  to date", HEAD `1a4bc1e316f7`, both lists at their pinned counts and bytes, the harness re-made, the preflight GO, "E193 data paths in any
  ref: 0" (10:24:00-10:24:01); step 4 FREE (10:24:11); step 5, 39 paths synced (10:24:17); step 6 start and one wait, rc 0 (10:24:23-10:24:30);
  step 7 rc 0 (10:24:56); step 8 start and one wait, rc 0 (10:25:03-10:25:10); step 9 rc 0, launched (10:25:17-10:25:22); step 10, five
  waits, the last rc 0 (11:08:32); step 11 rc 0, COLLECTED (11:08:51-11:08:54).
- **The copy:** one read-only copy back of the session's directory, **COPY-BACK EXACT** against the box's manifest (`session/MANIFEST.sha256`:
  25 files at the box's sha256, nothing else but `session.rc`). Each `telemetry.jsonl.gz` is gzip with no name and mtime 0; its uncompressed
  bytes are the manifest's `telemetry.jsonl`.
- **Privacy:** the collector's scrub (the box's home as `~`, every holder line's user and our own box login as `<login>`: no home-folder path
  and no login left), the desk-path gate as E183 note 5 ported it (CLEAN, both readers) and the history check (HISTORY OK) all passed;
  `facts-e193-a.json` is the collector's summary. `SHA256SUMS` (the collector's) pins every file but this README and itself.
- **The device-command audit** (`dmcmd_audit.py`, no allow-list, no exception): GO, 11 send sites, every one a READ, at step 2 on the desk,
  on the box after the build, and by the session's own preflight (`session/preflight.txt`).
- **The public-text scan** before this commit read every text file here, the text inside both `.gz` and this README, with the lab's
  sanitizer (its fixed list and the local privacy table) plus the private-network, Mac-home, scratch and e-mail patterns, and the round's
  classes over this README and the commit message. This README and the commit message: no hit. Its three hits in the collected files are
  one word, the kit's own name for E193's folder on aifoundry3 (KIT.md section 2), matched by the sanitizer's privilege-word pattern: twice in
  `session/session.log` (the session's line naming the box, its tree and that folder, and its harness line) and once in `session/harness.txt`
  (the same harness line); it names a folder, not an account's rights, and is kept as collected. The round's classes, read over the
  collected text files too, match only the device layer's own lines about the chip's on-die memory addressing in the two config reads'
  `.err` files and in each runner call's `device-stderr.txt` (the hardware's word for that memory, which the class lists because a desk path
  of ours holds the same word; there it names no path), kept as collected.

## Device commands sent

READs only: the session's start and closing `ettelem config` and each runner call's `ettelem sample --every-ms 100`, all through E128's
guard (dmcmd_audit GO, KIT.md section 6); step 7's config read before the session (`ettelem config` through the same guard, k6's
`s09_a3_reads_k6.sh`) was the only other management command the card lane sent. The host opened the ops node only (244 device processes:
the smoke's 10 and the main run's 234, every one exit 0); `et-who --check` sends no device command. No set of any kind (TDP, threshold,
clock, voltage), no reset, no statistics reset, no firmware-revisions query, no PMIC command, no power cycle. Nothing was killed.

## Files

| path | what |
|---|---|
| `session/` | `session.log` (the kits' session log), the two config reads (`config-start.json`, `config-end.json`, each with its guard's `.err`), the holder check's output (`etwho-start.txt`, empty: no holder), `first-card-command.txt`, the binaries' hashes (`hashes.txt`), the harness and preflight outputs (`harness.txt`, `preflight.txt`), the smoke's gate (`smoke-gate.txt`), the runner calls' own outputs (`smoke-runner.out`, `runner.out`, both empty), `MANIFEST.sha256` (the box's), `session.rc` |
| `smoke/`, `x04/` | each runner call's `run.log`, `events.jsonl`, `runs.jsonl`, `device-stdout.txt`, `device-stderr.txt`, `telemetry.jsonl.gz` (gzip, no name, mtime 0; its unpacked bytes are the box's manifest's); no `STOPPED` and no `stderr-*.txt` (no stop, no failed process) |
| `facts-e193-a.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it |

## Re-make it

From the top of the repository, nothing here opens a device; set D to this directory and R to an empty folder outside the repository
(the first line), then run the rest as they stand:

    D=docs/reports/data/2026-11-15-e193-x04-clock-sitting-a-aifoundry3; R=<an empty folder outside the repository>
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/x04" && cp "$D/x04/runs.jsonl" "$R/x04/" && gzip -dc "$D/x04/telemetry.jsonl.gz" > "$R/x04/telemetry.jsonl"
    for p in runs.jsonl telemetry.jsonl; do [ "$(awk -v p="x04/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")" = "$(shasum -a 256 "$R/x04/$p" | cut -d' ' -f1)" ] && echo "x04/$p: the box's bytes" || echo "x04/$p: not the box's bytes"; done
    /usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py "$R/x04" --out "$R/x04.json"
    /usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks "$R/x04.json" "$R/x04" --out "$R/checks.json"

They check every entry of `SHA256SUMS`; unpack the main run's telemetry and set it and `x04/runs.jsonl` against the box's own manifest
(`session/MANIFEST.sha256`: both lines must say "the box's bytes"); run the registered reducer (`proposal/src/reduce_x04.py`, sha256
98bbc174..., unchanged, no `--pvt`, no `--keep-warmup`); and read E193.md 8's nine checks with the kit's checker. Step 13
(`rb/s24_reduce_e193.sh A`) does the same from the card lane's runbook directory for this sitting.

## Next

The registered reducer and E193.md section 8's checker, after this commit only: `rb/s24_reduce_e193.sh A` checks the committed directory
(in HEAD, clean, `SHA256SUMS` every entry OK, the history check), sets `x04/runs.jsonl` and the unpacked telemetry against the box's
manifest, runs `reduce_x04.py` (unchanged) and `check_e193.py checks`, and writes `x04-e193-A.json` and `checks-e193-A.json`; a later lane
commits them beside this directory, with this README's reduced prices in a dated note. No score: the model session scores its sealed
forecasts privately against those published prices. Sitting B (block C) follows on its own rest, in its own data directory.

## Labels

Measured: every number above, from this sitting's own files. Registered: the arms, the protocol, the caps, the stops, the reduction
(E193.md). Desk checks of code: the kit's tests (KIT.md). Desk arithmetic of the measured records: the pass spans, peak times, clock counts,
launches a call and the order check. Not blind to: E193.md 13's list. Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2 (the desk);
Python 3.12.3 on aifoundry3 (the box).

SPDX-License-Identifier: Apache-2.0
