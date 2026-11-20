# E218's data README: the form the card lane fills for its data commit (Q230, lane kit-e218; kitted, not run)

*Thu 19 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md); E215 arm A's form ([../e215/DATA-README-FORM-e215.md](../e215/DATA-README-FORM-e215.md),
landed 8bde0182, whose arm A README followed it) for E218's one data directory. This is the form of `README.md` in
`docs/reports/data/<day>-e218-blind-matmul-aifoundry3/`, written by the card lane (`card-e218`) after step 12 (the collection) and before the data
commit, for a session in which at least one run started, in the lab's data-README form: **results first, then registered against happened, then
departures, each dated**. It is a form, not a result: every `<...>` is filled from the session's own files (`session/session.log`,
`session/queue.json`, `session/identity.json`, `data-e218.json`, `reduce-e218.txt`, the runbook's log, step 6n's report and judgement), and every
number carries its label. The README lies beside the data and is not in its `SHA256SUMS` (the collector made that list over the collected files).
A session in which no run started has no data directory: step 12 collects it into a gate stop's record, whose README has the shorter form at the
end of this file. The scorer runs after the data commit (step 13): its words are not in this README at the commit; a later lane adds them in a
dated note beside it.*

**The rules for this file.** No number from the owner's private pages or his A100 report. No sealed forecast's number (a sealed sha256 only, as
`tools/claims-v3/sealed-e218/` registers it). No lab user's login (the collector's scrub masked ours; write `<login>`). No credential or access
path. Times Pacific. The interpreter named. A check not run is NOT RUN. His words quoted without links. **The forecasts are BLIND**: every declared
model's frozen at MM1-v3.2's land `4e386f75` (pushed 19:50:09 PST Thu 19 Nov 2026: `tools/matmul/mm1/v3.2/out/e218/forecasts-e218.csv`
`52e78762...`, `forecasts-e218.json` `1236dd99...`), and 'MM1-v3.2 without its gemmLnc term' frozen by the registration commit
(`tools/claims-v3/e218/forecast-e218-reg.csv` `9edcf6ee...`); quote them only from their frozen files.

---

