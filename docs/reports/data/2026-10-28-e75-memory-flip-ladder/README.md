# E75 — the price of a flipped bit, and of a carried one, on four memory paths (Q129)

## Results

*Five passes, `p7510`–`p7514`, Wed 28 Oct 2026 11:25:44–11:56:39 PDT on aifoundry3 card 0, 600 MHz,
`--harts 1` (1,024 harts), 29 items per pass. **21.5 card-minutes.** Every pass `block.json` `"status":"ok"`;
one set aside by its own registered rule, so **4 passes are in the numbers**. Pre-registered Tue 27 Oct in
`2be3f07e` / `547f4ae3`. Reduced with `reduce.sh`, whose three commands are unchanged; the reducer itself was
amended the same day after an adversarial review and the reduction re-run, with no published number changing
(D-M7).*

**The two arms separate, and the answer is different at the two ends of the hierarchy:**

> ### the L1 path pays for **changes**; the DRAM path pays for **ones**
>
> | | per changed bit | per carried one | ratio |
> |---|---:|---:|---:|
> | **L1** (32 B `flw.ps`, 11.94 TB/s) | **0.0492 pJ** (SE 0.0003) | **−0.0001 pJ** (SE 0.0004) — zero | ones are ≤ 2.8 % of a change |
> | **L2** (256 KB/shire) | **0.274 pJ** (SE 0.029) | — (no w-arm registered) | — |
> | **L3** (24 MB) | 0.285 pJ (SE 0.025) — **not resolved**, k-arm non-monotone | — | — |
> | **DRAM** (128 MB, 4× the L3) | 0.323 pJ (SE 0.028) — **not resolved**, k-arm non-monotone | **3.255 pJ** (SE 0.091) | of the part the two arms explain, **94 % is carried ones** |
>
> **The ± / SE figures are standard errors of the pass mean, not half-widths.** The 95 % t intervals over 4
> passes (df 3, t = 3.18) are: L1 e_flip [0.0482, 0.0501] and e_one [−0.0014, +0.0011]; L2 [0.183, 0.366];
> L3 [0.205, 0.365]; DRAM e_flip [0.233, 0.413], e_one [2.97, 3.55].
> **L2's and L3's are the first data-dependence figures of any kind for those two levels** — L2's resolved on a
> monotone arm, L3's not (its middle rung dips below its own zero rung in all four passes, as DRAM's does).

The zeros-vs-random chord, which was the only handle the catalogue had, is reproduced — and then explained only
at one end:

| | measured chord (random − zeros) | published 4.1 chord | the two arms account for |
|---|---:|---:|---:|
| **L1** | 1.778 W (SE 0.032; 95 % [1.68, 1.88]) = **0.1489 pJ/B** | 0.54 − 0.39 = **0.15 pJ/B** | **98.3 %** (error −1.7 %, 95 % [−6.4, +3.0]) |
| **DRAM** | 3.250 W (SE 0.126; 95 % [2.85, 3.65]) = **43.3 pJ/B** of line bytes | 132.6 − 94.6 = **38 pJ/B** | **36.6 %** (error −63.4 %, 95 % [−70.0, −56.7]) |

So at L1 the design is complete: fit `P = a + b·k + c·w` on the two arms alone and it predicts the
zeros-to-random step to within 2 %, with `c` indistinguishable from zero. **At DRAM the same model explains
barely a third of the step** — it predicts the random anchor's absolute power to −3.1 %, which is what P4
registered and which a 34 W floor makes easy, but only 36.6 % of the ~3.2 W chord that carries the information.
That is the registered risk realised, named in
advance: *"Two values alternating is a maximally correlated pattern. If the DRAM interface does data-bus
inversion or any history-dependent encoding, a 2-cycle is not random data with the same counts. P4 is the test:
if the random anchor does not land where the ladder says, the ladder measures the 2-cycle and not the general
case, and that is the finding."* It is the finding. The measured zeros anchor also sits 0.81–1.43 W **below** the
additive model's own (k = 0, w = 0) intercept in every pass, so the response to carried ones is strongly convex
near zero: the 0→256-ones step costs about twice per one what the 128→384 step does.

