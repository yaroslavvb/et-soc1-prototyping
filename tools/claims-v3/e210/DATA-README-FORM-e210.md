# E210's data README: the form the card lane fills for its data commit (Q202, lane kit-e210; kitted, not run)

*Tue 17 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md); E206's form ([../e206/DATA-README-FORM-e206.md](../e206/DATA-README-FORM-e206.md),
the form E206 arm A's committed README followed) for E210's one data directory. This is the form of `README.md` in
`docs/reports/data/<day>-e210-switch-test-aifoundry3/`, written by the card lane after step 12 (the collection) and before the data commit, for
a session in which at least one run started, in the lab's data-README form: **results first, then registered against happened, then
departures, each dated**. It is a form, not a result: every `<...>` is filled from the session's own files (`session/session.log`,
`session/queue.json`, `session/identity.json`, `session/probe/maxalte-S2/probe.json`, `data-e210.json`, `reduce-e210.txt`, the runbook's log,
steps 6n's and 12n's reports), and every number carries its label. The README lies beside the data and is not in its `SHA256SUMS` (the
collector made that list over the collected files). A session in which no run started has no data directory: step 12 collects it into a gate
stop's record, whose README has the shorter form at the end of this file. The scorer runs after the data commit (step 13): its words are not in
this README at the commit; a later lane adds them in a dated note beside it.*

