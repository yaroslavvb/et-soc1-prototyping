# E188's data README, dated note 1 (Sun 15 Nov 2026; after the data verifier): the commit message's scan read the message before its trailer; one closing config read at 522 mV; the closing anchors' recorded quiet is the runner's starting value (measured 23.70-30.52 s); E188-C's coverage under both readings (PASS); the C-logging host's hash named exactly; the window under both readings of G; the closest margins; the firmware-revisions query's line under the owner's ruling; lines for the records

*Written on aifoundry2 from about 17:43 PST on Sun 15 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no
post), by the lane `fix-e188d` of Q186, after this directory's data verifier `verify-e188d` (Sun 15 Nov 2026, 17:14-17:43 PST: holds
with fixes; one low, five nits and a note, none of them a fault in a datum, a scored figure or a verdict; the verifier re-derived the 15
rules and 27 sub-words from the raw files with its own code and read the kit's words). [`README.md`](README.md) and
[`SHA256SUMS`](SHA256SUMS) (lab `f1b903d4`, 17:11:13 PST Sun 15 Nov 2026) stay as committed. **No number, rule, verdict or gate reading
changes, and nothing is scored.** The figures come from [`posthoc_note1_e188.py`](posthoc_note1_e188.py), which reads only committed
files: the files of this directory's data commit (the 350 that `SHA256SUMS` lists, `README.md` and `SHA256SUMS`) and, as text, the lines
this note cites in the runner, the reducer, the kit's scorer, pairing and forecast modules, the check of C, the host patch and E186's kit
note 2. Its output is [`posthoc-note1-e188.txt`](posthoc-note1-e188.txt) and [`posthoc-note1-e188.json`](posthoc-note1-e188.json)
("output §" below is that output's), and a re-run from this tree writes both byte for byte. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins
this note, the script, its two outputs, `README.md` and `SHA256SUMS`, so the line numbers below refer to their committed bytes; with
`SHA256SUMS` (350 entries), every file here at this note's commit is pinned but `SHA256SUMS-note1` itself. Interpreter: `/usr/bin/python3`
3.12.3 on aifoundry2. Labels: **registered** (E188.md with its amendments A1 and A2 and note 1, the kit as committed), **measured** (the
session's committed files), **desk check of code**, **post hoc** (desk readings after the data, deciding nothing).*

## 1. The commit message's scan read the message before its trailer (the verifier's finding 1, low)

Lines 194-198 say the round's public-text scans ran over "this README and the commit message", with "0 hits in the commit message"
(`pubscan_all.py`) and "in the commit message, none" (`tiers_scan.sh`). Both scans read the message as the card lane wrote it, **before
`commit_lab.sh` appended its two standard trailer lines**: the session line (a link to the round's session) and the co-author line (a
no-reply address). Every commit of the round has carried those two lines since Q177.

A desk check by this lane, with the same two scanners read by sha256 first (`pubscan_all.py` `47254ae0...`, `tiers_scan.sh`
`e05b84bd...`). It is not in the script, because the message is not a file of this directory:
- on the committed message (7 lines), `pubscan_all.py` reads **2 hits**, both on the co-author line's no-reply address (its two e-mail
  patterns), and `tiers_scan.sh` reads **1 network line**, the session link;
- on the same message without those two lines (5 lines, the message as written), it reads 0 hits and no class.

So lines 196 and 198 read: **0 hits and no class in the message as the lane wrote it; the committed message adds `commit_lab.sh`'s two
standard trailer lines, which the scans did not read.** The same trailer is on every data commit of the round (`7156ac15`, `96ef447c`,
`fe08ed67`, `1a4bc1e3`, `a6e17e83`), and E191's second-session note 1 (§ 4.1) records it there. For later lanes: scan the final message as
`commit_lab.sh` writes it, or list the two trailer lines as accepted. This note's own commit message was scanned in its final form, the
two trailer lines set apart and named (the last section).

## 2. One closing config read at 522 mV (finding 2, nit)

Output § 2 reads all 24 config reads: each of the 11 blocks' `config_start.json` and `config_end.json`, and the session's two. TDP 0 W,
threshold 65 C, power state max_power and 600 MHz are in all 24. `minion_mv` reads **523 in 23 and 522 in one**: the closing read of
PAIR's block, [`aifoundry3/e188/p18811/config_end.json`](aifoundry3/e188/p18811/config_end.json) (its `block.json` closes at 15:43:27
PST). That is a voltage reading inside a read. Nothing was set.

