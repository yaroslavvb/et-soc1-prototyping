# E182's data README, dated note 1 (Sun 8 Nov 2026; after the card day's data verifier): M1 was committed after box steps 1, 2 and 4's first runs and before every later step, T0 and the first datum; the claim lane made the day's one post, which had five states; four reported figures are rounded wrong in their last digit; `results.md` and `score.log` print E182-W-int8's arm-E word

*Written on the Intel at about 03:20 PST on Sun 8 Nov 2026, desk only, after the card day's data verifier of E182 (Sun 8 Nov 2026, about
02:14–02:44 PST: holds with fixes, 0 critical, 0 major, 1 minor and 5 nits, none in a datum, a scored figure or a verdict).
[`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `0f6a8c45`, 02:09:59 PST) stay as committed, and so does every file of step
11's collection and score and of october-forecast-model's arm. **No number, rule, verdict or gate reading changes, and nothing is
scored.** The note answers the verifier's six findings: one sentence of the README (§ 1, the minor fault), one cell of its runbook table
and its post paragraph (§ 2), four reported figures, the verifier's two and two more found here (§ 3), how `results.md`'s and
`score.log`'s word for E182-W-int8 is read (§ 4), and one process item (§ 5). The figures come from
[`posthoc_note1_e182.py`](posthoc_note1_e182.py), which reads only this directory's committed files (and, as text, the kit's frozen
[`forecast-e182.json`](../../../../tools/claims-v3/e182/forecast-e182.json) and E178's committed
[`scored.json`](../2026-11-06-e178-one-number-aifoundry3/scored.json), whose figures the README quotes) and imports no lab module. Its
output is [`posthoc-note1-e182.txt`](posthoc-note1-e182.txt) and [`posthoc-note1-e182.json`](posthoc-note1-e182.json) ("output §" below
is that output's), and a re-run from this tree writes both byte for byte. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins this note, the
script and its two outputs; with `SHA256SUMS` (465 files, unchanged) it pins every file here but `README.md` and the two lists. The
steps' times and the post's states come from the card day's runbook log for E182 and the lanes' Discord records, both kept outside the
repository, and the commits' times from git. For the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6, as the README.*

## 1. M1 came after the day's first four runbook calls, and before every later step, T0 and the first datum (fault 1, minor)

The README's "Departures and their dates" (line 149) says "M1 was committed before every E182 box step and before T0, so by section 8 it
is scored beside". The second half holds; the first does not. october-forecast-model's dated note M1
([`E182.md.dated-note-M1.md`](../../../../tools/claims-v3/e182/E182.md.dated-note-M1.md), lab `c958e33b`) was committed at 00:03:19 PST
and pushed at 00:03:22, after four of E182's runbook calls:

| PST, Sun 8 Nov 2026 | the call | against M1 |
|---|---|---|
| 00:01:55 | box step 1, the window (`rb/s02_window_e182.sh`), by the claim lane | before |
| 00:01:55–00:02:00 | box step 2's first run (`rb/s03_desk_e182_v5.sh`, at `45e514e3`): "october-forecast-model note M1 absent (not scored: E182.md section 8)" | before |
| 00:02:57 | the claim lane's probe of aifoundry3 (`ssh … true`, under its 15 s bound) | before |
| 00:03:03 | box step 4, the look (k6's `s05_look_k6.sh`: et-who, who, uptime): FREE | before |
| **00:03:19** | **M1 committed (`c958e33b`; pushed 00:03:22)** | |
| 00:03:23 | box step 3, the day's post, by the claim lane | after |
| 00:13:27–00:13:32 | box step 2's second run, at `c958e33b`: "october-forecast-model note M1 present (scored beside, by its reader)" | after |
| 00:13:40–00:13:42 | box step 5, the sync | after |
| 00:13:46–00:13:57 | box step 6, the train host's build (its job 00:13:48–00:13:51, [`logs/e182-build-attempts.txt`](logs/e182-build-attempts.txt)) and the box's checks | after |
| 00:14:19–00:14:20 | box step 7, the reads of the card's settings | after |
| 00:14:24–00:14:51 | box step 8, the dry pass (no device opened) | after |
| 00:15:28 | the look again: FREE | after |
| 00:15:41 | box step 9: the session's T0 ([`logs/session.log`](logs/session.log) line 3) | after |
| 00:15:42 | the session's opening config read, its first reading on the card ([`logs/config-session-start.json.time`](logs/config-session-start.json.time)) | after |

None of the four calls before M1 read the card or opened a device: steps 1 and 2 run at the desk, the probe runs `true` over ssh, and
the look counts holders and logins without opening a device or taking a lock. The rule that decides M1's scoring holds:
[`E182.md`](../../../../tools/claims-v3/e182/E182.md) section 8 asks for the note "committed before E182's first datum", and M1 came 12
minutes before T0 (output § 1 gives the committed side, T0 and the first reading, from this directory's logs). So the sentence reads:
**M1 was committed at 00:03:19 PST (`c958e33b`, pushed 00:03:22), after box step 1, step 2's first run, the claim lane's probe and step
4's first look (00:01:55–00:03:03), and before the post, step 2's second run, the sync and every later step, so before T0 (00:15:41) and
E182's first datum; by section 8 it is scored beside.** The commit message of `0f6a8c45` says only that step 2 ran "before and after M1's
commit (c958e33b, before T0)", which holds.

## 2. The day's one post: the claim lane made it, and it had five states (faults 4 and 2, nits)

The runbook table's row 3 (line 138) gives the post as "the card lane's, after the look". The card day's claim lane (claim-q156) made it,
at 00:03:23 PST, after its own look at 00:03:03 and under the Discord lock. So the cell reads: **the claim lane's, after its look.**

The post paragraph (lines 191–197) gives the post's first text, its read-back at 00:13:14 and this run's handover at 01:54:29. Between
those, E184's arm-B lane edited the same post twice; after them, E184's arm-S lane released it. Message `1568898719959744554`, in all its
states (Discord's own times, from the lanes' channel plans, with each lane's save time in brackets):

| state | PST | by | the text after the change |
|---|---|---|---|
| 1 | created 00:03:23 | the claim lane, after its look | `<ai> **Claude says:** using aifoundry3 for 2 h, until ~02:03 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)` |
| 2 | edited 00:13:45 (00:13:46) | E184's arm-B lane, taking aifoundry1 card 1 | state 1's text, then `; using aifoundry1 card 1 for 1 h, until ~01:13 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)` |
| 3 | edited 00:33:09 (00:33:11) | E184's arm-B lane, at its release | state 1's text again: arm B's clause dropped |
| 4 | edited 01:54:27 (01:54:29) | this run's lane, at its end | `<ai> **Claude says:** using aifoundry3 for 2.5 h, until ~04:24 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)` |
| 5 | edited 02:25:14 (02:25:16) | E184's arm-S lane, at its release | state 4's text, then ` — released` |

Each change ran under the Discord lock as a dry run, a save and a read-back, with `EXPECT_TEXT` equal to the state before it: each lane's
recorded before-text equals the previous state's text, newlines aside. This run's read at 00:13:14 found state 1, never edited, before
arm B's edit; the handover's plan at 01:54:12 found the 00:33 edit, with state 1's text. Every state is one line opening
`<ai> **Claude says:**`, with `for N h` in digits and the kinds page as its doc link. The claim lane's plan before the post found no card
post in the day before it, and each of the eleven plans after it, 00:03 to 02:26, found this one alone; no earlier day's post was
touched. Arm S's lane appended " — released" after its smoke gate read NO-GO and no pass ran (E184's arm-S record, `f8d94224`).

## 3. Four reported figures are rounded wrong in their last digit (fault 3, nit; two of them found here)

The script read again, at full precision, every figure the README prints from `scored.json`, `arm-m1-e182.json`, the kit's
`forecast-e182.json` and E178's `scored.json`: 200 figures (output § 2). It compared each with its source rounded to the README's printed
decimals. 196 read right. These four do not:

| README line | what | printed | the committed value | so it reads |
|---|---|---|---|---|
| 78 | E182-K: the kinds-pass couples' T5 | +0.200 | +0.1994757 (`scored.json` › `reported` › `E182-K` › `T5` › `kinds_pass` › `mean`) | **+0.199** |
| 80 | the couples' order term, T5 | +0.017 | +0.0164965 (› `order_term` › `T5` › `tau` › `mean`) | **+0.016** |
| 82 | T3's SFFS orientation mean | 0.1290 | 0.1289497 (› `trains` › `T3` › `orientation_means` › `SFFS`) | **0.1289** |
| 90 | `int8.e182_a85_b1`'s D − P | −0.210 | −0.2094834 (› `kinds` › `int8.e182_a85_b1` › `D_minus_P_w`) | **−0.209** |

Each reads as if it had been rounded twice, first to one more decimal (0.1995, 0.0165, 0.12895, −0.2095). The data verifier found the second
and the fourth. All four are reported readings: none is a verdict or decides one, none changes a reading's words (T5's order-term
interval still holds 0, and `int8.e182_a85_b1` is still the third largest miss against P), and none is in the commit message. One figure
sits exactly at a half: october-forecast-model's T3, −0.00955 W, printed −0.0096, which both usual roundings give. The README's ten
statements of count (for example "four of the twelve exclude 0" and "six of seven") count again as printed, and its ratios in words hold:
about a quarter (0.252), three times (3.33), about five times (4.70), a tenth (0.098), about 0.1 W (0.099). Not read again here: the
card's own counts and peaks (57,500 samples, 54.17 W, 65 °C), which the data verifier re-read from the telemetry.

So the four read: E182-K's "T5 at +0.199 [+0.174, +0.225]"; the order term's "T5 +0.016"; "T3 0.1260, 0.1289"; and
"`int8.e182_a85_b1` −0.209".

## 4. `results.md` and `score.log` print E182-W-int8's arm-E word (fault 5, nit; known and registered)

[`results.md`](results.md) line 15 and [`score.log`](score.log) line 12 give E182-W-int8 as PASS. That is `size_E`, arm E's reading,
which `scored.json` › `rules` › `E182-W-int8` › `verdict` carries
([`E182.md.dated-note-1.md`](../../../../tools/claims-v3/e182/E182.md.dated-note-1.md) section 2; output § 3). **The registered verdict
is `size_P`: FAIL HIGH**, 3.789 fJ a flip [1.447, 6.131] against P's 7.044. The README quotes it so (lines 49 and 52–53), naming
`results.md` and the verdict field; `score.log` prints the same field. Quote "E182-W-int8 FAIL HIGH (its size_P word; arm E PASS)",
never `results.md`'s or `score.log`'s PASS.

## 5. Sub-second Python outside the local slot (fault 6, nit; the card lane disclosed it)

The card lane ran its sub-second Python on the Intel outside the round's local slot (`slot.sh`): the summarizer, october-forecast-model's
reader, the peaks reader, the post's builders, `py_compile` and small JSON reads. Its two long jobs ran through the slot, one at a time:
step 11 v3's collection (01:56:18–01:58:15 PST) and the login scrubs with the public-text scan (01:59:22–02:05:23), by the round's slot
log, kept outside the repository. None ran on a lab box, and nothing is to be redone. This note's lane made one such call, a sub-second
read of `forecast-e182.json`'s keys at about 02:56 PST; its other Python, the script's runs among them, went through the slot.

## Lines for the records

1. M1 (`c958e33b`, 00:03:19 PST, pushed 00:03:22) came after box steps 1 and 2 and the first look (00:01:55–00:03:03), and before the
   post, step 2's second run, the sync and every later step, T0 (00:15:41) and the first datum: scored beside by E182.md section 8. Never
   "before every E182 box step".
2. The day's one post, `1568898719959744554`, had five states (the lanes' save times): created 00:03:23 by the claim lane ("for 2 h,
   until ~02:03 PST"); arm B's clause added at 00:13:46 and dropped at 00:33:11; this run's handover at 01:54:29 ("for 2.5 h, until
   ~04:24 PST"); " — released" at 02:25:16 by arm S's lane. Each change ran under the Discord lock with `EXPECT_TEXT`.
3. The post was the claim lane's, after its look; never "the card lane's".
4. E182-K's kinds-pass T5 is +0.199 (not +0.200), the order term's T5 +0.016 (not +0.017), T3's SFFS mean 0.1289 (not 0.1290), and
   `int8.e182_a85_b1`'s D − P −0.209 (not −0.210). The README's other 196 figures from the scorer's and the arm's files read right.
5. E182-W-int8: FAIL HIGH (size_P), arm E PASS. Never `results.md`'s or `score.log`'s PASS.
6. The card lane's sub-second Python ran outside the local slot; its collection and its scrub-and-scan job ran through it, one at a time.

## What does not change

Every reading, verdict, gate, stop and figure of the README stands, except the one sentence, the one table cell and the four printed
figures above. With this note's five new files in the directory (the four it pins and `SHA256SUMS-note1`):
- `SHA256SUMS` reads 465 of 465 OK, and `SHA256SUMS-note1` 4 of 4; the directory holds 472 files, and only `README.md` and the two lists
  are in neither list;
- the post hoc script, re-run in place and into an empty directory, writes its two outputs byte for byte;
- the login checks read every directory clean: `scrub_tree_e178.py --check` (285 files in 35 directories, 0 left) and E164's `--check`
  in all 57 directories; run_e78's stop line and lib.sh's line on other users appear in none of the new files;
- the desk-path gate (`nopath_q142s.py`, v3.1) reads the five new files with 0 hits;
- the public-text scan (`sanitize_extracts.py`'s fixed list, the private-network, Mac-home, scratch and e-mail patterns, and the data
  verifier's wider list) finds nothing in the five new files or in this commit's subject and body.

The scorer reads none of this note's files, and the data verifier re-made step 11's 462 files from the committed data at `0f6a8c45` (451
byte for byte, the 11 C logs equal unpacked), so no scored figure can move.

SPDX-License-Identifier: Apache-2.0
