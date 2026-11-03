# E139: the memory path's split again, more passes - the encoded part pays on the board and shows on the DDR die rail (aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
item 10, the memory path, the two verdicts [E132](../2026-11-02-e132-memory-split/README.md) left UNRESOLVED. Mon 2 Nov 2026 (week 45),
Q137. Pre-registered in `96b141f8` (committed 15:35:59 PST), before the claim and before any E139 pass:
[`tools/claims-v3/e139/README.md`](../../../../tools/claims-v3/e139/README.md). aifoundry3 card 0 at 600 MHz in every one of 20,469
samples; `ettelem config` read at the session's start (16:04:41) and end (16:41:37): TDP 0 W, threshold 65 °C, max_power, 600 MHz,
523 mV, both alike, never set. **Every device-management command sent was a read** (E132's nine kinds, two of them PMIC
voltage-register reads, which the owner's rule of 2 November 2026 allows); no write of any kind (`since_reset_ms` −1 in every sample).
Card session 16:04:40–16:41:37 PST, **36.9 of the 45 card-minutes allowed**: the smoke 13901 and its gate, the warm-up 13910 and
**eight headline passes, 13911–13918** (one more than the seven projected: passes took 201–230 s against E132's 239–268 s, so the
queue's rule let 13918 start).*

**In plain words.** When a memory read crosses the DRAM bus, the bus re-encodes some bytes (data-bus inversion) so fewer wires
switch. E132 asked whether those *encoded* bit changes cost power of their own, beyond the raw bits the power model already counts,
and whether they show on the DDR die's own supply; it could not quite say. E139 ran E132's images again, unchanged, eight more times.
**Both answers are now yes, on E139's passes alone**: the encoded part costs +0.213 W [0.150, 0.275] where 56 encoded toggles a line
move and +0.213 W [0.128, 0.298] where 448 move (**R4 PAYS**, about 0.46 pJ an encoded toggle), and it pulls the DDR die rail down
by 0.75 mV [0.52, 0.98] while the control that moves only raw bits leaves it still, −0.01 mV [−0.05, +0.02] (**R3 ENCODED**).
Both are **SETTLED** by the registered joint reading (the primary decides them; the pool with E132 agrees). My frozen expectation
was "more likely settled only pooled"; it settled alone.

## Results

Eight headline passes, none set aside on the primary (the board meter's dips removed, leakage `auto`; `e139.json`), as registered.

**1. The two rules E139 was run to settle** (registered primary = E139's passes alone):

| rule | quantity | E139 (n 8) | class | verdict | E132 (n 6) | pool E132 + E139 (n 14, secondary) | joint reading |
|---|---|---|---|---|---|---|---|
| **R3** encoded part at the DDR die rail | `el_64z` (raw control) | −0.013 mV [−0.050, +0.025] | still | **ENCODED: PASS** | −0.09 [−0.31, +0.13], UNRESOLVED | −0.046 [−0.119, +0.027], still: ENCODED | **SETTLED (ENCODED)** |
| | `RE64` (encoded) | −0.751 mV [−0.979, −0.524] | moves | | −0.77 [−1.02, −0.52] | −0.758 [−0.888, −0.627] | |
| | `wl_64z`, `eh_64z` | | both move | | | | |
| **R4** encoded part on the board | `E56` | +0.213 W [0.150, 0.275] | present | **PAYS: PASS** | +0.118 [−0.002, +0.237], UNRESOLVED | +0.172 [0.119, 0.224] | **SETTLED (PAYS)** |
| | `E448` | +0.213 W [0.128, 0.298] | present | | +0.166 [0.121, 0.210] | +0.193 [0.150, 0.237] | |

At every arm (leakage 0.2936 and 0.3803 W/°C; dips kept) R3 reads ENCODED and R4 PAYS: no verdict moves at an arm (`e139-leak*.json`,
`e139-unfiltered.json`). The frozen per-quantity guesses: `E56` near +0.12 W (read +0.21), `E448` near +0.17 (+0.21), `el_64z` near
−0.1 mV (−0.01), `RE64` near −0.77 (−0.75).

**2. The re-tests** (E132's rules and constants, unchanged; E132 PASSED all four):

| rule | E139 | pool (reported) |
|---|---|---|
| R1 the tie to E110 (six items within 0.3 W) | **PASS** (S128 0.145, S64 0.366, U4z 1.578, V128 0.304, V16 0.458, V64 0.663 W) | PASS |
| R2 where the line-to-line changes are paid | **PASS, EDGES**: `R_4` +0.290 W [0.244, 0.336], off every metered rail (rails sum −0.021 W) | PASS, EDGES |
| R5 the rail steps | **PASS** (board, NoC, SRAM, off PASS; minion UNRESOLVED) | **FAIL** (the NoC rail's class pattern) |
| R6 the high pins and the DDR rail | **PASS**: `Hp` +0.308 W [0.233, 0.384], 1.37 pJ a high pin a beat-line, RH64 and RH128 still | PASS |

The pool's R5 FAIL is reported only (the registered reading of R5 is E139's own); E132 alone and E139 alone each PASS it, so it is a
pooling of two sessions whose NoC-rail rung classes differ, not a new failure of the rule on either.

**3. What it does to predicting power and heat.** The power model prices memory traffic by toggled raw bits (E110's 64-bit path 0.71
pJ, 256-bit path 2.38 pJ or 1.15 with line edges; E132's line-edge placement). E139 adds **one term, settled: an encoded-toggle price on
the DRAM bus, 0.46 pJ an encoded toggle** (E56 0.463, E448 0.463 pJ on E139's passes; the pool 0.37 and 0.42), against E132's
provisional 0.26–0.36. On the two E-family images the residual the model leaves without the term, and with E132's frozen +0.185 W:

| | E132's passes: rms of `E56`, `E448` | E139's passes |
|---|---:|---:|
| model without an encoded term (residual = the encoded part) | 0.144 W | 0.213 W |
| with the frozen +0.185 W per image | 0.049 W | 0.028 W |

So the term removes most of the error on DRAM-bound images whose bus re-encodes bytes (up to about 0.2 W on this card), and E139
measured it on passes the term was not fitted on: the frozen +0.185 W predicted E139's +0.213 W to 0.028 W. And because RE64 moves the
DDR die rail while the raw control does not (R3), the term can be tied to the memory shire's supply, a reading every run already
records. **Heat**: the term enters only through board power, 0.2 W times the card's die rise per board watt (M6's heat term), a few
tenths of a degree at most; E139 measures no heat term (the die stayed at 57–58 °C through every pass).

## Registered against what happened

| | registered | happened |
|---|---|---|
| passes | warm-up 13910 + headline 13911 onward, queue deadline start + 42 min | 13910 + **13911–13918** (eight headline); passes 201–230 s |
| card time | ≤ 45 min | 36.9 min |
| stops | die 70 °C; board 65 W (`watch_e139.py`) | highest die 61 °C, board 53.52 W; no stop (`logs/watch.log` records only the watcher's start) |
| A1-style form check | config 0 W / 65 °C / 600 MHz at both ends; `since_reset_ms` −1 | PASS (both reads; −1 in all 20,469 samples) |
| expectation | R3 ENCODED, R4 PAYS, more likely SETTLED ONLY POOLED; R1, R2, R5, R6 PASS | R3, R4 SETTLED on the primary; R1, R2, R5, R6 PASS |
| departures | — | **D1**: eight headline passes, one more than the README's projected seven; the queue's registered rule (start + 42 min, longest pass so far) decided it, as the README allows ("13918 runs only if the passes run short"). **D2**: the reducer labels its output `"exp": "E132"` (its code is E132's, unchanged), as the registration said. **D3**: the collector's Python was numpy through `uv` on the Intel. **D4**: the session ran no separate form-check script; the check above was made on the collected files after the session |

## Device commands sent

As registered (the registration's § Device commands sent, E132's list): the stock `ettelem config` at the session's start and end and
`ettelem sample` through the session; all nine command kinds are READs, two of them PMIC voltage-register reads; the host program
(`enercat_host`, E99's, sha256 `f6633f1c…`, E132's binary) opens the ops node only. Never sent: the statistics reset, any SET_*, the
firmware-revisions query, a residency read. The checker's output is the registration's `dmcmd-audit.txt` (GO with the reviewed
`lib.sh:154` exception). Residual: aifoundry3's 7 Oct thermal build is not public (E130's A1).

## Card and post

`et-who` at the session's start and end: no process held a device node or card lock; other users' idle logins present, no device
process of theirs. The card was held from E138's session; the day's post (message 1566837317765963987) had its aifoundry3 clause
rewritten at 16:04:40 PST from "until ~16:39 PST" to "using aifoundry3 for 1 h, until ~17:10 PST" (EXPECT_TEXT, dry run, then save)
before this session started, and at 16:43:09 to "until ~17:40 PST" for E140, which followed on the same card.

## What it changes

- **Item 10**: the memory path's split is settled on this card: the encoded part pays (0.46 pJ an encoded toggle) and shows on the
  DDR die rail; the raw line-to-line part stays where E132 put it (off every metered rail).
- **The power model**: add the encoded-toggle term to the memory path (0.46 pJ, or E132's frozen +0.185 W per image as tested here).
  One card; E139 does not test another card or other images.

## Files

`e139.json` (primary), `runs.csv`, `e139-leak0.2936.json`, `e139-leak0.3803.json`, `e139-unfiltered.json` (dips kept),
`e139-pooled.json` (the secondary), `dips.json`, `dips-e132-pooled.json`, `passes/p139*` (raw: per-run records, telemetry, block.json),
`logs/` (session log, queue, smoke, watcher, the session's two config reads).
