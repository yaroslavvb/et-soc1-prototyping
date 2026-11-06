# Dated note 2 beside fw-q147's README (Fri 6 Nov 2026, week 45): its verifier's eight faults, written down

*Beside [`README.md`](README.md) (`8060a8f5`, 23:25:41 PST Thu 5 Nov 2026) and [dated note 1](README.md.dated-note-1.md)
(`3666425a`, 23:28:43 PST). It edits neither, nor `posthoc_card_check.py` or `posthoc-card-check.json`. Written by the records round
after the study (Q148(r)), desk only, from the faults an adversarial verifier of the study found (holds with fixes: one major, seven
minor) and the round critic confirmed. No fix pass of the study's own ran, so they are written here. **The verdict is unchanged: the
patch does not help, loading it risks a power cycle, NO-GO, not attempted.** Read the README and note 1 with these corrections.*

## 1. The open RTL's int8 op event is zero-gated (the major fault)

The README's section 1 ("In the open RTL the tensor-op events are control events ... So there an op count is the same for every kind of
number", lines 61-63), its table's class-S row ("Op events do not depend on the data (open RTL)", line 85) and note 1's last paragraph
("holding as written") are **wrong for int8**. In core-et `b38a1a3`, `rtl/shire/minion/vpu/vpu_ctrl.v`:

- the int8 event `TIMA_OPS` is the OR of the per-lane TIMA valids (`:1681`, `io_events[VPU_EVENT_TIMA_OPS] = |ex_tima_valid`), and each
  valid is gated by the zero mask built from TenA's and TenB's zero masks (`:817-830`). So `TIMA_OPS` counts only cycles in which at least
  one int8 lane is ungated, and it falls on zero operands;
- the float events (`TXFMA_32`, `TXFMA_3216`, `INT_OPS`, `:1683-1687`) and `TFMA_INST` (`:1695`) come from the instruction's control
  chain, as the README says. Those are control events, the same for every kind of number.

**The counter proposal the study did not weigh.** Q130(g)'s zero-gate correction proposed reading these micro-op counters "on zeros
against random per format" to "measure the gate's granularity without inferring it from power"
([`docs/reports/data/2026-10-31-q130-zero-gate-correction/README.md`](../../../docs/reports/data/2026-10-31-q130-zero-gate-correction/README.md),
lines 82-83), and E93 and E121 recorded that the counters were not read
([E93](../../../docs/reports/data/2026-11-01-e93-zero-gate-silicon/README.md) line 182, C10;
[E121](../../../docs/reports/data/2026-11-01-e121-zero-gate-replicate/README.md)). Weighed now, it supports the study's NO: in the open
RTL the float events cannot see the gate at all; `TIMA_OPS`, an OR over lanes, sees only fully gated int8 cycles, not the lane pairing E93
left inferred; and the gate is already closed at power resolution on two cards (E93, E121).

## 2. The seven minor faults, as corrected

1. **The issue-rate band** (README line 82): the catalogue's two-hart random rows do not all run 0.30-0.45 issues a hart-cycle. **102 of
   the 150 run 0.30-0.45; the median is 0.369, and the fastest, `nop`, runs 0.390** (48 rows sit below 0.30). `fmadd.ps` runs 0.3649 with
   both harts and 0.5814 with one (measured 26 Sep), as the anatomy's dated note gives it
   ([`NOTE-2026-11-05-fmadd-ps-public-facts.md`](../../../docs/reports/data/2026-11-05-q145a-anatomy-top-lines/NOTE-2026-11-05-fmadd-ps-public-facts.md),
   lines 47-48).
2. **"Energy per op" after V²** (the card-to-card row): after dividing by each session's V² the quantity is switched capacitance per op.
   Corrected: *after V² (switched capacitance per op) card 1 reads 1.103x on floats and 1.081x on int8 (medians; int8 spread 1.014-1.104);
   the raw rail energy per op is 1.008x / 0.988x.* The raw board ratio, 0.965x / 0.954x (0.963 over all items), sits beside two earlier
   readings of the same quantity: M10's frozen card-1 term 0.9616 and E82's 1.061x after C·V².
3. **The governor row** (line 83): "its misses are the service processor's idle reset" holds for E173's pinned clock (7.01 MHz rms, 0.07
   without the dipped passes). E175's governed 4.49 MHz is part dips, part data term: it still reads 3.82 MHz with every fallen pass
   dropped (post hoc). The patch's counters see neither, so the verdict stands.
4. **The reset** (section 4, step 3): at et-platform `836a4ab60`, `DM_CMD_RESET_ETSOC` (`firmware_update.c:45-86`) power-cycles the
   service processor and the PMIC (`pmic_force_power_off_on`) whenever a PMIC image was written by the update, which the update's PMIC
   step does unless it skips; otherwise it forces a PMIC reset with the PMIC watchdog armed. So: **a definite power cycle after an update
   that wrote the PMIC, otherwise a PMIC-forced reset.** The lab's command table classes both `SET_FIRMWARE_UPDATE` and `RESET_ETSOC` as
   WRITE ([`../dmcmd_table.json`](../dmcmd_table.json)), so `dmcmd_audit` reads NO-GO on any kit that sends either. The Master Minion's
   reset from its in-DDR copy (`DM_CMD_MM_RESET`) is a WRITE reset too, which the lab's rules forbid, and no host path to write that copy
   is established; the NO-GO stands by every route.
5. **The times and base:** the study was written about 22:58-23:28 PST on base `538c98ce` (the clone's HEAD from 22:54:13 PST), not
   "about 23:00-23:50" (README line 3), and dated note 1 was committed at 23:28:43 PST, not "about 23:35".
6. **The Tiers line** (line 41): it said nothing from a private tier is used. Corrected: the private field manual is cited by name and by
   gate names already public in E69's, E72's and E118's change records ([`../knob/CHANGE-RECORD.md`](../knob/CHANGE-RECORD.md),
   [`../lq6/CHANGE-RECORD.md`](../lq6/CHANGE-RECORD.md), [`../e118/CHANGE-RECORD.md`](../e118/CHANGE-RECORD.md)); no content beyond them.
7. **0.73%** (line 81) is **0.72%** (E171's fp32 random duty 0.99277, from the unrounded 1.11714e9 against 1.12527e9 steps a second).

**A disclosure:** the lane ran two short Python scripts outside the round's local slots (its public-text scanner and its result writer,
each under a second).

## 3. E179, and the Builds-on block

- **E179** (the README's lines 10, 82 and 162): E179 is **assigned, not registered** (Q147, item 4). Any registered kernel that needs an
  issue rate reads it from the stock counters (`hpmcounter4`/`5` over `hpmcounter3`) or from its loop count over device cycles.
- **Checked, added:** Q130(g)'s zero-gate correction, E93 and E121 (above). **Not used, added:** their counter proposal, answered in
  section 1.

## 4. For the owner

His item 6 allowed patched firmware "if it helps", by the maintainer's guidelines, and said to stop and ask if the procedure risks a power
cycle. It does not help, and it would risk one. **Nothing was attempted, and there is nothing to approve unless he wants it anyway**; then
the README's section 5 lists what it would take.

SPDX-License-Identifier: Apache-2.0
