# E206's data README: the form each arm's card lane fills for its data commit (Q198, lane kit-e206; kitted, not run)

*Mon 16 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md); E202's form ([../e202/DATA-README-FORM-e202.md](../e202/DATA-README-FORM-e202.md))
for E206's one-arm data directories. This is the form of `README.md` in `docs/reports/data/<day>-e206-matmul-sweep-aifoundry3/` (arm A) or
`...-aifoundry1-c1/` (arm B), written by that arm's card lane after step 12 (the collection) and before the data commit, for a session in which
at least one run started, in the lab's data-README form: **results first, then registered against happened, then departures, each dated**. It
is a form, not a result: every `<...>` is filled from the session's own files (`session/session.log`, `session/queue.json`,
`session/identity.json`, `data-e206.json`, `reduce-e206.txt`, the runbook's log), and every number carries its label. The README lies beside
the data and is not in its `SHA256SUMS` (the collector made that list over the collected files). A session in which no run started has no data
directory: step 12 collects it into a gate stop's record, whose README has the shorter form at the end of this file. The scorer runs after the
data commit (step 13): its words are not in this README at the commit; a later lane adds them in a dated note beside it.*

**The rules for this file.** No number from the owner's private pages or his A100 report. No sealed forecast's number. No lab
user's login (the collector's scrub masked ours; write `<login>`). No credential or access path. Times Pacific. The interpreter named. A check
not run is NOT RUN. His words quoted without links.

---

```
# E206 arm <A|B>, <day>, <aifoundry3 card 0 | aifoundry1 card 1> at 600 MHz as found: the matmul sweep: <RAN FULL (the smoke, the
stop-path test, <n> of <241|229> runs) / RAN SHORT (<n> of <241|229> runs: <why>) / STOPPED at <the stop> after <n> runs>

*<the day>, PST. E206, registered before any datum (<the registration's landed commit>; forecasts frozen in forecast-e206.json, sha256
d8f3a8b1...), kitted (<the kit's landed commit>), verified (<lane, verdict>) and readiness-checked (<lane, verdict>); run on the owner's go
(<his words and their times>). rgm136 (E136's binary, unchanged), built today on the box through the kernel gate (<the build record's
gate line>). Nothing was set on the card.*

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | <queue.json card_min> (no run after 112, cap 120); step 7's config read at <RB_OUT/e206-step7-<arm>.txt>, reported apart | measured (the session's clock) |
| the smoke: p001, p046, p021 (2 s each), then the stop-path test | <each: rc, launches, the check, cycles an op and its ratio to F1's point, the board's rise, the host's card>; the stop-path test <passed> | measured |
| runs: started, with counted launches, not started (why) | <n started> / <n with t_gemm> / <reduce-e206.txt's "not started" lines and runs_without_counted_launch> | measured |
| how the session ended | <"session end"; queue.json stop: none / the stop's words>; runner.rc <0 / 8 HUNG / 1 a crash, its CRASH line> | measured |
| telemetry samples, and those at 600 MHz | <n> / <n at 600 MHz>; off the clock: <n> | measured |
| board power, peak; the shires' mean, peak; the latch (minshire[2]) at the start and its highest | <W>; <C>; <C> / <C> (the stops: arm A 70 W / 70 C, arm B 72 W / 80 C; the latch read as E206.md A1 item 1 and KIT.md 4.1 read it) | measured |
| the opening and closing configuration reads | <config start>; <config end, or "not read: <why>"> | measured (READ) |
| the identity lines | <the config read's PCIe target, physical device ID, minion_mv>; <the identity read's counts and the sampler's nodes>; <each smoke host's stderr targets and held nodes> | measured |
| per point: cycles an op, cycles a GEMM, seconds a GEMM, p_work, p_rest, J over idle and J with the card at rest (each run, and the point's mean) | <the table from reduce-e206.txt> | measured (reduce_e206.py) |
| the ties (p001 at the start, the middle and the end) | <their t_gemm and J over idle> | measured; the drift reading is the scorer's (REPORTED) |
| the never-run search re-run before the commit (desk/neverrun_e206.py) | <which points another session (the model session's sweeps) ran first, or "none"> | a desk read, REPORTED |

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside
meter** (E184's arm S, the test of the meter itself, is pending). The joules over idle and with the card at rest carry that gain.

## Registered against happened

| registered (E206.md, plan-e206.json, KIT.md) | happened |
|---|---|
| <arm A: aifoundry3 card 0 at 600 MHz as found; the start config TDP 0 W / 65 C / 600 MHz> <arm B: aifoundry1 card 1, ET_DEVICES=1, card 1's lock; 65 W / 65 C / 600 MHz; nothing on card 0> | <the config reads; the identity lines; the clock in every sample> |
| the rest: 40 minutes since our last session on the box (on aifoundry1, either card) | <the box's last session of ours before E206 and its end; step 7's and step 9's "rest:" lines> |
| the window: G = the booking; last start G + 1:30, last end G + 3:30 | <G; the window; the session's start and end inside it> |
| the smoke, then the stop-path test; the order tie, pass 1, tie, pass 2, tie | <as run> |
| the stops and gates (KIT.md 4) | <any stop, gate wait or NO DATA run, and why> |
| reads only (dmcmd_audit_v2 GO); no SIGKILL; a plain timeout 10 on every device process | <the preflight's line; every process's rc; any HUNG line (then: reported and left)> |

## Departures (dated, before the results they touch)

- The go: <his words, as section 1 of CARD-LANE-BRIEF.md lists them>; G = the booking on its day; the post waived (his words, Sun 15 Nov 2026
  10:22:36 PST); the host's package counter not read; the desk aifoundry2 with `/usr/bin/python3` 3.12.3; the yvb3 session.
- The die line's hottest sensor read as E206.md's amendment A1 item 1 registers it (KIT.md section 4 item 1; not a departure): the latch at <its start value> C.
- <any other: a step re-run, a wait, a sealed forecast registered before the arm (its sha256 only, never its numbers), ...>

## Files

`session/` (the box's session directory, copied back exact and scrubbed), `data-e206.json` (the frozen scorer's input), `reduce-e206.txt` (the
reducer's table), `SHA256SUMS`. The scorer's outputs follow after the data commit (a later lane).
```

## The gate stop's record (no run started)

```
# E206 arm <A|B>, <day>: no run: <the gate's words> (a gate stop's record, never scored)

*<the day>, PST. The session <T0> on <box> stopped at <the gate> before any run: no data (E206.md 7: a point with no run is NO DATA).
<What the session did: the first card command or none; the identity lines if read; the smoke processes if any ran.> The arm may be tried
again as CARD-LANE-BRIEF.md section 3 says.*

## What happened
<the session log's lines from "session start" to "session end"; runner.rc; the runbook's step 10 reading>

## Departures
<as above>
```

SPDX-License-Identifier: Apache-2.0