Line 112's "the same at the close" is about the session's two ends (15:15:14 and 16:40:25, both 523 mV), step 7 and the smoke's two
ends. Line 150's "the same, 523 mV, at both ends" is about the session's ends too. Both stay true. The blocks' own reads add one reading
1 mV lower.

## 3. The closing anchors' recorded quiet is the runner's starting value (finding 3, nit)

**What the records hold.** Each train closes with E78's runner (`run_e78.py`) on fp32.randn, then fp32.zeros: the block's `a1` runs. That
runner is a new invocation. By output § 3 it started 0.037-0.042 s after the train's last process ended (its recorded `prev_end_ms` plus
one hour).

The runner starts its "end of the newest device process" at one hour before its own start
([`run_e78.py`](../../../../tools/claims-v3/kinds/run_e78.py) line 147: `last_end = [time.time() - 3600.0]`, E78 change 4). It moves
that value only after a device process it runs itself. The card read 62-63 C when `a1` began, above the 59 C preheat, so no heater ran
before `a1`'s first run. That run's recorded `quiet_s` (**3,623.66-3,630.48 s**) and `prev_end_ms` (an hour before the runner's start)
are therefore the starting value plus the wait, not a measured gap.

**Measured** from the committed records: from the train's last process end (the block's `marks.jsonl`) to `a1`'s first run's start,
**23.701-30.521 s**; to its first launch, 23.894-30.713 s (the verifier's 23.89-30.71 s). The required quiet is 2 s. The smoke's first
run (anchor_pi, quiet 3,600.01 s) shows the same starting value. It ran under the smoke's own protocol (launch at 200 C after 0 C, 0.2 s
quiet), and no reduction reads it. Those 8 runs are the only run marks with a recorded quiet of 1,000 s or more.

**What it changes: nothing** (desk check of code). The anchors' reduction ([`reduce_e78.py`](../../../../tools/claims-v3/kinds/reduce_e78.py),
unchanged, through `reduce_e188.py`) reads `prev_end_ms` only for `idle_after_prev_ms` (line 177). It reads `quiet_s` only for E78's
quiet gate (line 274). A run's D, and so the session's s, use windows timed from the run's first launch.

Under the measured previous end, both gates still pass in all seven trains:
- quiet: 23.701 s or more, against 1.95 s;
- `idle_after_prev_ms`: 22,694-29,513 ms, against 800 ms (line 297; recorded 3,622,657-3,629,475 ms).

[`runs-anchors.csv`](runs-anchors.csv) holds the recorded figures, with `idle_ok` True and `fail` 0 in all seven. No gate, D or s changes.
For a later kit: pass the train's last process end to the closing runner, or record the measured gap beside the runner's.

## 4. E188-C's coverage, both readings (finding 4, nit)

**Registered.** E188.md 5.3: "every launch of every E188 kind, trains and kinds passes included, has a C record the check of C judged PASS
against its own tiles".

**The kit's scorer reads less.** Its `c_status` ([`score_e188.py`](../../../../tools/claims-v3/e188/score_e188.py) line 128) reads 8,598
launches: the kept kinds passes' item records (870), and the seven train blocks' records (7,448) with their anchors (280). All are PASS.
It does not read the smoke's 106 launches (78 from the kinds items, 28 from the two train processes). Nor does it read the 40 launches of
the kinds passes' four burn-ins (the built-in pi).

**The check of C judged all 8,744** (output § 4): 8,598 + 106 + 40, every one PASS, none outside a named record or a burn-in.

