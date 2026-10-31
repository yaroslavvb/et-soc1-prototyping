# V3-KSPEED E84 — the speed of each kind of number on aifoundry1's card 0, under its own governor (Q130)

*Pre-registered Sat 31 Oct 2026 (week 44), before the `#community-lab` claim and before any E84 device access. This
commit freezes the design, the protocol ([`protocol.json`](protocol.json)), the predictions
([`predictions.json`](predictions.json)), the reduction ([`reduce_e84.py`](reduce_e84.py)) and the decision rules
below; the sha256 of each is in the commit and in every session's `e84.json`. Any change after it goes in Amendments at
the end, dated, before the data it touches.*

**The ask** (the owner, Sat 31 Oct 2026, about 13:1x PDT): *"feel free to use more cards"*. In Q130's plan this is
**E84**: E80's speed design repeated on a different card, so that the blog can say whether "zeros run faster" belongs
to the numbers or to one card's limits.

**Why card 0.** It differs from aifoundry2 (E80) in three ways at once:

- **another card**, at another voltage: 603 mV at 800 MHz against aifoundry2's 618 mV (E60's probe, below);
- **another firmware build**: release 1.4.1, BL2 0.21.2 on record (aifoundry2: 1.4.0, BL2 0.22.0). It idles at
  300 MHz between kernels, and its governor acts only while a kernel runs;
- **another cooling**: its fan was replaced on 2 Oct, and it runs cooler than card 1 under the same load
  ([`14-card-behaviour.md`](../../../../docs/findings/14-card-behaviour.md), the card table).

If zeros still run faster here, by roughly the same mechanism (random data hits the power and heat limits, zeros do
not), the effect belongs to the numbers. If the ordering changes, it belongs to a card's limits.

## Design

**Card and instrument, as they are.** aifoundry1, card 0, selected with `ET_DEVICES=0` and the card lock
`/run/lock/etsoc-shire0.lock`. Its firmware is read once, read-only, after the claim and before the smoke
(`run_e84.sh ident`, both cards' locks held non-blocking for the one `dev_mngt_service` call, as E82 did), and recorded.
Card 1's record turned out stale today (E82 amendment A1), so **the start read decides which build was measured**.
**Nothing is set on the card**: no TDP, threshold, clock, voltage, log level or reset.

**The runner is E80's.** [`run_e84.py`](run_e84.py) imports [`../run_kspeed.py`](../run_kspeed.py), which imports
E64's [`../../hpl/run_hpl.py`](../../hpl/run_hpl.py), and runs them unchanged except in the five places where
`run_hpl.py` names aifoundry2's single card:

1. **the card**: `ET_DEVICES=0` is set before anything starts, so every child process opens card 0 only;
2. **preflight**: aifoundry1, its own `build/sparsity` binaries (lib.sh:35-43), `build/ettelem-e84` (E64's
   `ettelem-dv2`, built on this host so it honours `ET_DEVICES`), both lock files, `et-holders` answering;
3. **the other-user test** before the session and before every launch process, as `lib.sh`'s `others_present` does
   on a two-card host (its amendment A3). Another user who is only logged in does not end the session. Any of these
   does, **on either card**:
   - another user's device node or card lock;
   - another user's device process, or a running CI job;
   - one of our own device processes or holders that is not this session's;
   - the `et_soc1` module's use count over the baseline (E64's own test).

   Other users' login names are never recorded;
4. **the queue drain** (only after a failed sampler start): the stock `dev_mngt_service` opens both cards'
   management nodes, so it runs only with card 1's lock taken non-blocking for the one call (lib.sh:126-143);
5. **the configuration check** after every run must equal card 0's own start read, not aifoundry2's 65/65.

The lock held for the session, `timeout 10` on every device process, the sampler without `--reset-ms`, the trace
ring, residencies and `ettelem config` after every run, the safety stops (85 °C; 97 W on three samples) and the stop
file are `run_hpl.py`'s own code. Any session stop is final for that session.

