# E192's data README, dated note 3 (Sun 15 Nov 2026): a correction to the time of the owner's go - it came at 19:52:40 PST, and his waiver of the post at 20:01:31 PST, not at about 14:50; with G at either, the window's last start comes earlier than as run (21:22:40 or 21:31:31, against 22:24:40) and its last end stays 23:30, the session lies inside every reading, and no datum, price, check or verdict changes (correction, post hoc)

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `a6e17e83`), note 1's five files
([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and the four beside it, `4e964246`) and note 2's six
([`README.md.dated-note-2.md`](README.md.dated-note-2.md) and the five beside it, `117312b1`), which all stay as committed. Written on
aifoundry2 from about 03:15 PST on Sun 15 Nov 2026 (week 46) by the clock, desk only (no card, no device, no call to another box, no
post), by the lane `note3-e192` of Q181. **This note is a correction, post hoc.** README.md gives the owner's go as "about 14:50" PST; it
came at 19:52:40 PST (§ 2). This note gives the corrected times and E192's window under each reading of G with them (§ 3). **No datum,
measured figure, price, check, verdict, rule, threshold, stop, cap or rest changes, and nothing is scored** (§ 4): only the go's time and
the one window bound built on it, the last start, differ, and the session lies inside the window under every reading. **The forecasts
stay sealed: no forecast number is here.** Labels: **registered** (E192.md and the kit as committed), **measured** (the session's committed
files), **correction** (the go's times, from the record § 2 names), **post hoc** (§ 3's arithmetic, done after the data and deciding
nothing), **desk check of code** (what the kit's bounds bind, § 3, and what the reducer and the checker read, § 4). [`SHA256SUMS-note3`](SHA256SUMS-note3) pins this note and the six
committed files of this directory whose lines it cites, so the line numbers below refer to their committed bytes; the registration's and
the kit's files are pinned by their own lists, E189's by E189's lists, and the k6 runbook's common library, which the kit's runbook sources, by its sha256 and its own list (§ 3).
E189's data note 3 (lab `a65734ad`) made the same correction for E189. The lane's desk arithmetic ran under `/usr/bin/python3` 3.12.3 on
aifoundry2.*

## 1. What README.md says

README.md gives the owner's go a time twice:
- the summary of the departures at its top (lines 11-12): "the go, by the owner's answer of about 14:50 PST naming the runs to follow
  E189 on aifoundry3 card 0 "as each becomes ready"";
- Departure 1 (lines 90-94), which quotes the card-time question, asked "at about 14:44 PST" (line 90): the owner answered
  "Yes, but I'll post on Discord" "(about 14:50)" (line 92).

Departure 2 quotes his answer to the next question (lines 95-96), "it's fine not to announce, the cards are unused", with no time. Notes 1
and 2 give no time for his go.

The window does not take its G from that time. Departure 4 (lines 104-110) takes the form "after another session of ours that day" and
sets G at "the moment the card lane held the round's booking of aifoundry3, **20:54:40 PST**" (line 107): "The last start is G+1:30 but no
later than 22:25: G+1:30 = 22:24:40, written to the whole minute below so that it is never later than G+1:30: **22:24 PST**; the last end
**23:30 PST**" (lines 107-109). The window's row (line 82) reads, registered, "his go's, inside one Pacific day", and, happened, "last
start 22:24, last end 23:30 PST; launched 21:07:42 (T0 21:07:37), ended 22:07:08".

## 2. The corrected times (correction)

The source is the orchestrating session's record of the owner's answers. It holds each question's and each answer's time to the
millisecond, in UTC; PST is UTC-8 on these dates. All times are Sat 14 Nov 2026, PST:

| time (PST) | the record |
|---|---|
| 14:44:01 | the card-time question that Departure 1 quotes is asked |
| 19:52:40 | his answer arrives: "Yes, but I'll post on Discord" |
| 19:54:39 | the next question is asked: whether to post the day's claim |
| 20:01:31 | his answer arrives: "it's fine not to announce, the cards are unused" |

To the millisecond the record reads 14:44:01.950, 19:52:40.332, 19:54:39.035 and 20:01:31.346.
- **His go came at 19:52:40**, 5 h 08 min 38 s after the question. It left the day's post to him.
- **His waiver of the post at 20:01:31 completed it** (Departure 2).
- "About 14:50" was the time the orchestrating session first wrote down for his answer. It was an assumption, made before that record's
  clock was read, and README.md carried it from there.
- The question's time, "about 14:44" in Departure 1 (line 90), was right.
- Both answers came after E192's registration and kit were committed (`a282aad6` at 19:40:05 PST and `a6fe5c20` at 19:40:45 PST, by
  their commit times); the question came before either.
- The card lane booked aifoundry3 at 20:54:40 (Departure 4), after both answers. The session's first card command came at 21:07:37
  (measured: [`session/first-card-command.txt`](session/first-card-command.txt), 1794719257; [`session/session.log`](session/session.log)
  line 4).
- E189's data note 3 ([`README.md.dated-note-3.md`](../2026-11-14-e189-blind-day-aifoundry3/README.md.dated-note-3.md) in E189's data
  directory, lab `a65734ad`, sha256 `7d01e144...` in its `SHA256SUMS-note3`) made the same correction for E189, from the same record.

