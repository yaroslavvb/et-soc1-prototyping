# E222's data README: the form the card lane fills for its data commit (Q236, lane kit-e222; kitted, not run)

*Fri 20 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md); E218's form ([../e218/DATA-README-FORM-e218.md](../e218/DATA-README-FORM-e218.md),
kit 5582edfc, whose README of E218's data `b445b0f5` followed it) for E222's one data directory. This is the form of `README.md` in
`docs/reports/data/<day>-e222-blind-matmul-aifoundry3/`, written by the card lane (`card-e222`) after step 12 (the collection) and before the data
commit, for a session in which at least one run started, in the lab's data-README form: **results first, then registered against happened, then
departures, each dated**. It is a form, not a result: every `<...>` is filled from the session's own files (`session/session.log`,
`session/queue.json`, `session/identity.json`, `data-e222.json`, `reduce-e222.txt`, the runbook's log, step 6n's report and judgement), and every
number carries its label. The README lies beside the data and is not in its `SHA256SUMS` (the collector made that list over the collected files).
A session in which no run started has no data directory: step 12 collects it into a gate stop's record, whose README has the shorter form at the
end of this file. The scorer runs after the data commit (step 13): its words are not in this README at the commit; a later lane adds them in a
dated note beside it.*

**The rules for this file.** No number from the owner's private pages or his A100 report. No sealed forecast's number (a sealed sha256 only, as
`tools/claims-v3/sealed-e222/` registers it). No lab user's login (the collector's scrub masked ours; write `<login>`). No credential or access
path. Times Pacific. The interpreter named. A check not run is NOT RUN. His words quoted without links. **The forecasts are BLIND**: every
forecaster's (MM1-v3.2, the three MM1-v3.3 candidates 'MM1-v3.2 + posimb', 'MM1-v3.2 + AF4' and 'MM1-v3.2 + L3S', 'MM1-v3.2 + all three' by
construction, MM1-v3.1, MM1-v3, MM1-v2) frozen by `OUT/reg-e222/FROZEN.txt` (written 13:50:25 PST Fri 20 Nov 2026, sha256 `172ed079...`, posted
13:51:12 PST before any E220 or E222 datum) and by the registration commit (`tools/claims-v3/e222/forecast-e222.json` `c4630d19...`, `.csv`
`223f943e...`, `.txt` `f2d8047f...`); quote them only from their frozen files.

---

