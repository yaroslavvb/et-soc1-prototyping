# V3-MF: the price of a flipped bit on the memory path (E75, Q129)

*Pre-registered Tue 27 Oct 2026 (week 44), 14:1x–15:3x PDT, on aifoundry1 (build and dry run only — no card was
opened anywhere for this file). Frozen at the commit that adds it, before the first measured pass on aifoundry3.
Changes after that go in Amendments, dated, before the data they touch.*

## The question

Q128 §5 item 5: **there is no flip ladder on a memory path.** A DRAM tensor load costs 94–134 pJ per byte where
a multiply-add costs 5.783 pJ, so the memory path is where most of a real kernel's energy goes, and the only
handle the catalogue has on its data dependence is one chord — zeros against random:

| path | zeros pJ/B | random pJ/B | the chord |
|---|---|---|---|
| L1 hit, `flw.ps` 32 B | 0.39 | 0.54 | +38% |
| own scratchpad, tensor load | 2.12 | 4.43 | +109% |
| DRAM, tensor load | 94.6 | 132.6 | +40% |
| L2 (3.11 pJ/B) and L3 (14.7 pJ/B) | — | — | **no pair at all**: 4.2's probe never set those bytes |

A chord is not a slope, and "random" moves two things at once: the number of **ones** carried and the number of
bits that **change** between consecutive transfers. One of them might be the whole story — a DDR bus with
data-bus inversion pays for ones; an on-chip bus pays for changes — and the chord cannot tell. This builds the
ladder at four levels and splits the two terms by construction.

## The design

Two kernels read a 256 B image the host repeats to fill whatever they touch, so the bytes on the wire are
designed, not sampled:

* **`ld_l1`** (EC_LD_L1, hand-written): eight `flw.ps` from `src+0, +32, … +224` — the image's eight **32 B
  blocks** in order, out of the L1. Element 256 bits, consecutive pairs (block i, block i+1).
* **`flw_pat`** (EC_FLW_PAT): 32 B vector loads `--stride 64` apart over `--region` bytes of this hart's slice,
  which the host fills with the image repeated. Stride 64 fetches **one 64 B line per load**, so the thing that
  travels is the line: element 512 bits, consecutive pairs (line i, line i+1). `--slice-bytes` sizes the working
  set and therefore picks the level, at 4.2's own sizes so the result is comparable to its published pJ/B.

`make_mf.py` builds each image from two values alternating, which makes both counts exact rather than
distributional: a toggling group T of k bit positions split in half between the two values (so every bit of T
changes on every transfer), plus W − k/2 static ones outside T (so both values carry W ones). Then
popcount(E_j ^ E_{j+1}) = k and popcount(E_j) = W **exactly**, for every j, and `--check` re-derives both from the
bytes on disk.

| arm | items | what varies | what is held |
|---|---|---|---|
| k-arm | `mf_<lvl>_k<k>` | bits changing per transfer | ones per element = half the element |
| w-arm | `mf_<lvl>_w<W>` | ones per element | bits changing = half the element |
| anchors | `mf_<lvl>_zeros`, `mf_<lvl>_random` | the catalogue's own two points | — |

Levels, `--harts 1` (1,024 harts, 32 per shire): `l1` the 256 B image; `l2` 8 KB per hart = 256 KB per shire,
half the L2; `l3` 24 KB per hart = 24 MB in all; `dram` 128 KB per hart = 128 MB in all, 4× the 32 MB L3.
Rungs: L1 k = 0, 64, 128, 192, 256 (of 256) and W = 64, 192; DRAM k = 0, 128, 256, 384, 512 (of 512) and
W = 128, 384; L2 and L3 k = 0, 256, 512 — their first data-dependence figures of any kind.

**The scratchpad is not a rung.** The host cannot seed a scratchpad: with `--scp` the kernel reads
`EC_SCP_ADDR(…)`, which no host fill reaches, and the 4.2 scratchpad rows were filled by a separate store pass.
A scratchpad ladder needs a kernel mode that copies the image in first; that is registered here as **out of
scope**, with the reason, rather than run on bytes nobody set.

## Frozen predictions

Reference counts for the random operand law (floats in [0.5, 2) reinterpreted as words): **11.944 changes and
18.167 ones per 32-bit word**, so 95.6 changes / 145.3 ones per 256-bit block and 191.1 changes / 290.7 ones per
512-bit line. Chord slopes, (random − zeros) ÷ changes, are what P1 and P2 are centred on.

