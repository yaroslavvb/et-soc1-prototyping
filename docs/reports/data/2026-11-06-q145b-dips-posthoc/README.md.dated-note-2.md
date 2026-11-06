# Dated note 2 beside README.md (Fri 6 Nov 2026, week 45): the late climbs read at the sampler's resolution, and the interpreter the rebuild needs. POST HOC

*This note sits beside [`README.md`](README.md) and [dated note 1](README.md.dated-note-1.md) and changes nothing in them: the README,
note 1, their scripts, outputs, `SHA256SUMS` and `SHA256SUMS-1` stay as committed (`006c85eb`, `460ac80e`). Written by the records round
after round B (Q148(r)), desk only, from two minor faults round B's critic found. **Every figure here is POST HOC:** the data of E173-E175
existed first, and the oracle lattice below is fitted on each session's own falls.*

## 1. The late climbs at a process start: result 7, re-read

Note 1's result 7 reads: *"The seq arm expects 0.12, 7.20 and 0.55 late climbs on E173, E174 and E175, against 3, 3 and 5 seen in the
telemetry. That is under-predicted on aifoundry2 and over-predicted on card 0"*, and it owes a re-read of the start climb before card 0's
blind session. **That comparison sets two different things side by side:** the term's event (any climb ending after 1.50 s, edge climbs
ending at 1.51-1.55 s included) and the first 10 Hz telemetry reading at 800 MHz after 1.50 s, which lags the climb's end by up to one
sample.

Read at the sampler's resolution, by round B's critic's own code ([`posthoc_climbs_note2.py`](posthoc_climbs_note2.py), which imports only
the lab's ring decoder, `tools/claims-v3/hpl/sptrace_full.py`; output [`posthoc-climbs-note2.txt`](posthoc-climbs-note2.txt) and
[`.json`](posthoc-climbs-note2.json)), on the **oracle** lattice (fitted on all of a session's A1 falls with the card's period prior), with
the registered start climb (aifoundry2 0.31 s, card 0 0.39 s):

| session | burst processes | predicted climbs ending after 1.5 s / after 1.6 s | seen after 1.5 s / after 1.6 s | first 800 MHz reading − predicted end: median (p10, p90) |
|---|---|---|---|---|
| E173 (aifoundry2) | 165 | 0 / 0 | 3 / 0 | +0.012 s (−0.072, +0.086) |
| E174 (card 0) | 126 | 7 / 1 | 3 / 2 | −0.016 s (−0.098, +0.055) |
| E175 (aifoundry2) | 126 | 1 / 1 | 5 / 1 | +0.008 s (−0.071, +0.076) |

- Seven of aifoundry2's eight "seen" late climbs read their first 800 MHz sample at 1.525-1.532 s, where the oracle lattice ends the climb
  at 1.41-1.46 s: they are sampler lag, not late climbs. Six of card 0's seven predicted ones end at 1.51-1.55 s: edge climbs.
- **At one sample past the edge (1.6 s)** the lattice predicts 0 / 1 / 1 late climbs on E173 / E174 / E175, and the telemetry shows
  0 / 2 / 1: E175's BURST-83 is predicted at 1.97 s and seen at 2.03 s; E174's BURST-18 predicted at 2.03 s and seen at 1.98 s; E174's
  BURST-29 seen at 1.97 s and not predicted.
- So **the registered start climb fits to the sampler's resolution on both cards** (it may run 0.04-0.07 s long, under one service
  processor pass). An edge climb costs under 1 MHz on its own pass, so it does not carry C0-F's +0.74 MHz mean either.

**What changes.** The owed re-read of the start climb before card 0's blind session becomes **optional, on both cards**. If a blind
session scores late climbs at all, it reads them at the sampler's resolution (the climb's end plus one 0.1 s sample) or reports them only.
No registered rule, verdict or figure of note 1 changes.

## 2. The interpreter the rebuild needs

Note 1's rebuild line says "Python 3". Its outputs depend on the interpreter: Python 3.12 and later add floats in `sum()` with
compensated summation. Run under Python 3.9.6, `posthoc-dips-a1.json` differs from the committed file in 39 lines and
`posthoc-dips-a1.txt` in 2, in the last digits only (for example E174's oracle C0-F 1.9006 against 1.9013 MHz); under Python 3.13 both
rebuild byte for byte. **The committed files are Python 3.13.11's; rebuild them with Python 3.12 or later**, or read last-digit
differences as interpreter rounding. No quoted figure or verdict moves. `dipterm_a1.py`'s self-test and `climb_c0_a1.py` were made under
3.13 too, and rebuild byte for byte under 3.9.6 as well. The README's own study (`posthoc_dips_q145b.py`) rebuilds byte for byte under the system Python 3.9.6, as it was made. The next
governed session's registration names the interpreter its scorer runs under.

## Files

| file | what |
|---|---|
| `README.md.dated-note-2.md` | this note |
| [`posthoc_climbs_note2.py`](posthoc_climbs_note2.py) | round B's critic's code, committed unchanged but for its docstring's and label's naming: A1's DT-N re-derived from A1's text, and the late climbs at the sampler's resolution |
| [`posthoc-climbs-note2.json`](posthoc-climbs-note2.json), [`posthoc-climbs-note2.txt`](posthoc-climbs-note2.txt) | its output and its printed summary |
| [`SHA256SUMS-2`](SHA256SUMS-2) | the four files above, `SHA256SUMS` and `SHA256SUMS-1` |

Rebuild from the repository's top level (no third-party module; about 2 s on one core). The committed output is the system Python
3.9.6's; under Python 3.13.11 the printed summary is identical and the JSON differs in one line, the last digit of an internal lattice
phase (`phi_ms`), the same interpreter effect as section 2's:

```bash
python3 -I -B docs/reports/data/2026-11-06-q145b-dips-posthoc/posthoc_climbs_note2.py . \
  docs/reports/data/2026-11-06-q145b-dips-posthoc/posthoc-climbs-note2.json > docs/reports/data/2026-11-06-q145b-dips-posthoc/posthoc-climbs-note2.txt
```

SPDX-License-Identifier: Apache-2.0
