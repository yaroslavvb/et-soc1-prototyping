# E189's data README, dated note 1 (Sat 14 Nov 2026; after the data verifier): the Files table gains sparse parity's `host.rec`; the busy-reading flags read 3-5%; the scrub found nothing to replace; the window's G read two ways, and the rule that decides; the departures came after the collection; S1T's margin on the starting die (post hoc); lines for the records

*Written on aifoundry2 from about 21:10 PST on Sat 14 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no
post), by the lane `fix-e189d` of Q174, after E189's data verifier `verify-e189d` (Sat 14 Nov 2026, 20:37-20:59 PST: holds with fixes;
five nits and one post hoc note, none of them a fault in a datum, a scored figure or a verdict; the four registered rules re-derived from
the raw files by its own code, with the kit's words and counts). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab
`fa9098c4`, git 20:34:12 PST Sat 14 Nov 2026) stay as committed. **No number, rule, verdict or gate reading changes, and nothing is
scored.** The figures come from [`posthoc_note1_e189.py`](posthoc_note1_e189.py), which reads only committed files: the files of this
directory's data commit (the 228 that `SHA256SUMS` lists, `README.md` and `SHA256SUMS`), the registration's list
`SHA256SUMS-e189-registration` with the ten files it pins, and, as text, the lines this note cites. For § 6 it loads the frozen scorer,
`score_e189.py`, as registered, only after that list reads every entry OK, and uses the scorer's own pass reader, its forecast module's
`given()` and its verdict count. Its output is [`posthoc-note1-e189.txt`](posthoc-note1-e189.txt) and
[`posthoc-note1-e189.json`](posthoc-note1-e189.json) ("output §" below is that output's), and a re-run from this tree writes both byte
for byte. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins this note, the script, its two outputs, `README.md` and `SHA256SUMS`, so the line
numbers below refer to their committed bytes; with `SHA256SUMS` (228 entries), every file here is pinned but `SHA256SUMS-note1` itself.
Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** (E189.md and the kit as committed), **measured** (the
session's committed files), **desk check of code**, **post hoc** (desk readings after the data, deciding nothing).*

## 1. The Files table leaves out sparse parity's `host.rec` (nit)

Line 137, the Files table's row for `passes/<configuration>/p<k>/`, lists every file of a pass but one. Sparse parity's four passes also
hold **`host.rec`**: its host's per-hart result records, binary. Each is 131,072 bytes, 2,048 records of 64 bytes, one a hart
(`SppRecord` is 64 bytes by [`sparseparity_args.h`](../../../../workloads/sparseparity/sparseparity_args.h) line 165, and `SPP_HARTS` is
2048, line 61). The host reads them back from the card after each launch
([`main.cpp`](../../../../workloads/sparseparity/host/main.cpp) line 1228) and writes them at its end with `--records-out` (line 1279),
which E189's runner points at the pass's `host.rec` ([`e189_common.py`](../../../../tools/claims-v3/e189/e189_common.py) line 78); so
each file holds its burst's last launch. All four are in `SHA256SUMS` and in the box's `session/MANIFEST.sha256` at the same sha256
(output § 1). The collector's own description names the file ([`collect_e189.py`](../../../../tools/claims-v3/e189/collect_e189.py)
line 11); the scorer does not read it. With it, the row's list reads: `telemetry.jsonl.gz`, `host.json`, `host-raw.json` (the ledger
programs), `host.err`, **`host.rec` (sparse parity only: its host's per-hart result records of the burst's last launch, 2,048 of 64
bytes, binary)**, `run.json`, `pass.json`, `energy.json` and `energy.txt`.

## 2. The busy-reading flags read 3-5% (nit)

Line 61 says five passes carry the reducer's note of one busy board reading at idle, "which it reports as moving its catalogue
cross-check (about 3-4% low)". The five flags give **3, 3, 4, 5 and 3%**: copy, random p2 (1 of 36 busy readings) and p4 (1 of 38),
3% each; sort, sorted p2 (1 of 24), 4%, and p3 (1 of 21), 5%; sparse parity p4 (1 of 27), 3% (output § 2). So line 61 reads "about
3-5% low". The note concerns the reducer's catalogue cross-check only: the headline the scorer reads, `board.j_per_solve` (the SP's
board average), does not alias such readings, as each flag says, so no scored figure moves.

## 3. The scrub found nothing to replace (nit)

Line 124 says the collector's scrub ran and that "the box's home path became `~`". The scrub ran, and **it replaced nothing**:
- every one of the 178 files that the box's `session/MANIFEST.sha256` lists is at its listed sha256 here (the runner writes that list
  on the box, last, before the copy-back: [`run_e189.py`](../../../../tools/claims-v3/e189/run_e189.py) line 606), so the scrub changed
  none of them;
