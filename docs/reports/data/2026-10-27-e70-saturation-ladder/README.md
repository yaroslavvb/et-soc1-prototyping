# E70 — the saturation ladder and the A-side multi-bit ladder (Q129, aifoundry3, 2026-10-27)

*Pre-registered in [`tools/claims-v3/hs/README.md`](../../../tools/claims-v3/hs/README.md) — three candidate laws,
per-rung predictions from each, five discriminators D1–D5, eight scored predictions P1–P8, four departures D-a…D-d
and amendments A18/A19 — committed as `bd39b335` at **14:07:07 PDT, 42 s before the card was claimed (14:07:49 PDT,
from the Discord message's own snowflake) and 1 min 33 s before the first measured launch (14:08:40 PDT)**. Card runs
2026-10-27, 14:08:40 → 14:43:20 PDT, **aifoundry3 only**, whose governor is latched at 600 MHz by its boot-time
TDP 0, so every number here is a 600 MHz, 521.6 mV number — the same card, clock and voltage as E65's B-side scan and
E67's A-side scan, which is what lets the three price lists be added without a conversion. Claimed in
`#community-lab` at 14:07:49 PDT, released by appending to that claim after this README was pushed (E67's A17).
**No card setting was changed: no clock was set and the governor was not touched.***

## The headline

The per-bit price list E65 and E67 built over-predicts a whole random word by **about 2×** (E67's closure: ratios
0.43 and 0.50). Q128 §5 named two candidate causes — **shared wires**, where the deficit is set by *which* bits
flip, and **interaction**, where it is set by *how many*. E70 turned the one knob that separates them, the layout of
the flipping bits at fixed Hamming weight, and the answer is not close:

**It is the wires. The deficit is set by which bits flip, and one parameter describes it.**

| fit over the 15 B-side rungs (9 low-layout + 7 spread, the shared h = 23 point excluded) | residual rms |
|---|---|
| the best **any** "how many" law can do (a free value per h) | 1.358 W |
| **one saturating curve in the additive sum**, `ΔW = W∞·(1 − e^(−S/W∞))`, ceiling refitted on E70's own rungs | **0.232 W** |
| the same curve with the ceiling **frozen** before the run at E60's 12.58 W | 0.595 W |
| pure additivity — summing the single-bit prices | 6.062 W |

The spread layout costs **3.860 ± 0.052 W more than the low layout at h = 8** — 74 SE from the zero a "how many"
law requires, while h is identical in the two. The saturating curve has one free parameter and it collapses both
layouts onto the additive sum over a 0.6 → 12.1 W range.

**The ceiling, and what it is a property of.**

| side | ceiling `W∞` (6 passes, SE from the between-pass scatter) | ratio to the B side |
|---|---|---|
| B (4,096 designed flips per multiply-add) | **10.52 ± 0.19 W** | 1 |
| A (2,048 designed flips per multiply-add) | **6.38 ± 0.07 W** | **0.51** |

The A-side ceiling is **not** the B side's: it is the B side's scaled by the operand's designed flip rate (the
registered alternative, 6.29 W, against the registered primary of a shared 12.58 W). So the saturating resource is
counted per flip *opportunity*, not per multiplier array, and prediction **P5 fails as registered** and is reported
as failed.

**The two ceilings add up to the whole random-data step.** E67 measured, on this card and in this protocol,
`anchor_zeros` 27.83 W, the constant-operand level ≈ 36.4 W (E70: `lq_h0` 36.47, `aq_h0` 36.33, `anchor_pi` 36.35 W —
within 0.4 W of E67's) and `anchor_randn` 52.49 W. That splits the 24.66 W zeros→random board step in two:

- **8.6 W — lane un-gating:** the operands become non-zero but never change (the chip gates a lane whose operand
  word is zero);
- **16.1 W — operand-flip switching**, against a ceiling of **10.52 + 6.38 = 16.90 ± 0.20 W**.

Random fp32 data therefore already sits at **95% of the flip ceiling**. That is why more entropy buys nothing, and
it is the card-level reason a random-data matmul cannot be made to cost arbitrarily more than a predictable one.

## What it changes in Q128

| Q128 §5 | before E70 | after E70 |
|---|---|---|
| **item 2**, the saturation ladder | the price list over-predicts a random word ~2×; two candidate causes, neither tested | **closed**: the cause is shared wires (set by which bits), with a one-parameter law, its ceiling per operand side, and an rms of 0.232 W over 15 rungs |
| **item 4**, third point: no A-side multi-bit ladder | the carry-over between operands was a **choice** between 1.57 (raw single-bit) and 1.01 (turn-on-corrected), moving the prediction 6% | **measured**: ρ = **1.29 ± 0.06** over h = 12, 16, 23 (1.266 ± 0.011, 1.365 ± 0.033, 1.246 ± 0.020), between the two candidates and nearer neither |
| the closure (E67's P8, FAIL at 0.43 / 0.50) | the measured price list could not reproduce a random-word step | with the frozen-ceiling law: `nrd_a` **0.77**, `nrd_b` **1.04**; with each side's own refitted ceiling, 1.21 and 1.17 |

**It moves no pJ in the bottom-up gate-level ledger, and this README does not claim it does.** E70 is a card-side
measurement. What it removes is the 2× discrepancy that made the measured price list unusable as the bridge between
the card and that ledger, and it replaces Q128's 6% modelling choice with a measured number. The Q128 waterfall's
"unaccounted 3.837 pJ" is unchanged by it; the chain's *use* of the price list is not.

## What ran

One item list, 29 runs a pass, so both ladders, their zeros and the random anchors share each pass's offset:

```
anchor_pi, lq_h0, lq_h1, lq_h2, lq_h3, lq_h4, lq_h6, lq_h8, lq_h12, lq_h16, lq_h23,
ls_h2, ls_h3, ls_h4, ls_h6, ls_h8, ls_h12, ls_h16,
aq_h0, alq_h1, alq_h2, alq_h4, alq_h8, alq_h12, alq_h16, alq_h23, nrd_a, nrd_b
```

Seven passes, 790–796, 4.5–5.3 min each, 34.7 min of card time in all (registered cap 75 min). **203 of 203 runs
passed every per-run gate**; the die ran 57 → 58 °C in every pass; the host's 1-minute load average stayed
0.72–1.32 against the registered 4.0 (departure D-b), and the measured op rate held at 1.1208–1.1210 Gop/s per
minion across all seven passes — the sustained rate change E67's A16 found never happened here.

**One pass was set aside, by the gate departure D-a put in for exactly this case.** Pass 792's four
constant-operand runs span **0.489 W** against the registered 0.45 W, while its `anchor_pi` first-versus-last drift
is only +0.110 W — so **E67's registered gate would have kept it and D-a's caught it**, which is what A15 predicted
would happen. The registered reduction is therefore over **six passes (790, 791, 793–796)**.

🛑 **Which reduction is the registered one.** `hl.json` is `hl/reduce_hl.py`'s output and carries *its* pass gate
(E67's drift rule), which sets aside nothing, so its `cards.aifoundry3` numbers are over all seven passes.
**E70's registered numbers are `report.md` / `scored.json`**, which recompute every contrast from `runs.csv` as a
paired per-pass difference and apply the registered D-a gate. Where the two differ, the six-pass numbers are E70's.
The leakage sensitivity files (`hl-leak*.json`) are seven-pass reductions; they exist to size the slope's effect,
which is at most 0.28 W on the dearest rung, not to restate the result.

## The three ladders

Per-rung tables with SEs, fJ per flipped bit, the additive sum and each law's prediction are in
[`report.md`](report.md); `scored.json` has every number machine-readable. The shape, in brief:

| h | low layout `lq` ΔW (W) | fJ per flipped bit | spread layout `ls` ΔW (W) | fJ per flipped bit | A side `alq` ΔW (W) | fJ per flipped bit |
|---|---|---|---|---|---|---|
| 1 | 0.606 ± 0.017 | 132 | — | — | 0.282 ± 0.070 | 123 |
| 2 | 0.928 ± 0.042 | 101 | 2.085 ± 0.012 | 227 | 0.829 ± 0.097 | 181 |
| 3 | 1.294 ± 0.016 | 94 | 3.459 ± 0.096 | 251 | — | — |
| 4 | 1.505 ± 0.201 | 82 | 4.427 ± 0.036 | 241 | 1.578 ± 0.017 | 172 |
| 6 | 2.357 ± 0.083 | 86 | 5.885 ± 0.118 | 214 | — | — |
| 8 | 3.248 ± 0.028 | 88 | 7.108 ± 0.049 | 194 | 1.957 ± 0.070 | 107 |
| 12 | 5.502 ± 0.041 | 100 | 8.890 ± 0.050 | 161 | 3.482 ± 0.016 | 126 |
| 16 | 8.364 ± 0.028 | 114 | 9.749 ± 0.250 | 133 | 5.709 ± 0.136 | 155 |
| 23 | 12.145 ± 0.158 | 115 | = `lq_h23` by construction | — | 7.560 ± 0.042 | 143 |

**The price per flipped bit is not a function of h.** In the low layout it falls 132 → 82 fJ and then climbs back to
115 fJ, because each rung adds a dearer bit than the last and that cancels the saturation; in the spread layout, whose
mask reaches the dear high bits at every h, it falls monotonically 227 → 133 fJ. The quantity that behaves is the
ratio of the measured step to the additive sum, which falls 0.969 → 0.301 (low), 0.952 → 0.348 (spread) and
0.615 → 0.230 (A side) — a single function of the additive sum, in all three.

## The discriminators

**D1, the matched-h layout contrast** (ΔW(ls) − ΔW(lq) per pass, paired): +1.158 ± 0.046, +2.165 ± 0.093,
+2.922 ± 0.194, +3.528 ± 0.162, **+3.860 ± 0.052**, +3.388 ± 0.035, +1.385 ± 0.227 W at h = 2, 3, 4, 6, 8, 12, 16.
A "how many" law needs 0 at every h; pure additivity needs 1.054 → 12.916 W; the frozen coverage law predicted
0.923 → 2.427 W. The measured curve rises, peaks at h = 8–12 and falls back toward 0 at h = 16 — on its way to the
exact 0 that h = 23 forces, where the two masks are the same mask. The frozen law tracks that non-monotone shape;
no law in h can produce it at all.

**D2**, above. **D3**: the turn-on a "how many" law needs to be one constant runs **0.091 → 1.219 W** over the
B-side rungs, a factor of 13.4, with 10 of the 15 rungs more than 3 SE from the 1.351 ± 0.281 W the E67 grid
measured. **D4**: ρ, the A-side price per flipped bit over the B-side price per flipped bit at matched h, is
0.93 ± 0.23, 1.82 ± 0.25, 2.60 ± 0.76, 1.205 ± 0.041, 1.266 ± 0.011, 1.365 ± 0.033, 1.246 ± 0.020 at
h = 1, 2, 4, 8, 12, 16, 23. **D5**, the closure, is in the table above.

## The registered rules, scored

| rule | what it asked | measured | verdict |
|---|---|---|---|
| **P1** | ΔW(ls) − ΔW(lq) > 2.0 W at ≥ 3 SE at h = 8 | 3.860 ± 0.052 W, 73.9 SE from zero | **PASS** |
| **P2** | the spread rungs' rms against the frozen coverage curve ≤ 2.0 W, and ≤ additivity's / 3 | 0.832 W against 8.468 W, a factor of 10.2 | **PASS** |
| **P3** | Spearman ρ(ΔW/S, S) < −0.7 **and** \|ρ vs S\| > \|ρ vs h\| | ρ vs S −0.804 (first clause holds), ρ vs h −0.836 | **FAIL** |
| **P4** | the implied turn-on spans > 4×, and ≥ 1 rung > 3 SE from the grid's 1.351 W | 13.4× (0.091…1.219 W), 10 rungs beyond 3 SE | **PASS** |
| **P5** | `alq` bends ≥ 2× **and** the A ceiling within 1.5× of the B ceiling | bend metric 0.86× (no bend by that metric); A ceiling 6.37 W vs B 12.58 W, ratio 0.51 | **FAIL** |
| **P6** | ρ(12) and ρ(16) in [0.7, 2.5], and ρ(16) < ρ(2) | 1.27, 1.37, both in band; 1.37 < 1.82 | **PASS** |
| **P7** | both closure ratios in [0.7, 1.4] with the selected law | `nrd_a` 0.77, `nrd_b` 1.04 (frozen ceiling) | **PASS** |
| **P8** | E60's 7 `lq` rungs reproduce within 0.6 W, `lq_h23` within 1.0 W | largest \|E70 − E60\| below h = 23 is 0.207 W; `lq_h23` 0.116 W | **PASS** |

**Why P3 failed, honestly.** Its first clause holds (ρ(ΔW/S, S) = −0.804). Its second clause — that the univariate
Spearman against S beats the one against h — cannot work on this design: *within* a layout h and S rise together
almost monotonically, so a single-variable rank correlation cannot separate them, and the one against h came out
marginally larger (0.836 vs 0.804). The registered metric was a poor instrument for the question, and the question
is answered instead by D1 and D2, which are the discriminators the registration itself named as deciding the
verdict. The rule is reported FAIL and is not reinterpreted into a pass.

**Why P5 failed, honestly.** Both clauses fail, in different ways. The *bend* clause compared the A side's
per-position price at h = 23 (0.329 W) with its price at h = 1 (0.282 W); because the A-side single-bit prices rise
steeply with position, the low-k mask picks up dear bits as k grows and the per-position price *rises*, so the
registered metric sees no bend even though the ladder saturates hard (its measured/additive ratio falls
0.615 → 0.230). The *ceiling* clause fails because the A-side ceiling really is 0.51 × the B side's, i.e. the
registered alternative was right and the registered primary was wrong. That is the more interesting of E70's two
failures: it says the ceiling is a property of the operand's flip rate, not of the multiplier array.

## Files

| File | What |
|---|---|
| `report.md`, `scored.json` | **the registered result**: `hs/report_e70.py` over the six passes D-a keeps, every contrast paired per pass |
| `hl.json`, `runs.csv`, `reduce.txt` | `hl/reduce_hl.py` over all seven passes (its own pass gate sets aside none) |
| `hl-leak0.2/0.3/0.4.json`, `runs-leak*.csv`, `reduce-leak*.txt` | departure D-d: the same reduction at three fixed leakage slopes |
| `predictions-e70.json` | every frozen prediction, written by `hs/predict_e70.py` from E60's, E65's and E67's published aifoundry3 numbers only |
| `manifest.json` | the operand set `build/hl-gen5`: every item and its designed flip counts, re-derived from the files |
| `aifoundry3/hl/p790…p796` | per pass: `block.json`, `configs.json`, `gen.sha256` (the operand files that ran), `manifest.txt` (`et-lab-manifest`), `marks.jsonl`, `run.log`, `runs.jsonl`, `code.sha256`, `telemetry.jsonl.gz`, `tiles/` |
| `logs/e70-setup.log`, `logs/e70-sat.log`, `logs/e70-load.jsonl` | the setup checks (card, host, byte-identity), the pass queue, and the host-load sampler at 0.5 Hz for the whole session (departure D-b) |

**Operand set and code.** `build/hl-gen5`, generated and `--check`ed on the box before the first launch. **Every
operand file E60, E65 and E67 ran is byte-identical in it** — 154 of 154 against `build/hl-gen4` and 87 of 87
against `build/hl-gen3`, checked on the box, and 154 of 154 against the committed generator on the Intel before the
registration commit — so nothing already measured changes. `alq_h1` is byte-identical to E67's `abit_0` by
construction (same shared A base word, same single flipped bit), checked in setup: a free tie between the two
experiments' A-side numbers, and it reads 0.282 ± 0.070 W here against E67's 0.459 ± 0.241 W for the same file.
Re-reducing E67's 14 committed passes with amendment A19's `reduce_hl.py` reproduces its committed `hl.json`
exactly, every value, paths aside.

## Leakage sensitivity (departure D-d)

The registered correction is `reduce_hl.py`'s within-run fit on this card's own passes, **0.198 W/°C** (195 runs),
in line with E67's 0.175 and E65's 0.17–0.18. Re-run at the fixed slopes 0.2, 0.3 and 0.4 W/°C — the band that
brackets E66's measured aifoundry2 idle slope of 0.294 W/°C — the rungs move by at most **0.28 W** (`lq_h23`
12.112 → 11.828 W, 2.3%); `ls_h16` moves 0.25 W, `alq_h23` 0.18 W. Every verdict above is unchanged across that
band. **aifoundry3's own idle slope is measured by E71, not here**, so this is a labelled sensitivity and not a
correction.

## Departures from plan, and other honest notes

- **Pass count.** Seven passes ran where the registration targeted seven (minimum four); six survived the gates.
- **No RTL replay** for `lq_h3`, `lq_h6`, any `ls` rung or any `alq` rung (departure D-c): Verilator is not on this
  host. Those rungs are scored against the three measured laws, never against a prediction that does not exist.
- **`collect_e70.sh` was corrected after the run**, before any reduction was published: its call of `report_e70.py`
  was missing `--closure` and `--blocks`, so the first run of it produced a report with no D5 table and no
  per-pass load column. The fix adds two arguments to a tool invocation; it changes no rule, no gate, no reduction
  and no measured number, and the published `report.md` is the complete one.
- **`report_e70.py` itself landed with the data commit, not the registration commit** (the registration named it as
  a file and froze every rule and every prediction it scores, in `tools/claims-v3/hs/README.md` and
  `predictions-e70.json`). It is mechanical: it recomputes the registered contrasts from `runs.csv` and scores the
  registered bands. This is disclosed here rather than left to be noticed.
- **The anchors `anchor_zeros` and `anchor_randn` were not in E70's item list**; the 8.6 W / 16.1 W split above
  takes them from **E67**, on the same card, clock, voltage and launch protocol four days apart. E70's own
  constant-operand level agrees with E67's to 0.4 W, which is the comparison's noise floor.
- **`logs/e70-setup.log` is scrubbed.** Its `who` block carried five other lab users' login names (idle shell
  logins only — none held the card, and E60's departure D1 is what lets them not block). The names are replaced by
  `<other lab user N>` with the tty kept; nothing else in the log is altered. This repository is public.
- **Nothing on the card was changed.** No clock was set, the governor was not touched, no firmware or OTA path was
  used, and the card was free (`et-who`: no holder) before the first launch and after the last.
