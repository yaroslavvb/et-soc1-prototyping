# Dated note 2 beside 09-method.md (Fri 6 Nov 2026, week 45): note 1's section 3 reworded, aifoundry2's SP pass, and what E64's 1.3 s leaves unexplained

*This note sits beside [`09-method.md`](09-method.md) and its [dated note 1](09-method.md.dated-note-1.md) (`43f8436a`), and
edits neither. It gives public facts and the lab's committed measurements only. It corrects note 1's section 3, as the dip lane's
verifier found it; note 1's sections 1 and 2 stand. Its time is its commit's. Desk only: no card was touched.*

## Builds on

- **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 03:50 PST. Public rows read: P01, P03, L11, L22, H24, H28. The
  ids are opaque pointers into a private inventory.
- **Used:** `docs/findings/14-card-behaviour.md` line 794 (E41's pass under the 10 Hz sampler); `docs/findings/05-claims.md`
  lines 770 and 773 (E58); E64's README line 103 and `tools/claims-v3/hpl/surface_hpl.py` lines 152-168 (the pass E64's model
  fitted); `device-bootloaders/src/ServiceProcessorBL2/rtos_task/dm_task.c` lines 222 and 267 at `aifoundry-org/et-platform`
  `836a4ab60`; the dip study's dated note 1, result 5
  ([`2026-11-06-q145b-dips-posthoc/README.md.dated-note-1.md`](../reports/data/2026-11-06-q145b-dips-posthoc/README.md.dated-note-1.md),
  `460ac80e`), which reads the pass on E173-E175's committed telemetry.
- **Not used:** the card schematic's sense network (R406), still owed (note 1).
- **Tiers:** public only.

## What note 1's section 3 said, and what does not hold

Note 1 said: "E64's 1.3 s is about E58's 1.05-1.10 s plus one pass of 0.24-0.26 s (1.29-1.36 s). It is a filter close to the
source's, seen one pass late, rather than a slower filter." Three parts of that do not hold:

1. **0.24-0.26 s is aifoundry3's pass, not aifoundry2's.** E58 read 0.255 s on aifoundry3 under the 10 Hz sampler (05-claims.md
   line 773), and findings 14 gives a new `board_w` every 263 ms there. On aifoundry2 under the same sampler:
   - findings 14 gives a new `board_w` every **156 ms** (E41, line 794);
   - the committed telemetry gives **164.9 ms** on E173 and **166.8 ms** on E175, medians over runs of the mean time between
     `board_w` changes at 800 MHz (p10-p90 156-175 and 160-184 ms).

   E64's 0.24 s is the pass its model fitted: `surface_hpl.py` searches a time constant of 0.4-3.0 s against a pass of 0.13,
   0.16, 0.20 or 0.24 s and keeps the lowest clock error (lines 152-168). 0.24 s is the largest pass it tried, so the fit sat at
   the edge of its grid. It is not a measured pass.
2. **"Seen one pass late" is E58's finding for the rails as the host reads them.** E58 read `board_avg_w` itself as current, not a
   pass late (05-claims.md line 770).
3. **The governor reads the average in the pass that refreshes it.** `dm_task.c` refreshes the SP's copy of the PMIC's power
   (`update_module_soc_power`, line 222) and checks the power conditions (`check_power_throttle_conditions`, line 267) in the same
   pass.

## The reading that replaces it

- **E64's fitted 1.3 s is 0.20-0.25 s longer than E58's measured filter** (1.05 s on aifoundry3, 1.10 s on card 1).
- **E58's filter plus one aifoundry2 pass is about 1.21-1.27 s.** That leaves about 0.03-0.09 s that these data do not explain.
  And by point 3 a whole pass of delay is not in the source's order of events.
- **So the gap is left unexplained.** aifoundry2's own filter was never measured (E58's caveat), and its PMIC runs 1.5.0, not the
  public 1.7.0. A slower filter on aifoundry2, the fit's own trade between its time constant and its pass, or both, could carry
  it.
- **The check is owed, on E64's own traces:** set the governor model's filter from the source and E58, with aifoundry2's measured
  pass, and fit only what is left.
- **For the dip term:** its board lag (`BOARD_LAG_S`, 0.24 s) is a separate parameter, sourced to the same passes. Amendment A1
  ([`tools/claims-v3/dipterm/REGISTRATION.md.dated-note-4.md`](../../tools/claims-v3/dipterm/REGISTRATION.md.dated-note-4.md),
  `3002edaf`) reports the board at 0.17 s beside it, as a sensitivity arm.

Note 1's last paragraph (09-method.md's rail averages of 1.13 / 1.24 / 1.15 s are the version-3 check's estimates, and E58's step
fits are the measured filter) stands.

## Files

| file | what |
|---|---|
| `09-method.md.dated-note-2.md` | this note |
| [`09-method.md.dated-notes.sha256`](09-method.md.dated-notes.sha256) | this note, dated note 1 and `09-method.md`, the last two unchanged |

SPDX-License-Identifier: Apache-2.0