**Both readings and the rule.** As the kit scores it, E188-C reads PASS. Read to include the smoke and the burn-ins, it reads PASS too,
8,744 of 8,744. The rule that decides is E188.md 5.3 as the kit's frozen scorer implements it. Both readings give PASS, so **E188-C reads
PASS** either way and no train reads NOT SCORED. Line 107's "8,744 of 8,744 launches PASS" is the check of C's own count over all ten C
logs: the wider reading. For later kits: say whether the smoke's launches and the burn-ins are inside the C rule.

## 5. The C-logging host's hash, named exactly (finding 5, nit)

[`pairing_e188.py`](../../../../tools/claims-v3/e188/pairing_e188.py) calls the hash "FNV-1a 64" (lines 15 and 42). Three places compute
it:
- the C-logging host's `ccFnv` ([`patch_host_ccheck.py`](../../../../tools/claims-v3/ccheck/patch_host_ccheck.py) line 46);
- `fnv64` in the check of C ([`ccheck.py`](../../../../tools/claims-v3/ccheck/ccheck.py) line 85);
- `fnv64` in the pairing (line 43).

All three have FNV-1a's form, with the **offset basis 1469598103934665603**. FNV-1a's standard basis is 14695981039346656037, one digit
longer. E186's kit note 2 § 3 already named this (its line 48).

Output § 5 tests it on this day's records:
- all **1,200** tiles records of the ten C logs (2,048 bytes each, A then B; 1,092 in the seven train logs) equal the hash of their own
  bytes under the host's basis, and **none** under the standard one;
- all 8,744 C records carry the hash of a tiles record of their own log.

Host and checkers use the same constant, so E188-SCHED's identity check holds. The verifier also compared the logged tile bytes with the
registered tiles directly: 7,448 of 7,448. Read "FNV-1a 64" in E188's kit as **"the C-logging host's FNV-1a-form 64-bit hash, offset basis
1469598103934665603"**. For later kits: a comment that names the basis as used, in the kit and in the check of C's docs.

## 6. The window under both readings of G (finding 6, nit)

Lines 27-30 give one reading: form (a) with G = the booking (15:10:41 PST), so last start 16:41 and last end 18:41. With G = his words
of 15:05:27 PST (line 21), the same form gives **16:36 and 18:36** (output § 6). Every gate the go lines name holds under both readings:

| gate | when | inside both readings? |
|---|---|---|
| steps 5, 6, 8 and 9 | all by 15:15:19; T0 15:15:14 | yes |
| step 9's launch + 100 min | 16:55:19 | yes |
| the queue's last item (18821, started 16:33:58, projected 410 s) | projected end 16:40:48 | yes |
| the session's end | 16:40:25 | yes |
| step 11 | started 16:40:45, more than 10 minutes before either last end | yes |

