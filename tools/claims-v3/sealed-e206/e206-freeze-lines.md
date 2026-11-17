# E206's freeze lines from the model session's sealed forecasts (a dated note outside E206's pinned folder)

*Registered Mon 16 Nov 2026 (week 47), PST, at the desk on aifoundry2, by Q201's lane `ready-e206b`, before any datum of E206's arm B
(aifoundry1 card 1): when this note was committed, no `docs/reports/data/*e206*-aifoundry1-c1*` path and no E206 gate-stop record of
aifoundry1 was in any ref. Its source is the round's record of sealed E206 forecasts: the orchestrator's copy of each sha256 the model session
posted, with its post id and time (last updated 19:08:39 PST Mon 16 Nov 2026). Nothing here was measured; no card was touched.*

## Freeze line 1 (arm B only)

`E206 sealed forecast (the model session's, from its frozen matmul model, for all 119 points on arm A and arm B's 113 points at 600 MHz), posted as #2.6.1.1.1.2 in the owner's private coordination thread at 19:07:38 PST Mon 16 Nov 2026: sha256 bc750c73d600f2cc389a1c9207be7bd37579324853df697dbdb5cceecea12977; its printed table: sha256 b16a83e28f7f72ce04bc0d25e49d4b196feeb470ef4ce33e7f4c6f925c60702d`

- **The arm it freezes: arm B alone.** It was posted 41 minutes after arm A's data commit (`d7e4f35e`, 18:26:14 PST Mon 16 Nov 2026), so
  it is **not a freeze line of arm A**: the round's record reads it for arm A as REPORTED, after the data, and the model session agreed in
  the same thread (19:56:19 PST) that arm A counts as post-data for its forecast. Arm B had not run when it was posted, and has no datum
  in any ref as this note is committed: it is a freeze line of arm B's 113 points.
- **What it holds, as the post names it** (no number of it is known to the lab): cycles, seconds, board and rest watts and joules both
  ways for each point, with transistor switches and electrons reported beside.
- **It stays sealed:** no number of it is in the lab; no lab file reads, scores or reports against it; nothing E206 registers (the points,
  F1 and F2 in `tools/claims-v3/e206/forecast-e206.json`, the bands, the rules, the order, the stops, the card time) depends on it. The model
  session scores it privately against the data E206 publishes.

## Why this note, and why here

- E206.md section 0: "A sealed sha256 posted there before E206's data commit is a freeze line of E206: it is registered in a dated note
  outside this pinned folder (`tools/claims-v3/sealed-e206/e206-freeze-lines.md`, E198's precedent), committed before the arm it covers runs;
  it stays sealed (no number of it in the lab, no lab rule scores it)."
- KIT.md section 4 item 21: "a sealed sha256 the model session posts for E206's points before an arm's data commit is registered in
  `tools/claims-v3/sealed-e206/e206-freeze-lines.md` before that arm runs; the card lane checks the round's record of them at its step 0."
  CARD-LANE-BRIEF.md section 1: while the round's record lists a sealed sha256 for E206 that this file does not register, arm B's card lane
  does not book.
- This file is outside `tools/claims-v3/e206/`: E206's registration and kit stay as committed (its history check reads additions under
  that folder only), and no rule, forecast, band, threshold, order, card time, cap or stop changes.

## Labels

A desk record of posted hashes (their post ids and times from the round's record). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