**Kernel and tiles.** `sparsity_host --test fma --pattern none --values file:<tile>`, one 16×16 TensorFMA repeated by
hart 0 of each of the 1,024 minions, ~0.5 s launches back to back. The kernel binary is the same file as aifoundry2's
(`sparsity.elf` sha256 `990807f4…`). The host binary is aifoundry1's own build (`e0fbecce…`). The tiles are 11 of
Q130(s) revision 2 (`kinds.json` sha256 `9586568f…`), each checked by sha256 before the session:

| format | kinds |
|---|---|
| fp32 | zeros, ones, randn, sparse90, bf16trunc |
| fp16 | zeros, ones, randn |
| int8 | zeros, full (= E64's int8 `randn`), neg_ones |

**The blocks** ([`protocol.json`](protocol.json), order seed 84; E80's shapes, which are E64's):

| block | runs | start | load |
|---|---|---|---|
| `SMOKE` | fp32 randn, fp16 ones, int8 full, 2 s each | none | not analysed: checks the `file:` path, `ET_DEVICES=0` and that the trace ring decodes on this build |
| `BURST` | 11 kinds × 2 passes, each pass shuffled | die reading ≤ 55 °C | one 6 s process |
| `SUS` | 11 kinds, shuffled | die reading ≤ 57 °C | nine back-to-back 8 s processes (~76 s) |
| `SUS2` | fp32 zeros and fp32 randn again, last | die reading ≤ 57 °C | as SUS |

35 runs. `run_hpl`'s plan is 38 min plus the cooling gates. The cap is 60 card-minutes for the session; the smoke has
its own 5. A cap reached ends the session cleanly, and whatever has not run is reported missing.

## The governor at card 0's build (read before predicting)

**The source.** BL2 0.21.2 is not in the public et-platform history. The public repository has branches `master`,
`docker_test` and `og`, and its changelog has no 0.21.1 or 0.21.2 entry. So E84 reads 0.21.0's close instead:
`50310b06` (2024-09-25), `thermal_pwr_mgmt.c` `check_power_throttle_conditions()` at `:853-915`, the single-pass
governor that 0.22.0 still runs. 0.22.0 (`836a4ab`) shows what changed after it.

**The arms.** One decision per management pass, and only while active power management is on **and the master
minion is not idle** (`:866-868`). That is the "acts only while a kernel runs" of the card table. In order:

1. **thermal**: one point down if the integer mean of the minion-shire sensors is over the 65 °C threshold and the
   clock is above the floor (`:872-884`);
2. **power down**: else one point down if the PMIC's running average is over the TDP (`:886-896`);
3. **power up**: else one point up if the average is under the TDP and the clock is below the top (`:898-908`).

**The wrap hazard.** At 0.21.0 the average is held in a `uint16_t` of mW (`:858-859`). An average over 65.535 W then
reads as a few watts, so the power arm could never step down. 0.22.0 widened it (SW-22147).

**What card 0 did on 20 Oct (E60's heater probe).** Committed telemetry,
`docs/reports/data/2026-10-20-bitflip-ladder/aifoundry1-c0/hl-probe/p1/telemetry.jsonl.gz`:

- fp32 random data at 800 MHz / 603 mV drew 72–74 W board at a 55–61 °C die;
- the clock stepped 800 → 700 MHz on the samples whose PMIC average (`sp.board_avg_w`) read 65.8–65.9 W, and back up
  at 64.8–65.0 W. So **card 0's build does not wrap**: its power arm acts at the TDP like 0.22.0's;
- between processes the clock drops to a 300 MHz / 398 mV point. 0.21.0's idle handler goes to the flash boot clock
  (`:1968-1972`), so 0.21.2 differs from it there;
- inside one process the clock climbs 600 → 700 → 800 over the first ~1.0–1.5 s and then holds across launch
  boundaries. E60's `hl/p8/runs.jsonl`, `anchor_pi`: launches 0–1 at 0.599–0.604 GHz, launch 2 at 0.743–0.745, then
  0.799.

So each 8 s process of a sustained run starts with a climb that costs every kind some speed. E84 labels those samples
`ramp` and reports their share.

**Numbers carried into the predictions.**

- **Power**: card 0's fp32 random-data reading at 800 MHz (73–74 W) over E80's predicted p800 for aifoundry2
  (81.6 W) is a factor 0.907. It is applied to E80's predicted p800 for the other kinds
  ([`../predictions.json`](../predictions.json)). Kinds over 65 W at 800 MHz on card 0: fp32 randn (~74 W),
  bf16trunc (~72 W), fp16 randn (~71 W). All the others sit at or under ~52 W.
- **Heat**: the same probe gives about 0.44 °C per W at τ_th 14 s (50 °C at 19.5 W idle; +11 °C over ~25 s at a
  ~50 W mean). A 65 W average then settles near 67–70 °C, over the trip, by the last 40 s of a 76 s run. The ~52 W
  kinds settle near 62–64 °C, under it.

## Predictions (frozen in [`predictions.json`](predictions.json))

| kind | burst limit | sustained limit | p800 expected (W) | burst MHz expected | sustained MHz (non-ramp) expected |
|---|---|---|---|---|---|
| fp32 zeros | none | none | 30–36 | 790–800 | 795–800 |
| fp32 ones | none | none | 44–53 | 790–800 | 780–800 |
| fp32 randn | **power** | **thermal** | 70–76 | 720–790 | 600–700 |
| fp32 sparse90 | none | none | 31–37 | 790–800 | 795–800 |
| fp32 bf16trunc | **power** | **thermal** | 68–75 | 725–795 | 600–710 |
| fp16 zeros | none | none | 30–36 | 790–800 | 795–800 |
| fp16 ones | none | none | 43–51 | 790–800 | 780–800 |
| fp16 randn | **power** | **thermal** | 66–74 | 730–800 | 600–720 |
| int8 zeros | none | none | 31–37 | 790–800 | 795–800 |
| int8 full | none | none | 42–50 | 790–800 | 780–800 |
| int8 neg_ones | none | none | 32–38 | 790–800 | 795–800 |

The two limit columns are scored (E84-P3). The expected ranges are context only, never verdicts.

## Decision rules (frozen; `reduce_e84.py` implements them)

**Definitions.**

- **Burst clock**: the mean sampled clock from 1.5 s after the first launch to the end of the work, over the samples
  inside a kernel launch, at every clock the card reads. Card 0 has a 300 MHz point; E80 kept only 600/700/800, the
  only points aifoundry2 has. The **burst cell** is the mean of the two passes; its interval is the two passes.
- **Sustained clock**: the mean over the last 40 s of the work, every in-work sample, averaged over the kind's runs.
  The non-ramp mean is reported beside it.
- **Rates** (TFLOPS for fp32 and fp16, TOPS for int8) are the kernel's own operations over its own wall time, as
  E80's.
- **Card 0's own idle level**: the board W, die and clock between the sampler's start and the first launch, per run.
  p800 is E64's: the median board W in the first second at 800 MHz. **p800_sw** is p800 minus the same type's zeros
  p800. This replaces E80's switching term c, which rests on aifoundry2's registered B_f.
- **Burst limit**, from the trace ring: the first throttle-down line in the work (`power` or `thermal`), else
  `none`. The governor's inputs as the sampler reads them are reported beside it:
  - a die reading ≥ 66 °C in the prior 2 s → thermal;
  - otherwise the PMIC average over the TDP in the prior 0.5 s → power.
- **Sustained labels**: every in-work sample of the last 40 s gets one label, in the governor's own priority order:
  - `800`: it reads 800 MHz;
  - `thermal`: the last throttle-down line since its process started is thermal, or a die reading ≥ 66 °C in the
    prior 2 s;
  - `power`: the last throttle-down line since its process started is power, or, where the ring does not reach, the
    PMIC average over the TDP in the prior 0.5 s;
  - `ramp`: none of those, and no 800 MHz sample yet in its process;
  - `other`: anything else.

  The **sustained limit** is decided on the non-ramp samples:
  - `none` if ≥ 90% of them read 800;
  - otherwise `thermal` if the thermal label covers ≥ 50% of those below 800;
  - otherwise `power` if the power label does;
  - otherwise `unresolved`, which counts as wrong.

**Primary rules.**

- **E84-P1, zeros at least as fast as random data in every format.** clock(zeros) − clock(heavy) ≥ −10 MHz, where
  heavy is randn for fp32, randn for fp16 and full for int8. It is scored in the burst cell and in the sustained cell,
  six comparisons, and all six must hold.
- **E84-P2, int8 the least throttled.** With deficit = 800 MHz − clock, deficit(int8 full) ≤ deficit(fp16 randn) +
  5 MHz and ≤ deficit(fp32 randn) + 5 MHz. It is scored in the burst cells and in the sustained cells, and both must
  hold.
- **E84-P3, the limiting test read from the trace ring.** The measured burst limit matches the frozen label for at
  least 9 of the 11 kinds, and the sustained limit for at least 9 of 11. A kind is right only if every one of its runs
  carries the label.

**Secondary.**

- **E84-S1**: P2 on the format means of the sustained deficit over all the kinds measured.

**Under-resolved.** P1 needs six comparisons, P2 two and P3 eleven kinds per block. With fewer, a rule cannot PASS,
though a FAIL already decided by the cells present stands.

**Context, never a verdict.**

- The same cells on aifoundry2 from E80 (`--e80` reads its `results.json`);
- the zeros-over-random clock ratio on both cards;
- the firmware read at the start;
- the residencies.

**Departures from E80's design, named.**

1. 11 kinds, not 18, under a 60 card-minute cap. The kinds are the ones the brief named.
2. The burst mean counts every clock the card reads, not only 600/700/800.
3. The sustained limit is read on non-ramp samples. Where the ring does not reach, the power arm's own input (the
   PMIC average) labels power. E80 used a 1.5 s ramp window and left those samples `other`.
4. The configuration check compares with card 0's own start read.
5. Idle logins of other users do not end the session (lib.sh A3); device use by anyone on either card does.
6. Switching is read as p800 over the type's zeros, with card 0's own idle level per run, not E64's aifoundry2 B_f.
7. The two sustained replicates are fp32 zeros and fp32 randn, in their own block run last (`SUS2`), so the 11 primary
   sustained runs come first under the cap. `reduce_e84.py` passes them to `reduce_hpl.run_metrics` as SUS runs.

## What a result fills

For each of the 11 kinds, the blog's kinds-of-numbers table gets these cells on a second card and firmware build:

- burst MHz and sustained MHz;
- TFLOPS or TOPS at each;
- board W (p800, burst mean, sustained mean) and p800 over the type's zeros;
- die °C;
- the limiting test.

It also gets the zeros-over-random speed ratio beside aifoundry2's. The data goes to
`docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/`.

## Files

| file | what |
|---|---|
| `protocol.json` | the blocks, the tiles, the gates, the safety caps |
| `run_e84.py` | the runner: E80's `run_kspeed.py` and E64's `run_hpl.py`, with the five card-0 replacements |
| `run_e84.sh` | the stages on aifoundry1: `setup` (no device), `ident`, `smoke`, `go`, `status`, `wait`, `final` |
| `predictions.json` | the frozen predictions, the governor reading and the rules |
| `reduce_e84.py` | the registered reduction (per-run metrics from `reduce_hpl.run_metrics`, unchanged) |

Run on aifoundry1 from `~/nekko`, after copying `tools/claims-v3/kspeed/` there from the freeze commit:

```bash
E84_FREEZE=<sha> bash tools/claims-v3/kspeed/e84/run_e84.sh setup    # no device access
E84_FREEZE=<sha> bash tools/claims-v3/kspeed/e84/run_e84.sh ident    # after the claim
E84_FREEZE=<sha> bash tools/claims-v3/kspeed/e84/run_e84.sh smoke
E84_FREEZE=<sha> bash tools/claims-v3/kspeed/e84/run_e84.sh go
python3 tools/claims-v3/kspeed/e84/reduce_e84.py <data>/s1 --e80 docs/reports/data/2026-10-31-e80-kinds-speed/results.json \
  --out <data>/results.json > <data>/reduce.txt                       # on the Intel
```

## Amendments

*(none yet)*
