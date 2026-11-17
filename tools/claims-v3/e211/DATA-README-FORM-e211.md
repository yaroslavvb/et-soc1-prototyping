# E211's data README: the form the card lane fills for its data commit (Q204, lane kit-e211; kitted, not run)

*Tue 17 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md); E206's form ([../e206/DATA-README-FORM-e206.md](../e206/DATA-README-FORM-e206.md),
the form E206 arm A's committed README followed), as E207's kit ported it (Q199), for E211's one data directory. This is the form of `README.md`
in `docs/reports/data/<day>-e211-second-kernel-aifoundry3/`, written by the card lane after step 12 (the collection) and before the data commit,
for a session in which at least one run started, in the lab's data-README form: **results first, then registered against happened, then
departures, each dated**. It is a form, not a result: every `<...>` is filled from the session's own files (`session/session.log`,
`session/queue.json`, `session/identity.json`, `data-e211.json`, `reduce-e211.txt`, the runbook's log, step 6n's report), and every number
carries its label. The README lies beside the data and is not in its `SHA256SUMS` (the collector made that list over the collected files). A
session in which no run started has no data directory: step 12 collects it into a gate stop's record, whose README has the shorter form at the
end of this file. The scorer runs after the data commit (step 13): its words are not in this README at the commit; a later lane adds them in a
dated note beside it.*

