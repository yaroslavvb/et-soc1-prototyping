# E194's card-lane brief, dated note 1: the reboot gate answered by E194.md's dated amendment A1 (E194's own firmware gate, fwread-e194's read of record); steps 2, 4 and 9 in their v2 forms; the window from the card lane's booking, on that booking's day; E191's third-session folders in step 2 v2's never-run check (Q187, revised before its land in Q191; before any E194 datum)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q187, lane `amend-e194`; revised before its land the same evening, from about
22:10 PST, in Q191 by the lane `fix-amend194` after its verifier's findings: the window's day, the go for a later day, the never-run
reading and the labels), beside [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md), which stays as committed; written with
[E194.md's dated amendment A1](E194.md.dated-amendment-A1.md) and [the kit's dated note 1](KIT.md.dated-note-1.md), before any E194 datum.
No card was claimed, no device command was sent, nothing was posted. It changes no forecast, band, rule, threshold, K, order, plan, cap or
registered stop line. Where this note and the brief differ, this note governs E194's card day.*

## 1. What changes in the brief's section 1 (what the go must carry)

- **THE REBOOT GATE is answered (A1-3), no longer closed.** aifoundry2 booted 2026-11-13 16:53:28 PST; fwread-e194's firmware read of
  aifoundry2 card 0 (`15cb0fcb`, 2026-11-15 15:22:02 PST) reads EQUAL to E69's read of record in all seven fields and is the card's firmware
  read of record for E194 from A1 on. **E194's own gate** (`rb/fwgate_e194.sh`) passes only when that record is there as committed and
  reads EQUAL (on the desk), and the box booted strictly before 2026-11-15 15:22:02 PST (on the box). **If the box reboots after that
  second, the gate closes again: no session, report it** (a new read of record and a dated note are another lane's).
- **The window (A1-4): G = the moment this card lane holds the aifoundry2 booking** (step B prints BOOKED; the booking's owner file holds the
  time), **on that booking's own Pacific day: Sun 15 Nov 2026 or a later day** (the round moved every card day to Mon 16 Nov 2026 or later
  after its stop at about 18:05 PST Sun). Last start G+1:30, last end G+3:30, each rounded UP to the whole minute, inside that Pacific day:
  on any such day **G at 20:29:00 PST or earlier that day**, else no E194 session that day (release the booking; on a later day a new
  booking is that day's G). Step 1 writes it, on that day: `rb/s02_window_e194.sh <YYYY-MM-DD> <last start> <last end>`. The gate's boot
  condition is the same on every day: a boot at or after 2026-11-15 15:22:02 PST closes the gate.
- **The go**, recorded by the lane: his words of 15:05:27 PST ("yes, feel free to run it, feel free to read firmware as well") with his
  standing words of Sun 15 Nov 2026 (10:05:42 and 10:22:36 PST); for a day after it, his words of 17:21:16 PST, "Try again" (received at
  or before 21:28:59 PST) and his words received at or before 21:51:09 PST, with the report of his words of 19:34:12 PST beside them, each
  verbatim in A1-0 (the dashboard page's link elided); his ruling of 15:07:01 PST on the firmware-revisions query (A1-0). On a later day
  the same words are the go unless he says otherwise. The registered items unchanged: aifoundry2 card 0 under its governor as found, reads
  only, about 95 card-minutes (cap 110); **the package counter not read**; **the post: none** (his standing waiver, 10:22:36 PST, in his
  words).
- **The never-run check (A1-8):** step 2 v2 also leaves out every directory at HEAD named exactly
  `docs/reports/data/<YYYY-MM-DD>-e191-blind-day-aifoundry1-c1-s3` (E191's third session, of any day), each named in the check's line and in
  the step's last line. Any other folder that names the instance, or a third-session folder not at HEAD, makes it refuse (16): no box step
  that day; report it. **Once such a folder is at HEAD, the kit's pinned quick set (`desk/checks_e194.sh`) reads its never-run case NAMED
  BEFORE**: readiness reads that case under A1-8 (answered by step 2 v2's command reading NEVER RAN); its other cases stand.
- **The anchor lines** the go names: the kit's (`q183-anchor-lines-e194.txt`'s, from the kit's land) and the amendment's (its LAND.md: the
  amendment commit an ancestor of HEAD; `SHA256SUMS-e194-amendment-A1` at its stated sha256, every entry OK; step 2 v2,
  `rb/s03_desk_e194_v2.sh`, outside that list, at its stated sha256). **The only commit of any ref that names a `docs/reports/data/*e194*`
  path is `15cb0fcb`** (the firmware read: expected, not E194 data; the kit's anchor line 7 reads it as 1 line). Any other such commit or
  path: no box step that day.

## 2. The rows of the brief's section 2 that change (everything else is the brief's)

| # | the step | what to do with its exit |
|---|---|---|
| 2 | **`rb/s03_desk_e194_v2.sh`** with `RB_GITLOCK` set, under slot.sh, THE LOAD RULE first; never inside the lab-git lock | as the brief's row 2; its last line names the amendment's list and the firmware read's list at their pins, "E191's third-session folders at HEAD (0)" (or their count and names, each left out of the never-run check: A1-8), "the only E194 data in any ref the firmware read of record (15cb0fcbfb11)" and FWGATE-E194 RECORD EQUAL |
| 4 | the look, **`rb/s05_look_e194_v2.sh`** (right after step Q raises the flag) | FREE (0), with the line "identity: the host booted 2026-11-13 16:53:28, before E194's firmware read of record of 2026-11-15 15:22:02 PST (EQUAL to E69's; E194.md A1): ok"; HELD (17): `--wait`, at most 30 minutes in all; **16: the gate says stop** (the record not EQUAL as committed, read on the desk before any box call, or a boot at or after the read): no launch, report the gate's words |
| 9 | **`rb/s11_session_e194_v2.sh FULL`** (never `--rapl-allowed`) | 0 launched (its identity line, rest line and P2 count in the runbook log); 10 refused (as the brief's row 9); **16: the gate says stop** (the record, read on the desk before any box call, or IDENTITY-STOP on the box: a boot at or after the read): nothing launched, report it |

The brief's row "9-" (step 10's session reading against step 9's launch line) reads the same name: step 9 v2 launches
`setsid nohup bash tools/claims-v3/e194/session_e194.sh`, as v1 did. Steps 1, 3, 5-8, 10-13, Q, Q' and E are the brief's, unchanged.

## 3. What changes in the brief's section 3 (Never)

- "Never a launch past the reboot gate without the owner's dated ruling" is met by A1 **only through the v2 look and launch**: never the v1
  look or launch on E194's day (they still read k6's rule and refuse this boot), never a launch while E194's gate refuses.
- **The card lane sends no firmware query:** the session's commands are E194.md 11's, unchanged (A1-6), and the read of record is
  fwread-e194's. Everything else in section 3 stands.

## Labels

Every figure here is **registered** (E194.md and its amendment A1) or a **desk check of code** (the kit's dated note 1), or a **desk read**
(the boot time, the round's records of the landed commits). **Nothing new is measured here; the read's time, rc and seven values are
measured** (as committed in `15cb0fcb`). The owner's words are quoted in A1-0 with their times; the report of his words at 19:34:12 PST is
labelled as a report. Nothing here is blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
