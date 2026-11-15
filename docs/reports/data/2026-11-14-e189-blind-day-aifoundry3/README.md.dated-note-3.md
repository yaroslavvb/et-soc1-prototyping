# E189's data README, dated note 3 (Sun 15 Nov 2026): a correction to note 1 § 4's premise - the owner's go came at 19:52:40 PST and his waiver of the post at 20:01:31 PST, not at about 14:50, so section 13's letter and the as-run reading both hold the whole session; the no-data reading does not arise, and no verdict changes (correction, post hoc)

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `fa9098c4`), note 1's five files
([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and the four beside it, `caca0c1f`) and note 2's four
([`README.md.dated-note-2.md`](README.md.dated-note-2.md) and the three beside it, `830a3901`), which all stay as committed. Written on
aifoundry2 from about 00:05 PST on Sun 15 Nov 2026 (week 46) by the clock, desk only (no card, no device, no call to another box, no
post), by the lane `note3-e189` of Q180. **This note is a correction, post hoc.** README.md and note 1 give the owner's go as "about
14:50" PST; it came at 19:52:40 PST (§ 2). This note gives the corrected times and redoes note 1 § 4's window arithmetic with them (§ 3).
**No datum, measured figure, rule, verdict, forecast, band or threshold changes, and nothing is scored** (§ 4): only the go's
time and the letter's window figures built on it change, and with them note 1 § 4's no-data reading does not arise. Labels: **registered**
(E189.md and the kit as committed), **measured** (the session's committed files), **correction** (the go's times, from the record § 2
names), **post hoc** (§ 3's arithmetic, done after the data and deciding nothing). [`SHA256SUMS-note3`](SHA256SUMS-note3) pins this
note and the seven committed files of this directory whose lines it cites, so the line numbers below refer to their committed
bytes; E189.md's and KIT.md's are pinned by the registration's and the kit's lists (§ 3). The lane's desk
arithmetic ran under `/usr/bin/python3` 3.12.3 on aifoundry2.*

## 1. What note 1 § 4 said

Note 1 § 4 (lines 54-87) read the window from G two ways. Its premise is line 61: "His go came at about 14:50 PST (README line 88)".
README.md gives that time twice: in Departure 1 (line 88), the owner answered "Yes, but I'll post on Discord" "(about 14:50)"; and
Departure 6 (line 102) says "His go came at about 14:50 PST without a window time". On that premise note 1 § 4 found:
- **as run** (Departure 6, G = the booking, 20:04:17 PST): the window open throughout, and the frozen scorer's words the day's verdicts
  (lines 67-70);
- **by the letter of section 13** (G = his go, about 14:50 PST): last start about 16:20 and last end about 18:20 PST, and the first card
  command 3 h 51 min 45 s after that last start, so the window had closed before the session began; section 12 would then read no
  session, no data, and each of the four rules NOT DECIDED (lines 71-74);
- **the rule that decides**, the registration's departure rule, for the as-run reading; read by its form alone, that rule "would leave
  section 13's letter in force, and the day would be no data" (lines 76-84; the quote is lines 81-82).

Note 1 § 7's line 4 (lines 138-141) repeats both readings. Note 1's output prints the letter's figures on the same premise:
[`posthoc-note1-e189.txt`](posthoc-note1-e189.txt) line 46, and [`posthoc-note1-e189.json`](posthoc-note1-e189.json) > `s4_window` >
`literal` (`go_about` "14:50:00", `last_start_about` "16:20:00", `last_end_about` "18:20:00"). Its script takes the go's time from
README.md line 88 ([`posthoc_note1_e189.py`](posthoc_note1_e189.py) line 230).

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
- **His waiver of the post at 20:01:31 completed it.**
- "About 14:50" was the time the orchestrating session first wrote down for his answer. It was an assumption, made before that record's
  clock was read, and README.md and note 1 carried it from there.
- The question's time, "about 14:44" in Departure 1 (line 86), was right.
- The card lane took its booking of aifoundry3 at 20:04:17 (Departure 6), after both answers. The session's first card command came at
  20:11:45.076 (measured: `session/queue.json` > `t_first_ms`, 1794715905076).

## 3. The window under each reading of G (post hoc)

**Registered.** E189.md (sha256 `98b385b6...`, pinned in `SHA256SUMS-e189-registration`), section 13, lines 353-354, alone: "from his go at
G, last start G+1:30, last end G+3:30, inside one Pacific day and at least 30 minutes before the approval lapses". Section 12 (line 343)
counts "the window closed" among the gates that mean "no session (or no further pass): no data, never a failed prediction". E189 ran
alone that day: E183's last session had ended on Fri 13 Nov 2026 (Departure 6), so the alone form applies.

**Rounding.** Section 13 gives the bounds as G+1:30 and G+3:30 and names no rounding, so the exact second is the bound. The table also
gives two whole-minute forms:
- rounded up to the next whole minute, as step 1's window was written as run (Departure 6: 21:35 and 23:35, 43 s past the exact bounds);
- rounded down, as note 1 § 4 asks of later days.

**Measured** (`session/session.log` lines 1, 15, 62 and 67; `session/queue.json`):
- T0 1794715904 = 20:11:44, and the first card command at 20:11:45.076;
- pass 1 started at 20:13:50, and pass 24, the last, at 20:25:03;
- the session ended at 20:27:30 (the close at 20:27:30.247);
- the cap's end bound, 110 card-minutes after the first card command, was 22:01:45.076.

| reading | G (PST) | last start, G+1:30 (whole minute up / down) | last end, G+3:30 (up / down) | the session against it (measured) | section 12 |
|---|---|---|---|---|---|
| note 1's premise (superseded) | about 14:50:00 | 14:50:00 + 1:30:00 = 16:20:00 | 14:50:00 + 3:30:00 = 18:20:00 | the first card command 3:51:45 after the last start; the session's end 2:07:30 after the last end | closed: no data; **does not arise** |
| the letter of section 13: G = his go | 19:52:40 | 19:52:40 + 1:30:00 = 21:22:40 (21:23 / 21:22) | 19:52:40 + 3:30:00 = 23:22:40 (23:23 / 23:22) | the first card command 0:19:05 after G; pass 24's start 0:57:37 before the last start (0:56:57 before it rounded down); the session's end 2:55:10 before the last end (2:54:30) | open over the whole session |
| the letter: G = the waiver that completed his go | 20:01:31 | 20:01:31 + 1:30:00 = 21:31:31 (21:32 / 21:31) | 20:01:31 + 3:30:00 = 23:31:31 (23:32 / 23:31) | 0:10:14 after G; 1:06:28 before the last start (1:05:57); 3:04:01 before the last end (3:03:30) | open over the whole session |
| as run (Departure 6): G = the booking | 20:04:17 | 20:04:17 + 1:30:00 = 21:34:17 (21:35 as written / 21:34) | 20:04:17 + 3:30:00 = 23:34:17 (23:35 as written / 23:34) | 0:07:28 after G; 1:09:14 before the last start (1:08:57); 3:06:47 before the last end (3:06:30) | open over the whole session |

Times are h:mm:ss. The session's end is session.log's 20:27:30, as note 1 § 4 counted it. In the three readings that rest on the record:
- every last end falls inside the Pacific day 2026-11-14 (the latest, 23:34:17, 25 min 43 s before midnight; 23:35 as written, 25 min);
- the cap's end bound comes more than 1 h 20 min before every last end;
- pass 24 started hours before the kit's own rule (KIT.md lines 159-160, pinned in `SHA256SUMS-e189-kit` at sha256
  `59a4bd49...`: a pass starts at least 150 s before the window's last end) could bind.

The other two things section 13 ties the window to did not arise that day (note 1 § 4): the post was waived (Departure 4), and from
aifoundry2 there was no approval to lapse (Departure 3).

## 4. What changes, and what does not

- **The letter of section 13 now gives the day the as-run reading gives.** With G = his go (19:52:40, or 20:01:31 when the waiver
  completed it), the window was open from the first card command to the close, in every form of § 3. Both of note 1 § 4's readings
  therefore give one day: every pass counts by section 8.2, and the frozen scorer's words are the day's verdicts, **with no competing
  reading: E189-S1 FAIL, E189-S1T PASS, E189-S2 FAIL, E189-S2T FAIL** (note 2, [`scores-e189.json`](scores-e189.json)).
- **The no-data reading does not arise.** Note 1 § 4's letter reading (the window closed by about 16:20 and 18:20, section 12's no data,
  each rule NOT DECIDED) rested on the wrong time. The departure rule read by its form alone (note 1 lines 81-82) leaves section 13's
  letter in force, and the letter now gives the same day as the as-run reading. So the rule has nothing left to decide about the window.
- **Departure 6 stays, as a departure of form that bore on nothing.** The round read G as the booking, 20:04:17: 11 min 37 s after his
  go and 2 min 46 s after the waiver, so its exact bounds fell that much later than the letter's, and the bounds step 1 wrote (21:35
  and 23:35) 43 s later still. The session ended 2 h 54 min 30 s before the earliest of the letter's last ends (23:22, rounded down).
  Departure 6 touches no datum, frozen forecast, band, threshold or rule of section 8. Note 1 § 5 (the departures, set before the
  session and published after the collection) stands as written.