**The rules for this file.** No number from the owner's private pages or his A100 report. No sealed forecast's number (a sealed sha256 only, as
`tools/claims-v3/sealed-e211/` registers it). No lab user's login (the collector's scrub masked ours; write `<login>`). No credential or access
path. Times Pacific. The interpreter named. A check not run is NOT RUN. His words quoted without links. **The forecasts are BLIND** (MM1-v1
through the desk map, MM1-S, F1, F2, the chip-lines null NC, the no-walk null N0 and family C's C1, frozen in `forecast-e211.json` `90e8d1ae...`
with E211's registration before any E211 datum); quote them only from their frozen files.

---

```
# E211, <day>, aifoundry3 card 0 at its pinned 600 MHz: the second kernel (rgm211, rgm136 with its C-block walk swapped, and rgm136's own
non-cooperative loads, against MM1-v1 through the desk map, F1 and the chip-lines null): <RAN FULL (the smoke, the stop-path test, <n> of 38
runs) / RAN SHORT (<n> of 38 runs: <why>) / STOPPED at <the stop> after <n> runs>

*<the day>, PST. E211, registered before any datum (<the registration's landed commit>, with Amendment A1 made before the land; its forecasts frozen in forecast-e211.json 90e8d1ae...),
kitted (<the kit's landed commit>), verified (<lane, verdict>) and readiness-checked (<lane, verdict>); run on the owner's go (<his words and
their times>), after E207's data commit (<its commit>) and E210's session on this card. rgm136 (E136's binary, unchanged) and rgm211 (E211's)
built today on the box through their kernel gates (<the build record's two gate lines>); every process gated by its arm family (THE IDENTITY GATE
PER PROCESS). Nothing was set on the card.*

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | <queue.json card_min> (planned 20.4; no run after 30, cap 35); step 7's config read at <RB_OUT/e211-step7-A.txt>, reported apart | measured (the session's clock) |
| the smoke: s01 (gemmL2x2x2, rgm136), s02 (gemmLn2x2x2, rgm211), s03 (gemmLnc2x2x2, rgm211's host on rgm136's ELF), 2 s each, then the stop-path test | <each: its identity gate's words, rc, launches, the check, the walk (s02 nm, s03 mn; walk_ok on every launch, walk_launches_bad), cycles an op (the counter's mean) and its ratio to MM1's counter-mean forecast, the board's rise, the host's card>; the stop-path test <passed> | measured |
| THE IDENTITY GATE PER PROCESS | <every process's gate words: "GATE OK: ..." for each of the 41 processes, or the first GATE FAILED and where the session stopped> | measured (the gate's reading of the box's ELFs) |
| THE WALK CHECK | <every rgm211-host process (gemmLn: nm; gemmLnc: mn): walk_ok true on every launch and walk_launches_bad 0, or the first failure and THE KERNEL STOP it caused> | measured |
| runs: started, with counted launches, not started (why) | <n started> / <n with t_gemm> / <reduce-e211.txt's "not started" lines and runs_without_counted_launch> | measured |
| how the session ended | <"session end"; queue.json stop: none / the stop's words (a kernel stop names its run and family)>; runner.rc <0 / 8 HUNG / 1 a crash, its CRASH line> | measured |
| telemetry samples, and those at 600 MHz | <n> / <n at 600 MHz>; off the clock: <n> | measured |
| board power, peak (family W and family C apart); the shires' mean, peak; the latch (minshire[2]) at the start and its highest | <W> / <W>; <C>; <C> / <C> (the stops: 70 W on 3 samples, 70 C; the latch read as E206.md A1 item 1 and KIT.md 4.1 read it; the line 65 W) | measured |
| the opening and closing configuration reads | <config start>; <config end, or "not read: <why>"> | measured (READ) |
| the identity lines | <the config read's PCIe target, physical device ID, minion_mv>; <the identity read's counts and the sampler's nodes>; <each smoke host's stderr targets and held nodes> | measured |
| per point: cycles an op (the wall: cycles_gemm / ops a minion a GEMM; the counter's mean: the host's cycles_per_op), seconds a GEMM, p_work, p_rest, J over idle and J with the card at rest (each run, and the point's mean) | <the table from reduce-e211.txt> | measured (reduce_e211.py) |
| per pair: the ratio rgm211 / rgm136 (the wall; its W or X block's own runs; the controls x01 and x02 first, with Amendment A1's c_hat, the mean of their ln ratios, and whether A1 applies) and family C's ratio (gemmLnc over its C-block twin) | <from data-e211.json, by the scorer's definitions; the verdicts are the scorer's, after the data commit> | measured; the verdicts REPORTED later |
| the never-run search repeated right before the first card command (step 6n; `neverrun-e211-card.txt`, `neverrun-e211-card.json`) | <its NEVER-RUN-E211 line: rgm211 on a card before E211 (none, or the keys and where); the gemmLn/gemmLnc configurations found and the simulator's apart; the twins with a card record (E206 arm A's four in sample; E207's three run before E211, expected); aifoundry3 searched or NOT SEARCHED> | a desk read, REPORTED (rgm211 found on a card before E211: the dated note, and the orchestrator told) |

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside
meter** (E184's arm S, the test of the meter itself, is pending). The joules over idle and with the card at rest carry that gain.

## Registered against happened

| registered (E211.md, plan-e211.json, KIT.md) | happened |
|---|---|
| aifoundry3 card 0 at 600 MHz as found; the start config TDP 0 W / 65 C / 600 MHz | <the config reads; the identity lines; the clock in every sample> |
| E211 books no card before E207's data commit; after E210 on this card | <E207's data commit and its time; E210's session end; G after both> |
| the rest: 40 minutes since our last session on aifoundry3 | <the box's last session of ours before E211 and its end; step 7's and step 9's "rest:" lines> |
| the window: G = the booking; last start G + 1:30, last end G + 3:30 | <G; the window; the launch before the last start; the session's start and end inside it> |
| the never-run search right before the first card command | <step 6n's time and line; step 7 within 30 minutes of it> |
| the smoke (one process of each arm family, each its family's first on the card, short), then the stop-path test; the order: family X, family W, family C (38 runs, n 4-41) | <as run> |
| the identity gate per process; the walk check; the kernel stops for gemmLn and gemmLnc | <every gate OK, every walk OK, or the stop> |
| the stops and gates (KIT.md 4) | <any stop, gate wait or NO DATA run, and why> |
| reads only (dmcmd_audit_v2 GO); no SIGKILL; a plain timeout 10 on every device process | <the preflight's line; every process's rc; any HUNG line (then: reported and left)> |

## Departures (dated, before the results they touch)

- The go: <his words, as section 1 of CARD-LANE-BRIEF.md lists them>; G = the booking on its day; the post waived (his words, Sun 15 Nov 2026
  10:22:36 PST); the host's package counter not read; the desk aifoundry2 with `/usr/bin/python3` 3.12.3; the yvb3 session.
- The die line's hottest sensor read as E206.md's amendment A1 item 1 registers it and plan-e211.json adopts it (not a departure): the latch at
  <its start value> C.
- <any other: a step re-run, a wait, a sealed forecast registered before the day (its sha256 only, never its numbers), step 6n's --desk-only
  form, ...>

## Files

`session/` (the box's session directory, copied back exact and scrubbed), `data-e211.json` (the frozen scorer's input), `reduce-e211.txt` (the
reducer's table), `neverrun-e211-card.txt` and `neverrun-e211-card.json` (step 6n's report, copied in by the collection), `SHA256SUMS` (all of
these). The scorer's outputs follow after the data commit (a later lane).
```

## The gate stop's record (no run started)

```
# E211, <day>: no run: <the gate's words> (a gate stop's record, never scored)

*<the day>, PST. The session <T0> on aifoundry3 stopped at <the gate> before any run: no data (E211.md 7: a point or case with no run is NO
DATA). <What the session did: the first card command or none; the identity lines if read; the smoke processes if any ran, with their identity
gates and walks.> E211 may be tried again as CARD-LANE-BRIEF.md section 3 says.*

## What happened
<the session log's lines from "session start" to "session end"; runner.rc; the runbook's step 10 reading>

## Departures
<as above>
```

SPDX-License-Identifier: Apache-2.0
