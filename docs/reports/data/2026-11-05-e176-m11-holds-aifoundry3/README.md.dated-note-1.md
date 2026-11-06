# E176's data README, dated note 1 (Thu 5 Nov 2026; after the records' verifier): G0's line is the kit README's lines 79 and 95, and R0 fell from 54.75 °C to 53.48 °C

*Written on the Intel at about 21:30 PST on Thu 5 Nov 2026, desk only. [`README.md`](README.md) (lab `5db7bcf7`, the records round
Q143(r)) stays as committed. **No number, rule, verdict or gate reading changes, and nothing is scored.** The note answers two minor faults
found by the verifier of those records (Thu 5 Nov 2026, about 20:33–21:16 PST), both in the README's words. The figures below come from
[`posthoc_note1_e176.py`](posthoc_note1_e176.py), which reads only this directory's committed telemetry and marks and imports no scorer,
with its output in [`posthoc-note1-e176.txt`](posthoc-note1-e176.txt) (§ numbers below are that output's). For the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8, as the README.*

## 1. Where E176's kit states G0's line: lines 79 and 95, not 79 and 188

The README's G0 row (line 32) cites the line "holds run only if the room is at most 53.0 °C" at
"[`e176/README.md`](../../../../tools/claims-v3/e176/README.md), lines 79 and 188". That kit README has one version (`03582d2f`, 12:38:01 PST)
and 158 lines, so there is no line 188. **G0 is stated at line 79** ("G0: R0's room ≤ 53.0 °C, else no hold, exit 7", in the list of what the kit
keeps from E166) **and at line 95** (the order on aifoundry3: "on a rested card (G0: the room ≤ 53.0 °C; the cool pattern ≤ 51.5 °C)",
which runs on to line 96). Lines 68
and 85 also name 53.0 °C: H_E's warm pattern in (51.5, 53.0] °C, and the other holds' planned peaks at a 53.0 °C room. Quote it as "lines 79
and 95". The gate and its reading are unchanged: G0 REFUSED at 17:27:34 PST.

## 2. R0's start and end values

The README's "R0's fall after the smoke" row (line 51) says the 34-sensor mean "fell from **54.814 °C** at +0 s to **53.487 °C** at +300 s".
Neither value is at the time it names. Read again from [`aifoundry3/e176/p17620/telemetry.jsonl.gz`](aifoundry3/e176/p17620/telemetry.jsonl.gz)
and [`marks.jsonl`](aifoundry3/e176/p17620/marks.jsonl), with E97's conversion of the raw codes and the sample filter (status 0, no fault, 34
codes) as [`smoke_gate_e176.py`](../../../../tools/claims-v3/e176/smoke_gate_e176.py) has them, 3,064 of 3,064 samples usable (§ 1–2):

| what | time (PST) | the 34-sensor mean |
|---|---|---|
| the measured pass's first telemetry sample | 17:22:30.983, 3.268 s before R0 began; 33 samples precede R0 | 54.814 °C, the README's "+0 s" value |
| R0's start, the rest mark's `t_start_ms` | 17:22:34.251 | |
| R0's first sample | 17:22:34.283 (+0.032 s) | **54.748 °C** (its first second's mean 54.745 °C, 10 samples) |
| R0's sample nearest +299 s | 17:27:33.283 | 53.487 °C, the README's "+300 s" value |
| R0's last sample | 17:27:34.183 (+299.932 s) | **53.476 °C** (its last second's mean 53.485 °C, 10 samples) |
| R0's end, the rest mark's `t_end_ms` | 17:27:34.274 | |

So **R0 fell from 54.75 °C at its start to 53.48 °C at its end**. 54.81 °C is the pass's first sample, 3.3 s before R0 began, and 53.487 °C
is R0's sample at +299 s. The pass's highest 34-sensor mean, 54.819 °C at 17:22:31.083, also came before R0. Quote it as "from 54.81 °C at
the pass's first sample, 3.3 s before R0 (54.75 °C at R0's start), to 53.48 °C at R0's end".

**What does not change** (§ 3–4): G0's room, the mean over R0's last 120 s, reads 53.5821 °C from 1,200 of 1,200 samples, equal to the rest
mark's `idle_c` and the room mark's `mean34_c`; the slope over R0's last 240 s is −1.689 °C per 10 min (2,400 samples, least squares); the
smoke's first sample, the idle floor, reads 53.202 °C at 17:21:17.362 (board 23.97 W); and G0's room sat 0.380 °C above it. The README's
other figures stand. [`docs/findings/03-experiments.md`](../../../findings/03-experiments.md)'s E176 entry, which quoted "54.81 to 53.49 °C",
carries a dated clause saying the same, and 04's E176 row names this note.

SPDX-License-Identifier: Apache-2.0