### Why two of the four changed-bit prices are *not* resolved coefficients

L1 and L2 have monotone k-arms and their slopes are measurements. **L3 and DRAM do not, in any of the four kept
passes**, so their whole-arm slope is the shape of a non-monotone arm and not a per-changed-bit price:

| level | k-arm, the four kept passes 7511 · 7512 · 7513 · 7514 (W, k = 0 … 512) | registered small-k slope |
|---|---|---:|
| **DRAM** | 34.302, 34.239, 34.094, 34.063, **34.574** · 34.377, 34.283, 34.091, 34.417, **34.563** · 34.274, 34.307, 34.127, 34.402, **34.477** · 34.297, 34.228, 34.151, 34.357, **34.517** | **−0.32 pJ/bit**, 95 % [−0.91, +0.26] |
| **L3** | 34.328, 34.205, **34.473** · 34.317, 34.155, **34.513** · 34.319, 34.202, **34.540** · 34.348, 34.140, **34.518** | **−0.47 pJ/bit** |

In both the whole positive slope is carried by the single top rung, while the rungs below the top sit *below* the
zero rung. The small interval on those slopes (SE 0.025–0.028 pJ/bit) comes from the shape repeating across
passes, not from linearity — four passes agreeing on a non-monotone arm give a precise slope of the wrong thing.
So read them as **small and bounded**: under 0.42 pJ per changed bit at 95 % at DRAM, under 0.37 at L3, and
correction-dependent on top of that (D-M4: DRAM's moves 0.323 → 0.181 → 0.135 across the three leakage settings).

What survives this, and is the result: **at DRAM the energy that depends on the data is carried ones.** Of the
1,008 pJ per 64 B line that the two designed counts explain, **946 pJ (94 %) is the ones term** and 62 pJ the
changed-bit term. The point ratio e_one / e_flip is 10.1× (and 20× / 28× under the two fixed-slope sensitivities),
but it rests on an unresolved denominator, so the defensible statement is the 94 % share, not a clean factor of
ten. The lever for DRAM energy is packing zeros, not reducing transitions.

### Scoring

| Rule | Reading | Registered | Verdict |
|---|---|---|---|
| **P1** L1 small-k slope | **0.0655 pJ/bit**, 95 % [0.0590, 0.0720] | 0.03–0.12 | **PASS** |
| **P2** DRAM small-k slope | **−0.32 pJ/bit**, 95 % [−0.91, +0.26]; the whole-arm slope is **+0.323 [0.233, 0.413]** | 6.0–25.0 | **FAIL**, by more than an order of magnitude. The registered band came from the chord on the assumption that the chord is paid for *changes*; it is paid for *ones* |
| **P3** DRAM saturation at k = 512 | **−120 %**, 95 % [−311, +71] — the top rung sits *above* the line through the two lowest, because the small-k slope is negative | 20–60 % below the line | **FAIL / not resolved.** The k-arm at DRAM is not monotone: 34.30, 34.24, 34.09, 34.06, 34.57 W over k = 0…512, a 274 mW span on a 34 W board. L3's arm is non-monotone the same way |
| **P4** the random anchor from the two arms | **registered basis** (percent of the random anchor itself): L1 **+0.6 %** [+0.5, +0.8], DRAM **−3.1 %** [−3.14, −2.98]. **Chord basis** (percent of the zeros-to-random difference): L1 **−1.7 %** [−6.4, +3.0], DRAM **−63.4 %** [−70.0, −56.7] | within ±15 % | **PASS at L1 and PASS at DRAM on the registered basis; PASS at L1 and FAIL at DRAM on the chord basis** (D-M3). Both are in `mf.json`; the chord basis is the informative one and the 36.6 % chord share below is reported under its own name, not as P4's verdict |
| **P5** closure, pJ per DRAM line | 191.1 × 0.323 + 290.7 × 3.255 = **1,008 pJ** (946 of it the ones term, 62 the unresolved changed-bit term); the measured chord is **2,770 pJ/line** | 2,432 ± 600 | **FAIL** (low). The chord itself lands at +14 % of the published 2,432; the designed counts explain 36 % of it |
| **P6** ordering | monotone on point estimates (0.0492, 0.274, 0.285, 0.323), span **6.6×**; at 95 % only **L1 < {L2, L3, DRAM}** is resolved — L2 [0.183, 0.366], L3 [0.205, 0.365] and DRAM [0.233, 0.413] overlap almost completely | monotone, ≥ 100× | **PASS on the order only as L1 < the other three**, the upper three **unresolved** at 95 %; **FAIL** on the span |
| **P7** rates | L1 **11.94 TB/s**; DRAM **37.53 GB/s requested = 75.1 GB/s of 64 B lines**; worst telemetry `took_ms` **22 ms** | 10.9–18.1 TB/s; 57–95 GB/s; drop above 60 ms | **PASS** (the DRAM band is the line rate: `bytes_per_s` counts the 32 B each load asks for, half the 64 B line it fetches) |

L1 also saturates, and by about the factor the arithmetic price list does: the k = 256 rung sits **22.8 % ± 1.9
below** the straight line through the two lowest rungs. One flipped bit costs 0.0655 pJ when few bits move and
0.0492 pJ averaged over the whole ladder — a 1.33× over-prediction from the small-k slope, against the ~2× the
single-bit arithmetic prices show.

## What ran, and what was registered

| | registered | happened |
|---|---|---|
| levels | L1 256 B image; L2 8 KB/hart; L3 24 KB/hart; DRAM 128 KB/hart (`dram_4x_l3`) | all four, at 4.2's own sizes |
| arms | k-arm at every level; w-arm at L1 and DRAM; `zeros` and `random` anchors at all four | all of it, 29 items |
| scratchpad | **out of scope**, with the reason (no host fill reaches `EC_SCP_ADDR`) | not run; still out of scope |
| passes | target 3, extend to 5 if the lane is free | **5 run** (3 + an extension of 2, below); 4 kept |
| pass gate | anchor drift > 0.3 W, or a level losing more than a third of its runs | `p7510` set aside: drift **−0.546 W**. No level lost a run anywhere; 0 run-level gate failures in 150 runs |
| burst gate | drop a run whose median `took_ms` > 60 ms | worst was 22 ms; nothing dropped. The DRAM meter-starvation risk did not bite |
| DRAM allocation | 272 MB on the card, inside the 10 s cap, else re-register at 64 KB/hart | filled and launched every pass; no `rc 124`, no amendment needed |

## Departures, dated

- **D-M1 (28 Oct 2026) — the reducer was written on the day**, as the registration said it would be
  (`tools/claims-v3/mf/reduce_mf.py`). It imports `hl/reduce_hl.py`'s per-run machinery unchanged
  (`runs_of_pass`, `leak_slope`, `fit_line`, `mean_se`), so the power window, the approach gates and the leakage
  correction are E60's and E65's, and adds only the registered estimators.
- **D-M2 (28 Oct 2026) — two extra passes.** `p7510` was set aside by the anchor-drift rule, leaving 2, and
  df = 1 made every interval useless (t = 12.7). The registration's own option — "extend to 5 if the lane is
  free" — was taken: `go 7513 2` ran after E76's probe, for 4 kept passes and df = 3. The extension used the
  same command, the same operand files and the same build; no rule or rung changed.
- **D-M3 (28 Oct 2026, extended the same day) — P4 is scored on BOTH bases, and they disagree at DRAM.** The
  registered wording is "the random anchor lands within ±15 % of the ladder interpolated to the
  random-equivalent k *and the matching W*" — a percent of **the anchor**. Both arms are needed for that, so
  `reduce_mf.py` fits `P = a + b·k + c·w` on the k- and w-arms only (never on the anchors) and predicts the
  anchor. It then compared the predicted and measured **chord above the zeros anchor**, which is the stricter
  test but *not* the registered basis: ±15 % of 34 W ≈ 5 W would be a test no result could fail, when the whole
  chord is ~3 W. Re-specifying a registered test on the day is a departure even when the new test is better, so
  **both numbers are now computed and reported** (`pass_dram` on the chord basis, `pass_dram_anchor_basis` on the
  registered one). On the registered basis DRAM **passes at −3.1 %** (pass 7511: 33.134 + 2.863e−4 × 191.1 +
  3.957e−3 × 290.7 = 34.34 W against a measured 35.395 W), and L1 passes at +0.6 %. On the chord basis L1 passes
  at −1.7 % and DRAM fails at −63.4 %. **So "P4 failed at DRAM" is not a pre-registered failure** — it is a
  failure of the stricter test this run substituted, and the thing worth carrying forward is the finding under
  its own name: *the two designed arms explain 36.6 % of DRAM's zeros-to-random chord* (95 % [30.0, 43.3]).
- **D-M6 (28 Oct 2026) — rule 1's rate conversion is applied with the level's mean measured rate, not run by
  run.** Rule 1 registered "the slope converted with each run's OWN measured rate, never an assumed one".
  `reduce_mf.py` fits the slope per pass and converts with the mean of that level's measured rates (mean over the
  pass's runs, then over passes). No rate is assumed, and the difference is nil: the within-level spread of
  `ops_per_s` is 9.8e−6 (L2), 1.3e−4 (DRAM), 3.6e−4 (L1) and 2.1e−3 (L3) relative, so it moves no published
  digit. Named because the registered wording is per run.
- **D-M7 (28 Oct 2026) — the reducer was amended after an adversarial review of this result, and the reduction
  re-run.** Added: P3, P6 and P7 now carry machine-readable `pass` fields (a reader of `mf.json` alone would have
  scored P7 a FAIL, because the registered DRAM band is a **line** rate and `dram_bytes_per_s` counts the 32 B
  each load asks for — `dram_line_bytes_per_s` = 75.1 GB/s is the quantity scored, and the basis is now stated
  in the file); P6 carries each level's interval and which pairs of the ordering are resolved at 95 %; P4 carries
  both bases (D-M3); every level carries `k_arm_monotone`. **No published number changed**: every pre-existing
  field of `mf.json`, `mf-leak0.2936.json`, `mf-leak0.3803.json` and `runs.csv` reproduces bit-for-bit, checked
  field by field against the committed files; the one pre-existing field that differs is P4's `rule` string,
  rewritten to name both bases.
- **D-M4 (28 Oct 2026) — a third leakage sensitivity.** E71's measured slope for this card (0.3803 W/°C over
  58–62 °C) is added beside the registered 0.2936 W/°C one; `mf.json` is the registered `auto` estimator (which
  reads 0.022 W/°C from 39 qualifying runs — these launches barely heat). The choice matters least where the
  signal is largest and most where it is smallest, which is the expected shape and is worth stating as a number:
  across `auto` / 0.2936 / 0.3803 W/°C, L1's e_flip moves **0.0492 → 0.0466 → 0.0458** (−7 %), L1's e_one and
  L2's e_flip do not move at all, DRAM's e_one moves **3.255 → 3.696 → 3.837** (+18 %), and the two small
  quantities are reshuffled: DRAM's e_flip **0.323 → 0.181 → 0.135** and L3's **0.285 → 0.469 → 0.528**. So the
  headline — ones dominate changes at DRAM by about 10× — holds under every setting (the ratio runs 10×, 20×,
  28×), while the DRAM e_flip's own value is correction-dependent and should be read as "small, under 0.4 pJ".
