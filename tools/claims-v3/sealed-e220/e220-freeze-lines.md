# E220's freeze lines from the model session's sealed forecasts (a dated note outside E220's pinned folder)

*Registered Fri 20 Nov 2026 (week 47), PST, at the desk on aifoundry2, by Q220s's lane `seal-e220`, before either arm's first card command
and before any E220 datum (arm A on aifoundry1 card 1 at 600 MHz, arm B on aifoundry2 card 0 under its governor): when this note was
written (14:39:09 PST), GitHub main read `2f0ab9cd` by ls-remote, and no path under `docs/reports/data` holding `e220` and no
`docs/reports/gate-stops/*e220*` record was in any ref (every GitHub head fetched and scanned, and the desk's lab clone; read by E220's own
datum readings, the folder-level globs `docs/reports/data/*-e220-*-aifoundry1-c1/**` that arm A's step 0 (its line D0) and step 2 use and
`docs/reports/data/*-e220-blind-matmul-aifoundry2*/**` that arm B's step 2 uses (its check 11), by the same glob over any folder named
`*e220*`, and by the pathspec `docs/reports/data/*e220*`, which takes a file as well as a folder); the commit that adds this note was made
only after the same scan read none again. Its source is the post's words and sha256 as the round's orchestrator relayed them; the round's
record of sealed E220 forecasts (`W/out/orch/sealed-e220.txt`) is written only after this note is on GitHub main, because each card lane's
step 0 reads both (E220.md section 0). Nothing here was measured; no card was touched.*

## Freeze line 1 (all 158 of E220's points on both arms)

`E220 sealed forecast (the model session's, from its frozen matmul model v3.6 with its v3.5 and v3.4 beside, for all 158 of E220's points on both arms: arm A's 84 on aifoundry1 card 1 at 600 MHz, arm B's 74 on aifoundry2 card 0 under its governor), posted as #2.8.5.1.1.1 in the owner's private coordination thread at 13:26:12 PST Fri 20 Nov 2026: sha256 f2cf18f0ea1d3e590a7cecdd663ba3f2314a0bcb11e5e23e7aeb3b8e91dd5b82`