## 3. The window under each reading of G (post hoc)

**Registered.** [E192.md](../../../../tools/claims-v3/e192/E192.md) (sha256 `4d8cbd1a...`, pinned in `SHA256SUMS-e192-registration`)
counts the window and the go among "a gate before the sampler (a holder, the lock, the rest, the window, the go)", which means "no
session: no data" (section 11, line 265); its row for what ends a session once begun names "a live stop, a holder between passes, the
cap" (line 267), not the window. Section 10 (lines 256-257) sets the rest: "E192's first card command at least 40 minutes after the end of
the previous session of ours on that card". Section 12 (lines 273-274) lists what his go must name. E192.md sets no figures for the window.

**The form** is the kit's ([CARD-LANE-BRIEF.md](../../../../tools/claims-v3/e192/CARD-LANE-BRIEF.md) lines 28-29, sha256 `dbd2e492...`
in `SHA256SUMS-e192-kit`): "The window from the go at G, inside one Pacific day: alone on aifoundry3 that day, last start G+1:30 and last
end G+3:30; after another session of ours there that day, its end plus the 40-minute rest before E192's first card command". E189 ran on
the card first that day (Departure 4, lines 104-105), so the second form applies, with the readiness check's figures as Departure 4 gives
them: **last start G+1:30 but no later than 22:25, last end 23:30.**

