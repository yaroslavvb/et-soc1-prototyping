# The card lane's brief for E186, dated note 1: steps 2, 5 and 11 run as v2, step 5 is never run beside a session of ours, the card-minutes at measured times, and the words for the pairing check (Q158; before any datum)

*Sun 8 Nov 2026 (week 45), PST, on the Intel, desk only (Q158, lane `fix-e186`). It sits beside [KIT-BRIEF.md](KIT-BRIEF.md), which stays
as committed (`523002be`), and is read with it, before the runbook, on the day the owner's go names. It carries out the kit's dated note 1
([KIT.md.dated-note-1.md](KIT.md.dated-note-1.md)) and the registration's dated amendment A1
([E186.md.dated-amendment-A1.md](E186.md.dated-amendment-A1.md), `17cf100f`) for the card lane. **No rule, forecast, threshold, statistic,
power figure, plan, cap or stop changes here.** Where a line below and the brief differ, this note governs.*

## What changes in the brief

1. **Steps 2, 5 and 11 run as v2:** step 2 is `rb/s03_desk_e186_v2.sh` (it runs step 2 v1 first, then the history check v2 and the session
   scale's six lists at their pins), step 5 is `rb/s07_a3_sync_e186_v2.sh`, step 11 is `rb/s22_collect_e186_v2.sh`. Their v1 files are
   never run by hand that day. Every other step is as the brief says.
2. **Section 2, "Anything but 0 from step 2 is no box step that day,"** holds for step 2 v2: a stop from step 2 v1 inside it (v2 exits
   with v1's code), or v2's own `the desk check v2 failed: ...` (16, naming the list off its pin or `history-v2`), is no box step that day;
   the brief's one exception (a pull the upstream did not answer) is v1's and stands.
3. **Section 3, item 1 and item 4: never beside another session of ours.** Steps **5**, 6, 8 and 9 refuse it by code (step 5 v2 reads the
   box first, k6's `ours_live` and `jobs_live`, and refuses with 10 before anything is synced), and step 5 is also never run while a
   runbook job runs on the box (step 6's build among them). A 10 from step 5 v2 naming a session of ours: wait for it to end and be
   collected; naming a runbook job: read that job with its own step first.
4. **Section 4, the caps line.** It says *FULL about 93 card-minutes (cap 100)*. Read: **FULL about 93 card-minutes at E182's registered
   piece times; 89-99 at E182's measured block times** (about 99 at the mean times; at the longest the queue stops before A23-A15, and
   E186-GA then reads A15-A7 alone; E186.md section 7, KIT.md section 2); **cap 100**. PASSES about 28 (cap 40). The post's `for 2 h` covers
   either.
5. **Section 6, step 11.** Step 11 v2 adds, after COPY-BACK EXACT and before any scoring, **the history check v2** (a committed or
   uncommitted change since step 2 to E186's, M12's, E182's or the session scale's route's files stops it, 16: the raw copy stays, nothing
   is scored, a dated note first), and its collector runs **the pairing check** over every train block. A train not paired reads NOT
   SCORED: a reading, never a stop; the step's last line and `<out>/pairing-e186.status.txt` name it, and the data README records it.

## The words the records use (adds to section 7)

- **E186-PAIR** is a gate on the records (A1-2), never a measurement: PASS, or FAIL naming the trains; a train it fails reads "NOT SCORED
  (the pairing check)".
- **s not read** is A1-1's registered branch: the four ladder trains' SIZE and WHICH words, E186-GB and E186-GA NOT SCORED, and E186-M over
  S23, Q63-sign, Q63-swap, Q3-sign and Q3-swap (its power 0.91-0.99 in every case); in the fallback, E186-LV NOT SCORED (A1-1b).
- The merged list's second source is **the second candidate list** (A1-3).

*Labels: every plan, cap, stop, clause and verdict word above is **registered** (E186.md with A1, its note M1, the kit with its note 1, E182's
kit and brief as E186's kit takes them); nothing here is blind, held out or measured.*

SPDX-License-Identifier: Apache-2.0