```
# E218, <day>, aifoundry3 card 0 at its pinned 600 MHz: MM1-v3.2's blind matmul day (52 points: G 12, Gt 11, Y 15, F 14; the tie t01): <RAN FULL (the
opening smoke, the stop-path test, <n> of 107 runs and the G block's smoke s03) / RAN SHORT (<n> of 107 runs: <why>) / STOPPED at <the stop> after <n> runs>

*<the day>, PST. E218, registered before any datum (<the registration's landed commit>: the freeze line of 'MM1-v3.2 without its gemmLnc term', the
rules and the scorer), kitted (<the kit's landed commit>), verified (<lane, verdict>) and readiness-checked (<lane, verdict>); run on the owner's go
(<his words and their times>). The forecasts' freeze line, MM1-v3.2's land 4e386f75 (committed 19:50:04 PST Thu 19 Nov 2026), and the registration
commit were on GitHub main before the booking; step 0 read both (<the STEP0-E218 line>). rgm136 (E136's binary, unchanged) and rgm211's host tree
(E211's) built today on the box: rgm136's ELF through THE KERNEL GATE and rgm211's tree through THE TREE GATE (<the build record's two gate lines>);
every process gated by its family's ELF - both families run rgm136's ELF ('rgm136 gemmL' on rgm136's host; 'rgm136 gemmLnc' on rgm211's host,
walk mn). Nothing was set on the card.*

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | <queue.json card_min> (planned 48.0; no run after 60, cap 70); step 7's config read at <RB_OUT/e218-step7-A.txt>, reported apart | measured (the session's clock) |
| the opening smoke, then the stop-path test | s01 gemmL2x2x2 fp32 (rgm136's host and ELF: the session's gate), 2 s: <its identity gate, the check of C, the counter's mean, the board's rise; the stop-path test's words> | measured |
| THE G BLOCK, LAST, AND ITS SMOKE s03 (E218.md 3, its own stop path) | <s03 gemmLnc2x2x2 fp32 (rgm211's host, rgm136's ELF) at place 84 after its own 10 s rest: good / FAILED for its family alone (its words; queue.json's families_dropped; then g01-g12 not started, NO DATA)>; then the G runs (g08 g04 g11 g01 g03 g02 g10 g12 g06 g07 g05 g09, then reversed): each started or not, and why; the board's peak in the block against the 70 W x3 stop; a board stop there, if any, and the runs it cost | measured |
| THE IDENTITY GATE PER PROCESS | <every process's gate words by its family ('rgm136 gemmL', 'rgm136 gemmLnc'): "GATE OK: ..." for each, or the first GATE FAILED and where the session stopped> | measured (the gate's reading of the box's ELFs) |
| THE WALK CHECK | <every rgm211-host process ('rgm136 gemmLnc', walk mn): walk_ok true on every launch and walk_launches_bad 0, or the first failure and THE KERNEL STOP it caused> | measured |
| runs: started, with counted launches, not started (why) | <n started> / <n with t_gemm> / <reduce-e218.txt's "not started" lines and runs without a counted launch> | measured |
| how the session ended | <"session end"; queue.json stop: none / the stop's words (a kernel stop names its run and family)>; runner.rc <0 / 8 HUNG / 1 a crash, its CRASH line> | measured |
| telemetry samples, and those at 600 MHz | <n> / <n at 600 MHz>; off the clock: <n> | measured |
| board power, peak; the shires' mean, peak; the latch (minshire[2]) at the start and its highest | <W>; <C>; <C> / <C> (the stops: 70 W on 3 samples, 70 C; the latch read as E213 and E215 arm A read it; the planning line 67.0 W; the highest planning peak 56.46 W at g09; E215's gemmLnc bounds REPORTED, the highest 65.44 W at g05) | measured |
| the opening and closing configuration reads | <config start>; <config end, or "not read: <why>"> | measured (READ) |
| the identity lines | <the config read's PCIe target and physical device ID>; <the identity read's counts and the sampler's nodes>; <each smoke host's stderr targets and held nodes> | measured |
| per point: cycles an op (the wall: cycles_gemm / ops a minion a GEMM; the counter's mean: the host's cycles_per_op), seconds a GEMM, p_work, p_rest, the die at the start (each run, and the point's mean) | <the table from reduce-e218.txt> | measured (reduce_e218.py) |
| the never-run search repeated right before the first card command (step 6n; `neverrun-e218-card.txt`, `.json`; `judge-e218-card.txt`, `.json`; `labels-e218.json`) | <its NEVER-RUN-E218 line: n of 52 registered points never ran; ran, labelled 'ran before' (E218.md 4): <none / the points, each file's date against the freeze line REPORTED>; the scan's files read> | a desk read; the labels go to the scorer |

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside
meter** (E184's arm S, the test of the meter itself, is pending). The watts carry that gain.

## Registered against happened

| registered (E218.md, plan-e218.json, KIT.md) | happened |
|---|---|
| aifoundry3 card 0 at 600 MHz as found; the start config TDP 0 W / 65 C / 600 MHz | <the config reads; the identity lines; the clock in every sample> |
| the freeze lines on GitHub main before the booking (MM1-v3.2's land; the registration commit; the kit commit) and the sealed-forecast check (step 0) | <the STEP0-E218 line; any seal registered in tools/claims-v3/sealed-e218/ (its sha256 only; a later seal in a new note, its record line a comment)> |
| the rest: 40 minutes since our last session on aifoundry3 | <the box's last session before E218 and its end; step 7's and step 9's "rest:" lines> |
| the window: G = the booking; last start G + 1:30, last end G + 3:30 | <G; the window; the launch before the last start; the session's start and end inside it> |
| the never-run search right before the first card command | <step 6n's time and line; step 7 within 30 minutes of it> |
| the opening smoke s01, then the stop-path test; the order: tie t01, pass 1 (40: every Gt, Y and F point once), tie, pass 2 (40, reversed), tie, then the G block (s03 and 24 runs): 107 runs and 2 smoke processes | <what ran, in order; any run not started and why> |
| the identity gate per process (both families); the walk check; the kernel stops for the rgm211-host family | <every gate OK, every walk OK, or the stop> |
| the stops and gates (KIT.md 4) | <any stop, gate wait or NO DATA run, and why> |
| reads only (dmcmd_audit_v2 GO); no SIGKILL; a plain timeout 10 on every device process | <the preflight's line; every process's rc; any HUNG line (then: reported and left)> |

## Departures (dated, before the results they touch)

- The go: <his words, as section 1 of CARD-LANE-BRIEF.md lists them>; G = the booking on its day; the post waived (his words, Sun 15 Nov 2026
  10:22:36 PST); the host's package counter not read; the desk aifoundry2 with `/usr/bin/python3` 3.12.3; the yvb3 session.
- The registration's D1 (g07t and y03a dropped before any datum; the orchestrator's answer of Thu 19 Nov 2026: keep the drop, 52 points) is a
  registered item, not a departure of the day; say so.
- The die line's hottest sensor read as E213 and E215 arm A read it (not a departure): the latch at <its start value> C.
- <any other: a step re-run, a wait, a sealed forecast registered before the day (its sha256 only, never its numbers), a point labelled 'ran
  before' by step 6n (the dated note's name), ...>

## Files

`session/` (the box's session directory, copied back exact and scrubbed), `data-e218.json` (the frozen scorer's input), `reduce-e218.txt` (the
reducer's table), `neverrun-e218-card.txt`, `neverrun-e218-card.json`, `judge-e218-card.txt`, `judge-e218-card.json` and `labels-e218.json`
(step 6n's report, judgement and labels, copied in by the collection), `SHA256SUMS` (all of these). The scorer's outputs follow after the data
commit (a later lane).
```

## The gate stop's record (no run started)

```
# E218, <day>: no run: <the gate's words> (a gate stop's record, never scored)

*<the day>, PST. The session <T0> on aifoundry3 card 0 stopped at <the gate> before any run: no data (E218.md 7: a point or case with no run is
NO DATA). <What the session did: the first card command or none; the identity lines if read; the smoke process if it ran, with its identity
gate.> E218 may be tried again as CARD-LANE-BRIEF.md section 3 says.*

## What happened
<the session log's lines from "session start" to "session end"; runner.rc; the runbook's step 10 reading>

## Departures
<as above>
```

SPDX-License-Identifier: Apache-2.0