- of the data commit's other 52 files (the 48 `energy.json` and `energy.txt` the desk wrote, `MANIFEST.sha256`, `runner.rc`,
  `SHA256SUMS` and `README.md`), only `README.md` holds a `~` at all, once, in that sentence; a replacement would have left one;
- no file of the data commit holds a home-directory path, the text inside every `.gz` included (output § 3).

So line 124 reads: the collector's scrub ran and found no home path to replace, and no home-directory path is in any file. The rest
of that paragraph stands.

## 4. The window: G read two ways, and the rule that decides (the verifier's nit 4)

**What the registration says** (registered). Section 13 (E189.md line 353), alone: "from his go at G, last start G+1:30, last end
G+3:30, inside one Pacific day and at least 30 minutes before the approval lapses". Section 12 (line 343) counts "the window closed"
among the gates whose meaning is "no session (or no further pass): no data, never a failed prediction". The status paragraph (lines
14-15): "A departure from anything here is a dated amendment written before the data it touches."

**What happened.** His go came at about 14:50 PST (README line 88). The answer he chose said he would give the window himself; he then
waived the post, and no window time came. Departure 6 (lines 102-106): the round read G as the moment the card lane held its booking of
aifoundry3, 20:04:17 PST, as its plan for Friday had; step 1 wrote the window at 20:09:04 PST as 21:35 and 23:35, each rounded up to the
whole minute, 43 s past G+1:30 = 21:34:17 and G+3:30 = 23:34:17 (output § 4).

**Both readings:**
- **As run (Departure 6):** the window was open from the first card command, 20:11:45.08, to the close, 20:27:30.25. Pass 24 started
  at 20:25:03, 1 h 09 min 14 s before G+1:30, and the session ended 3 h 06 min 47 s before G+3:30, so the rounding bore on nothing.
  Every pass counts by section 8.2, and the frozen scorer's words are the day's: E189-S1 FAIL, E189-S1T PASS, E189-S2 FAIL, E189-S2T
  FAIL.
- **By the letter of section 13** (G = his go, about 14:50 PST): last start about 16:20 and last end about 18:20 PST. The first card
  command came 3 h 51 min 45 s after that last start, so the window had closed before the session began. Section 12 then reads no
  session: no data, never a failed prediction, and each of the four rules would read NOT DECIDED, with no configuration scored. That is
  what the letter says; no score was run on it.

**The rule that decides** is the registration's own rule for departures, the status paragraph above. Departure 6 was dated and fixed
before any E189 datum: the round's plan (Fri 13 Nov 2026, not published) read G as the card lane's start after its booking, and step
1's window record (20:09:04 PST) came before the first card command (20:11:45). It was not an amendment beside E189.md, and it reached
the public record only in this directory's README, after the collection (§ 5). The part of the rule that guards against a choice made
after the data, written before the data it touches, is met. So the as-run reading stands: the frozen scorer's words are the day's
verdicts, with Departure 6 named beside them. Read by its form alone, the rule would leave section 13's letter in force, and the day
would be no data; that reading is recorded here, beside the verdicts. Neither reading touches a datum, a frozen forecast, a band, a
threshold or a rule of section 8. The two things section 13 ties the window to, the post's span ('for 2 h') and the approval's lapse,
did not arise that day: the post was waived, and aifoundry2 had no approval to lapse.

**For later card days** (no change to this data): the go lines say how G is read and round the bounds down, and a day's departures are
committed as a dated note before its session (§ 5).

## 5. The departures came after the collection (nit)

The README's departures (lines 84-112) are dated Sat 14 Nov 2026 and say they were "set by his go and the round's brief before the
session, written here after the collection and before the scorer ran". The status paragraph asks for a dated amendment written before
the data it touches. Of the eight items (output § 5):
- items 3, 4, 6 and 7 depart from E189.md or its kit:
  - 3: no network-access approval to name from aifoundry2;
  - 4: the post waived, on the owner's words;
  - 6: G and the window (§ 4);
  - 7: the desk's interpreter, 3.12.3, against the 3.9 and 3.13 that E189.md and KIT.md name;
- items 1 and 2 record registered defaults kept, item 5 a day the registration does not fix, and item 8 notes.

Item 3 reads as item 6 does (§ 4): by its letter, section 13 asks his go to name a fresh approval, and from aifoundry2 there was none to
name. Each departure was set before the session, in the owner's words and the round's dated plan and brief. None touches a datum, a
frozen number, a band, a threshold or a rule of section 8 (8.2's validity, 8.3's words), so no reading moves. What was missing is the
form: a dated amendment, published before the session.

## 6. S1T's margin on the starting die (post hoc; the verifier's note 6)

