# E210's freeze lines from the model session's sealed forecasts (a dated note outside E210's pinned folder)

*Registered Tue 17 Nov 2026 (week 47), PST, at the desk on aifoundry2, by Q210s's lane `seal-e210`, before E210's first card command and
before any E210 datum (aifoundry3 card 0): when this note was written (10:14:52 PST), GitHub main read `157d1b83` by ls-remote, and no
`docs/reports/data/*e210*` path and no `docs/reports/gate-stops/*e210*` record was in any ref (every GitHub head fetched and scanned, and the
desk's lab clone); the commit that adds this note was made only after the same scan read none again. Its source is the round's record of
sealed E210 forecasts (the orchestrator's copy of each sha256 the model session posted, with its post id and time; last updated 10:07 PST Tue
17 Nov 2026) and the post's words as the orchestrator relayed them. Nothing here was measured; no card was touched.*

## Freeze line 1 (E210's 22 cases)

`E210 sealed forecast (the model session's, from its frozen model v3 with its v2 beside as a reference, for E210's 22 cases on aifoundry3 card 0), posted as #11.4.1.1.1.1.1.1 in the owner's private coordination thread at 10:05:27 PST Tue 17 Nov 2026: sha256 81a84eb62936aa572f2f42f33dcccd2414ecae64300381bbdada63efa9c77ae3`

**The post** (#11.4.1.1.1.1.1.1, 10:05:27 PST Tue 17 Nov 2026), its words after the opening tag, verbatim:

> **Claude says:** The NDA box's forecast of E210's 22 cases from its frozen v3 (v2 beside as reference) is sealed, made at the lab repo's f5c53145 before any E210 datum: sha256 81a84eb62936aa572f2f42f33dcccd2414ecae64300381bbdada63efa9c77ae3.

"The NDA box" is the model session's name for its own box (E208.md section 0); the post names no foundry, process, library, cell or vendor.
"Its frozen v3 (v2 beside as reference)" names the model session's own matmul models, not the lab's MM1: its sealed forecasts of E206
(`tools/claims-v3/sealed-e206/`) name a v2 and a v3, and of E207 (`tools/claims-v3/sealed-e207/`) a v3. "Made at the lab repo's f5c53145"
names the lab's GitHub main when the model session read E210's registration (`7b59f719`, with amendment A1) and kit (`8f420314`): `f5c53145`
is E207's scorer outputs, the second commit after E210's kit (the first, `7726e127`, is E212's session a1c1-S4 data), and neither changes
anything under `tools/claims-v3/e210/`. The model session announced the seal in the same thread (#11.4.1.1.1.1, 09:14:55 PST) and asked that
E210's booking wait for it; the round's answer (#11.4.1.1.1.1.1, 09:16:19 PST) held E210's booking for a seal posted by 11:30 PST, to be
registered by the lab before E210's first card command. This note is that registration.

- **What it freezes: E210's 22 cases** (E210.md section 3; `tools/claims-v3/e210/points-e210.csv`, the case list E210.md section 0 names for
  sealed forecasts, and `points-e210.json`): nine fp32 operand patterns never run in a GEMM, with zeros, ones and sparse50 as controls and
  random as the reference, at two shapes of E136's rgm136 (S1 `gemmL1x1x1`, S2 `gemmL1x1x4`, fp32), as 171 runs in 54 chained A B B A
  blocks on aifoundry3 card 0 at its pinned 600 MHz. It was posted before E210's first card command: the round has held aifoundry3's booking
  for this seal since 09:45:09 PST, 20 minutes before the post, and E210's card lane takes no box step without that booking. It was posted
  before any E210 datum: none is in any ref as this note is written, nor when it is committed (above). It is a freeze line of all 22 cases.
- **What it holds, as the post names it:** a forecast of E210's 22 cases from the model session's frozen model v3, with its v2 beside as a
  reference. The post does not name its quantities; no number of it is known to the lab.
- **It stays sealed:** no number of it is in the lab; no lab file reads, scores or reports against it; nothing E210 registers (the cases, the
  five routes' frozen forecasts in `tools/claims-v3/e210/forecast-e210.json`, the rules, the order, the stops, the card time) depends on it.
  The model session scores it privately against the data E210 publishes.

## Why this note, and why here

- E210.md section 0: "A sealed sha256 posted there before E210's first card command is a freeze line of E210: it is registered in a dated
  note outside this pinned folder (`tools/claims-v3/sealed-e210/e210-freeze-lines.md`, E198's and E206's precedent), committed before that
  first card command; its sha256 only is quoted (no number of it in the lab; no lab rule scores it). A sha256 posted after E210's first card
  command is not a blind freeze and is recorded as such."
- KIT.md section 4 item 20: "a sealed sha256 the model session posts for E210's cases before the first card command is registered in
  `tools/claims-v3/sealed-e210/e210-freeze-lines.md` before that command; the card lane checks the round's record of them at its step 0;
  step 2 reports any such note (REPORTED). Its numbers never enter the lab." CARD-LANE-BRIEF.md section 1: while the round's record lists a
  sealed sha256 for E210 that this file does not register, E210's card lane does not book.
- This file is outside `tools/claims-v3/e210/`: E210's registration and kit stay as committed (its history check reads additions under that
  folder only, and lists this note's folder among the paths that must be clean), and no rule, forecast, threshold, order, card time, cap or
  stop changes.

## Labels

A desk record of a posted hash (its post id, time and words from the round's record). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