**What each bound binds** (desk check of code; the kit's files are under `tools/claims-v3/e192/`, each pinned in `SHA256SUMS-e192-kit`):
- **The last start:** "no new card session after the round's last start" (the k6 runbook's common library, which `rb/rb_e192.sh` sources at line 21,
  `tools/claims-v3/q141k-runbook/k6/rb_common.sh` lines 196-198, sha256 `93e177c1...` in its directory's `SHA256SUMS-drivers-v3`, unchanged since `9a2630ff` on Thu 5 Nov 2026). Steps 5
  and 9, and the starts of steps 6 and 8, refuse after it (`rb/s07_a3_sync_e192.sh` line 17, `rb/s08_a3_build_e192.sh` line 23,
  `rb/s10_a3_dry_e192.sh` line 18, `rb/s11_a3_session_e192.sh` line 18). It bounds the box steps up to the session's launch. Step 9 hands the session the last end as its
  deadline and no last start (`rb/s11_a3_session_e192.sh` lines 37 and 39), so no pass is bound by it.
- **The last end:** step 9 starts no session unless the 65-minute cap fits before it (`rb/s11_a3_session_e192.sh` line 19), and the
  session's wrapper refuses, before it opens anything, unless the same holds (`session_e192.sh` line 129). The passes are then bound by the
  cap: "no pass starts that could end after it" (`gate_e192.py` line 17).

**Rounding.** Departure 4 wrote the as-run last start to the whole minute below, so that it is never later than G+1:30 (step 1,
`rb/s02_window_e192.sh`, takes whole minutes: line 9). The table gives each exact bound and both whole-minute forms (down / up).

**Measured** (`session/session.log` lines 1, 4, 7 and 8; note 1 line 34; README.md lines 54-63 and 82):
- T0 1794719257 = 21:07:37, the session's first card command (the per-sensor probe); step 9's launched line read 21:07:42;
- the smoke began at 21:07:48, pass 0 at 21:08:23, pass 2 at 21:22:08, pass 3 at 21:28:35, pass 4 at 21:35:00 and pass 8, the last, at
  22:01:03 (each block's first mark);
- the cap, 65 card-minutes from the first card command, was at 22:12:37; the session ended at 22:07:08, after 3,571 s of card time and 9
  of 9 passes.

**The rest:** E189's session ended at 20:27:30
([`session/session.log`](../2026-11-14-e189-blind-day-aifoundry3/session/session.log) line 67 in E189's data directory, pinned in its
`SHA256SUMS`), so the rest opened at 21:07:30 (note 1 line 29), and the first card command came 7 s after it (note 1 line 35). The rest
does not depend on G.

| reading | G (PST) | last start = min(G+1:30, 22:25) (whole minute down / up) | last end | the session against it (measured) | passes begun after the last start | section 11's window gate |
|---|---|---|---|---|---|---|
| as run (Departure 4): G = the booking | 20:54:40 | min(22:24:40, 22:25:00) = 22:24:40 (22:24 as written / 22:25) | 23:30 | the first card command 0:12:57 after G and 1:17:03 before the last start (1:16:23 before 22:24); the cap 1:17:23 and the end 1:22:52 before the last end | none | passed |
| G = his go | 19:52:40 | min(21:22:40, 22:25:00) = 21:22:40 (21:22 / 21:23) | 23:30 | 1:14:57 after G; 0:15:03 before the last start (0:14:23 before 21:22); the cap 1:17:23 and the end 1:22:52 before the last end | 3-8 (2-8 against 21:22) | passed |
| G = the waiver that completed his go | 20:01:31 | min(21:31:31, 22:25:00) = 21:31:31 (21:31 / 21:32) | 23:30 | 1:06:06 after G; 0:23:54 before the last start (0:23:23 before 21:31); the cap 1:17:23 and the end 1:22:52 before the last end | 4-8 | passed |

Times are h:mm:ss. In every reading:
- 22:25 does not bind, so the last start is G+1:30 itself;
- the rest opened before the last start (by 15 min 10 s at the least, against 21:22:40; 14 min 30 s against 21:22), so the session
  could begin inside the window;
- step 9's launched line, 21:07:42, came 14 min 58 s before the earliest last start (14 min 18 s before 21:22);
- the last end, 23:30, falls 30 min before midnight, inside the Pacific day 2026-11-14;
- a pass begun after the last start is bound by the cap alone, as every pass is.

To the record's millisecond, G = 19:52:40.332 and 20:01:31.346 put those two readings' exact bounds 0.332 s and 0.346 s later and leave
their whole-minute forms as they are. No comparison in the table lies within a second of its bound (the closest is pass 2's start,
21:22:08, 8 s after 21:22 and 32 s before 21:22:40), so none changes.

**README.md's time as G.** In the same form, "about 14:50" would give a last start of about 16:20, 4 h 47 min 30 s before the rest
opened: no E192 session could have begun that day, and section 11 would read the window gate as failed, "no session: no data". No committed
E192 line made that reading (Departure 4 set G at the booking), and with the record's times it does not arise.

## 4. What changes, and what does not

- **What differs between the readings is the last start alone.** With G at his go it is 21:22:40, and with G at the waiver 21:31:31,
  against 22:24:40 as run (22:24 as written): 1 h 02 min 00 s and 53 min 09 s earlier, at whole seconds. The last end (23:30), the rest
  (21:07:30), the cap (22:12:37) and every measured time are the same in every reading.
- **What each reading gives for the day does not differ.** The session's first card command came after the rest opened and before the
  last start, and its cap and its end before the last end: the window gate passed, section 11's "no session: no data" does not arise, and
  every pass counts as run, the passes begun after an earlier last start included (§ 3).
- **No datum, price, check or verdict changes** (desk check of code). The registered reducer reads only the run's telemetry, run records and marks
  (`proposal/src/reduce_intbits.py` lines 137-139, `715fddaa...` in `SHA256SUMS-e192-registration`), and the section 7 checker only the run
  records, the telemetry and the reducer's output (`check_e192.py` lines 63-65, `ceb99e7c...` in `SHA256SUMS-e192-kit`): neither reads the
  go's time or the window. Note 2's prices and the checks' verdicts stand as committed ([`checks-e192.txt`](checks-e192.txt) line 9, as note
  2 line 174 quotes it: "CHECKS-E192: 1 PASS; 2 FAIL; 3 NOT EQUAL; 4 PASS; 5 FAIL; 6 FAIL; 7 REPORTED; 8 REPORTED"). Note 1's reading of the
  rest (met by 7 s) does not depend on G and stands.
- **Departure 4 stays, as a departure of form that bore on nothing.** The round read G as the booking, 20:54:40: 1 h 02 min 00 s after his
  go and 53 min 09 s after the waiver, so its last start fell that much later than with G at either, and the 22:24 that step 1 wrote is 40 s
  earlier than its exact bound. The session's first card command came 14 min 23 s before the earlier of their whole-minute last starts
  (21:22). Departure 4 touches no datum, sealed forecast, threshold, stop, cap or rule of E192.md.
- **Unchanged:** every datum, measured figure and flag of README.md (its go time, lines 11-12 and 92, is read as below); notes 1 and 2 and
  their files. The reducer, the checker and the kit read none of this note's files.
- **Read with this note** (the committed bytes stay; the corrected readings follow):
  - README.md lines 11-12, "the owner's answer of about 14:50 PST": his answer arrived at 19:52:40 PST, and his waiver of the post at
    20:01:31 PST.
  - README.md line 92, "(about 14:50)": his answer arrived at 19:52:40 PST, 5 h 08 min 38 s after the question of 14:44:01 (line 90's
    "about 14:44").
  - README.md lines 95-96, Departure 2: the post question was asked at 19:54:39 PST, and his answer arrived at 20:01:31 PST.
  - README.md line 82, the window's row, "his go's": with G at his go, last start 21:22:40 and last end 23:30 PST (with G at the waiver,
    21:31:31 and 23:30). The session lies inside them, as it lies inside the as-run 22:24 and 23:30.

## 5. Lines for the records

1. **His go, corrected** (correction): the card-time question was asked at 14:44:01 PST on Sat 14 Nov 2026.
   His answer, "Yes, but I'll post on Discord", arrived at 19:52:40. The post question was asked at 19:54:39,
   and his answer, "it's fine not to announce, the cards are unused", arrived at 20:01:31. The source is the
   orchestrating session's record of the owner's answers. "About 14:50" in README.md (lines 11-12 and 92) was
   an assumption written before that record was read.
2. **The window** (post hoc): in Departure 4's form (last start G+1:30 but no later than 22:25, last end 23:30), G = 19:52:40 (or
   20:01:31) gives last start 21:22:40 (21:31:31). As run, G = 20:54:40 gives 22:24:40, written 22:24. The last end is 23:30 in every
   reading. The session, from its first card command at 21:07:37 (7 s after the rest opened at 21:07:30) to its end at 22:07:08, lies
   inside every one; the last start bounds the launch, not the passes.
