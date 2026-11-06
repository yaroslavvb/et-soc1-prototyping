# Dated note 1 beside REGISTRATION.md (Fri 6 Nov 2026, week 45, about 02:42 PST): the scorer's v2, before any re-score is read

*This note sits beside [`REGISTRATION.md`](REGISTRATION.md) and changes nothing in it. The registration, `dipterm.py`,
`score_dipterm.py`, `selftest-dipterm.txt` and `SHA256SUMS` stay as committed in lab `7a099fb9` (02:36:55 PST), byte for byte. No
session it governs has run.*

## What happened

The post hoc study (Q145(b), desk only) was run twice:
- **02:38:43 PST:** it stopped on a sampler message line in a telemetry file. That was a reader fault in the study's own script,
  fixed there.
- **02:39:04 PST:** it called `score_dipterm.py` on E175, and the scorer refused, as its reproduction check is meant to: arm none
  gave E175-A2-G **4.4907 MHz rms, mean +0.1203**, against the committed **4.4923, +0.1206**. E173's and E174's checks had passed.

The script writes and prints its output only at its end, so neither run wrote or showed any figure of the term for any session.

**The cause.** `score_dipterm.py` takes a tile's measured value as the mean of its counted passes in `run_rows`. Those rows keep
each pass rounded to 0.1 MHz and 0.01 W (`reduce_kspeed.burst_extra` rounds `burst_mhz` to one decimal). The run's registered rules
read the tile means in `score.reported.tiles`, which are rounded only at 0.01 MHz. The two differ by up to 0.005 MHz a tile. That
moved E175's rms by 0.0016, over the check's 0.001.

## The fix: [`score_dipterm_v2.py`](score_dipterm_v2.py), a new file

v2 is the same scorer with one change. A tile's measured clock and board are the run's committed tile means
(`score.reported.tiles` > `burst_mhz`, `burst_w`). `run_rows` still name each tile's counted passes, and the term's expected
deficits are still averaged over those passes.
- The reproduction check is unchanged: arm none must give the committed rms and mean to 0.001.
- On all six committed rules that the study re-scores, v2's arm none gives the committed figures exactly, to the four decimals
  committed (checked at 02:40:31 PST with arm none only, before any arm of the term was computed with v2):
  - E173: P8-A2-F2 7.0119 / −2.6567 and P8-A2-Bp 1.0937 / −0.0353;
  - E174: P8-C0-F 4.5431 / −1.6048;
  - E175: E175-A2-G 4.4923 / +0.1206, E175-A2-Bp 0.668 / +0.532 and E175-A2-F2 1.2391 / +0.6512.

**What does not change:**
- the term (`dipterm.py`), which v2 imports unchanged, and every parameter, rule, line and arm of the registration;
- the forecast of its section 5.

Section 4's scorer is v2 from now on. A governed session's registration names `score_dipterm_v2.py` and this note's list
[`SHA256SUMS-1`](SHA256SUMS-1).

## Files

| file | what |
|---|---|
| `REGISTRATION.md.dated-note-1.md` | this note |
| [`score_dipterm_v2.py`](score_dipterm_v2.py) | the scorer, v2 |
| [`SHA256SUMS-1`](SHA256SUMS-1) | this note and v2, plus the four files `SHA256SUMS` lists and `SHA256SUMS` itself, all unchanged |

SPDX-License-Identifier: Apache-2.0