| # | prediction |
|---|---|
| P1 | **L1**: the small-k slope (k = 0 → 64) is **0.03–0.12 pJ per changed bit** (the chord says 0.050; E60's register read-port bit is 0.0208) |
| P2 | **DRAM**: the small-k slope (k = 0 → 128) is **6–25 pJ per changed bit** (the chord says 12.73) |
| P3 | **Saturation**: at DRAM the k = 512 rung sits **20–60% below** the straight line through the small-k slope — the lesson of the arithmetic price list, which over-predicts a whole random word about 2× |
| P4 | **The chord is reproduced**: at L1 and at DRAM the random anchor lands within **±15%** of the ladder interpolated to the random-equivalent k (95.6 and 191.1) and the matching W |
| P5 | **The two arms close**: 191.1·e_flip + 290.7·e_one = **2,432 ± 600 pJ per line** at DRAM (the measured zeros→random chord, 38 pJ/B × 64 B), and the zeros anchor against the k = 0 rung (which carries 256 ones and no changes) gives e_one on its own |
| P6 | **Ordering**: e_flip rises monotonically L1 < L2 < L3 < DRAM, spanning at least 100× end to end |
| P7 | **Rates hold**: bytes/s inside 4.2's bands per level (L1 ~14.5 TB/s, DRAM 76 GB/s ± 25%); every burst's median `took_ms` recorded, and a burst above 60 ms dropped (the meter-starvation trap, 14-card-behaviour.md: DRAM reads push a telemetry sample to 23–206 ms) |

## Decision rules (registered)

1. **Estimator**: per level, within-pass least squares of board power on changed bits per transfer over the k-arm
   rungs, averaged over passes, two-sided t interval on the between-pass scatter (df = passes − 1). The slope is
   converted to pJ per changed bit with each run's **own measured** `bytes_per_s` and element size, never an
   assumed rate. The w-arm is fitted the same way for e_one.
2. **Saturation** is tested as the signed departure of the top rung from the line through the two lowest rungs,
   with its own interval; "curvature" is reported as a number, not as an adjective.
3. **Burst gate**: a run whose telemetry median `took_ms` exceeds 60 ms is dropped (the reruns' rule). A level
   that loses more than a third of its runs in a pass is reported as unresolved at that level, not averaged.
4. **Temperature**: preheat 59 °C, launch at the first reading ≤ 58 °C, cap 78 °C, three unreachable runs in a
   row void the pass. Die temperature recorded per run; the slopes are reported with and without a temperature
   covariate.
5. **Passes**: target **3** (the DRAM arm's effect is ~40% of a large number), extend to 5 if the lane is free.
   L1's effect is small in absolute terms; if its interval spans zero after 3 passes it is reported as a bound.
6. **What it changes.** It closes the second half of Q128 §5 item 5 and gives the Horace chain the memory path's
   data-dependent term — the price per flipped bit at four levels, plus the first data-dependence figure for the
   L2 and the L3. It does **not** move the 3.837 pJ unaccounted on the multiply-add (that is arithmetic); it
   makes the load-to-watts model's memory term a measured coefficient instead of a chord, and it tells the
   "5.783 pJ per MAC vs 94–134 pJ per DRAM byte" comparison how much of the DRAM figure is the data and how much
   is the path.

## How to run it (aifoundry3, after E70 and E71)

    ssh aifoundry3
    cd ~/aifoundry
    bash tools/claims-v3/mf/run_e75.sh setup          # operand set + --check, pattern check, .text hashes, dry run
    bash tools/claims-v3/mf/run_e75.sh go 7510 3      # three passes, all four levels; log build/e75-mf.log
    # or, if the lane is short:
    bash tools/claims-v3/mf/run_e75.sh go1 7510 3     # L1 and DRAM only

**On aifoundry1 the dry run needs a card named** — `lib.sh` refuses to guess between its two cards —
so prefix it with `V3_DEVICE=0`. Under `V3_DRY=1` that opens nothing: it only names the data directory.

Watch: `ssh aifoundry3 'tail -3 ~/aifoundry/build/e75-mf.log'`. Stop between passes:
`touch ~/aifoundry/build/mf-STOP`. Data in `build/claims-v3/aifoundry3/mf/p<pass>/`; collect into
`docs/reports/data/2026-10-27-e75-memory-flip-ladder/`.

## Risks, and what each one does to the result

- **The meter starves on DRAM bursts** (14-card-behaviour.md): samples at 23–206 ms, 683 ms at worst, so a 4 s
  burst can get a handful of stale readings. Mitigation: rule 3's 60 ms gate, `--seconds 4` (ten 0.4 s launches
  per run, not one), and `took_ms` kept per sample. This is the largest risk to the DRAM arm.
- **Two values alternating is a maximally correlated pattern.** If the DRAM interface does data-bus inversion or
  any history-dependent encoding, a 2-cycle is not random data with the same counts. P4 is the test: if the
  random anchor does not land where the ladder says, the ladder measures the 2-cycle and not the general case,
  and that is the finding. Registered, not hidden.
- **The DRAM rung allocates 272 MB on the card** (2,048 × (128 KB + 8 KB of bank slack)) and the host fills and
  copies it before the first launch, inside the 10 s cap. If the run times out (rc 124, no `ENERCAT` line) the
  item is dropped and the level is re-registered at 64 KB per hart in an amendment. The dry run prints the
  command for inspection; the first real pass is the test.
- **L1's effect is small**: 0.15 pJ/B of 0.54 across the whole chord. Rule 5 turns an unresolved L1 into a bound.
- **Level identity.** 128 KB per hart is 4× the L3, not 8× as 4.2's DRAM row; some fraction of the DRAM rung's
  lines will hit the L3. The measured `bytes_per_s` per run is the check (DRAM's own line rate is 76 GB/s), and
  the level label in the data is `dram_4x_l3`, not `dram`.
- **Another user, or the demo service on aifoundry3**: `block.sh` stops on another user's device process or lock,
  holds `/run/lock/etsoc-shire0.lock`, and caps every device process at `timeout 10`.
- **No card is opened on aifoundry1**: `setup` and `dry` run under `V3_DRY=1`.

## Files

| file | what it is |
|---|---|
| `make_mf.py` | the operand images, the per-level commands, the designed counts; `--check` re-derives k and W from the bytes |
| `block.sh` | one pass as a `lib.sh` block: card lock, sampler, `timeout 10` per device process, stop on another user |
| `queue_mf.sh` | passes back to back, detached, stopping on `build/mf-STOP` |
| `run_e75.sh` | `setup` / `dry` / `go` / `go1` |
| `predictions.json` | P1–P7 and the decision rules, frozen with this commit |
| `../runitems.py` | the manifest-driven runner (per-item device arguments), with run_hl.py's approach protocol and record format |

## Amendments

*(none yet)*