```
# E222, <day>, aifoundry3 card 0 at its pinned 600 MHz: the MM1-v3.3 candidates' blind day (70 points: T 32, L3b 10, Y3 10, G3 7, G3t 7, R 4; the tie t01): <RAN FULL (the
opening smoke, the stop-path test, <n> of 120 runs and the G block's smoke s03) / RAN SHORT (<n> of 120 runs: <why>) / STOPPED at <the stop> after <n> runs>

*<the day>, PST. E222, registered before any datum (<the registration's landed commit>: its push E222's second freeze line, of every forecast, the
points, the rules, the plan and the scorer; the first FROZEN.txt's post, 13:51:12 PST Fri 20 Nov 2026), kitted (<the kit's landed commit>),
verified (<lane, verdict>) and readiness-checked (<lane, verdict>); run on the owner's go (<his words and their times>). The posted freeze line,
MM1-v3.2's land 4e386f75 and the three candidates' lands (badf08fa, 911651ee, 2a509f5a) and the registration commit were on GitHub main before the
booking; step 0 read them (<the STEP0-E222 line>). rgm136 (E136's binary, unchanged) and rgm211's host tree (E211's) built today on the box:
rgm136's ELF through THE KERNEL GATE and rgm211's tree through THE TREE GATE (<the build record's two gate lines>); every process gated by its
family's ELF - both families run rgm136's ELF ('rgm136 gemmL' on rgm136's host; 'rgm136 gemmLnc' on rgm211's host, walk mn). Nothing was set on
the card.*

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | <queue.json card_min> (planned 50.7; no run after 70, cap 80); step 7's config read at <RB_OUT/e222-step7-A.txt>, reported apart | measured (the session's clock) |
| the opening smoke, then the stop-path test | s01 gemmL2x2x2 fp32 (rgm136's host and ELF: the session's gate; E218's registered smoke), 2 s: <its identity gate, the check of C, the counter's mean, the board's rise; the stop-path test's words> | measured |
| THE G BLOCK, LAST, AND ITS SMOKE s03 (E222.md 3 and 6, its own stop path) | <s03 gemmLnc2x2x2 fp32 (rgm211's host, rgm136's ELF) at the kit's place 99 (the registered place 100) after its own 10 s rest: good / FAILED for its family alone (its words; queue.json's families_dropped; then rg01, wn01-wn07 and k01-k07 not started, NO DATA)>; then the G runs (wn01 wn05 wn04 wn03 wn02 wn06 wn07 k01 k02 k03 k04 rg01 k06 k05 k07, then k07 k05 k06 k04 k03 k02 k01): each started or not, and why; the board's peak in the block against the 70 W x3 stop; a board stop there, if any, and the runs it cost | measured |
| THE IDENTITY GATE PER PROCESS | <every process's gate words by its family ('rgm136 gemmL', 'rgm136 gemmLnc'): "GATE OK: ..." for each, or the first GATE FAILED and where the session stopped> | measured (the gate's reading of the box's ELFs) |
| THE WALK CHECK | <every rgm211-host process ('rgm136 gemmLnc', walk mn): walk_ok true on every launch and walk_launches_bad 0, or the first failure and THE KERNEL STOP it caused> | measured |
| runs: started, with counted launches, not started (why) | <n started> / <n with t_gemm> / <reduce-e222.txt's "not started" lines and runs without a counted launch> | measured |
| every process inside the plain timeout 10 (E218's R0 lesson; desk/timeout_e222.py) | <the longest process's length; any rc 124 and its run; every check of C exact or approx> | measured |
| how the session ended | <"session end"; queue.json stop: none / the stop's words (a kernel stop names its run and family)>; runner.rc <0 / 8 HUNG / 1 a crash, its CRASH line> | measured |
| telemetry samples, and those at 600 MHz | <n> / <n at 600 MHz>; off the clock: <n> | measured |
| board power, peak; the shires' mean, peak; the latch (minshire[2]) at the start and its highest | <W>; <C>; <C> / <C> (the stops: 70 W on 3 samples, 70 C; the latch read as E213, E215 arm A and E218 read it; the drop line 67.0 W; the highest planning peak 55.54 W at k07) | measured |
| the opening and closing configuration reads | <config start>; <config end, or "not read: <why>"> | measured (READ) |
| the identity lines | <the config read's PCIe target and physical device ID>; <the identity read's counts and the sampler's nodes>; <each smoke host's stderr targets and held nodes> | measured |
| per point: cycles an op (the wall: cycles_gemm / ops a minion a GEMM; the counter's mean: the host's cycles_per_op), seconds a GEMM, p_work, p_rest, the die at the start (each run, and the point's mean) | <the table from reduce-e222.txt> | measured (reduce_e222.py) |
| the never-run search repeated right before the first card command (step 6n; `neverrun-e222-card.txt`, `.json`; `judge-e222-card.txt`, `.json`; `labels-e222.json`) | <its NEVER-RUN-E222 line: n of 66 registered non-R points never ran on aifoundry3 card 0 by session records; ran before, labelled: <none / the points and the session records found>; family R RAN (exempt by family name: same-card repeats, REPORTED only); the positive control 4 of 4 RAN; the literal reading REPORTED; the scan's files read> | a desk read; the labels go to the scorer |

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside
meter** (E184's arm S, the test of the meter itself, is pending). The watts carry that gain.

## Registered against happened

| registered (E222.md, plan-e222.json, KIT.md) | happened |
|---|---|
| aifoundry3 card 0 at 600 MHz as found; the start config TDP 0 W / 65 C / 600 MHz | <the config reads; the identity lines; the clock in every sample> |
| the freeze lines (FROZEN.txt's post; MM1-v3.2's land and the candidates' lands; the registration commit; the kit commit) and the sealed-forecast check (step 0) | <the STEP0-E222 line; any seal registered in tools/claims-v3/sealed-e222/ (its sha256 only; a later seal in a new note, its record line a comment)> |
| the rest: 40 minutes since the last session on aifoundry3 card 0 | <the box's last session before E222 and its end (E218's ended 03:56:36 PST Fri 20 Nov 2026, or a later one); step 7's and step 9's "rest:" lines> |
| the window: G = the booking; last start G + 1:30, last end G + 3:30 | <G; the window; the launch before the last start; the session's start and end inside it> |
| the never-run search right before the first card command | <step 6n's time and line; step 7 within 30 minutes of it> |
| the opening smoke s01, then the stop-path test; the order: tie t01, pass 1 (55: every non-gemmLnc point once), tie, pass 2 (40: the L3b, Y3, T-L3, T-Y2 and R-Y points, pass 1's order reversed), tie, then the G block (s03 and 22 runs: every gemmLnc point once by PP32 ascending, then the G3 points again in reverse): 120 runs and 2 smoke processes | <what ran, in order; any run not started and why> |
| the identity gate per process (both families); the walk check; the kernel stops for the rgm211-host family | <every gate OK, every walk OK, or the stop> |
| the stops and gates (KIT.md 4) | <any stop, gate wait or NO DATA run, and why> |
| reads only (dmcmd_audit_v2 GO); no SIGKILL toward a device process; a plain timeout 10 on every device process | <the preflight's line; every process's rc; any HUNG line (then: reported and left)> |

## Departures (dated, before the results they touch)

- The go: <his words, as section 1 of CARD-LANE-BRIEF.md lists them>; G = the booking on its day; the post waived (his words, Sun 15 Nov 2026
  10:22:36 PST); the host's package counter not read; the desk aifoundry2 with `/usr/bin/python3` 3.12.3; the yvb2 session.
- Family R (E218's own y01a, y01b, g01, g01t, re-run here) is in no rule (E222.md 3): its repeats are REPORTED against E218's committed data by the
  scorer; say so.
- The die line's hottest sensor read as E213, E215 arm A and E218 read it (not a departure): the latch at <its start value> C.
- <any other: a step re-run, a wait, a sealed forecast registered before the day (its sha256 only, never its numbers), a point labelled 'ran
  before' by step 6n (the dated note's name), ...>

## Files

`session/` (the box's session directory, copied back exact and scrubbed), `data-e222.json` (the frozen scorer's input), `reduce-e222.txt` (the
reducer's table), `neverrun-e222-card.txt`, `neverrun-e222-card.json`, `judge-e222-card.txt`, `judge-e222-card.json` and `labels-e222.json`
(step 6n's report, judgement and labels, copied in by the collection), `SHA256SUMS` (all of these). The scorer's outputs follow after the data
commit (a later lane), the cross-card rule once E220's data are committed and verified.
```

## The gate stop's record (no run started)

```
# E222, <day>: no run: <the gate's words> (a gate stop's record, never scored)

*<the day>, PST. The session <T0> on aifoundry3 card 0 stopped at <the gate> before any run: no data (E222.md 7: a point or case with no run is
NO DATA). <What the session did: the first card command or none; the identity lines if read; the smoke process if it ran, with its identity
gate.> E222 may be tried again as CARD-LANE-BRIEF.md section 3 says.*

## What happened
<the session log's lines from "session start" to "session end"; runner.rc; the runbook's step 10 reading>

## Departures
<as above>
```

SPDX-License-Identifier: Apache-2.0