The queue ran with its deadline as set, 18:41:00 (`logs/queue.out`). At 18:36 it would have refused no item. The two readings' window
bounds differ, and no verdict or scored reading changes (the form of E189's note 3). The rule as run is the readiness check's form (a),
recorded before the session with G = the booking.

## 7. The closest margins (finding 7, note; post hoc, deciding nothing)

From `scored-e188.json` at the session's s (output § 7). A + margin is inside the band by that much; a - margin is outside by that much.

| word | margin |
|---|---|
| B22 SIZE M12 (the closest pass) | +0.00052 W |
| B19 SIZE M12 (FAIL LOW) | -0.00099 W |
| GB1 SIZE M12 (FAIL LOW) | -0.00099 W |
| GB1 REPEAT (DIFFERS HIGH) | a gap of 0.00057 W above E186-GB |
| GA23 SIZE M12, a bit (PASS) | +0.00069 W |
| GA23 REPEAT (AGREES) | overlap 0.00040 W |

At the session's s this arithmetic gives the kit's 31 words and sub-words.

**Moving s alone** (every train's rate ratio as measured), by E188.md 4.2's scaling (`forecast_e188.lines_at`: M10's line takes s, and
M12's adds its fixed increment): **every word and sub-word that takes s holds for s in [0.97905, 1.16630].** Below that range, B22's SIZE
M12 fails low first, and B22 would read NEITHER. Above it, GA23's REPEAT first reads DIFFERS LOW. The measured s, 1.01377, is inside the
range, and so is s = 1.

The verifier's own readings agree with the range: every word holds at s = 1 with rate ratio 1, and at s 1.0353 and 1.10; at s 0.95 B22
alone reads NEITHER; the alternative readings of s are 1.0144-1.0353. Their rate-ratio part was not re-run here.

## 8. The firmware-revisions query's line, under the owner's ruling (a records clause)

Lines 184-185 list "the firmware-revisions query" among the commands **never sent**, after E188.md section 6's own list. Line 26 says
"E188 sends no firmware query". Both are true of the session, whose checker read GO before any device opened.

The owner ruled at **15:07:01 PST Sun 15 Nov 2026**, verbatim: "Firmware revisions query was a false positive. It should have never been
forbidden. Reading operations and firmware are always allowed." So those lines record a read E188 did not need. They do not record a
command E188 was barred from sending: by his ruling the query is a read, allowed like every read. The lab's command table classed it
otherwise before his ruling, and his ruling calls that a false positive. Nothing in E188's data, rules or readings changes.

## 9. Lines for the records

1. **The commit message's scan** (§ 1): 0 hits and no class in the message as the lane wrote it. The committed message adds
   `commit_lab.sh`'s two standard trailer lines, on which `pubscan_all.py` reads 2 hits (the no-reply address) and `tiers_scan.sh` 1
   network line (the session link).
2. **The config reads** (§ 2): 23 of 24 at 523 mV, and PAIR's closing block read at 522 mV; TDP, threshold, power state and clock the same
   in all 24; nothing set.
3. **The closing anchors' quiet** (§ 3): the recorded 3,623.66-3,630.48 s is the runner's starting value; measured 23.701-30.521 s, against
   2 s. No gate, D or s changes.
4. **E188-C** (§ 4): PASS as scored (8,598 launches), and PASS read to include the smoke (106) and the burn-ins (40): 8,744 of 8,744.
5. **The hash** (§ 5): FNV-1a's form with the offset basis 1469598103934665603. All 1,200 tiles records match under it, and none under the
   standard basis.
6. **The window** (§ 6): G = his words gives 16:36 / 18:36; G = the booking (as run) gives 16:41 / 18:41. The session is inside both.
7. **The margins** (§ 7, post hoc): B22 SIZE M12 +0.00052 W is the closest pass. Every word holds for s in [0.97905, 1.16630].
8. **The firmware-revisions query** (§ 8): by the owner's ruling of 15:07:01 PST a read, always allowed. E188 needed none and sent none.

## What does not change

Every reading, verdict, gate, stop and figure of `README.md` and its files stands. Three readings are added beside them: lines 196 and
198, which § 1 reads with the trailer; lines 27-30's window, given under both readings in § 6; and lines 184-185, which § 8 reads under
the owner's ruling. The reducers, the scorer and the kit read none of this note's files.

This directory holds five new files: this note, the script, its two outputs and `SHA256SUMS-note1`. Before the commit:
- `SHA256SUMS` read 350 of 350 OK and `SHA256SUMS-note1` 6 of 6. The directory held 357 files, and every one but `SHA256SUMS-note1` was
  in one of the two lists;
- the script, run from a copy of this directory into an empty folder and again in place, wrote its two outputs byte for byte;
- the desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the lane's folders forbidden) read the five new files with 0 hits.
  A login check found no home path, no login, no e-mail address and no holder line in them;
- the public-text scan covered the five new files and this commit's full message as `commit_lab.sh` writes it. It used
  `sanitize_extracts.py`'s fixed list and the box's local table, plus the round's lists of private, vendor, access and mechanism words.
  It found nothing but two accepted items: the two standard trailer lines, set apart and named; and the hash's offset basis, a
  19-digit constant that the id class reads as a number of that shape (§ 5). The README's own two scanners, `pubscan_all.py` and
  `tiers_scan.sh`, read the same over the five files and the full message: 0 hits in the five files; on the message, the trailer's
  no-reply address (2 hits) and its session link (1 network line); and the basis (the id class).

SPDX-License-Identifier: Apache-2.0
