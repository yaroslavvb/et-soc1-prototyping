# Dated note 1 beside the README (Fri 6 Nov 2026, week 45): card 1's SRAM rail would carry about 1.4 times its reading, not 1.6; the 2 mV voltage agreement is September's idle reading, and in November aifoundry3's minion monitor reads 3-4 mV under its set point

*This note sits beside [`README.md`](README.md) (`707cd2c5`) and changes nothing in it; that file stays as committed. It corrects
two of its readings, as Q150's verifier found them, from this directory's own committed files and from committed telemetry. Every
figure is POST HOC, as the README's are: no registered number, rule or verdict of any run changes. Desk only: no card and no lab
machine was touched. Its time is its commit's.*

## Builds on

- **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 16:00 PST. Public rows read: P01, P03, L06, L08, L11, H24. The ids
  are opaque pointers into a private inventory.
- **Used:**
  - this directory's `reset_minmax_bylevel.json`, `reset_minmax_steady.json` and `reset_recovery.json`, as committed;
  - the energy manual's off-rail fit (`docs/energy-manual/04a-fine-grain.md`, `../2026-09-23-energy-manual/unmetered_fit.json`);
  - the kept passes of E171 (aifoundry3, 5 Nov), E172 (aifoundry1's card 1, 5 Nov) and E178 (aifoundry3, 6 Nov), each
    `telemetry.jsonl.gz`;
  - the check script committed with the sibling directory's dated note 1,
    [`../2026-11-06-q150-sensor-crosscheck/q150_note1_checks.py`](../2026-11-06-q150-sensor-crosscheck/q150_note1_checks.py), and its
    output `q150_note1_checks.json` (sections B and D), which records every input's sha256.
- **Not used:** the PMIC 1.3.0 source (not public); any card time.
- **Tiers:** public only.

## 1. Result 1's "about 1.6 times" is about 1.4 by the README's own two-update reading

The README divides a reset window's PMIC maximum by its average (1.59). In a reset window that average has not settled: the
README's own `reset_recovery.json` has card 1's SRAM average restarting at 0.77 of its window's last value and climbing for about
0.7 s. Under the two-update path the README cites (`IoTask.c` lines 1041-1048 of the public runtime 1.7.0: the statistic is updated
with phase 0 alone, then with phase 0 plus phase 1), the statistic's minimum is the phase-0 reading P0, its maximum the sum S, and its
settled average (P0 + S) / 2. The average then reports f = (P0 + S) / 2S of the sum, and the window's own minimum and maximum give it
without the unsettled average: **f = (m + M) / 2M**, with m and M the minimum and maximum over the average.

| card 1, SRAM rail, reset windows | samples | m (min / avg) | M (max / avg) | m / M | f = (m + M) / 2M | 1 / f |
|---|---:|---:|---:|---:|---:|---:|
| idle | 219 | 0.6268 | 1.5917 | 0.394 | **0.697** | **1.43** |
| board at 40 W or more | 61 | 0.6305 | 1.5753 | 0.400 | **0.700** | **1.43** |

(`q150_note1_checks.json` › `D_card1_sram_fraction`.) On a rail updated once per scan the same formula gives 0.95-0.98 (aifoundry2's
and aifoundry3's SRAM rails 0.978 and 0.979; every minion and NoC rail of the three cards 0.954-0.980), because a minimum and a maximum
are noise extremes; allowing for that, card 1's fraction is about 0.70-0.72. **So if the summed reading is the rail's power, the rail
carries about 1.4 times what the average reports (1.37-1.45 for a fraction of 0.69-0.73), not 1.6.**

The off-rail fit's figure, about 1.5, rests on an assumption. If card 1's SRAM reading is f of the rail and the rail's regulator loses
b of what it delivers, the fit's SRAM coefficient is (1 + b) / f - 1 = 0.540, so f = (1 + b) / 1.540:

| b, the SRAM regulator's delivery loss | f | 1 / f |
|---|---:|---:|
| 0.034-0.043 (aifoundry2's and aifoundry3's fitted coefficients) | 0.671-0.677 | 1.48-1.49 |
| 0.10 | 0.714 | 1.40 |
| 0.25 (a regulator 80% efficient) | 0.812 | 1.23 |

So the two estimates (about 1.43 and 1.48) agree only if card 1's SRAM regulator loses what the other two cards' fits say theirs do.
Neither is a measurement, and the mechanism stays a hypothesis (the PMIC 1.3.0 source is not public). What the README says would
settle it stands; what it touches stands, with the factor about 1.4 in place of 1.6.

## 2. Result 2's "within 2 mV, on every card" is September's idle reading

Result 2 read the version-3 check's reset windows of 25-26 September, idle samples. On November's kept passes the set points read
525 mV (aifoundry3) and 500 mV (card 1) in every sample, and the on-die monitors read (`q150_note1_checks.json` ›
`B_die_minus_set_point_by_load`; idle is the board within 2 W of its file's 5th percentile, busy more than 8 W above it):

| card, session | rail | idle: die - set point, mV (share of samples) | busy |
|---|---|---|---|
| aifoundry3, E171 | minion | -3 (95%), -2 (5%), -4 (0.5%) | -4 (54%), -3 (46%) |
| aifoundry3, E178 | minion | -3 (90%), -2 (9%), -4 (0.6%) | -3 (67%), -4 (33%) |
| aifoundry3, E171 and E178 | SRAM, NoC | -2, -1 (NoC -2 in 0.3%) | -2, -1 |
| card 1, E172 | minion | -1 (99.5%), -2 (0.5%) | -1 (51%), -2 (49%) |
| card 1, E172 | SRAM, NoC | +1, +1 | +1, +1 |

- **aifoundry3's minion monitor now reads 3 mV under its set point at idle (522 mV, against September's 523) and 3-4 mV under it under
  load.** Its SRAM and NoC rails, and card 1's three rails, read as in September: within 2 mV.
- `sp.minion_mv` equals `die_mv.minion` in 95.4-95.8% of aifoundry3's samples and 98.6% of card 1's, and is within 1 mV of it in
  99.9-100%: one measurement, as the sibling directory says.
- **The README's conclusion stands.** 4 mV is 0.8% of 525 mV, 1.5% in V squared: far from card 1's 10% excess after V squared, which a
  misreading would need about 25 mV to explain.
- Whether the 1 mV idle shift since September is in the rail, in the monitor or in the firmware build is not separated here.
- The README calls 521.7 and 498.7 mV "October's set points". They are E78's and E82's on-die minion readings
  (`../2026-10-31-e78-kinds-energy-matrix/README.md` line 10, `../2026-10-31-e82-kinds-aifoundry1/README.md` line 90); the set
  points were 525 and 500 mV.

## Files

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| [`README.md.dated-note-1.sha256`](README.md.dated-note-1.sha256) | this note, the README (unchanged) and the three files of this directory section 1 reads |

The numbers come from `../2026-11-06-q150-sensor-crosscheck/q150_note1_checks.json`, written from the top of the repository by

    python3 -I docs/reports/data/2026-11-06-q150-sensor-crosscheck/q150_note1_checks.py . \
        > docs/reports/data/2026-11-06-q150-sensor-crosscheck/q150_note1_checks.json

SPDX-License-Identifier: Apache-2.0