- **Unchanged:** every datum, measured figure and flag of README.md (its go time, lines 88 and 102, is read as below); note 1 §§ 1-3,
  5 and 6 (S1T's margin) and the rest of its output, § 4's as-run figures (`s4_window` > `as_run`) included; note 2 and its files. The
  scorer, the reducer and the kit read none of this note's files.
- **Read with this note** (the committed bytes stay; the corrected readings follow):
  - README.md line 88, "(about 14:50)": his answer arrived at 19:52:40 PST.
  - README.md line 102, "His go came at about 14:50 PST without a window time": his go came at 19:52:40 PST, and his waiver of the post
    at 20:01:31 PST, without a window time.
  - Note 1 line 61, "His go came at about 14:50 PST (README line 88)": at 19:52:40 PST (§ 2).
  - Note 1 lines 71-74, the letter's bullet: with G = 19:52:40 PST, last start 21:22:40 and last end 23:22:40 PST. The window was open
    over the whole session, every pass counts, and the four rules read the frozen scorer's words.
  - Note 1 lines 81-82 and § 7's line 4 (lines 138-141): both readings give the day the frozen scorer's words. There is no no-data
    reading.
  - Note 1's output (`posthoc-note1-e189.txt` line 46; `posthoc-note1-e189.json` > `s4_window` > `literal`): the letter's figures on
    the old premise. § 3's table gives them on the corrected one.

## 5. Lines for the records

1. **His go, corrected** (correction): the card-time question was asked at 14:44:01 PST on Sat 14 Nov 2026.
   His answer, "Yes, but I'll post on Discord", arrived at 19:52:40. The post question was asked at 19:54:39,
   and his answer, "it's fine not to announce, the cards are unused", arrived at 20:01:31. The source is the
   orchestrating session's record of the owner's answers. "About 14:50" in README.md (lines 88 and 102) and
   note 1 (lines 61, 71 and 139) was an assumption written before that record was read.
2. **The window** (post hoc): by the letter of section 13, G = 19:52:40 (or 20:01:31) gives last start 21:22:40 (21:31:31) and last end
   23:22:40 (23:31:31). As run, G = 20:04:17 gives 21:34:17 and 23:34:17, written 21:35 and 23:35. The session, 20:11:44-20:27:30, lies
   inside every one.
3. **No verdict changes:** note 1 § 4's no-data reading does not arise. The verdicts stand with no competing reading:
   E189-S1 FAIL, E189-S1T PASS, E189-S2 FAIL, E189-S2T FAIL.

## 6. Checks before the commit

- In a copy of this directory with the two new files: `SHA256SUMS` 228 of 228, `SHA256SUMS-note1` 6 of 6, `SHA256SUMS-note2` 3 of 3
  and `SHA256SUMS-note3` 8 of 8 entries OK; 241 files, every one in a list but `SHA256SUMS-note1`, `SHA256SUMS-note2` and
  `SHA256SUMS-note3` themselves.
- Every time and interval in §§ 2-3 was re-derived from the committed files named there and the record's four times, by the lane's
  desk arithmetic and again by its verifier's (`verify-n3e189`, after its fixes), and found equal to the text here; every line this
  note cites holds the words it is cited for. The arithmetic is written out in § 3, so it can be redone by hand.
- The desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the round's folders forbidden) read the two new files with 0 hits,
  and a login check found no home path, no login and no holder line in them or in this commit's subject and body.
- The public-text scan (the lab's `sanitize_extracts.py`, its fixed list and the box's local table, and the round's lists of private,
  vendor, access and mechanism words) found nothing in the two new files or in this commit's subject and body but the owner's quoted
  answer of 19:52:40 itself, which names the lab's chat service, a word on the round's private list, as README.md line 88 does
  (reviewed and kept: they are his words).

## What does not change

Every datum, measured figure, verdict, stop and as-run gate reading of `README.md`, note 1, note 2 and their files stands. This note
corrects one time, the owner's go, and the arithmetic built on it (§ 4 lists the lines that read differently with it). This lane
reached no box, opened no device and changed no committed file.

SPDX-License-Identifier: Apache-2.0
