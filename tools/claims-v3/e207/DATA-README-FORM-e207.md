# E207's data README: the form the card lane fills for its data commit (Q199, lane kit-e207; kitted, not run)

*Mon 16 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md); E206's form ([../e206/DATA-README-FORM-e206.md](../e206/DATA-README-FORM-e206.md),
the form E206 arm A's committed README followed) for E207's one data directory. This is the form of `README.md` in
`docs/reports/data/<day>-e207-blind-matmul-aifoundry3/`, written by the card lane after step 12 (the collection) and before the data commit, for
a session in which at least one run started, in the lab's data-README form: **results first, then registered against happened, then
departures, each dated**. It is a form, not a result: every `<...>` is filled from the session's own files (`session/session.log`,
`session/queue.json`, `session/identity.json`, `data-e207.json`, `reduce-e207.txt`, the runbook's log, step 6n's report), and every number
carries its label. The README lies beside the data and is not in its `SHA256SUMS` (the collector made that list over the collected files). A
session in which no run started has no data directory: step 12 collects it into a gate stop's record, whose README has the shorter form at the
end of this file. The scorer runs after the data commit (step 13): its words are not in this README at the commit; a later lane adds them in a
dated note beside it.*

**The rules for this file.** No number from the owner's private pages or his A100 report. No sealed forecast's number. No lab user's login
(the collector's scrub masked ours; write `<login>`). No credential or access path. Times Pacific. The interpreter named. A check not run is NOT
RUN. His words quoted without links. **The forecasts are BLIND** (MM1-v1, F1 and F2 frozen in `25d2e74e`, pushed 21:14:57 PST Mon 16 Nov 2026,
before any E207 datum); quote them only from their frozen files.

---

```
# E207, <day>, aifoundry3 card 0 at its pinned 600 MHz: the blind matmul day (MM1-v1 against F1 and F2 on 53 never-run points): <RAN FULL (the
smoke, the stop-path test, <n> of 109 runs) / RAN SHORT (<n> of 109 runs: <why>) / STOPPED at <the stop> after <n> runs>

*<the day>, PST. E207, registered before any datum (<the registration's landed commit>; the forecasts MM1-v1's, frozen in 25d2e74e with F1 and
F2 beside), kitted (<the kit's landed commit>), verified (<lane, verdict>) and readiness-checked (<lane, verdict>); run on the owner's go (<his
words and their times>). rgm136 (E136's binary, unchanged), built today on the box through the kernel gate (<the build record's gate line>).
Nothing was set on the card.*

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | <queue.json card_min> (planned 40.6; no run after 60, cap 70); step 7's config read at <RB_OUT/e207-step7-A.txt>, reported apart | measured (the session's clock) |
| the smoke: b01, b02, b03 (2 s each), then the stop-path test | <each: rc, launches, the check, cycles an op (the counter's mean) and its ratio to MM1-v1's counter-mean forecast, the board's rise, the host's card>; the stop-path test <passed> | measured |
| runs: started, with counted launches, not started (why) | <n started> / <n with t_gemm> / <reduce-e207.txt's "not started" lines and runs_without_counted_launch> | measured |
| how the session ended | <"session end"; queue.json stop: none / the stop's words>; runner.rc <0 / 8 HUNG / 1 a crash, its CRASH line> | measured |
| telemetry samples, and those at 600 MHz | <n> / <n at 600 MHz>; off the clock: <n> | measured |
| board power, peak; the shires' mean, peak; the latch (minshire[2]) at the start and its highest | <W>; <C>; <C> / <C> (the stops: 70 W on 3 samples, 70 C; the latch read as E206.md A1 item 1 and KIT.md 4.1 read it) | measured |
| the opening and closing configuration reads | <config start>; <config end, or "not read: <why>"> | measured (READ) |
| the identity lines | <the config read's PCIe target, physical device ID, minion_mv>; <the identity read's counts and the sampler's nodes>; <each smoke host's stderr targets and held nodes> | measured |
| per point: cycles an op (the wall: cycles_gemm / ops a minion a GEMM; the counter's mean: the host's cycles_per_op), seconds a GEMM, p_work, p_rest, J over idle and J with the card at rest (each run, and the point's mean) | <the table from reduce-e207.txt> | measured (reduce_e207.py) |
| the ties (t01 = E206's p001, at the start, the middle and the end) | <their t_gemm and J over idle; t01 beside E206 arm A's p001 on this card> | measured; the bridge reading is the scorer's (REPORTED) |
| the never-run search repeated right before the first card command (step 6n; `neverrun-e207-card.txt`, `neverrun-e207-card.json`, `ranbefore-e207-card.json`) | <its NEVER-RUN line: n of 53 points, m of 47 cases; RAN BEFORE, CASE RAN BEFORE and TO DATE (each with where and why, or "none"); AFTER THE FREEZE (REPORTED, kept in every rule); DESK-ONLY (dismissed, with the folders); aifoundry3 searched or NOT SEARCHED; the model session's `ee-*` folders not read; E208's arms file at the registered bytes or changed> | a desk read, REPORTED (a labelled point or case: the dated note, E207.md A1 items 2-3) |
| runs that printed no check of C (the reducer's `checks_missing`; collect's "checks of C" line) | <n of m runs; 0 expected; any such run named> | measured (E207.md A1 item 7: R0 cannot see them) |

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside
meter** (E184's arm S, the test of the meter itself, is pending). The joules over idle and with the card at rest carry that gain.

## Registered against happened

| registered (E207.md, plan-e207.json, KIT.md) | happened |
|---|---|
| aifoundry3 card 0 at 600 MHz as found; the start config TDP 0 W / 65 C / 600 MHz | <the config reads; the identity lines; the clock in every sample> |
| the rest: 40 minutes since our last session on aifoundry3 | <the box's last session of ours before E207 and its end; step 7's and step 9's "rest:" lines> |
| the window: G = the booking; last start G + 1:30, last end G + 3:30 | <G; the window; the launch before the last start; the session's start and end inside it> |
| the never-run search right before the first card command | <step 6n's time and line; step 7 within 30 minutes of it> |
| the smoke, then the stop-path test; the order t01, pass 1, t01, pass 2, t01 (109 runs) | <as run> |
| the stops and gates (KIT.md 4) | <any stop, gate wait or NO DATA run, and why> |
| reads only (dmcmd_audit_v2 GO); no SIGKILL; a plain timeout 10 on every device process | <the preflight's line; every process's rc; any HUNG line (then: reported and left)> |

## Departures (dated, before the results they touch)

- The go: <his words, as section 1 of CARD-LANE-BRIEF.md lists them>; G = the booking on its day; the post waived (his words, Sun 15 Nov 2026
  10:22:36 PST); the host's package counter not read; the desk aifoundry2 with `/usr/bin/python3` 3.12.3; the yvb3 session.
- The die line's hottest sensor read as E206.md's amendment A1 item 1 registers it and E207.md 6 adopts it (not a departure): the latch at
  <its start value> C.
- <any other: a step re-run, a wait, a sealed forecast registered before the day (its sha256 only, never its numbers), step 6n's --desk-only
  form, ...>

## Files

`session/` (the box's session directory, copied back exact and scrubbed), `data-e207.json` (the frozen scorer's input), `reduce-e207.txt` (the
reducer's table), `neverrun-e207-card.txt`, `neverrun-e207-card.json` and `ranbefore-e207-card.json` (step 6n's report and its dating, copied in
by the collection), when 6n names a RAN BEFORE, CASE RAN BEFORE or TO DATE one `README.md.dated-note-1.md` (and `ranbefore-e207-labels.json`
if a TO DATE one was dated after the freeze), `SHA256SUMS` (the collected files; the README, its dated note and the labels file lie beside
it, as the README does). The scorer's outputs and the after-score tool's (E207.md A1: THE
REGISTERED VERDICTS, the family-level check, the checks read) follow after the data commit (a later lane).
```

## The gate stop's record (no run started)

```
# E207, <day>: no run: <the gate's words> (a gate stop's record, never scored)

*<the day>, PST. The session <T0> on aifoundry3 stopped at <the gate> before any run: no data (E207.md 7: a point or case with no run is NO
DATA). <What the session did: the first card command or none; the identity lines if read; the smoke processes if any ran.> E207 may be tried
again as CARD-LANE-BRIEF.md section 3 says.*

## What happened
<the session log's lines from "session start" to "session end"; runner.rc; the runbook's step 10 reading>

## Departures
<as above>
```

SPDX-License-Identifier: Apache-2.0