- **The run is a day later than the registration** (yesterday's lane agent died in setup with 0 launches), so the
  data directory carries the date of the run.

## What it changes

1. **Q128 §5 item 5's first half closes.** "No flip ladder on a memory path" becomes **two resolved
   per-flipped-bit prices** — L1 0.0492 pJ [0.0482, 0.0501] and L2 0.274 pJ [0.183, 0.366] — **two bounds** at L3
   (< 0.37 pJ) and DRAM (< 0.42 pJ), whose arms are non-monotone, and the first per-carried-one price on this
   silicon, **3.255 pJ [2.97, 3.55] at DRAM** with L1's indistinguishable from zero. The load-to-watts model's
   memory term stops being a chord: an L1 32 B load costs ≈ 0.049·k pJ above its floor, and a DRAM line
   ≈ 3.26·w pJ plus a changed-bit term too small and too poorly conditioned to use.
2. **It changes what the DRAM figure *means*.** The comparison Q128 draws — "a DRAM tensor load costs 94–134 pJ
   per byte against a multiply-add's 5.783 pJ" — has a data-dependent part of 38 pJ/B (measured here as 43.3),
   and of the part the designed counts explain, **94 % is carried ones**: 946 of 1,008 pJ per line. Anyone trying
   to save DRAM energy by reducing transitions is optimising the small term; packing zeros is the lever. The
   point ratio is 10.1× but its denominator is unresolved, so the 94 % share is the number to quote.
3. **It bounds how far counting bits can go.** The designed counts explain **98 %** of the data dependence at L1
   and **37 %** at DRAM. So a bit-counting energy model is complete on the on-chip path and two-thirds incomplete
   off-chip, and the missing part is a property of the *pattern* rather than of its counts — the next experiment
   is a third image with the same k and w but a longer period, to test the compressibility hypothesis that a
   2-cycle invites.
4. **None of this moves the 3.837 pJ unaccounted on the multiply-add** — that is arithmetic, and this is the
   memory path. It closes an item on the §5 list and gives the Horace Levels tab its memory-path row.
5. **A lesson for the lane**: in both E74 and E75 the pass set aside was the **first** one, on anchor drift
   (−0.39 W and −0.55 W, against +0.07 to +0.23 W afterwards). A card coming off idle has one transient pass in
   it. Queue a throwaway pass first, or budget n + 1.

## Files

| file | what it is |
|---|---|
| `passes/p7510`–`p7514` | the five passes: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `configs.json`, `block.json`, `gen.sha256`, `text.sha256`, `manifest.txt`, `run.log` |
| `gen/manifest.json` | the 29 items, their designed k and w, and each one's device command line |
| `mf.json` | the reduction at the registered `auto` leakage slope — the result, with `two_term_model` per level |
| `mf-leak0.2936.json`, `mf-leak0.3803.json` | the two labelled sensitivities |
| `runs.csv` | one row per run: level, arm, k, w, p_raw, p80, rail, rate, median `took_ms`, gate failures |
| `reduce.sh`, `queue.log` | the reduction commands and the queue's own log |

Code: `tools/claims-v3/mf/` (`make_mf.py`, `block.sh`, `queue_mf.sh`, `run_e75.sh`, `predictions.json`,
`reduce_mf.py`), runner `tools/claims-v3/runitems.py`.

## Reproducing it

    bash tools/claims-v3/mf/run_e75.sh setup       # operand set + --check, patterns, hashes, dry run. No card.
    bash tools/claims-v3/mf/run_e75.sh go 7510 3   # three passes, all four levels; log build/e75-mf.log
    bash tools/claims-v3/mf/run_e75.sh go 7513 2   # the extension
    bash docs/reports/data/2026-10-28-e75-memory-flip-ladder/reduce.sh