This is the first sealed forecast of the model session's registered for E220. E220's own forecasts (MM1-v3.2 registered; MM1-v3.1, MM1-v3
and MM1-v2 beside it) are frozen by E220's registration (`6901854c`, E220.md section 0), each made by its model's landed predictor unchanged
(MM1-v3.2's land `4e386f75` among them); the three MM1-v3.3 candidates frozen beside them (`tools/matmul/mm1/v3.3-cands/`) are REPORTED only. This note changes none
of them.

**The post** (#2.8.5.1.1.1, 13:26:12 PST Fri 20 Nov 2026), its words after the opening tag, verbatim:

> **Claude says:** Thanks for holding: our forecast of all 158 of E220's points (arm A 84, arm B 74) from the frozen v3.6, with v3.5 and v3.4 beside, is sealed at 13:26:05 PST before any E220 datum, made at 2f0ab9cdc: sha256 f2cf18f0ea1d3e590a7cecdd663ba3f2314a0bcb11e5e23e7aeb3b8e91dd5b82.

"Our forecast" is the model session's: the session on its own box, which it calls "the NDA box" (E208.md section 0, as E211's note says;
this post does not use that name). The post names no foundry, process, library, cell or vendor. "The frozen v3.6, with v3.5 and v3.4
beside" names the model session's own matmul models, not the lab's MM1 (MM1-v3.2, `tools/matmul/mm1/v3.2/`, whose frozen forecasts E220
scores, with MM1-v3.1's, MM1-v3's and MM1-v2's beside them). Its v3.6 is the model of the sealed forecast of E221, the model session's
sixth matmul sweep ([`../e221/E221.md`](../e221/E221.md): "a blind test of the frozen v3.6 (frozen Fri 03:18 PST)"); its v3.5 is the model
of E215's freeze line 1 ([`../sealed-e215/e215-freeze-lines.md`](../sealed-e215/e215-freeze-lines.md)), of E216's
([`../sealed-e216/e216-freeze-lines.md`](../sealed-e216/e216-freeze-lines.md)) and of E218's
([`../sealed-e218/e218-freeze-lines.md`](../sealed-e218/e218-freeze-lines.md)); its v3.4 is the model of E212's fourth freeze line
([`../sealed-e212/e212-freeze-lines-3.md`](../sealed-e212/e212-freeze-lines-3.md)) and of E214's second
([`../sealed-e214/e214-freeze-lines.md`](../sealed-e214/e214-freeze-lines.md)).

"Made at 2f0ab9cdc" names the lab commit the model session made the forecast at: `2f0ab9cd` is E220's kit, committed 12:32:22 PST Fri 20
Nov 2026 on E220's registration `6901854c` (committed 12:31:40 PST, its push the freeze line of E220's points and forecasts), which
descends from MM1-v3.2's land `4e386f75` (committed 19:50:04 PST Thu 19 Nov 2026). The kit only adds the run kit's 123 files under
`tools/claims-v3/e220/` and changes no registered file. GitHub main still read `2f0ab9cd` when this note was written. That it was sealed before any E220 datum is borne out by the scans
above (none existed in any ref); its seal time (13:26:05 PST) is the model session's own statement, which nothing here depends on. The
model session asked in the same thread (#2.8.5.1, 12:38:33 PST) that E220's first card command wait for its sealed forecast, its sha256 by
about 13:50 PST; the round agreed (#2.8.5.1.1, 12:40:09 PST), with a bound of 14:30 PST. This note is that registration. It registers this
one seal.

- **What it freezes: all 158 of E220's points on both arms** (E220.md section 3; `tools/claims-v3/e220/points-e220.json`), each registered
  as never run on its arm's card (E220.md section 4): arm A, 84 points on aifoundry1 card 1 at 600 MHz (family X 52, L3 8, Y2 10, G2 7, G2t 7), and arm B, 74 points on aifoundry2
  card 0 under its governor (X 42, L3 8, Y2 10, G2 7, G2t 7). Family X is E218's points as cross-card twins, L3 the L3 edges, Y2 the
  equal-count layout pairs, and G2 the gemmLnc term at small excess with its cooperative twins G2t. It was posted before either arm's first
  card command: each arm's card lane (card-e220a, card-e220b) starts only after E220's readiness check returns, takes no box step without
  its booking, and never books over an orchestrator's hold (CARD-LANE-BRIEF.md section 3, row B: "an `orch-hold-*` line: wait, never book
  over it"; section 4, row B: a busy booking is waited for). E220's readiness check wrote its result at 14:38:18 PST, and at 14:38:21 PST the round took both boxes' bookings (aifoundry1 and aifoundry2) as `orch-hold-e220-seal` (its hold for this seal), before either card lane could book: when the post came, no lane had booked either box (the readiness check had not yet written its result), and as this note is written both boxes are still held by that hold. It was posted before any E220 datum: none is in any ref as this note is written, nor when it is committed
  (above). It is a freeze line of both arms' points.
- **What it holds, as the post names it:** a forecast of all 158 of E220's points (arm A 84, arm B 74) from the model session's frozen
  matmul model v3.6, with its v3.5 and v3.4 beside. The post does not name its quantities; no number of it is known to the lab.
- **It stays sealed:** no number of it is in the lab; no lab file reads, scores or reports against it; nothing E220 registers (the points;
  the forecasts of MM1-v3.2, MM1-v3.1, MM1-v3 and MM1-v2 frozen by the registration `6901854c`; the bands, the rules, the head-to-heads,
  the cross-card rule, the order, the stops, the card time) depends on it, and neither do the MM1-v3.3 candidates REPORTED beside them. The
  model session scores it privately against the data E220 publishes.

## Why this note, and why here

- E220.md section 0: "A sealed sha256 the model session posts on the owner's coordination thread before an arm's first card command is a
  freeze line of that arm: the orchestrator writes it to its record `W/out/orch/sealed-e220.txt`, and it is registered in a dated note
  outside this pinned folder, `tools/claims-v3/sealed-e220/e220-freeze-lines.md` (E207's, E210's, E211's, E213's, E215's, E216's and
  E218's form), committed before that arm's card lane books. **Each card lane's step 0 reads both the record and the note, so a seal must be
  registered before the card lane books** (the E206 lesson). A seal posted after one has been registered goes in a NEW note
  (`e220-freeze-lines-2.md`) with its record line as a COMMENT. It stays sealed: no number of it enters the lab, no lab rule scores it."
- KIT.md, the round's lessons, the row "THE SEALED-FORECAST CHECK AT STEP 0": "arm A `rb/s00_step0_e220a.sh` S1; arm B
  `rb/s00_sealed_e220b.sh` (and step 2's check 10)", desk-tested by arm A's runbook test (its case S0) and arm B's (its cases P10-P12b and
  Z1-Z4).
- CARD-LANE-BRIEF.md section 1: "Every seal the model session posts for E220 is registered in
  `tools/claims-v3/sealed-e220/e220-freeze-lines.md` before either arm books (a later one in `e220-freeze-lines-2.md`, its record line a
  COMMENT): each arm's step 0 reads both (arm A `rb/s00_step0_e220a.sh` S1, arm B `rb/s00_sealed_e220b.sh`)."
- The checks: arm A's step 0 line S1, in `tools/claims-v3/e220/rb/s00_step0_e220a.sh` (every sealed sha256 on a line of the record that is
  not a comment and reads `E220 <sha256> ...` must appear in this note at HEAD; any other non-blank line that is not a comment is
  unreadable and refused); arm B's step 0 S1, `tools/claims-v3/e220/rb/s00_sealed_e220b.sh` (every 64-hex sha256 on a line of the record that is not a
  comment must appear in this note at HEAD; a record that exists but cannot be read is refused), which arm B's step 2,
  `tools/claims-v3/e220/rb/s03_desk_e220b.sh`, calls as its check 10, its check 9 printing every sha256 registered in
  `tools/claims-v3/sealed-e220/e220-freeze-lines*.md`; the readiness check's step-0 anchor read carries the second for both arms as its line
  S1g. Arm A's step 2, `tools/claims-v3/e220/rb/s03_desk_e220a.sh`, does not read the record: it lists this note's folder among E220's paths
  that must read clean before and after its checks, includes the folder in its read that nothing was written while it ran, and reports this
  note's commits.
- This file is outside `tools/claims-v3/e220/`, and nothing under that folder or `tools/claims-v3/e220-notes/` changes: E220's registration,
  its dated note 1 and its kit stay as committed (both arms' history checks,
  `tools/claims-v3/e220/rb/check_history_e220a.py` and `tools/claims-v3/e220/rb/check_history_e220b.py`, admit only additions under that
  folder since the registration and list this note's folder among the run paths that must be clean), and no rule, forecast, band,
  threshold, order, card time, cap or stop changes.

## Labels

A desk record of a posted hash (its post id, time and words as the round's orchestrator relayed them). Nothing here is measured, blind, held
out or post hoc.

SPDX-License-Identifier: Apache-2.0
