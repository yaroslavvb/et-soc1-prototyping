# NV validation: pre-registration (skeleton, not frozen)

**Status:** skeleton, written 2026-09-28 before any card run, revised the same day after the safety and science reviews
(DESIGN.md §10). `freeze.sh` refuses to freeze while any placeholder below is unfilled. At the freeze, this file's
SHA-256 goes into `PREREG.sha256` and into `LOCK.sha256` with the runner. It is also recorded in
`docs/findings/03-experiments.md` with the commit. After the freeze, any change is an amendment in §7, written and
dated before any validation data it touches is looked at.

The predictions and decision rules are in `predictions.json`. They were fixed before the first card write (its
SHA-256 in `PREDICTIONS.sha256`, recorded in `03-experiments.md`) and are not changed here.

Frozen: TBD (date, commit, the SHA-256 of this file).

## 1. What is validated

`DESIGN.md` gives the theories, the measurement and the rules. This file freezes them for one card, and adds the values
that development supplied.

- **Card:** aifoundry2 (firmware 1.3.1, BL2 0.20.0), after DV2's validation there has ended and the owner has
  released it (`build/claims-v3/aifoundry2/nv/CARD-RELEASED`). It has run no NV pass. Before the freeze it runs only
  `--probe`, which records no power. aifoundry1's card 1 was the first choice; it is refused because its BL2 0.18.0
  writes every NoC set to the flash (DESIGN.md §2).
- **Passes:**
  - 101 to 100 + N, where N is `prereg.json` `val_passes`, the rule's N for the development SD (§3). Pass p takes
    order (p − 101) mod 6.
  - Two spares follow. They run only while fewer than N passes ended ok. Each takes the order of the earliest pass
    whose status is not ok and that no ok spare has replaced.
- **Code and binaries:** every file in `LOCK.sha256`. `block.sh` refuses a validation pass unless it checks.
- **Levels:** 485, 540 and 600 mV. **Configurations:** E42's eight `wsep` (P = 0 and ½, d = 1–4).
- **Heat:** E42's heater: 76 °C before the first set, and one launch before any idle window or configuration below
  69 °C.

## 2. Items and decision rules (as DESIGN.md §5 and predictions.json, fixed here)

Exponent n: Q(V) = Q(485)·(V/485)^n, the least-squares slope per pass of ln Q on ln(V/485). The verdict interval is the
hull of the 95% t-interval and the 95% percentile bootstrap over passes (20,000 resamples, seed 20260928).

| Band | Exponent |
|---|---|
| TH-0 | (−∞, 0.5] |
| TH-V1 | [0.5, 1.5] |
| TH-V2 | [1.5, 2.5] |
| TH-X | [2.5, ∞) |
| TH-LEAK | [1.0, 3.5] |

- **PASS:** the verdict interval lies inside the band.
- **FAIL:** it lies wholly outside it.
- **INSUFFICIENT:** otherwise, or fewer than 5 valid passes.
- **NOT DECIDED:** a gating control did not pass.

| Item | Quantity | Registered theory | Its prediction on this card | Gated by |
|---|---|---|---|---|
| NV-D (primary) | the data part per bit·hop, mesh rail | TH-V2 (rivals TH-V1, TH-0, TH-X) | n = 2: from 89.48 to 110.9 at 540 mV and 136.9 at 600 mV fJ/bit/hop | C-METER, C-BW |
| NV-Z | the zeros part per bit·hop | TH-DI (V² band) | n = 2: from 43.87 to 54.4 and 67.1 | C-METER, C-BW |
| NV-I | the idle mesh rail corrected to the pass's 485 mV idle die temperature (0.028/°C) | TH-LEAK (rival TH-I-0) | n ∈ [1.0, 3.5]: ×1.11–1.46 at 540 mV, ×1.24–2.11 at 600 mV; where the interval sits against 1.25 is descriptive | C-METER |
| NV-T | the random bit in all | reported (V2 band) | | C-METER, C-BW |
| R1 | n_D, validation against development | replication | the 95% Welch interval of the difference inside ±tol (nD, sdD, nDev, tol: `prereg.json`) | |

**Controls:**

- **C-N:** ≥ 5 valid passes.
- **C-RESTORE:** every pass restored and verified.
- **C-REPRO:** the median D at 485 mV within ±10% of 89.48. It gates absolute figures and the Q63 line, not the
  theories.
- **C-METER:** board idle W per rail idle W across the levels, temperature-corrected; PASS inside [0.9, 1.8]. NOT
  APPLICABLE if the rail's idle did not rise by 0.25 W; then only the zero theories are decided.
- **C-BW:** bytes per launch at 540 and 600 mV within ±0.5% of the pass's 485 mV value, for every configuration.
- **C-DROPS:** reported.

**Burst drops and pass validity** are as in DESIGN.md §5. The thresholds are in nv.json `limits` and `analysis`, frozen
by the lock.

## 3. Values fixed from development (filled at the freeze)

- **Development passes** used (aifoundry3): TBD. Their exponents, from `reduce.py --card aifoundry3`:
  - n_D = TBD [hull TBD]
  - n_Z = TBD
  - n_I (corrected) = TBD, uncorrected TBD
  - C-METER ratio = TBD, C-BW's largest deviation = TBD
- **Development controls:** C-REPRO TBD. Drops by cause: TBD.
- **prereg.json:**
  - `nD` = TBD, `sdD` = TBD, `nDev` = TBD: the development n_D, its per-pass SD and the valid development passes;
  - `tol` = TBD. The proposal is 0.5, half a band's width. With sdD of 0.15–0.20 and 6 passes on each card, the
    Welch half-width is 0.19–0.26, and a true difference of 0 then passes with probability about 0.96 or more;
  - `val_passes` = TBD, the rule's N for sdD (`nvlib.py nrule`; `freeze.sh` checks it). If the rule needs more than
    12, the design is revisited by an amendment instead.
- **Changes to nv.json after the design** (timing, limits, heater, drops only), with the reason: TBD, or "none".
- **The development card's heat and temperature:** aifoundry3 is pinned and ran without a heater. aifoundry2's
  heat_c is TBD (76 unless development or the probe shows the 85 °C mean limit at risk).

## 4. Stopping and spares

`run-queue.sh` runs 101–114 in order. Every pass after 100 + N + 2 exits at once as beyond the plan. A spare exits at
once when N passes ended ok. No pass is added after the queue ends, and no pass is removed from the analysis except by
the rules of DESIGN.md §5.

An ALERT stops everything. Validation resumes only after a person has looked. Any pass run after an ALERT is reported
separately, and the alert is reported with the results.

## 5. What is reported whatever the outcome

- every item's verdict with its interval, and, for NOT DECIDED, the verdict it would have had;
- the per-pass exponents;
- the ratios at 540 and 600 mV;
- the controls;
- the drops by cause;
- the on-die-voltage exponents, the board-power slopes, the SRAM and minion rails per level, the burst heating, the
  uncorrected n_I and the end-of-pass drift (not decided);
- the order balance of the valid passes;
- the one-line Q63 conclusion from `reduce.py`, with its extrapolation labelled.

A failed prediction is reported as failed.

## 6. Analysis command

```bash
python3 tools/claims-v3/nv/reduce.py --card aifoundry2 --dev-ref tools/claims-v3/nv/prereg.json \
    --data <the collected data root> --out nv-validation.json
```

## 7. Amendments after the freeze

None.