3. **No datum, price, check or verdict changes** (desk check of code): only the last start differs between the readings. CHECKS-E192 stands: 1 PASS; 2 FAIL;
   3 NOT EQUAL; 4 PASS; 5 FAIL; 6 FAIL; 7 REPORTED; 8 REPORTED.

## 6. Checks before the commit

- In a copy of this directory with the two new files: `SHA256SUMS` 27 of 27, `SHA256SUMS-note1` 6 of 6, `SHA256SUMS-note2` 5 of 5 and
  `SHA256SUMS-note3` 7 of 7 entries OK; 42 files, every one in a list but `SHA256SUMS-note1`, `SHA256SUMS-note2` and `SHA256SUMS-note3`
  themselves.
- Every time and interval in §§ 2-4 was re-derived from the committed files named there and the record's four times by the lane's desk
  arithmetic and found equal to the text here; every line this note cites holds the words it is cited for, and every link resolves. The
  arithmetic is written out in § 3, so it can be redone by hand.
- The desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the round's folders forbidden) read the two new files with 0 hits,
  and a login check found no home path, no login and no holder line in them or in this commit's subject and body.
- The public-text scan (the lab's `sanitize_extracts.py`, its fixed list and the box's local table, and the round's lists of private,
  vendor, access and mechanism words) found nothing in the two new files or in this commit's subject and body but the owner's quoted
  answer of 19:52:40 itself, which names the lab's chat service, a word on the round's private list, as README.md line 92 does (reviewed
  and kept: they are his words).

## What does not change

Every datum, measured figure, price, check verdict, stop and as-run gate reading of `README.md`, note 1, note 2 and their files stands.
This note corrects one time, the owner's go, and the window bound built on it (§ 4 lists the lines that read differently with it). The
seal is kept: no forecast number is here, and nothing here scores E192. This lane reached no box, opened no device and changed no
committed file.

SPDX-License-Identifier: Apache-2.0