**Registered.** Section 5.2 (lines 177-178) takes T0 as `die_c.before`, the before bracket's `minshire[0]`. The frozen scorer's E189-S1T
(line 254: within 5% on at least 5 of 6) reads **PASS, 6 of 6**. Its e_j_total values are −0.0080 (copy, zeros), −0.0224 (copy,
random), −0.0253 (SHA-256), −0.0455 (sort, sorted), −0.0395 (sort, shuffled) and −0.0188 (sparse parity). Every T0 read 49-51 °C, below
the footing law's 52-66 °C band, so `given()` priced the card at rest by the exponential law in all 24 passes, as registered (output §
6). The die reads whole degrees (section 14, line 364), and the before bracket averages those readings.

**Post hoc** (deciding nothing): the same frozen code with every pass's T0 moved by one uniform delta, the measured values as committed:
- **Downward:** sort, sorted leaves the 5% band at −0.428 °C, which leaves 5 of 6 within, still PASS. Sort, shuffled leaves at
  −0.997 °C, where S1T's word becomes FAIL, 4 of 6. At −1.0 °C the six read −0.01846, −0.03213, −0.03571, −0.05588, −0.05003 and
  −0.02690, in the order above.
  The other four leave the band only at −2.4 °C or below: SHA-256 at −2.423, copy, random at −2.914, sparse parity at −4.029 and copy,
  zeros at −4.197 °C.
- **Upward:** S1T stays PASS through +5 °C. Only copy, zeros leaves the band, at +4.772 °C (output § 6).

**Both readings and the rule.** At T0 as measured, S1T is PASS, 6 of 6. If every T0 were 1 °C below its reading, S1T would be FAIL, 4 of
6. The rule that decides is section 5.2's T0, the measured `die_c.before`, read by section 8.3's E189-S1T: **PASS stands**, and the
margin is reported beside it, never as a reading of the day. The verifier puts this margin beside S1T when `scores-e189.json` is
committed; that later commit can cite this section.

**A desk check beside it.** The frozen scorer, run again at the desk on this committed directory as step 13 runs it, wrote the kit's
`scores-e189.json` byte for byte (sha256 `ac8770ba7a1cdf995370c94c5736fda25156e833f9da3b93381f393ee624363c`). This script's delta 0
equals that file's e_j_total for every configuration, to 5e-11.

## 7. Lines for the records

1. **`host.rec`:** sparse parity's per-hart result records of each pass's last launch (4 files, each 2,048 records of 64 bytes, binary),
   in `SHA256SUMS` and the box's manifest; the Files table's row names it with this note (§ 1).
2. **The busy-reading flags:** five passes, about 3-5% low on the catalogue cross-check, never the headline (§ 2).
3. **The scrub:** it ran and found nothing to replace: 178 of 178 copied files at the box's own sha256, no `~` outside README.md, no
   home-directory path anywhere (§ 3).
4. **The window:** read as run (G = the booking, 20:04:17 PST), it was open throughout and the scorer's words are the day's verdicts. By
   the letter of section 13 (G = his go, about 14:50 PST), it closed at about 16:20, and section 12 would make the day no data. The
   departure rule decides for the as-run reading: G's reading was dated and fixed before any datum, though never an amendment and
   published after the collection (§ 4).
5. **The departures:** set before the session, published only after the collection. Later card days commit a day's departures as a
   dated note before its session; their go lines say how G is read and round the bounds down (§ 5).
6. **S1T:** PASS, 6 of 6 (registered). Its margin on the starting die (post hoc): sort, sorted leaves the 5% band at −0.43 °C, and S1T's
   word changes at −1.00 °C (4 of 6). Upward, nothing changes through +5 °C (§ 6).
7. **The frozen scorer, re-run at the desk** on the committed directory: byte for byte the kit's `scores-e189.json`, sha256
   `ac8770ba...` (§ 6).

## What does not change

Every reading, verdict, gate, stop and figure of `README.md` and its files stands. The exceptions are the printed details §§ 1-3 correct
(line 137's row, line 61's share, line 124's wording) and the readings §§ 4 and 6 set beside the verdicts. The reducer, the scorer and
the kit read none of this note's files. With the five new files in this directory (this note, the script, its two outputs and
`SHA256SUMS-note1`), before the commit:
- `SHA256SUMS` read 228 of 228 OK and `SHA256SUMS-note1` 6 of 6; the directory held 235 files, and every one but `SHA256SUMS-note1`
  was in one of the two lists;
- the script, run from a copy of this directory into an empty folder and again in place, wrote its two outputs byte for byte;
- the desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the lane's folders forbidden) read the five new files with 0 hits,
  and a login check found no home path, no login and no holder line in them;
- the public-text scan (`sanitize_extracts.py`'s fixed list and the box's local table, and a list of private, vendor and mechanism
  words) found nothing in the five new files or in this commit's subject and body.

SPDX-License-Identifier: Apache-2.0