**The rules for this file.** No number from the owner's private pages or his A100 report. No sealed forecast's number. No lab user's login
(the collector's scrub masked ours; write `<login>`). No credential or access path. Times Pacific. The interpreter named. A check not run is NOT
RUN. His words quoted without links. **The forecasts are frozen before any E210 datum** (`forecast-e210.json` `dbc2d3f3...`, in the
registration's landed commit) and **blind to every E210 datum**, but informed by the lab's committed data (E206, E208, E65, MM1-v1: E210.md's
label); quote them only from their frozen files.

---

```
# E210, <day>, aifoundry3 card 0 at its pinned 600 MHz: the switch test (nine operand patterns never run in a GEMM, at gemmL1x1x1 and gemmL1x1x4,
in chained A B B A blocks against random): <RAN FULL (the opening, <n> of 171 runs) / RAN SHORT (<n> of 171 runs: <why>) / STOPPED at <the
stop> after <n> runs>

*<the day>, PST. E210, registered before any datum (<the registration's landed commit>; the routes R1, R3, R3L, R2 and R4 frozen in
forecast-e210.json), kitted (<the kit's landed commit>), verified (<lane, verdict>) and readiness-checked (<lane, verdict>); run on the owner's
go (<his words and their times>). rgm136 (E136's binary, unchanged; the patterns reach the host as tile files), built today on the box through
the kernel gate (<the build record's gate line>). Nothing was set on the card.*

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | <queue.json card_min> (planned about 73; no run after 85, the session ends at 95); step 7's config read at <RB_OUT/e210-step7-A.txt>, reported apart | measured (the session's clock) |
| the opening: 60 s at rest; the smoke (random@S1, zeros@S1, random@S2, 2 s each) | <the rest's board and die (the die gate); each smoke process: rc, launches, the check, cycles an op (the counter's mean) and its ratio to E206's at the shape (p029, p080, p034), the board's rise, the host's card> | measured |
| THE PROBE (maxalte@S2, 2 s, under the die gate) and the stop-path test | <the probe: its gate, rc, launches, its check, the board's highest and the die's highest from its start to the end of its 4 s tail, IN or OUT and why (maxalte left the session: its six runs NOT STARTED, its case NO DATA); if the probe tripped (OUT, or the live 70 W stop at the probe: a gate stop), say so with its readings beside E210.md A1 item 7's reading (a 2 s probe runs about 1 W and 1-3 C under a 6 s run of the same case)>; the stop-path test <passed> | measured; the probe's readings REPORTED, never scored |
| runs: started, with counted launches, not started (why) | <n started> / <n with t_gemm> / <reduce-e210.txt's NOT STARTED lines and runs_without_counted_launch> | measured |
| runs and processes the scorer sets aside or reports by name (E210.md A1 items 5 and 6) | <every process that printed no check of C (the scorer's `R0` › `missing_REPORTED`: its run out of its block by Q, never an R0 FAIL); every run with counted launches but no telemetry sample inside them (data-e210.json's `runs_without_a_sample_inside`: no clock keys, p_work null, set aside by Q); or "none"> | measured |
| how the session ended | <"session end"; queue.json stop: none / the stop's words>; runner.rc <0 / 8 HUNG / 1 a crash, its CRASH line> | measured |
| telemetry samples, and those at 600 MHz | <n> / <n at 600 MHz>; off the clock: <n> | measured |
| board power, peak; the shires' mean, peak; the latch (minshire[2]) at the start and its highest | <W>; <C>; <C> / <C> (the stops: 70 W on 3 samples, 70 C; the latch read as E206.md A1 item 1 and KIT.md 4.1 read it; the line 65 W: the planning peaks S1 59.54 W, S2 62.05 W) | measured |
| the opening and closing configuration reads | <config start>; <config end, or "not read: <why>"> | measured (READ) |
| the identity lines | <the config read's PCIe target, physical device ID, minion_mv>; <the identity read's counts and the sampler's nodes>; <each smoke host's stderr targets and held nodes> | measured |
| per run: cycles an op (the counter's mean), seconds a GEMM, p_work, p_rest, J over idle a GEMM = (p_work - p_rest) t_gemm | <the table from reduce-e210.txt> | measured (reduce_e210.py) |
| per block (R P P R, chained): the pattern runs' mean J over idle less the flanking random runs' mean, the time equality (cycles an op and t_gemm within +-0.1%) | <the blocks; the scorer computes them after the data commit: here the reducer's runs only, or "the scorer's (after the data commit)"> | measured; the block values are the scorer's |
| the ties (001 and 002, the warm-ups; 171, the closing; random@S1) and the random runs' drift | <their t_gemm and J over idle; beside E206 arm A's p029 on this card> | measured; REPORTED |
| the never-run search, repeated (step 6n right before the first card command: `neverrun-e210-card.*`, `named-by-card.json`; step 12n before the data commit: `neverrun-e210-late.*`, `named-by-late.json`) | <each NEVER-RUN line as printed: n of 9 patterns by E210.md A1 item 1 (both conditions count a GEMM string only inside a host launch record); by named tile files in launch records k of 9, and anywhere (the registered condition ii) k2 of 9, and where; the generators not the host's in launch records and elsewhere, with the files naming them; the registered rule as first written m of 9; aifoundry3 searched or NOT SEARCHED; then which patterns ran before (A1), and by whose run and when> | a desk read, REPORTED (E210.md 4: a pattern found run stays in E210; this README says which) |

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside
meter** (E184's arm S, the test of the meter itself, is pending). The joules over idle carry that gain; E210's routes' constants absorb it, and
the fractions of D are unaffected (E210.md 9).

## Registered against happened

| registered (E210.md, points-e210.json, KIT.md) | happened |
|---|---|
| aifoundry3 card 0 at 600 MHz as found; the start config TDP 0 W / 65 C / 600 MHz | <the config reads; the identity lines; the clock in every sample> |
| the rest: 40 minutes since our last session on aifoundry3 (E207's) | <the box's last session of ours before E210 and its end; step 7's and step 9's "rest:" lines> |
| the window: G = the booking; last start G + 1:30, last end G + 3:30 | <G; the window; the launch before the last start; the session's start and end inside it> |
| the never-run search repeated before the data commit | <step 6n's time and line; step 7 within 30 minutes of it; step 12n's time and line> |
| the opening: 60 s at rest, the smoke, THE PROBE (64 W / 63 C), the stop-path test; then 171 runs in the registered order | <as run; the probe IN or OUT> |
| the stops and gates (KIT.md 4) | <any stop, gate wait or NO DATA run, and why> |
| reads only (dmcmd_audit_v2 GO); no SIGKILL; a plain timeout 10 on every device process | <the preflight's line; every process's rc; any HUNG line (then: reported and left)> |

## Departures (dated, before the results they touch)

- The go: <his words, as section 1 of CARD-LANE-BRIEF.md lists them>; G = the booking on its day; the post waived (his words, Sun 15 Nov 2026
  10:22:36 PST); the host's package counter not read; the desk aifoundry2 with `/usr/bin/python3` 3.12.3; the yvb3 session.
- The die line's hottest sensor read as E206.md's amendment A1 item 1 registers it and E210.md 6 adopts it (not a departure): the latch at
  <its start value> C.
- <any other: a step re-run, a wait, a sealed forecast registered before the first card command (its sha256 only, never its numbers), step 6n's
  --desk-only form, ...>

## Files

`session/` (the box's session directory, copied back exact and scrubbed), `data-e210.json` (the frozen scorer's input), `reduce-e210.txt` (the
reducer's table), `neverrun-e210-card.txt`, `neverrun-e210-card.json`, `named-by-card.json` (step 6n's report) and `neverrun-e210-late.txt`,
`neverrun-e210-late.json`, `named-by-late.json` (step 12n's), copied in by the collection, `SHA256SUMS` (all of these). The scorer's outputs
follow after the data commit (a later lane).
```

## The gate stop's record (no run started)

```
# E210, <day>: no run: <the gate's words> (a gate stop's record, never scored)

*<the day>, PST. The session <T0> on aifoundry3 stopped at <the gate> before any run: no data (E210.md 8: a case with no complete block is NO
DATA). <What the session did: the first card command or none; the identity lines if read; the smoke and probe processes if any ran.> E210 may
be tried again as CARD-LANE-BRIEF.md section 3 says.*

## What happened
<the session log's lines from "session start" to "session end"; runner.rc; the runbook's step 10 reading>

## Departures
<as above>
```

SPDX-License-Identifier: Apache-2.0
